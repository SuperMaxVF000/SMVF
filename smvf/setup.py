"""SMVF First-Run Setup Wizard. Made by SuperMaxVF"""

import asyncio
import getpass
import sys

from .utils import C, cprint, print_banner
from . import config as cfg


def ask(prompt: str, secret: bool = False, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    full_prompt = f"{C.BOLD}{C.COMET}{prompt}{suffix}: {C.RESET}"
    try:
        if secret:
            val = getpass.getpass(full_prompt)
        else:
            val = input(full_prompt)
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    return val.strip() or default


def run_setup() -> None:
    """Interactive first-run config wizard (terminal only, no webserver)."""
    print_banner()

    cprint("╔══════════════════════════════════════════════════════╗", C.NEBULA, bold=True)
    cprint("║     🚀  SMVF ПЕРВОНАЧАЛЬНАЯ НАСТРОЙКА  🚀            ║", C.STAR, bold=True)
    cprint("╚══════════════════════════════════════════════════════╝", C.NEBULA, bold=True)
    print()
    cprint("Добро пожаловать! Сейчас мы настроим SMVF. Made by SuperMaxVF", C.AURORA)
    cprint("Данные сохраняются ТОЛЬКО локально в smvf_config.json", C.DIM + C.WHITE)
    print()

    cprint("📡 Шаг 1/4 — Telegram API", C.GALAXY, bold=True)
    cprint("  Получи на https://my.telegram.org → API development tools", C.BBLACK)
    api_id = ask("  API ID (число)")
    while not api_id.isdigit():
        cprint("  ❌ API ID должен быть числом!", C.BRED)
        api_id = ask("  API ID (число)")
    api_hash = ask("  API Hash")
    while len(api_hash) < 10:
        cprint("  ❌ Слишком короткий хэш!", C.BRED)
        api_hash = ask("  API Hash")

    print()
    cprint("📞 Шаг 2/4 — Номер телефона", C.GALAXY, bold=True)
    cprint("  Формат: +79001234567", C.BBLACK)
    phone = ask("  Номер телефона")
    while not phone.startswith("+") or len(phone) < 10:
        cprint("  ❌ Неверный формат!", C.BRED)
        phone = ask("  Номер телефона")

    print()
    cprint("⌨️  Шаг 3/4 — Настройки", C.GALAXY, bold=True)
    prefix = ask("  Префикс команд", default=".")
    if not prefix:
        prefix = "."

    print()
    cprint("💎 Шаг 4/4 — Премиум", C.GALAXY, bold=True)
    premium_raw = ask("  Есть Telegram Premium? (y/n)", default="n").lower()
    premium = premium_raw in ("y", "yes", "да", "д")

    # Save
    cfg.load_config()
    cfg.set_value("api_id", int(api_id))
    cfg.set_value("api_hash", api_hash)
    cfg.set_value("phone", phone)
    cfg.set_value("command_prefix", prefix)
    cfg.set_value("premium_emoji", premium)

    print()
    cprint("✅ Конфигурация сохранена!", C.BGREEN, bold=True)
    cprint("🔐 Сейчас нужно войти в аккаунт — введи код из Telegram:", C.BCYAN)
    print()
