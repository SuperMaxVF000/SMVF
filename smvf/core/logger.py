"""
SMVF Logger — Made by SuperMaxVF
Dual logging: terminal (colored) + file + Telegram log group.
"""
import asyncio
import logging
import os
from datetime import datetime
from typing import Optional

from colorama import Fore, Style, init

init(autoreset=True)

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_FILE = os.path.join(_BASE, "logs", "smvf.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

_LEVEL_COLOR = {
    "INFO":    Fore.CYAN,
    "OK":      Fore.GREEN,
    "WARN":    Fore.YELLOW,
    "ERROR":   Fore.RED,
    "NETWORK": Fore.MAGENTA,
    "DEBUG":   Fore.WHITE,
}
_LEVEL_EMOJI = {
    "INFO":    "ℹ️",
    "OK":      "✅",
    "WARN":    "⚠️",
    "ERROR":   "❌",
    "NETWORK": "🔌",
    "DEBUG":   "🔍",
}


class SMVFLogger:
    def __init__(self):
        self._tg_client = None
        self._log_group_id: Optional[int] = None
        self._setup_file()

    def _setup_file(self):
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            encoding="utf-8",
        )
        self._flog = logging.getLogger("SMVF")

    def set_tg(self, client, group_id: int):
        self._tg_client = client
        self._log_group_id = group_id

    def _ts(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _print(self, level: str, msg: str):
        color = _LEVEL_COLOR.get(level, Fore.WHITE)
        print(f"{color}🌌 [{self._ts()}] [{level}] {msg}{Style.RESET_ALL}")

    def _write(self, level: str, msg: str):
        lvl = {
            "OK": logging.INFO, "WARN": logging.WARNING,
            "ERROR": logging.ERROR, "NETWORK": logging.INFO,
        }.get(level, logging.INFO)
        self._flog.log(lvl, f"[{level}] {msg}")

    def _tg_send(self, level: str, msg: str):
        if not (self._tg_client and self._log_group_id):
            return
        emoji = _LEVEL_EMOJI.get(level, "•")
        text = f"{emoji} `{self._ts()}` **[{level}]**\n{msg}"

        async def _send():
            try:
                await self._tg_client.send_message(
                    self._log_group_id, text, parse_mode="md"
                )
            except Exception:
                pass

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(_send())
            else:
                loop.run_until_complete(_send())
        except Exception:
            pass

    def _log(self, level: str, msg: str):
        self._print(level, msg)
        self._write(level, msg)
        self._tg_send(level, msg)

    def info(self, msg: str):    self._log("INFO", msg)
    def ok(self, msg: str):      self._log("OK", msg)
    def warn(self, msg: str):    self._log("WARN", msg)
    def network(self, msg: str): self._log("NETWORK", msg)

    def error(self, msg: str, exc: Exception = None):
        full = f"{msg}: {exc}" if exc else msg
        self._log("ERROR", full)

    def startup(self, version: str):
        text = (
            f"🚀 **SMVF Userbot v{version}** started\n"
            f"⏰ {self._ts()}\n"
            f"✦ Made by SuperMaxVF\n"
            f"🔗 github.com/SuperMaxVF000/SMVF"
        )
        self._print("OK", text)
        self._write("OK", text)
        self._tg_send("OK", text)

    def shutdown(self):
        text = f"🌙 SMVF stopped at {self._ts()}"
        self._print("INFO", text)
        self._write("INFO", text)
        self._tg_send("INFO", text)


_logger: Optional[SMVFLogger] = None


def get_logger() -> SMVFLogger:
    global _logger
    if _logger is None:
        _logger = SMVFLogger()
    return _logger
