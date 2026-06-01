# Менеджер inline-бота SMVF v1.2beta
# Inline-бот отвечает на запросы юзербота через inline_query
# Сообщения отправляются "via @smvfinlineXXXX" — именно так работает Hikka

import asyncio
import logging
from typing import Optional

from telethon import TelegramClient as BotClient
from telethon import events

from ..core.database import get as cfg_get, set_value as cfg_set
from ..inline.botfather import auto_create_bot, verify_token
from ..utils.colors import Colors, cprint
from ..utils.i18n import t

logger = logging.getLogger(__name__)

_bot_client:   Optional[BotClient] = None
_bot_username: Optional[str]       = None


def get_bot_client() -> Optional[BotClient]:
    return _bot_client

def get_bot_username() -> Optional[str]:
    return _bot_username


async def setup_inline_bot(main_client) -> bool:
    global _bot_client, _bot_username

    saved_token    = cfg_get("inline_bot_token", "")
    saved_username = cfg_get("inline_bot_username", "")

    # Проверяем сохранённый токен
    if saved_token:
        verified = await verify_token(saved_token)
        if verified:
            _bot_username = verified
            cprint(t("inline_exists", username=verified), Colors.GREEN)
            await _start_bot_client(main_client, saved_token)
            return True
        else:
            logger.warning("Сохранённый токен недействителен, создаём новый...")
            cfg_set("inline_bot_token",    "")
            cfg_set("inline_bot_username", "")

    # Автосоздание
    result = await auto_create_bot(main_client)
    if result:
        token, username = result
        cfg_set("inline_bot_token",    token)
        cfg_set("inline_bot_username", username)
        _bot_username = username
        await _start_bot_client(main_client, token)
        return True

    # Ручной ввод
    cprint(t("inline_fail"), Colors.YELLOW)
    token_input = input(t("inline_token_prompt")).strip()
    if token_input:
        verified = await verify_token(token_input)
        if verified:
            cfg_set("inline_bot_token",    token_input)
            cfg_set("inline_bot_username", verified)
            _bot_username = verified
            cprint(t("inline_exists", username=verified), Colors.GREEN)
            await _start_bot_client(main_client, token_input)
            return True

    cprint(t("inline_skip"), Colors.YELLOW)
    return False


async def _start_bot_client(main_client, token: str) -> None:
    global _bot_client

    from ..version import BOT_SESSION_NAME

    api_id   = cfg_get("api_id")
    api_hash = cfg_get("api_hash")

    bot = BotClient(BOT_SESSION_NAME, api_id, api_hash)
    await bot.start(bot_token=token)
    _bot_client = bot

    _register_handlers(bot, main_client)
    asyncio.create_task(_run_bot(bot))
    logger.info("Inline-бот запущен: @%s", _bot_username)


def _register_handlers(bot: BotClient, main_client) -> None:

    @bot.on(events.InlineQuery)
    async def on_inline(event: events.InlineQuery) -> None:
        query = (event.text or "").strip()
        await _handle_inline_query(event, query)

    @bot.on(events.CallbackQuery)
    async def on_callback(event: events.CallbackQuery) -> None:
        await _handle_callback(event, main_client)


async def _handle_inline_query(event: events.InlineQuery, query: str) -> None:
    """
    Обрабатываем inline-запросы.
    Форматы:
      photo:<url>|<caption>   — фото с подписью
      gif:<url>|<caption>     — анимация/GIF
      video:<url>|<caption>   — видео
      <текст>                 — текстовое сообщение
    """
    try:
        builder = event.builder

        if not query:
            await event.answer([
                builder.article(title="SMVF Userbot", text="🤖 SMVF Inline Bot активен")
            ], cache_time=0)
            return

        # Фото
        if query.startswith("photo:"):
            rest = query[6:]
            url, caption = (rest.split("|", 1) + [""])[:2]
            await event.answer([
                builder.photo(file=url.strip(), text=caption.strip() or None, parse_mode="html")
            ], cache_time=0)
            return

        # GIF / анимация
        if query.startswith("gif:"):
            rest = query[4:]
            url, caption = (rest.split("|", 1) + [""])[:2]
            await event.answer([
                builder.document(
                    file=url.strip(),
                    text=caption.strip() or None,
                    parse_mode="html",
                )
            ], cache_time=0)
            return

        # Видео
        if query.startswith("video:"):
            rest = query[6:]
            url, caption = (rest.split("|", 1) + [""])[:2]
            await event.answer([
                builder.document(
                    file=url.strip(),
                    text=caption.strip() or None,
                    parse_mode="html",
                )
            ], cache_time=0)
            return

        # Текст с кнопками: текст||btn_name:url||btn2:url2
        if "||" in query:
            parts   = query.split("||")
            text    = parts[0].strip()
            from telethon import Button
            buttons = []
            for btn_raw in parts[1:]:
                if ":" in btn_raw:
                    bname, burl = btn_raw.split(":", 1)
                    burl = burl.strip()
                    if burl.startswith(("http", "t.me", "tg://")):
                        buttons.append([Button.url(bname.strip(), burl)])
            await event.answer([
                builder.article(
                    title="Message",
                    text=text,
                    parse_mode="html",
                    buttons=buttons or None,
                )
            ], cache_time=0)
            return

        # Обычный текст
        await event.answer([
            builder.article(title="Message", text=query, parse_mode="html")
        ], cache_time=0)

    except Exception as e:
        logger.error("Inline query ошибка: %s", e)
        try:
            await event.answer([
                event.builder.article(title="Error", text="⚠️ Ошибка")
            ], cache_time=0)
        except Exception:
            pass


async def _handle_callback(event: events.CallbackQuery, main_client) -> None:
    try:
        me     = await main_client.get_me()
        sender = await event.get_sender()
        if sender.id != me.id:
            await event.answer("❌ Эта кнопка не для вас", alert=True)
            return

        data = event.data or b""

        if data == b"confirm_yes":
            from ..core.database import runtime_get, runtime_del
            key = f"confirm_{event.chat_id}_{me.id}"
            cmd = runtime_get(key)
            if cmd:
                runtime_del(key)
                await event.answer("✅ Подтверждено")
                await main_client.send_message(event.chat_id, cmd)
            else:
                await event.answer("❌ Истекло")

        elif data == b"confirm_no":
            from ..core.database import runtime_del
            runtime_del(f"confirm_{event.chat_id}_{me.id}")
            await event.answer("❌ Отменено")
            await event.edit("❌ Отменено")
        else:
            await event.answer()

    except Exception as e:
        logger.error("Callback ошибка: %s", e)


async def _run_bot(bot: BotClient) -> None:
    while True:
        try:
            await bot.run_until_disconnected()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.warning("Inline-бот упал: %s. Перезапуск через 10с...", e)
            await asyncio.sleep(10)
            try:
                await bot.connect()
            except Exception:
                pass


async def send_via_inline(main_client, chat_id: int, text: str, image_url: str = "") -> bool:
    """
    Отправляем сообщение через inline-бота — появляется "via @smvfinlineXXXX".

    :param main_client: Клиент юзербота.
    :param chat_id: ID чата.
    :param text: Текст (HTML).
    :param image_url: Если есть — отправляем как фото.
    :return: True если успешно.
    """
    if not _bot_username:
        return False
    try:
        if image_url:
            query = f"photo:{image_url}|{text}"
        else:
            query = text
        # Обрезаем до 255 символов — лимит inline query
        results = await main_client.inline_query(_bot_username, query[:255])
        if results:
            await results[0].click(chat_id)
            return True
    except Exception as e:
        logger.debug("send_via_inline: %s", e)
    return False
