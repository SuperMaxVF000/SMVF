"""
SMVF Core — Made by SuperMaxVF
"""
import asyncio, os, time
from telethon import TelegramClient
from smvf.core.config import get_config
from smvf.core.logger import get_logger
from smvf.core.loader import ModuleLoader
from smvf.core.watchdog import Watchdog
from smvf.inline.bot import ensure_bot, ensure_log_group
from smvf.inline.bot_pm import setup_bot_pm
from smvf import __version__

_BASE   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SESSION = os.path.join(_BASE, "data", "smvf_user.session")


class SMVFCore:
    def __init__(self):
        self.cfg        = get_config()
        self.log        = get_logger()
        self.client     = None
        self.bot        = None
        self.loader     = None
        self.watchdog   = None
        self._start_time = time.time()

    async def start(self):
        self.log.info("🌌 Starting SMVF...")
        await self._connect_user()
        self.bot = await ensure_bot(self.client, self.cfg, self.log)
        await ensure_log_group(self.client, self.bot, self.cfg, self.log)
        self.log.set_tg(self.client, self.cfg.get("log_group_id"))
        self.log.startup(__version__)

        await setup_bot_pm(self.bot, self.cfg, self.log)

        self.loader = ModuleLoader(self.client, self.bot, self.cfg, self.log, self)
        await self.loader.load_all()

        self.watchdog = Watchdog(self.client, self.log, self.cfg)
        asyncio.ensure_future(self.watchdog.run())

        self.log.ok("🚀 SMVF is ready!")
        await self._send_startup_to_log_group()
        await self.client.run_until_disconnected()

    async def _connect_user(self):
        self.log.info("Connecting user session...")
        self.client = TelegramClient(SESSION, self.cfg["api_id"], self.cfg["api_hash"])
        await self.client.start(phone=self.cfg["phone"])
        me = await self.client.get_me()
        self.cfg.set("owner_id", me.id)
        self.log.ok(f"Signed in as {me.first_name} (id={me.id})")

    async def _send_startup_to_log_group(self):
        gid = self.cfg.get("log_group_id")
        if not gid:
            return
        logo    = os.path.join(_BASE, "assets", "smvf_logo.png")
        modules = self.loader.get_loaded() if self.loader else []
        caption = (
            f"🚀 **SMVF v{__version__} started**\n"
            f"⏰ `{self._ts()}`\n"
            f"✦ Made by SuperMaxVF\n\n"
            f"📦 Modules loaded: `{len(modules)}`\n"
            f"⏱ Uptime: `{self.uptime}`\n"
            f"🔗 [GitHub](https://github.com/SuperMaxVF000/SMVF)"
        )
        try:
            if os.path.exists(logo):
                await self.client.send_file(gid, logo, caption=caption, parse_mode="md")
            else:
                await self.client.send_message(gid, caption, parse_mode="md")
        except Exception as e:
            self.log.warn(f"Could not send startup message to log group: {e}")

    async def stop(self):
        self.log.shutdown()
        if self.watchdog:
            self.watchdog.stop()
        if self.client:
            await self.client.disconnect()
        if self.bot:
            await self.bot.disconnect()

    @property
    def uptime(self) -> str:
        d = int(time.time() - self._start_time)
        h, r = divmod(d, 3600)
        m, s = divmod(r, 60)
        return f"{h}h {m}m {s}s"

    @staticmethod
    def _ts() -> str:
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
