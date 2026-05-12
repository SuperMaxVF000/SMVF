"""
SMVF Space Screensaver — Made by SuperMaxVF
Renders stars, comets and the SMVF banner in the terminal.
Anti-burn: characters and positions drift every frame.
"""
import os
import sys
import time
import random

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    _HAS_COLOR = True
except ImportError:
    _HAS_COLOR = False
    class _Fore:
        CYAN = MAGENTA = BLUE = WHITE = YELLOW = LIGHTCYAN_EX = \
        LIGHTMAGENTA_EX = LIGHTYELLOW_EX = RED = GREEN = ""
    class _Style:
        RESET_ALL = ""
    Fore = _Fore()
    Style = _Style()

STARS   = ["✦", "✧", "★", "☆", "·", "∗", "⋆", "✴", "✵", "✶", "✷", "✸", "✺"]
COMETS  = ["═►", "─►", "──►"]
COLORS  = [
    Fore.CYAN, Fore.MAGENTA, Fore.BLUE, Fore.WHITE,
    Fore.YELLOW, Fore.LIGHTCYAN_EX, Fore.LIGHTMAGENTA_EX,
]

BANNER_LINES = [
    "  ███████╗███╗   ███╗██╗   ██╗███████╗",
    "  ██╔════╝████╗ ████║██║   ██║██╔════╝",
    "  ███████╗██╔████╔██║██║   ██║█████╗  ",
    "  ╚════██║██║╚██╔╝██║╚██╗ ██╔╝██╔══╝  ",
    "  ███████║██║ ╚═╝ ██║ ╚████╔╝ ██║     ",
    "  ╚══════╝╚═╝     ╚═╝  ╚═══╝  ╚═╝     ",
    "          Made by SuperMaxVF   v1.0    ",
]


def _term_size():
    try:
        return os.get_terminal_size()
    except Exception:
        return os.terminal_size((80, 24))


def _clear():
    os.system("cls" if os.name == "nt" else "clear")


def _draw_frame(width: int, height: int, frame: int):
    rows: list[list] = [
        [(" ", Fore.WHITE)] * width for _ in range(height)
    ]

    # Stars (drift with frame)
    rng = random.Random(frame // 4)
    star_count = min(width * height // 10, 250)
    for _ in range(star_count):
        x = rng.randint(0, width - 1)
        y = rng.randint(0, height - 1)
        blink = rng.random() < 0.25
        sym = "·" if blink else rng.choice(STARS)
        col = rng.choice(COLORS)
        rows[y][x] = (sym, col)

    # Comets (horizontal, speed varies)
    rng2 = random.Random(frame // 2 + 7)
    for _ in range(4):
        speed  = rng2.randint(1, 4)
        cy     = rng2.randint(1, height - 2)
        cx     = (frame * speed + rng2.randint(0, width - 1)) % (width + 15) - 15
        trail  = rng2.randint(5, 14)
        head   = "►"
        rows[cy][max(0, min(cx, width - 1))] = (head, Fore.YELLOW)
        for i in range(1, trail):
            tx = cx - i
            if 0 <= tx < width:
                fade = "═" if i < trail // 2 else "─"
                rows[cy][tx] = (fade, Fore.WHITE)

    # Build output
    lines = []
    for row in rows:
        line = "".join(col + ch for ch, col in row)
        lines.append(line + Style.RESET_ALL)
    _clear()
    print("\n".join(lines), end="", flush=True)

    # Overlay banner (centered)
    bh = len(BANNER_LINES)
    by = max(0, (height - bh) // 2)
    palette = [
        Fore.CYAN, Fore.LIGHTCYAN_EX, Fore.MAGENTA,
        Fore.LIGHTMAGENTA_EX, Fore.YELLOW, Fore.WHITE, Fore.CYAN,
    ]
    for i, bline in enumerate(BANNER_LINES):
        bx = max(0, (width - len(bline)) // 2)
        color = palette[i % len(palette)]
        sys.stdout.write(f"\033[{by + i + 1};{bx + 1}H{color}{bline}{Style.RESET_ALL}")
    sys.stdout.flush()


def run_screensaver(duration: float = 4.0):
    """Show space screensaver for `duration` seconds, then clear."""
    size = _term_size()
    w, h = size.columns, size.lines
    end  = time.time() + duration
    frame = 0
    try:
        while time.time() < end:
            _draw_frame(w, h, frame)
            time.sleep(0.10)
            frame += 1
    except (KeyboardInterrupt, Exception):
        pass
    finally:
        _clear()
