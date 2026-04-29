"""SMVF Background Tasks. Made by SuperMaxVF"""

import asyncio
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from telethon import TelegramClient

from . import logger as log
from . import config as cfg


async def keepalive_task(client: "TelegramClient") -> None:
    """Ping Telegram every 60 s to stay alive. Never sleeps for good."""
    log.info("Keepalive задача запущена")
    fails = 0
    while True:
        try:
            await client.get_me()
            fails = 0
        except Exception as e:
            fails += 1
            log.warn(f"Keepalive сбой #{fails}: {e}")
            if fails >= 5:
                log.error("5 подряд сбоев keepalive — проблемы с сетью!")
                gid = cfg.get("log_group_id")
                if gid:
                    try:
                        await client.send_message(
                            gid,
                            "⚠️ <b>SMVF: проблемы с сетью!</b> 5 сбоев keepalive подряд.",
                            parse_mode="html",
                        )
                    except Exception:
                        pass
        await asyncio.sleep(60)


async def reconnect_watcher(client: "TelegramClient") -> None:
    """Watch for disconnects and reconnect."""
    while True:
        await asyncio.sleep(30)
        try:
            if not client.is_connected():
                log.warn("Клиент отключён — переподключаю...")
                await client.connect()
                log.ok("Переподключено!")
        except Exception as e:
            log.error(f"Ошибка переподключения: {e}")


async def log_startup(client: "TelegramClient", start_ts: float) -> None:
    """Send startup message to log group."""
    gid = cfg.get("log_group_id")
    if not gid:
        return
    me = await client.get_me()
    import platform, sys
    text = (
        "🚀 <b>SMVF запущен!</b>\n\n"
        f"👤 Пользователь: <a href='tg://user?id={me.id}'>{me.first_name}</a>\n"
        f"🕐 Время запуска: <code>{time.strftime('%Y-%m-%d %H:%M:%S')}</code>\n"
        f"🐍 Python: <code>{sys.version.split()[0]}</code>\n"
        f"🖥 ОС: <code>{platform.system()} {platform.machine()}</code>\n"
        f"📦 Версия SMVF: <code>1.0.0</code>\n\n"
        "<i>✦ Made by SuperMaxVF ✦</i>"
    )
    try:
        await client.send_message(gid, text, parse_mode="html")
    except Exception as e:
        log.warn(f"Не смог отправить сообщение о запуске в лог-группу: {e}")


def start_tasks(client: "TelegramClient", loop: asyncio.AbstractEventLoop) -> None:
    loop.create_task(keepalive_task(client))
    loop.create_task(reconnect_watcher(client))
