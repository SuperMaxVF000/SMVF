# SMVF Userbot — точка входа
# Порядок инициализации:
#   1. Проверка Python
#   2. Загрузка конфига / мастер настройки
#   3. Настройка логирования
#   4. Подключение к Telegram
#   5. Создание inline-бота
#   6. Создание лог-группы
#   7. Загрузка встроенных модулей
#   8. Загрузка внешних модулей
#   9. Отправка стартового сообщения
#  10. Keepalive loop

import asyncio
import importlib
import logging
import signal
import sys
import time

from .version import __version_str__, MIN_PYTHON, SESSION_NAME
from .utils.colors import Colors, cprint
from .utils.i18n import set_lang, t
from .utils.logger import setup_logging, install_tg_log, stop_tg_log
from .utils.platform import detect_platform
from .core.database import load_config, get as cfg_get, set_value as cfg_set, runtime_set
from .core.dispatcher import setup_dispatcher
from .core.keepalive import keepalive_loop, request_shutdown
from .core.loader import load_all_modules

logger = logging.getLogger(__name__)

EXTERNAL_MODULES_DIR = "modules"


def run() -> None:
    """Точка входа SMVF. Вызывается из __main__.py."""
    # Проверка версии Python
    if sys.version_info < MIN_PYTHON:
        min_str = ".".join(str(x) for x in MIN_PYTHON)
        cur_str = ".".join(str(x) for x in sys.version_info[:3])
        print(t("python_version", min=min_str, current=cur_str))
        sys.exit(1)

    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        cprint("\n" + t("stopped"), Colors.YELLOW)
    except Exception as e:
        cprint(f"\n❌ Критическая ошибка: {e}", Colors.RED)
        logger.critical("Критическая ошибка при запуске", exc_info=True)
        sys.exit(1)


async def _main() -> None:
    """Главная асинхронная функция."""

    # ── Шаг 1: Конфиг ────────────────────────────────────────────────────
    config = load_config()
    lang = config.get("language", "ru")
    set_lang(lang)

    # ── Шаг 2: Логирование ────────────────────────────────────────────────
    setup_logging()

    # Баннер
    _print_banner()

    # ── Шаг 3: Подключение к Telegram ────────────────────────────────────
    from telethon import TelegramClient
    from .core.database import get_credentials

    api_id, api_hash, phone = get_credentials()
    prefix = cfg_get("command_prefix", ".")

    cprint(t("connecting"), Colors.CYAN)

    client = TelegramClient(SESSION_NAME, api_id, api_hash)

    # Подключаемся и авторизуемся
    await _authorize(client, phone)

    me = await client.get_me()
    name = f"{me.first_name or ''} {me.last_name or ''}".strip() or str(me.id)
    cprint(t("connected", name=name, id=me.id), Colors.GREEN)

    # Сохраняем время старта
    start_time = time.time()
    runtime_set("start_time", start_time)
    runtime_set("me", me)

    # ── Шаг 4: Диспетчер команд ──────────────────────────────────────────
    setup_dispatcher(client)

    # ── Шаг 5: Встроенные модули ──────────────────────────────────────────
    cprint(t("modules_loading"), Colors.CYAN)
    builtin_count = _load_builtin_modules(client, prefix, lang)
    logger.info("Встроенных модулей загружено: %d", builtin_count)

    # ── Шаг 6: Inline-бот ────────────────────────────────────────────────
    from .inline.manager import setup_inline_bot, get_bot_username
    bot_ready = await setup_inline_bot(client)
    bot_username = get_bot_username() or "—"

    # ── Шаг 7: Лог-группа ────────────────────────────────────────────────
    log_chat_id = await _setup_log_group(client, me, bot_username)
    if log_chat_id:
        install_tg_log(client, log_chat_id)

    # ── Шаг 8: Внешние модули ────────────────────────────────────────────
    ext_count = await load_all_modules(client, EXTERNAL_MODULES_DIR, prefix, lang)
    total_modules = builtin_count + ext_count
    cprint(t("modules_done", count=total_modules), Colors.GREEN)

    # ── Шаг 9: Стартовое сообщение ───────────────────────────────────────
    platform_str = _platform_display()
    start_msg = t(
        "startup_msg",
        name=name,
        time=time.strftime("%Y-%m-%d %H:%M:%S"),
        platform=platform_str,
        modules=total_modules,
        bot=bot_username,
    )

    # Отправляем в лог-группу
    if log_chat_id:
        try:
            await client.send_message(log_chat_id, start_msg, parse_mode="html")
        except Exception as e:
            logger.warning("Не удалось отправить стартовое сообщение: %s", e)

    cprint(t("ready"), Colors.BRIGHT_GREEN, bold=True)

    # ── Шаг 10: Keepalive ────────────────────────────────────────────────
    # Graceful shutdown при SIGTERM / SIGINT
    loop = asyncio.get_event_loop()

    def _handle_signal() -> None:
        cprint(t("stopping"), Colors.YELLOW)
        request_shutdown()

    try:
        loop.add_signal_handler(signal.SIGTERM, _handle_signal)
        loop.add_signal_handler(signal.SIGINT,  _handle_signal)
    except NotImplementedError:
        pass  # Windows

    try:
        await keepalive_loop(client)
    finally:
        await stop_tg_log()
        cprint(t("stopped"), Colors.YELLOW)
        if client.is_connected():
            await client.disconnect()


async def _authorize(client, phone: str) -> None:
    """
    Явный интерактивный флоу авторизации Telegram.
    Не использует client.start() чтобы избежать проблем с вводом
    в контейнерных средах (UserLand, Docker).

    Алгоритм:
      1. Подключаемся.
      2. Если сессия уже авторизована — готово.
      3. Запрашиваем код через явный input() в терминале.
      4. Если нужен пароль 2FA — запрашиваем его.

    :param client: Telethon TelegramClient (не подключён).
    :param phone: Номер телефона из конфига.
    """
    import asyncio
    from telethon.errors import (
        SessionPasswordNeededError,
        PhoneCodeInvalidError,
        PhoneCodeExpiredError,
        FloodWaitError,
    )

    await client.connect()

    if await client.is_user_authorized():
        return

    cprint("📱 Авторизация — отправляем код на " + phone, Colors.CYAN)

    # Запрашиваем отправку кода
    try:
        sent = await client.send_code_request(phone)
    except FloodWaitError as e:
        cprint(f"❌ Слишком много попыток. Подождите {e.seconds} секунд.", Colors.RED)
        raise

    # Цикл ввода кода (до 3 попыток)
    for attempt in range(1, 4):
        try:
            code = input(
                f"🔑 Введите код из Telegram (попытка {attempt}/3): "
            ).strip()
            if not code:
                cprint("❌ Код не может быть пустым.", Colors.RED)
                continue

            await client.sign_in(phone, code, phone_code_hash=sent.phone_code_hash)
            cprint("✅ Авторизация успешна!", Colors.GREEN)
            return

        except PhoneCodeInvalidError:
            cprint("❌ Неверный код. Попробуйте ещё раз.", Colors.RED)
            if attempt == 3:
                raise

        except PhoneCodeExpiredError:
            cprint("❌ Код истёк. Запрашиваем новый...", Colors.YELLOW)
            sent = await client.send_code_request(phone)

        except SessionPasswordNeededError:
            # Двухфакторная аутентификация
            cprint("🔐 Требуется пароль 2FA.", Colors.YELLOW)
            for pwd_attempt in range(1, 4):
                import getpass
                password = getpass.getpass(
                    f"🔐 Введите пароль 2FA (попытка {pwd_attempt}/3): "
                )
                try:
                    await client.sign_in(password=password)
                    cprint("✅ Авторизация с 2FA успешна!", Colors.GREEN)
                    return
                except Exception as pwd_err:
                    cprint(f"❌ Неверный пароль: {pwd_err}", Colors.RED)
                    if pwd_attempt == 3:
                        raise
            return


def _load_builtin_modules(client, prefix: str, lang: str) -> int:
    """
    Загружаем встроенные модули через прямой импорт.

    :return: Количество успешно загруженных.
    """
    from .modules import BUILTIN_MODULES
    count = 0
    for mod_path in BUILTIN_MODULES:
        try:
            mod = importlib.import_module(mod_path)
            if hasattr(mod, "register"):
                mod.register(client)
                name = mod_path.split(".")[-1]
                logger.info(t("module_loaded", name=name, type="builtin"))
                count += 1
        except Exception as e:
            name = mod_path.split(".")[-1]
            logger.error(t("module_failed", name=name, error=str(e)))
    return count


async def _setup_log_group(client, me, bot_username: str) -> int | None:
    """
    Создаём или находим лог-группу.
    Если ID уже сохранён в конфиге — проверяем что группа существует.

    :return: ID лог-группы или None.
    """
    saved_id = cfg_get("log_chat_id")

    # Проверяем существующую группу
    if saved_id:
        try:
            await client.get_entity(saved_id)
            cprint(t("loggroup_exists"), Colors.GREEN)
            return saved_id
        except Exception:
            logger.warning("Лог-группа не найдена (ID: %s), создаём новую...", saved_id)

    cprint(t("loggroup_creating"), Colors.CYAN)

    try:
        from telethon.tl.functions.channels import CreateChannelRequest, InviteToChannelRequest
        from telethon.tl.functions.messages import ExportChatInviteRequest

        # Создаём мегагруппу
        result = await client(CreateChannelRequest(
            title="SMVF Logs",
            about="SMVF Userbot — системные логи",
            megagroup=True,
        ))
        chat = result.chats[0]
        chat_id = chat.id

        # Добавляем inline-бота если он создан
        if bot_username and bot_username != "—":
            try:
                bot_entity = await client.get_entity(f"@{bot_username}")
                await client(InviteToChannelRequest(chat, [bot_entity]))
            except Exception as e:
                logger.warning("Не удалось добавить бота в лог-группу: %s", e)

        # Сохраняем ID (с минусом — это супергруппа)
        full_id = int(f"-100{chat_id}")
        cfg_set("log_chat_id", full_id)
        cprint(t("loggroup_created"), Colors.GREEN)
        return full_id

    except Exception as e:
        logger.error("Ошибка создания лог-группы: %s", e)
        return None


def _platform_display() -> str:
    """Строка платформы для стартового сообщения."""
    key = detect_platform()
    icons = {
        "rpi":      "🍓 Raspberry Pi",
        "termux":   "📱 Android (Termux)",
        "userland": "📱 Android (UserLand)",
        "linux":    "🐧 Linux",
        "unknown":  "❓ Unknown",
    }
    return icons.get(key, "❓ Unknown")


def _print_banner() -> None:
    """Печатаем ASCII-баннер в терминал."""
    banner = f"""
{Colors.BRIGHT_CYAN}{Colors.BOLD}
  ███████╗███╗   ███╗██╗   ██╗███████╗
  ██╔════╝████╗ ████║██║   ██║██╔════╝
  ███████╗██╔████╔██║██║   ██║█████╗
  ╚════██║██║╚██╔╝██║╚██╗ ██╔╝██╔══╝
  ███████║██║ ╚═╝ ██║ ╚████╔╝ ██║
  ╚══════╝╚═╝     ╚═╝  ╚═══╝  ╚═╝
{Colors.RESET}{Colors.BRIGHT_WHITE}         Userbot v{__version_str__} by @SuperMaxVF
{Colors.DIM}   t.me/MadeBySuperMaxVF | github.com/SuperMaxVF000
{Colors.RESET}"""
    print(banner)
