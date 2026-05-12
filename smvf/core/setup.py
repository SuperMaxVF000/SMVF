"""
SMVF Setup Wizard — Made by SuperMaxVF
Interactive terminal setup on first launch. No web server.
"""
import getpass
from colorama import Fore, Style, init

init(autoreset=True)

_BANNER = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════╗
║  ✦ ✧ ✦  SMVF Userbot v1.0  ✦ ✧ ✦                  ║
║         Made by SuperMaxVF                          ║
║  ─────────────────────────────────────────────────  ║
║  🌌 github.com/SuperMaxVF000/SMVF                   ║
║  📡 t.me/MadeBySuperMaxVF                           ║
╚══════════════════════════════════════════════════════╝{Style.RESET_ALL}"""

_INTRO = f"""
{Fore.MAGENTA}✦ First launch! Let's configure SMVF.{Style.RESET_ALL}
{Fore.CYAN}You will need:
  1. api_id and api_hash — get them at https://my.telegram.org
  2. Your Telegram account phone number
  3. A bot token — create one via @BotFather (optional, auto-created)
{Style.RESET_ALL}"""


def _prompt(text: str, secret: bool = False) -> str:
    label = f"{Fore.YELLOW}  ❯ {text}: {Style.RESET_ALL}"
    try:
        if secret:
            return getpass.getpass(label)
        return input(label).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        raise SystemExit("Setup cancelled.")


async def first_run_check():
    from smvf.core.config import get_config
    cfg = get_config()
    if cfg.is_configured():
        return

    print(_BANNER)
    print(_INTRO)

    # api_id
    api_id = _prompt("API ID (integer)")
    while not api_id.isdigit():
        print(f"{Fore.RED}  ✗ API ID must be a number{Style.RESET_ALL}")
        api_id = _prompt("API ID (integer)")

    # api_hash
    api_hash = _prompt("API Hash (32 chars)")
    while len(api_hash.strip()) != 32:
        print(f"{Fore.RED}  ✗ API Hash must be exactly 32 characters{Style.RESET_ALL}")
        api_hash = _prompt("API Hash (32 chars)")

    # phone
    phone = _prompt("Phone number (+79...)")

    # bot_token — optional
    bot_token = _prompt("Bot token (press Enter to skip — create via @BotFather)")

    # prefix
    prefix = _prompt("Command prefix [default: .]") or "."

    # premium
    prem = _prompt("Do you have Telegram Premium? (y/n)").lower()
    premium = prem in ("y", "yes", "да", "д")

    cfg.set("api_id",    int(api_id))
    cfg.set("api_hash",  api_hash.strip())
    cfg.set("phone",     phone)
    cfg.set("prefix",    prefix)
    cfg.set("premium",   premium)
    if bot_token:
        cfg.set("bot_token", bot_token.strip())

    print(f"\n{Fore.GREEN}  ✦ Config saved! Starting SMVF...{Style.RESET_ALL}\n")
