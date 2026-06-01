# Встроенный модуль SMVF v1.2beta: Info
# .info — карточка информации через inline-бота (via @smvfinlineXXXX)
# .setbanner — URL или ответ на фото/гиф/видео
# Расширенные переменные: python, modules, lang, os, machine, cpu_count

import logging
import os
import time
from telethon import events, Button

from ..core.database import get as cfg_get, set_value as cfg_set, runtime_get
from ..core.dispatcher import register_builtin
from ..utils.helpers import format_uptime, escape_html
from ..utils.platform import detect_platform, get_cpu_usage, get_ram_usage_mb, get_platform_info
from ..version import __version_str__, LINKS

logger = logging.getLogger(__name__)

_INFO_IMAGE_KEY = "info_custom_image"
_INFO_MSG_KEY   = "info_custom_message"
_INFO_BTN_KEY   = "info_custom_button"

_PLATFORM_NAMES = {
    "rpi":      "🍓 Raspberry Pi",
    "termux":   "📱 Android (Termux)",
    "userland": "📱 Android (UserLand)",
    "linux":    "🐧 Linux",
    "unknown":  "❓ Unknown",
}

BANNER_DIR = "assets"


def register(client) -> None:
    register_builtin("info",       _info_handler)
    register_builtin("setbanner",  _setbanner_handler)
    register_builtin("setbtn",     _setbtn_handler)
    register_builtin("setinfo",    _setinfo_handler)
    register_builtin("resetinfo",  _resetinfo_handler)
    logger.debug("Модуль info зарегистрирован")


async def _build_info_text(client) -> str:
    me          = await client.get_me()
    has_premium = getattr(me, "premium", False)
    name        = escape_html(f"{me.first_name or ''} {me.last_name or ''}".strip() or str(me.id))
    user_id     = me.id
    prefix      = cfg_get("command_prefix", ".")
    lang        = cfg_get("language", "ru")

    start_time  = runtime_get("start_time", time.time())
    uptime_str  = format_uptime(time.time() - start_time)

    cpu         = get_cpu_usage()
    ram         = get_ram_usage_mb()
    pinfo       = get_platform_info()
    platform_key= detect_platform()
    platform_str= _PLATFORM_NAMES.get(platform_key, "❓ Unknown")
    modules_cnt = len(runtime_get("loaded_modules_count", 0) or [])

    import sys
    python_ver  = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    cpu_count   = pinfo.get("cpu_count", 1)
    machine     = pinfo.get("machine", "?")
    ram_total   = pinfo.get("ram_total_mb", 0)

    # Premium emoji или обычные
    def ico(premium_id, fallback):
        if has_premium:
            return f'<emoji document_id={premium_id}>{fallback}</emoji>'
        return fallback

    owner_ico   = ico(5373141891321699086, "😎")
    version_ico = ico(5469741319330996757, "💫")
    prefix_ico  = ico(5472111548572900003, "⌨️")
    uptime_ico  = ico(5451646226975955576, "⏱")
    cpu_ico     = ico(5431449001532594346, "⚡️")
    ram_ico     = ico(5359785904535774578, "💾")
    mod_ico     = ico(5188377234672400162, "📦")
    py_ico      = ico(5372981976804366741, "🐍")
    plat_ico    = ico(5407025283456835913, "🖥")

    custom_msg = cfg_get(_INFO_MSG_KEY, "")
    if custom_msg:
        try:
            return custom_msg.format(
                name=name, user_id=user_id, version=__version_str__,
                prefix=prefix, uptime=uptime_str, cpu=f"{cpu:.1f}%",
                ram=f"{ram} MB", platform=platform_str, modules=modules_cnt,
                lang=lang.upper(), python=python_ver,
                cpu_count=cpu_count, machine=machine,
                ram_total=f"{ram_total} MB",
            )
        except (KeyError, ValueError):
            pass

    ram_bar = ""
    if ram_total > 0:
        pct  = min(100, int(ram / ram_total * 100))
        fill = int(pct / 10)
        ram_bar = f" [{'█'*fill}{'░'*(10-fill)}] {pct}%"

    return (
        f"⭐ <b>SMVF Userbot</b>\n\n"
        f"{owner_ico} <b>Владелец:</b> "
        f'<a href="tg://user?id={user_id}">{name}</a> '
        f'<code>#{user_id}</code>\n'
        f"{version_ico} <b>Версия:</b> <code>{__version_str__}</code>\n"
        f"{prefix_ico} <b>Префикс:</b> <code>{escape_html(prefix)}</code>\n"
        f"{py_ico} <b>Python:</b> <code>{python_ver}</code>\n"
        f"{uptime_ico} <b>Аптайм:</b> <code>{uptime_str}</code>\n"
        f"{cpu_ico} <b>CPU:</b> <code>{cpu:.1f}%</code> × {cpu_count} ядер\n"
        f"{ram_ico} <b>RAM:</b> <code>{ram} MB</code>{ram_bar}\n"
        f"{plat_ico} <b>Платформа:</b> {platform_str} <code>{machine}</code>\n"
        f"{mod_ico} <b>Язык:</b> {lang.upper()}\n\n"
        f'📢 <a href="{LINKS["tg_channel"]}">Канал</a> · '
        f'<a href="{LINKS["youtube"]}">YouTube</a> · '
        f'<a href="{LINKS["github"]}">GitHub</a>'
    )


async def _info_handler(event: events.NewMessage.Event) -> None:
    """.info — карточка юзербота через inline-бота"""
    await event.delete()

    text         = await _build_info_text(event.client)
    custom_image = cfg_get(_INFO_IMAGE_KEY, "")
    custom_btn   = cfg_get(_INFO_BTN_KEY, [])
    bot_username = cfg_get("inline_bot_username", "")

    buttons = None
    if custom_btn and len(custom_btn) == 2:
        buttons = [[Button.url(custom_btn[0], custom_btn[1])]]

    # Пытаемся отправить через inline-бота (via @smvfinlineXXXX)
    if bot_username:
        try:
            if custom_image:
                query = f"photo:{custom_image}|{text}"
            else:
                query = text
            results = await event.client.inline_query(bot_username, query[:255])
            if results:
                await results[0].click(event.chat_id)
                return
        except Exception as e:
            logger.debug("Info inline ошибка: %s", e)

    # Fallback — прямая отправка
    if custom_image:
        await event.client.send_file(
            event.chat_id, custom_image,
            caption=text, parse_mode="html", buttons=buttons,
        )
    else:
        await event.client.send_message(
            event.chat_id, text, parse_mode="html", buttons=buttons,
        )


async def _setbanner_handler(event: events.NewMessage.Event) -> None:
    """
    .setbanner <url>         — установить баннер из URL
    .setbanner               — (ответ на фото/гиф/видео) скачать и установить
    .setbanner (без аргумент)— сброс баннера
    """
    args = (event.raw_text or "").split(None, 1)

    # Ответ на медиа-сообщение — скачиваем и сохраняем локально
    reply = await event.get_reply_message()
    if reply and reply.media:
        await event.edit("⬇️ Скачиваем медиа...", parse_mode="html")
        try:
            os.makedirs(BANNER_DIR, exist_ok=True)

            # Определяем расширение по типу медиа
            import mimetypes
            from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
            media = reply.media

            if isinstance(media, MessageMediaPhoto):
                ext = ".jpg"
            elif isinstance(media, MessageMediaDocument):
                doc  = media.document
                mime = getattr(doc, "mime_type", "")
                ext  = mimetypes.guess_extension(mime) or ".bin"
                # Нормализуем расширения
                ext = {".jpe": ".jpg", ".jpeg": ".jpg"}.get(ext, ext)
            else:
                await event.edit("❌ Неподдерживаемый тип медиа.", parse_mode="html")
                return

            save_path = os.path.join(BANNER_DIR, f"info_banner{ext}")
            await event.client.download_media(reply.media, file=save_path)

            # Сохраняем локальный путь
            cfg_set(_INFO_IMAGE_KEY, save_path)
            await event.edit(
                f"✅ <b>Баннер установлен!</b>\n"
                f"📁 Сохранён как: <code>{escape_html(save_path)}</code>",
                parse_mode="html",
            )
        except Exception as e:
            await event.edit(f"❌ Ошибка скачивания: {escape_html(str(e))}", parse_mode="html")
        return

    # URL из аргументов
    if len(args) >= 2:
        url = args[1].strip()
        if not url.startswith(("http://", "https://")):
            await event.edit("❌ Укажите корректный URL (http:// или https://)", parse_mode="html")
            return
        cfg_set(_INFO_IMAGE_KEY, url)
        await event.edit(
            f"✅ <b>Баннер установлен!</b>\n<code>{escape_html(url)}</code>",
            parse_mode="html",
        )
        return

    # Без аргументов — сброс
    cfg_set(_INFO_IMAGE_KEY, "")
    await event.edit("✅ Баннер сброшен.", parse_mode="html")


async def _setbtn_handler(event: events.NewMessage.Event) -> None:
    """.setbtn Название | url — кнопка под .info"""
    parts = (event.raw_text or "").split(None, 1)
    if len(parts) < 2:
        cfg_set(_INFO_BTN_KEY, [])
        await event.edit("✅ Кнопка сброшена.", parse_mode="html")
        return

    raw = parts[1].strip()
    if "|" not in raw:
        await event.edit("❌ Формат: <code>.setbtn Название | https://...</code>", parse_mode="html")
        return

    btn_name, btn_url = raw.split("|", 1)
    btn_name = btn_name.strip()
    btn_url  = btn_url.strip()

    if not btn_url.startswith(("http://", "https://", "t.me/", "tg://")):
        await event.edit("❌ Некорректный URL.", parse_mode="html")
        return

    cfg_set(_INFO_BTN_KEY, [btn_name, btn_url])
    await event.edit(
        f"✅ Кнопка: <b>{escape_html(btn_name)}</b> → <code>{escape_html(btn_url)}</code>",
        parse_mode="html",
    )


async def _setinfo_handler(event: events.NewMessage.Event) -> None:
    """.setinfo <текст> — кастомный текст .info"""
    args = (event.raw_text or "").split(None, 1)
    if len(args) < 2:
        cfg_set(_INFO_MSG_KEY, "")
        await event.edit("✅ Текст .info сброшен к стандартному.", parse_mode="html")
        return
    cfg_set(_INFO_MSG_KEY, args[1].strip())
    await event.edit(
        "✅ <b>Текст .info обновлён!</b>\n\n"
        "Переменные: <code>{name}</code> <code>{version}</code> <code>{prefix}</code> "
        "<code>{uptime}</code> <code>{cpu}</code> <code>{ram}</code> <code>{platform}</code> "
        "<code>{modules}</code> <code>{lang}</code> <code>{python}</code> "
        "<code>{cpu_count}</code> <code>{machine}</code> <code>{ram_total}</code>",
        parse_mode="html",
    )


async def _resetinfo_handler(event: events.NewMessage.Event) -> None:
    """.resetinfo — сброс всех настроек .info"""
    cfg_set(_INFO_IMAGE_KEY, "")
    cfg_set(_INFO_MSG_KEY,   "")
    cfg_set(_INFO_BTN_KEY,   [])
    await event.edit("✅ Все настройки <code>.info</code> сброшены.", parse_mode="html")
