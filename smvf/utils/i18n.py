# Интернационализация — все строки интерфейса SMVF
# Язык выбирается один раз при первом запуске и сохраняется в конфиге

from typing import Dict, Any

# Все строки интерфейса
_STRINGS: Dict[str, Dict[str, str]] = {

    # ── Приветствие и первый запуск ────────────────────────────────────────
    "welcome": {
        "ru": (
            "╔══════════════════════════════╗\n"
            "║   SMVF Userbot v{version}      ║\n"
            "║   by @SuperMaxVF             ║\n"
            "╚══════════════════════════════╝"
        ),
        "en": (
            "╔══════════════════════════════╗\n"
            "║   SMVF Userbot v{version}      ║\n"
            "║   by @SuperMaxVF             ║\n"
            "╚══════════════════════════════╝"
        ),
    },
    "choose_lang": {
        "ru": "Выберите язык / Choose language:\n  [1] Русский\n  [2] English",
        "en": "Выберите язык / Choose language:\n  [1] Русский\n  [2] English",
    },
    "lang_set": {
        "ru": "✅ Язык установлен: Русский",
        "en": "✅ Language set: English",
    },

    # ── Настройка учётных данных ───────────────────────────────────────────
    "setup_header": {
        "ru": "🔧 Первоначальная настройка SMVF",
        "en": "🔧 SMVF Initial Setup",
    },
    "setup_api_id": {
        "ru": "Введите API_ID (число с my.telegram.org): ",
        "en": "Enter API_ID (number from my.telegram.org): ",
    },
    "setup_api_hash": {
        "ru": "Введите API_HASH (строка с my.telegram.org): ",
        "en": "Enter API_HASH (string from my.telegram.org): ",
    },
    "setup_phone": {
        "ru": "Введите номер телефона (формат +79001234567): ",
        "en": "Enter phone number (format +79001234567): ",
    },
    "setup_prefix": {
        "ru": "Введите префикс команд (Enter = '.'): ",
        "en": "Enter command prefix (Enter = '.'): ",
    },
    "setup_saved": {
        "ru": "✅ Настройки сохранены в config.json",
        "en": "✅ Settings saved to config.json",
    },
    "setup_error_api_id": {
        "ru": "❌ API_ID должен быть числом. Попробуйте снова.",
        "en": "❌ API_ID must be a number. Try again.",
    },

    # ── Подключение ────────────────────────────────────────────────────────
    "connecting": {
        "ru": "🔌 Подключение к Telegram...",
        "en": "🔌 Connecting to Telegram...",
    },
    "connected": {
        "ru": "✅ Подключён как {name} (ID: {id})",
        "en": "✅ Connected as {name} (ID: {id})",
    },
    "connect_failed": {
        "ru": "❌ Ошибка подключения: {error}",
        "en": "❌ Connection failed: {error}",
    },
    "reconnecting": {
        "ru": "🔄 Переподключение... попытка {attempt}/{max}",
        "en": "🔄 Reconnecting... attempt {attempt}/{max}",
    },
    "reconnect_ok": {
        "ru": "✅ Переподключение успешно",
        "en": "✅ Reconnected successfully",
    },
    "reconnect_fail": {
        "ru": "❌ Не удалось переподключиться. Ожидание {secs}с...",
        "en": "❌ Reconnect failed. Waiting {secs}s...",
    },

    # ── Inline-бот ────────────────────────────────────────────────────────
    "inline_creating": {
        "ru": "🤖 Создание inline-бота...",
        "en": "🤖 Creating inline bot...",
    },
    "inline_created": {
        "ru": "✅ Inline-бот создан: @{username}",
        "en": "✅ Inline bot created: @{username}",
    },
    "inline_exists": {
        "ru": "✅ Inline-бот активен: @{username}",
        "en": "✅ Inline bot active: @{username}",
    },
    "inline_fail": {
        "ru": "⚠️ Не удалось создать inline-бота. Введите токен вручную:",
        "en": "⚠️ Failed to create inline bot. Enter token manually:",
    },
    "inline_token_prompt": {
        "ru": "Токен бота от @BotFather (или Enter чтобы пропустить): ",
        "en": "Bot token from @BotFather (or Enter to skip): ",
    },
    "inline_skip": {
        "ru": "⚠️ Inline-бот не настроен. Некоторые функции недоступны.",
        "en": "⚠️ Inline bot not configured. Some features unavailable.",
    },

    # ── Лог-группа ────────────────────────────────────────────────────────
    "loggroup_creating": {
        "ru": "📋 Создание лог-группы...",
        "en": "📋 Creating log group...",
    },
    "loggroup_created": {
        "ru": "✅ Лог-группа создана",
        "en": "✅ Log group created",
    },
    "loggroup_exists": {
        "ru": "✅ Лог-группа найдена",
        "en": "✅ Log group found",
    },

    # ── Модули ────────────────────────────────────────────────────────────
    "modules_loading": {
        "ru": "📦 Загрузка модулей...",
        "en": "📦 Loading modules...",
    },
    "module_loaded": {
        "ru": "✅ Модуль загружен: {name} [{type}]",
        "en": "✅ Module loaded: {name} [{type}]",
    },
    "module_failed": {
        "ru": "❌ Ошибка загрузки {name}: {error}",
        "en": "❌ Failed to load {name}: {error}",
    },
    "modules_done": {
        "ru": "📦 Загружено модулей: {count}",
        "en": "📦 Modules loaded: {count}",
    },
    "module_incompatible": {
        "ru": "⚠️ Модуль {name} пропущен (несовместим)",
        "en": "⚠️ Module {name} skipped (incompatible)",
    },

    # ── Готовность ────────────────────────────────────────────────────────
    "ready": {
        "ru": (
            "╔════════════════════════════════════╗\n"
            "║  ✅ SMVF запущен и готов к работе  ║\n"
            "╚════════════════════════════════════╝"
        ),
        "en": (
            "╔════════════════════════════════════╗\n"
            "║  ✅ SMVF is running and ready      ║\n"
            "╚════════════════════════════════════╝"
        ),
    },
    "startup_msg": {
        "ru": (
            "🚀 <b>SMVF Userbot запущен</b>\n\n"
            "👤 Аккаунт: {name}\n"
            "🕐 Время запуска: {time}\n"
            "📱 Платформа: {platform}\n"
            "📦 Модулей загружено: {modules}\n"
            "🤖 Inline-бот: @{bot}\n\n"
            "🔗 <a href=\"https://t.me/MadeBySuperMaxVF\">Канал</a> | "
            "<a href=\"https://github.com/SuperMaxVF000\">GitHub</a>"
        ),
        "en": (
            "🚀 <b>SMVF Userbot started</b>\n\n"
            "👤 Account: {name}\n"
            "🕐 Start time: {time}\n"
            "📱 Platform: {platform}\n"
            "📦 Modules loaded: {modules}\n"
            "🤖 Inline bot: @{bot}\n\n"
            "🔗 <a href=\"https://t.me/MadeBySuperMaxVF\">Channel</a> | "
            "<a href=\"https://github.com/SuperMaxVF000\">GitHub</a>"
        ),
    },

    # ── Остановка ─────────────────────────────────────────────────────────
    "stopping": {
        "ru": "⛔ Остановка SMVF...",
        "en": "⛔ Stopping SMVF...",
    },
    "stopped": {
        "ru": "⛔ SMVF остановлен",
        "en": "⛔ SMVF stopped",
    },

    # ── Платформы ─────────────────────────────────────────────────────────
    "platform_rpi":     {"ru": "🍓 Raspberry Pi", "en": "🍓 Raspberry Pi"},
    "platform_termux":  {"ru": "📱 Android (Termux)", "en": "📱 Android (Termux)"},
    "platform_userland":{"ru": "📱 Android (UserLand)", "en": "📱 Android (UserLand)"},
    "platform_linux":   {"ru": "🐧 Linux", "en": "🐧 Linux"},
    "platform_unknown": {"ru": "❓ Неизвестно", "en": "❓ Unknown"},

    # ── Ошибки ────────────────────────────────────────────────────────────
    "python_version": {
        "ru": "❌ Требуется Python {min}+. Установлен: {current}",
        "en": "❌ Python {min}+ required. Installed: {current}",
    },
    "config_not_found": {
        "ru": "⚙️ Конфиг не найден. Запускаем мастер настройки...",
        "en": "⚙️ Config not found. Starting setup wizard...",
    },
}


# Текущий язык (загружается из конфига)
_current_lang: str = "ru"


def set_lang(lang: str) -> None:
    """Устанавливаем язык интерфейса."""
    global _current_lang
    if lang in ("ru", "en"):
        _current_lang = lang


def get_lang() -> str:
    """Возвращаем текущий язык."""
    return _current_lang


def t(key: str, **kwargs: Any) -> str:
    """
    Получаем строку по ключу на текущем языке.

    :param key: Ключ строки из _STRINGS.
    :param kwargs: Аргументы для format().
    :return: Строка на текущем языке.
    """
    entry = _STRINGS.get(key, {})
    text = entry.get(_current_lang, entry.get("ru", f"[{key}]"))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text
