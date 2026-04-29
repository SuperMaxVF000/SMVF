"""SMVF Main Entry Point. Made by SuperMaxVF"""

import asyncio
import os
import sys
import time

from . import config as cfg
from . import logger as log
from .utils import (
    C, cprint, print_banner, ensure_dir,
    start_screensaver, stop_screensaver,
)


async def main() -> None:
    print_banner()

    # Init dirs
    for d in ("modules", "logs", "assets"):
        ensure_dir(d)

    # Init logger
    log_file = log.init_logger()
    log.info(f"SMVF v1.0.0 запускается. Лог: {log_file}")

    # Load / create config
    cfg.load_config()

    if not cfg.is_configured():
        from .setup import run_setup
        run_setup()
        cfg.load_config()

    api_id   = cfg.get("api_id")
    api_hash = cfg.get("api_hash")
    phone    = cfg.get("phone")

    # Connect Telegram
    from telethon import TelegramClient
    client = TelegramClient("smvf_session", api_id, api_hash)

    log.info("Подключаюсь к Telegram...")
    await client.start(phone=phone)
    me = await client.get_me()
    log.ok(f"Авторизован как {me.first_name} ({me.id})")

    loop = asyncio.get_event_loop()

    # Ensure inline bot
    from .inline import ensure_inline_bot, ensure_log_group, run_inline_bot_handler
    await ensure_inline_bot(client)

    # Ensure log group
    group_id = await ensure_log_group(client)
    if group_id:
        log.set_tg_client(client, group_id)
        log.start_flush_task(loop)

    # Load modules
    from . import loader
    log.info("Загружаю модули...")
    count = await loader.load_all(client)
    log.ok(f"Загружено модулей: {count}")

    # Setup dispatcher
    from . import dispatcher, core_modules  # noqa: F401 — registers handlers
    dispatcher.setup_dispatcher(client)

    # Background tasks
    from . import tasks
    tasks.start_tasks(client, loop)
    await tasks.log_startup(client, time.time())

    # Start inline bot in background
    loop.create_task(run_inline_bot_handler(client))

    cprint("\n✦ SMVF готов к работе! Made by SuperMaxVF ✦\n", C.STAR, bold=True)
    log.ok("SMVF полностью запущен!")

    # Screensaver runs in a daemon thread — starts after a quiet period
    # We run it only if stdin is a tty (real terminal)
    if sys.stdin.isatty():
        log.info("Запускаю скринсейвер (космос)...")
        start_screensaver()

    try:
        await client.run_until_disconnected()
    finally:
        stop_screensaver()
        log.info("SMVF остановлен.")
