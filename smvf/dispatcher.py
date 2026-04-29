"""SMVF Dispatcher — handles incoming messages. Made by SuperMaxVF"""

import asyncio
import re
import time
import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from telethon import TelegramClient

from telethon import events

from . import config as cfg
from . import logger as log

_client = None
_start_time = time.time()


def get_uptime() -> float:
    return time.time() - _start_time


def setup_dispatcher(client: "TelegramClient") -> None:
    global _client
    _client = client

    @client.on(events.NewMessage(outgoing=True))
    async def on_message(event):
        prefix = cfg.get("command_prefix", ".")
        text   = event.raw_text or ""

        if not text.startswith(prefix):
            return

        parts   = text[len(prefix):].split(maxsplit=1)
        cmd     = parts[0].lower() if parts else ""
        args    = parts[1] if len(parts) > 1 else ""

        # check aliases
        aliases = cfg.get("aliases", {})
        if cmd in aliases:
            cmd = aliases[cmd]

        # dispatch to core modules first, then loaded modules
        from . import core_modules
        handler = core_modules.get_handler(cmd)

        if handler:
            try:
                await handler(event, args, client)
            except Exception as e:
                tb = traceback.format_exc()
                log.error(f"Ошибка в команде .{cmd}: {e}\n{tb[:500]}")
                try:
                    await event.edit(f"❌ <b>Ошибка в .{cmd}:</b>\n<code>{str(e)[:200]}</code>", parse_mode="html")
                except Exception:
                    pass

    log.ok("Диспетчер команд активен")
