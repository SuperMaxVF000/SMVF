"""SMVF Core Modules. Made by SuperMaxVF"""

import asyncio
import os
import platform
import sys
import time
from typing import Callable, Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from telethon import TelegramClient
    from telethon.tl.custom import Message

from . import config as cfg
from . import logger as log
from . import loader
from .utils import format_uptime

# registry: cmd -> async handler(event, args, client)
_handlers: Dict[str, Callable] = {}

_start_time = time.time()


def register(cmd: str):
    def deco(fn):
        _handlers[cmd] = fn
        return fn
    return deco


def get_handler(cmd: str) -> Optional[Callable]:
    return _handlers.get(cmd)


# ─────────────────────────────────────────────────────────────────────────────
# .info
# ─────────────────────────────────────────────────────────────────────────────

@register("info")
async def cmd_info(event, args: str, client: "TelegramClient"):
    """Show userbot info. Reply to media to set it. .info set <text> to set text.
    .info button <text>|<url> to set button."""
    msg = event.message

    # .info set <text>
    if args.startswith("set "):
        cfg.set_value("info_text", args[4:].strip())
        await event.edit("✅ Текст .info обновлён!")
        return

    # .info button <text>|<url>
    if args.startswith("button "):
        parts = args[7:].split("|", 1)
        if len(parts) == 2:
            cfg.set_value("info_button_text", parts[0].strip())
            cfg.set_value("info_button_url", parts[1].strip())
            await event.edit("✅ Кнопка .info обновлена!")
        else:
            await event.edit("❌ Формат: .info button Текст|https://url")
        return

    # .info media — reply to photo/video/gif to set
    if args == "media":
        reply = await msg.get_reply_message()
        if not reply:
            await event.edit("❌ Ответь на фото/видео/гиф командой .info media")
            return
        if reply.photo:
            media = await client.download_media(reply.photo, "smvf_info_media.jpg")
            cfg.set_value("info_media", media)
            cfg.set_value("info_media_type", "photo")
            await event.edit("✅ Медиа для .info установлено (фото)!")
        elif reply.video or reply.gif or reply.document:
            ext = ".mp4"
            media = await client.download_media(reply.media, f"smvf_info_media{ext}")
            cfg.set_value("info_media", media)
            cfg.set_value("info_media_type", "video")
            await event.edit("✅ Медиа для .info установлено (видео/гиф)!")
        else:
            await event.edit("❌ Поддерживаются фото, видео, гиф")
        return

    # .info clear media
    if args == "clear media":
        cfg.set_value("info_media", None)
        cfg.set_value("info_media_type", None)
        await event.edit("✅ Медиа удалено из .info")
        return

    # Build info text
    me = await client.get_me()
    uptime  = format_uptime(time.time() - _start_time)
    mods    = len(loader.get_loaded())
    prefix  = cfg.get("command_prefix", ".")
    version = "1.0.0"

    premium_star = ""
    if cfg.get("premium_emoji") and me.premium:
        premium_star = " ⭐"

    custom_text = cfg.get("info_text", "")
    if custom_text:
        info_body = custom_text
    else:
        info_body = (
            f"🌌 <b>SMVF Userbot</b>{premium_star} <i>v{version}</i>\n\n"
            f"👤 <b>Владелец:</b> <a href='tg://user?id={me.id}'>{me.first_name}</a>\n"
            f"⏱ <b>Аптайм:</b> <code>{uptime}</code>\n"
            f"📦 <b>Модулей:</b> <code>{mods}</code>\n"
            f"⌨️ <b>Префикс:</b> <code>{prefix}</code>\n"
            f"🖥 <b>Система:</b> <code>{platform.system()} {platform.machine()}</code>\n\n"
            f"📡 <a href='https://t.me/MadeBySuperMaxVF'>Канал</a> | "
            f"👨‍💻 <a href='https://t.me/Mad3BySuperMaxVF'>Dev</a> | "
            f"🔗 <a href='https://github.com/SuperMaxVF000/SMVF'>GitHub</a>\n\n"
            f"<i>✦ Made by SuperMaxVF ✦</i>"
        )

    btn_text = cfg.get("info_button_text", "")
    btn_url  = cfg.get("info_button_url", "")
    buttons  = None
    if btn_text and btn_url:
        from telethon import Button
        buttons = [Button.url(btn_text, btn_url)]

    media_path = cfg.get("info_media")
    media_type = cfg.get("info_media_type")

    await event.delete()

    if media_path and os.path.exists(media_path):
        send_fn = client.send_file
        kwargs  = dict(
            entity=event.chat_id,
            file=media_path,
            caption=info_body,
            parse_mode="html",
            buttons=buttons,
        )
        if media_type == "video":
            kwargs["supports_streaming"] = True
        await send_fn(**kwargs)
    else:
        await client.send_message(
            event.chat_id,
            info_body,
            parse_mode="html",
            buttons=buttons,
            link_preview=False,
        )


# ─────────────────────────────────────────────────────────────────────────────
# .ping
# ─────────────────────────────────────────────────────────────────────────────

@register("ping")
async def cmd_ping(event, args: str, client: "TelegramClient"):
    """Show ping and uptime. Reply to media to attach. .ping media to set."""
    msg = event.message

    if args == "media":
        reply = await msg.get_reply_message()
        if not reply:
            await event.edit("❌ Ответь на фото/видео/гиф командой .ping media")
            return
        if reply.photo:
            media = await client.download_media(reply.photo, "smvf_ping_media.jpg")
            cfg.set_value("ping_media", media)
            cfg.set_value("ping_media_type", "photo")
            await event.edit("✅ Медиа для .ping установлено!")
        elif reply.video or reply.gif or reply.document:
            media = await client.download_media(reply.media, "smvf_ping_media.mp4")
            cfg.set_value("ping_media", media)
            cfg.set_value("ping_media_type", "video")
            await event.edit("✅ Медиа для .ping установлено (видео)!")
        return

    if args == "clear media":
        cfg.set_value("ping_media", None)
        await event.edit("✅ Медиа .ping удалено")
        return

    t0    = time.perf_counter()
    await event.edit("🛰 Пингую...")
    delay = (time.perf_counter() - t0) * 1000
    uptime = format_uptime(time.time() - _start_time)

    me = await client.get_me()
    premium_star = ""
    if cfg.get("premium_emoji") and me.premium:
        premium_star = " ⭐"

    text = (
        f"🌌 <b>SMVF Ping</b>{premium_star}\n\n"
        f"🏓 <b>Задержка:</b> <code>{delay:.2f} мс</code>\n"
        f"⏱ <b>Аптайм:</b> <code>{uptime}</code>\n\n"
        f"<i>✦ Made by SuperMaxVF ✦</i>"
    )

    media_path = cfg.get("ping_media")
    media_type = cfg.get("ping_media_type")

    if media_path and os.path.exists(media_path):
        await event.delete()
        kwargs = dict(entity=event.chat_id, file=media_path, caption=text, parse_mode="html")
        if media_type == "video":
            kwargs["supports_streaming"] = True
        await client.send_file(**kwargs)
    else:
        await event.edit(text, parse_mode="html")


# ─────────────────────────────────────────────────────────────────────────────
# .help
# ─────────────────────────────────────────────────────────────────────────────

@register("help")
async def cmd_help(event, args: str, client: "TelegramClient"):
    prefix = cfg.get("command_prefix", ".")
    mods   = loader.get_loaded()

    core_cmds = list(_handlers.keys())
    core_text = " • " + f"\n • ".join(f"<code>{prefix}{c}</code>" for c in sorted(core_cmds))

    mod_lines = []
    for mname in sorted(mods.keys()):
        mod_lines.append(f"  📦 <code>{mname}</code>")

    mods_text = "\n".join(mod_lines) if mod_lines else "  <i>нет загруженных модулей</i>"

    text = (
        "🌌 <b>SMVF Help</b>\n\n"
        f"<b>⚙️ Встроенные команды:</b>\n{core_text}\n\n"
        f"<b>📦 Загруженные модули:</b>\n{mods_text}\n\n"
        f"📡 <a href='https://t.me/MadeBySuperMaxVF'>Канал</a> | "
        f"👨‍💻 <a href='https://t.me/Mad3BySuperMaxVF'>Dev</a>\n"
        f"<i>✦ Made by SuperMaxVF ✦</i>"
    )
    await event.edit(text, parse_mode="html", link_preview=False)


# ─────────────────────────────────────────────────────────────────────────────
# .mod — module management
# ─────────────────────────────────────────────────────────────────────────────

@register("mod")
async def cmd_mod(event, args: str, client: "TelegramClient"):
    """Module management. .mod load <url|reply> / .mod unload <name> / .mod list"""
    parts = args.split(maxsplit=1)
    sub   = parts[0].lower() if parts else "list"
    rest  = parts[1] if len(parts) > 1 else ""

    if sub == "list":
        mods = loader.get_loaded()
        if not mods:
            await event.edit("📦 <b>Нет загруженных модулей</b>", parse_mode="html")
            return
        lines = "\n".join(f"• <code>{n}</code>" for n in sorted(mods))
        await event.edit(f"📦 <b>Модули ({len(mods)}):</b>\n{lines}", parse_mode="html")

    elif sub == "load":
        url_or_name = rest.strip()
        if url_or_name.startswith("http"):
            await event.edit("⬇️ Скачиваю модуль...")
            try:
                import aiohttp
                async with aiohttp.ClientSession() as s:
                    async with s.get(url_or_name) as r:
                        code = await r.text()
                name = url_or_name.split("/")[-1].replace(".py", "")
                ok   = await loader.load_module_from_code(client, code, name)
                await event.edit(f"{'✅' if ok else '❌'} Модуль <code>{name}</code> {'загружен' if ok else 'не загружен'}!", parse_mode="html")
            except Exception as e:
                await event.edit(f"❌ Ошибка: <code>{e}</code>", parse_mode="html")
        else:
            # try reply
            reply = await event.message.get_reply_message()
            if reply and reply.document:
                await event.edit("⬇️ Загружаю файл...")
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
                    await client.download_media(reply.media, tmp.name)
                    ok = await loader.load_module(client, tmp.name)
                os.unlink(tmp.name)
                await event.edit(f"{'✅' if ok else '❌'} Модуль {'загружен' if ok else 'не загружен'}!", parse_mode="html")
            else:
                await event.edit("❌ Укажи URL или ответь на .py файл")

    elif sub == "unload":
        name = rest.strip()
        ok   = await loader.unload_module(name)
        await event.edit(f"{'✅' if ok else '❌'} Модуль <code>{name}</code> {'выгружен' if ok else 'не найден'}!", parse_mode="html")

    else:
        await event.edit("❌ Неизвестная команда. Используй: .mod list / .mod load <url> / .mod unload <name>")


# ─────────────────────────────────────────────────────────────────────────────
# .alias
# ─────────────────────────────────────────────────────────────────────────────

@register("alias")
async def cmd_alias(event, args: str, client: "TelegramClient"):
    """Manage command aliases. .alias add <alias>=<cmd> / .alias del <alias> / .alias list"""
    parts = args.split(maxsplit=1)
    sub   = parts[0].lower() if parts else "list"
    rest  = parts[1] if len(parts) > 1 else ""

    aliases = cfg.get("aliases", {})

    if sub == "add":
        if "=" not in rest:
            await event.edit("❌ Формат: .alias add к=команда")
            return
        k, v = rest.split("=", 1)
        aliases[k.strip()] = v.strip()
        cfg.set_value("aliases", aliases)
        await event.edit(f"✅ Алиас <code>{k.strip()}</code> → <code>{v.strip()}</code> добавлен!", parse_mode="html")
    elif sub == "del":
        k = rest.strip()
        if k in aliases:
            del aliases[k]
            cfg.set_value("aliases", aliases)
            await event.edit(f"✅ Алиас <code>{k}</code> удалён!", parse_mode="html")
        else:
            await event.edit(f"❌ Алиас <code>{k}</code> не найден!", parse_mode="html")
    else:
        if not aliases:
            await event.edit("📋 <b>Алиасов нет</b>", parse_mode="html")
            return
        lines = "\n".join(f"• <code>{k}</code> → <code>{v}</code>" for k, v in aliases.items())
        await event.edit(f"📋 <b>Алиасы:</b>\n{lines}", parse_mode="html")


# ─────────────────────────────────────────────────────────────────────────────
# .restart / .update
# ─────────────────────────────────────────────────────────────────────────────

@register("restart")
async def cmd_restart(event, args: str, client: "TelegramClient"):
    await event.edit("🔄 <b>Перезапускаю SMVF...</b>", parse_mode="html")
    await asyncio.sleep(1)
    os.execv(sys.executable, [sys.executable, "-m", "smvf"])


@register("update")
async def cmd_update(event, args: str, client: "TelegramClient"):
    await event.edit("🔄 <b>Обновляю SMVF с GitHub...</b>", parse_mode="html")
    proc = await asyncio.create_subprocess_shell(
        "git pull origin main",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    out = (stdout + stderr).decode()[:500]
    await event.edit(f"📡 <b>Обновление:</b>\n<code>{out}</code>\n\nПерезапусти SMVF командой .restart", parse_mode="html")
