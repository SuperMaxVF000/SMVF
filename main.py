#!/usr/bin/env python3
# ╔═══════════════════════════════════════════════════════╗
# ║              SMVF Userbot v1.0                       ║
# ║           Made by SuperMaxVF                         ║
# ║   https://github.com/SuperMaxVF000/SMVF              ║
# ║   https://t.me/MadeBySuperMaxVF                      ║
# ╚═══════════════════════════════════════════════════════╝
import asyncio
import os
import sys

# Ensure project root is on path so "smvf.*" imports always work
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from smvf.core.screensaver import run_screensaver
from smvf.core.setup import first_run_check
from smvf.core.core import SMVFCore


async def _run():
    await first_run_check()
    core = SMVFCore()
    try:
        await core.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await core.stop()


if __name__ == "__main__":
    run_screensaver(duration=4)
    asyncio.run(_run())
