"""SMVF Logger — file + TG group. Made by SuperMaxVF"""

import asyncio
import logging
import os
import sys
import time
from datetime import datetime
from typing import Optional

from .utils import C, smvf_log, ensure_dir

LOGS_DIR = "logs"
_log_file: Optional[str] = None
_tg_client = None
_log_group_id: Optional[int] = None
_buffer: list[str] = []
_buffer_task: Optional[asyncio.Task] = None


def init_logger() -> str:
    ensure_dir(LOGS_DIR)
    fname = os.path.join(LOGS_DIR, f"smvf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    global _log_file
    _log_file = fname

    # also configure stdlib logging
    logging.basicConfig(
        level=logging.WARNING,
        format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(fname, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return fname


def _write_to_file(line: str) -> None:
    if _log_file:
        with open(_log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def log(level: str, msg: str, tg: bool = True) -> None:
    """Log to terminal + file + optionally buffer for TG."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    smvf_log(level, msg)
    _write_to_file(line)
    if tg and _log_group_id:
        _buffer.append(f"<code>[{ts}]</code> <b>[{level}]</b> {msg}")


def info(msg: str, tg: bool = True):   log("INFO",  msg, tg)
def ok(msg: str, tg: bool = True):     log("OK",    msg, tg)
def warn(msg: str, tg: bool = True):   log("WARN",  msg, tg)
def error(msg: str, tg: bool = True):  log("ERROR", msg, tg)
def debug(msg: str, tg: bool = False): log("DEBUG", msg, tg)


def set_tg_client(client, group_id: int) -> None:
    global _tg_client, _log_group_id
    _tg_client = client
    _log_group_id = group_id


async def _flush_loop() -> None:
    """Flush buffered TG log messages every 5 seconds."""
    global _buffer
    while True:
        await asyncio.sleep(5)
        if _buffer and _tg_client and _log_group_id:
            chunk = _buffer[:20]
            _buffer = _buffer[20:]
            text = "\n".join(chunk)
            try:
                await _tg_client.send_message(_log_group_id, text, parse_mode="html")
            except Exception:
                pass


def start_flush_task(loop: asyncio.AbstractEventLoop) -> None:
    global _buffer_task
    _buffer_task = loop.create_task(_flush_loop())
