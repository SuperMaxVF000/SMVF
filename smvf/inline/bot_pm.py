"""
SMVF Bot PM Handler — Made by SuperMaxVF
Greets users who write to the inline bot, like Hikka does.
"""
import os
from telethon import events, Button


async def setup_bot_pm(bot, cfg, log):
    """Register /start handler on the inline bot."""
    if not bot:
        return

    @bot.on(events.NewMessage(pattern="/start", incoming=True))
    async def start_handler(event):
        owner_id = cfg.get("owner_id")
        prefix   = cfg.get("prefix", ".")
        bot_username = cfg.get("inline_bot_username", "this bot")

        text = (
            "🌌 <b>SMVF Userbot</b> <code>v1.0</code>\n"
            "✦ <i>Made by SuperMaxVF</i>\n\n"
            f"This is the inline bot for <b>SMVF</b>.\n"
            f"It sends messages on behalf of the userbot owner.\n\n"
            f"<b>How to use inline mode:</b>\n"
            f"Type <code>@{bot_username} </code> in any chat to trigger inline results.\n\n"
            f"<b>Userbot commands (type in any chat):</b>\n"
            f"<code>{prefix}help</code> — all commands\n"
            f"<code>{prefix}info</code> — info card\n"
            f"<code>{prefix}ping</code> — latency &amp; uptime\n"
            f"<code>{prefix}mod install &lt;url&gt;</code> — install module\n\n"
            f"📡 <a href='https://t.me/MadeBySuperMaxVF'>Channel</a>  "
            f"💻 <a href='https://t.me/Mad3BySuperMaxVF'>Dev</a>  "
            f"🔗 <a href='https://github.com/SuperMaxVF000/SMVF'>GitHub</a>"
        )

        buttons = [
            [Button.url("📡 Channel", "https://t.me/MadeBySuperMaxVF"),
             Button.url("💻 Dev",     "https://t.me/Mad3BySuperMaxVF")],
            [Button.url("🔗 GitHub",  "https://github.com/SuperMaxVF000/SMVF")],
        ]

        logo = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "assets", "smvf_logo.png"
        )

        try:
            if os.path.exists(logo):
                await event.respond(file=logo, message=text, parse_mode="html", buttons=buttons)
            else:
                await event.respond(text, parse_mode="html", buttons=buttons)
        except Exception as e:
            log.warn(f"Bot PM error: {e}")
            await event.respond(text, parse_mode="html")

    log.ok("Bot /start handler registered")
