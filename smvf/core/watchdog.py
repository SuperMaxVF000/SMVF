"""
SMVF Watchdog — Made by SuperMaxVF
Keeps the bot alive, monitors network and system resources.
Logs to Telegram and file when issues detected.
"""
import asyncio
import socket
import time
import psutil
from smvf.core.logger import SMVFLogger


class Watchdog:
    def __init__(self, client, log: SMVFLogger, cfg):
        self.client = client
        self.log    = log
        self.cfg    = cfg
        self._running = True
        self._last_net_warn = 0.0
        self._interval = int(cfg.get("healthcheck_interval", 30))

    def stop(self):
        self._running = False

    async def run(self):
        self.log.info("🐶 Watchdog started")
        while self._running:
            await asyncio.sleep(self._interval)
            await self._check_network()
            self._check_resources()

    async def _check_network(self):
        """Ping Telegram API, reconnect on failure."""
        reachable = await asyncio.get_event_loop().run_in_executor(
            None, self._ping_tg
        )
        if reachable:
            return
        now = time.time()
        if now - self._last_net_warn > 120:
            self.log.network("⚠️ Telegram unreachable! Reconnecting...")
            self._last_net_warn = now
        try:
            if not self.client.is_connected():
                await self.client.connect()
                self.log.network("✅ Reconnected to Telegram.")
        except Exception as e:
            self.log.network(f"Reconnect failed: {e}")

    @staticmethod
    def _ping_tg() -> bool:
        try:
            socket.create_connection(("api.telegram.org", 443), timeout=5)
            return True
        except OSError:
            return False

    def _check_resources(self):
        mem  = psutil.virtual_memory()
        cpu  = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage("/")
        if mem.percent > 90:
            self.log.warn(f"🔴 RAM: {mem.percent:.1f}% used — running low!")
        if cpu > 95:
            self.log.warn(f"🔴 CPU: {cpu:.1f}% — high load!")
        if disk.percent > 95:
            self.log.warn(f"🔴 Disk: {disk.percent:.1f}% full!")
