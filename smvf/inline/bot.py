"""
SMVF Inline Bot + Log Group — Made by SuperMaxVF
"""
import asyncio
import os
from telethon import TelegramClient, events
from telethon.tl.functions.messages import CreateChatRequest
from telethon.tl.functions.channels import CreateChannelRequest
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors import FloodWaitError, ChatWriteForbiddenError


async def ensure_bot(client, cfg, log):
    token = cfg.get("bot_token")
    if not token:
        log.warn("No bot_token — create one via @BotFather and add to data/config.json")
        return None
    _BASE = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    session = os.path.join(_BASE, "data", "smvf_bot.session")
    bot = TelegramClient(session, cfg["api_id"], cfg["api_hash"])
    await bot.start(bot_token=token)
    me = await bot.get_me()
    cfg.set("inline_bot_username", me.username)
    log.ok(f"Inline bot: @{me.username}")

    # Set bot commands via Telegram Bot API
    asyncio.ensure_future(_set_bot_commands(bot, log))
    return bot


async def _set_bot_commands(bot, log):
    try:
        from telethon.tl.functions.bots import SetBotCommandsRequest
        from telethon.tl.types import BotCommand, BotCommandScopeDefault
        await bot(SetBotCommandsRequest(
            scope=BotCommandScopeDefault(),
            lang_code="",
            commands=[
                BotCommand("start", "Show SMVF info"),
                BotCommand("help",  "List all modules"),
            ]
        ))
        log.ok("Bot commands set")
    except Exception as e:
        log.warn(f"Could not set bot commands: {e}")


async def ensure_log_group(client, bot, cfg, log):
    """Create log group if missing or deleted. Remember id in config."""
    group_id = cfg.get("log_group_id")
    if group_id:
        try:
            entity = await client.get_entity(int(group_id))
            log.ok(f"Log group OK: {entity.title} (id={group_id})")
            return
        except Exception:
            log.warn("Log group gone — recreating...")

    await _create_log_group(client, bot, cfg, log)


async def _create_log_group(client, bot, cfg, log):
    for attempt in range(3):
        try:
            # Use channel (supergroup) — more reliable than basic chat
            result = await client(CreateChannelRequest(
                title="🌌 SMVF Logs",
                about="SMVF Userbot log group — Made by SuperMaxVF",
                megagroup=True,
            ))
            channel = result.chats[0]
            gid = -100_000_000_000 - channel.id  # standard supergroup id format
            # Simpler: use the id directly from peer
            from telethon.utils import get_peer_id
            gid = get_peer_id(result.chats[0])
            cfg.set("log_group_id", gid)
            log.ok(f"Log group created (id={gid})")

            # Add bot to group
            if bot:
                try:
                    bot_me = await bot.get_me()
                    await client(InviteToChannelRequest(
                        channel=channel,
                        users=[bot_me.username],
                    ))
                    log.ok(f"Bot @{bot_me.username} added to log group")
                except Exception as e:
                    log.warn(f"Could not add bot: {e}")

            # Welcome message
            await client.send_message(gid,
                "🌌 **SMVF Logs**\n\n"
                "✦ Version: `1.0`\n"
                "✦ Made by SuperMaxVF\n"
                "📡 [GitHub](https://github.com/SuperMaxVF000/SMVF)\n\n"
                "All userbot events are logged here.",
                parse_mode="md",
            )
            return
        except FloodWaitError as e:
            log.warn(f"FloodWait {e.seconds}s before creating log group...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            log.error(f"Log group creation attempt {attempt+1} failed: {e}")
            if attempt == 2:
                log.error("Giving up on log group creation.")
            await asyncio.sleep(3)
