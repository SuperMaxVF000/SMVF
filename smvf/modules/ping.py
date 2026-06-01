# Встроенный модуль SMVF: Ping
# Команда .ping — замеряет задержку, показывает аптайм
# Поддерживает кастомное изображение (.pingset <url>)
# Поддерживает premium emoji если у пользователя есть Telegram Premium

import logging
import time
from telethon import events

from ..core.database import get as cfg_get, set_value as cfg_set, runtime_get
from ..core.dispatcher import register_builtin
from ..inline.manager import send_via_inline
from ..utils.helpers import format_uptime, escape_html

logger = logging.getLogger(__name__)

# Ключи в конфиге
_PING_IMAGE_KEY = "ping_custom_image"

# Время старта (устанавливается при регистрации)
_start_time: float = 0.0


def register(client) -> None:
    """Регистрируем команды ping-модуля."""
    global _start_time
    _start_time = runtime_get("start_time", time.time())

    register_builtin("ping", _ping_handler)
    register_builtin("pingset", _pingset_handler)
    register_builtin("pingreset", _pingreset_handler)

    logger.debug("Модуль ping зарегистрирован")


async def _ping_handler(event: events.NewMessage.Event) -> None:
    """
    .ping — проверка связи.
    Измеряет задержку редактирования сообщения.
    Если установлено изображение — отправляет через inline via @bot.
    """
    start = time.perf_counter_ns()

    # Первый edit для измерения задержки
    msg = await event.edit("🏓")
    elapsed_ms = round((time.perf_counter_ns() - start) / 1_000_000, 2)

    uptime_secs = time.time() - _start_time
    uptime_str  = format_uptime(uptime_secs)

    # Проверяем premium для красивых emoji
    me = await event.client.get_me()
    has_premium = getattr(me, "premium", False)

    if has_premium:
        ping_icon = '<emoji document_id=5431449001532594346>⚡️</emoji>'
        up_icon   = '<emoji document_id=5451646226975955576>⌛️</emoji>'
    else:
        ping_icon = "⚡️"
        up_icon   = "⏱"

    text = (
        f"{ping_icon} <b>Pong!</b>\n\n"
        f"📡 <b>Задержка:</b> <code>{elapsed_ms} мс</code>\n"
        f"{up_icon} <b>Аптайм:</b> <code>{uptime_str}</code>"
    )

    custom_image = cfg_get(_PING_IMAGE_KEY, "")

    if custom_image:
        # Удаляем текущее сообщение и отправляем через inline (via @bot)
        await msg.delete()
        bot_username = cfg_get("inline_bot_username", "")
        if bot_username:
            try:
                query = f"photo:{custom_image}|{text}"
                results = await event.client.inline_query(bot_username, query[:255])
                if results:
                    await results[0].click(event.chat_id)
                    return
            except Exception as e:
                logger.debug("Ping inline ошибка: %s", e)
        # Fallback: отправляем фото напрямую
        await event.client.send_file(
            event.chat_id,
            custom_image,
            caption=text,
            parse_mode="html",
        )
    else:
        await msg.edit(text, parse_mode="html")


async def _pingset_handler(event: events.NewMessage.Event) -> None:
    """
    .pingset <url> — устанавливаем кастомное изображение для пинга.
    .pingset (без аргументов) — показываем текущее изображение.
    """
    text = event.raw_text or ""
    args = text.split(None, 1)

    if len(args) < 2:
        current = cfg_get(_PING_IMAGE_KEY, "")
        if current:
            await event.edit(
                f"🖼 <b>Текущее изображение ping:</b>\n<code>{escape_html(current)}</code>\n\n"
                "Используй <code>.pingset &lt;url&gt;</code> чтобы изменить\n"
                "или <code>.pingreset</code> чтобы сбросить.",
                parse_mode="html",
            )
        else:
            await event.edit(
                "🖼 Изображение для ping не установлено.\n"
                "Используй <code>.pingset &lt;url&gt;</code> чтобы установить.",
                parse_mode="html",
            )
        return

    url = args[1].strip()
    if not url.startswith(("http://", "https://")):
        await event.edit("❌ Укажите корректный URL (http:// или https://)", parse_mode="html")
        return

    cfg_set(_PING_IMAGE_KEY, url)
    await event.edit(
        f"✅ <b>Изображение для ping установлено!</b>\n<code>{escape_html(url)}</code>",
        parse_mode="html",
    )


async def _pingreset_handler(event: events.NewMessage.Event) -> None:
    """
    .pingreset — сбрасываем кастомное изображение.
    """
    cfg_set(_PING_IMAGE_KEY, "")
    await event.edit("✅ Изображение для ping сброшено.", parse_mode="html")
