"""SMVF Inline Bot & Log Group Manager. Made by SuperMaxVF"""

import asyncio
import re
import time
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from telethon import TelegramClient

from . import config as cfg
from . import logger as log

_inline_client: Optional["TelegramClient"] = None


async def _try_bot_token(token: str) -> Optional[str]:
    """Return bot username if token valid, else None."""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://api.telegram.org/bot{token}/getMe", timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status == 200:
                    data = await r.json()
                    if data.get("ok"):
                        return data["result"]["username"]
    except Exception:
        pass
    return None


async def ensure_inline_bot(client: "TelegramClient") -> bool:
    """Check existing bot or create a new one via BotFather."""
    token = cfg.get("inline_bot_token", "")
    if token:
        username = await _try_bot_token(token)
        if username:
            log.ok(f"Inline-бот активен: @{username}")
            return True
        else:
            log.warn("Токен инлайн-бота недействителен, создаём новый...")

    log.info("Создаю inline-бот через BotFather...")
    try:
        me = await client.get_me()
        uid = str(me.id)[-5:]
        ts  = str(int(time.time()))[-4:]
        bot_name     = f"SMVF_{uid}{ts}"
        bot_username = f"smvf_{uid}{ts}_bot"

        bf = await client.get_entity("BotFather")

        await client.send_message(bf, "/newbot"); await asyncio.sleep(2)
        await client.send_message(bf, f"SMVF {uid}"); await asyncio.sleep(2)
        await client.send_message(bf, bot_username); await asyncio.sleep(3)

        msgs = await client.get_messages(bf, limit=3)
        token = None
        for m in msgs:
            if m.text and "token" in m.text.lower():
                match = re.search(r"(\d{8,}:[A-Za-z0-9_-]{30,})", m.text)
                if match:
                    token = match.group(1)
                    break

        if not token:
            log.error("Не смог получить токен от BotFather")
            return False

        # enable inline
        await client.send_message(bf, "/setinline"); await asyncio.sleep(1)
        await client.send_message(bf, f"@{bot_username}"); await asyncio.sleep(1)
        await client.send_message(bf, "smvf"); await asyncio.sleep(1)

        cfg.set_value("inline_bot_token", token)
        cfg.set_value("inline_bot_username", bot_username)
        log.ok(f"Inline-бот создан: @{bot_username}")
        return True

    except Exception as e:
        log.error(f"Ошибка создания инлайн-бота: {e}")
        return False


async def ensure_log_group(client: "TelegramClient") -> Optional[int]:
    """Check existing log group or create a new one."""
    group_id = cfg.get("log_group_id")

    if group_id:
        try:
            entity = await client.get_entity(group_id)
            log.ok(f"Лог-группа найдена: {entity.title}")
            return group_id
        except Exception:
            log.warn("Лог-группа недоступна, создаю новую...")

    log.info("Создаю лог-группу...")
    try:
        from telethon.tl.functions.channels import CreateChannelRequest, InviteToChannelRequest
        from telethon.tl.functions.messages import ExportChatInviteRequest

        result = await client(CreateChannelRequest(
            title="🌌 SMVF Logs",
            about="SMVF Userbot — Лог-канал. Made by SuperMaxVF",
            megagroup=True,
        ))
        group = result.chats[0]
        group_id = group.id
        # make it negative for supergroup
        full_id = int(f"-100{group_id}")

        cfg.set_value("log_group_id", full_id)

        # invite inline bot
        bot_username = cfg.get("inline_bot_username", "")
        if bot_username:
            try:
                bot_entity = await client.get_entity(bot_username)
                await client(InviteToChannelRequest(channel=group, users=[bot_entity]))
            except Exception:
                pass

        log.ok(f"Лог-группа создана (id={full_id})")

        # send welcome
        me = await client.get_me()
        welcome = (
            "🌌 <b>SMVF Лог-канал запущен!</b>\n\n"
            f"👤 Пользователь: <a href='tg://user?id={me.id}'>{me.first_name}</a>\n"
            f"🤖 Инлайн-бот: @{bot_username}\n"
            f"📡 Канал: <a href='https://t.me/MadeBySuperMaxVF'>@MadeBySuperMaxVF</a>\n"
            f"👨‍💻 Dev: <a href='https://t.me/Mad3BySuperMaxVF'>@Mad3BySuperMaxVF</a>\n\n"
            "<i>✦ Made by SuperMaxVF ✦</i>"
        )
        await client.send_message(full_id, welcome, parse_mode="html")
        return full_id

    except Exception as e:
        log.error(f"Ошибка создания лог-группы: {e}")
        return None


async def run_inline_bot_handler(client: "TelegramClient") -> None:
    """Run inline bot as a separate Telethon client for callback handling."""
    token = cfg.get("inline_bot_token", "")
    if not token:
        return

    try:
        from telethon import TelegramClient as TC, events, Button
        api_id   = cfg.get("api_id")
        api_hash = cfg.get("api_hash")

        bot = TC("smvf_inline_bot", api_id=api_id, api_hash=api_hash)
        await bot.start(bot_token=token)
        global _inline_client
        _inline_client = bot
        log.ok("Inline-бот обработчик запущен")

        @bot.on(events.InlineQuery())
        async def handle_inline(event):
            from telethon.tl.types import (
                InputBotInlineResultArticle,
                InputBotInlineMessageText,
            )
            results = [
                InputBotInlineResultArticle(
                    id="smvf_info",
                    title="SMVF Info",
                    description="Информация о боте",
                    send_message=InputBotInlineMessageText(
                        message="✦ <b>SMVF Userbot</b> — Made by SuperMaxVF\n"
                                "📡 @MadeBySuperMaxVF | 🔗 github.com/SuperMaxVF000/SMVF",
                        no_webpage=True,
                    ),
                )
            ]
            await event.answer(results, cache_time=0)

        await bot.run_until_disconnected()
    except Exception as e:
        log.error(f"Inline-бот упал: {e}")


def get_inline_client():
    return _inline_client
