"""SMVF Terminal Utils — Space Theme. Made by SuperMaxVF"""

import os
import sys
import time
import random
import asyncio
import threading
from datetime import datetime


# ── ANSI Colors ──────────────────────────────────────────────────────────────

class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"

    BLACK   = "\033[30m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"

    BBLACK   = "\033[90m"
    BRED     = "\033[91m"
    BGREEN   = "\033[92m"
    BYELLOW  = "\033[93m"
    BBLUE    = "\033[94m"
    BMAGENTA = "\033[95m"
    BCYAN    = "\033[96m"
    BWHITE   = "\033[97m"

    # Space gradient palette
    SPACE    = "\033[38;5;57m"   # deep purple
    NEBULA   = "\033[38;5;93m"   # violet
    STAR     = "\033[38;5;226m"  # bright yellow
    COMET    = "\033[38;5;51m"   # ice blue
    AURORA   = "\033[38;5;46m"   # aurora green
    GALAXY   = "\033[38;5;201m"  # pink
    COSMOS   = "\033[38;5;99m"   # indigo


def cprint(text: str, color: str = C.WHITE, bold: bool = False, end: str = "\n") -> None:
    prefix = C.BOLD if bold else ""
    print(f"{prefix}{color}{text}{C.RESET}", end=end)


def get_terminal_size():
    try:
        return os.get_terminal_size()
    except OSError:
        return os.terminal_size((80, 24))


def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def log_line(level: str, msg: str) -> str:
    colors = {
        "INFO":    C.BCYAN,
        "OK":      C.BGREEN,
        "WARN":    C.BYELLOW,
        "ERROR":   C.BRED,
        "DEBUG":   C.BBLACK,
        "SPACE":   C.NEBULA,
    }
    color = colors.get(level, C.WHITE)
    return f"{C.DIM}[{timestamp()}]{C.RESET} {color}[{level}]{C.RESET} {msg}"


def smvf_log(level: str, msg: str) -> None:
    print(log_line(level, msg))


# ── SMVF Banner ───────────────────────────────────────────────────────────────

BANNER = r"""
  ███████╗███╗   ███╗██╗   ██╗███████╗
  ██╔════╝████╗ ████║██║   ██║██╔════╝
  ███████╗██╔████╔██║██║   ██║█████╗  
  ╚════██║██║╚██╔╝██║╚██╗ ██╔╝██╔══╝  
  ███████║██║ ╚═╝ ██║ ╚████╔╝ ██║     
  ╚══════╝╚═╝     ╚═╝  ╚═══╝  ╚═╝     
"""

def print_banner():
    cols, _ = get_terminal_size()
    palette = [C.SPACE, C.NEBULA, C.COMET, C.AURORA, C.GALAXY, C.COSMOS, C.BCYAN]
    lines = BANNER.split("\n")
    for i, line in enumerate(lines):
        color = palette[i % len(palette)]
        print(f"{C.BOLD}{color}{line.center(cols)}{C.RESET}")
    print()
    subtitle = "✦ Space Userbot v1.0 ✦  Made by SuperMaxVF"
    print(f"{C.BOLD}{C.STAR}{subtitle.center(cols)}{C.RESET}")
    links = "📡 t.me/MadeBySuperMaxVF  |  👨‍💻 t.me/Mad3BySuperMaxVF  |  🔗 github.com/SuperMaxVF000/SMVF"
    print(f"{C.DIM}{C.BCYAN}{links.center(cols)}{C.RESET}")
    print()


# ── Space Screensaver ─────────────────────────────────────────────────────────

SPACE_CHARS = ["★", "☆", "✦", "✧", "✩", "✪", "⋆", "·", "°", "∗", "✫", "✬", "✭"]
COMET_CHARS = ["━", "═", "─", "‐"]
SPACE_COLORS = [
    C.STAR, C.COMET, C.NEBULA, C.AURORA, C.GALAXY, C.COSMOS,
    C.BCYAN, C.BMAGENTA, C.BBLUE, C.BYELLOW, C.BWHITE, C.DIM + C.WHITE,
]

_screensaver_active = False
_screensaver_thread = None


def _screensaver_loop():
    global _screensaver_active
    cols, rows = get_terminal_size()
    grid = [[(" ", C.RESET) for _ in range(cols)] for _ in range(rows)]
    comets = []

    def rand_star():
        return random.choice(SPACE_CHARS), random.choice(SPACE_COLORS)

    def rand_comet():
        return {
            "row": random.randint(0, rows - 1),
            "col": random.randint(0, cols - 5),
            "len": random.randint(4, 12),
            "speed": random.randint(1, 3),
            "color": random.choice([C.COMET, C.BWHITE, C.BCYAN, C.BBLUE]),
            "tick": 0,
        }

    # seed grid
    for r in range(rows):
        for c in range(cols):
            if random.random() < 0.05:
                grid[r][c] = rand_star()

    for _ in range(3):
        comets.append(rand_comet())

    sys.stdout.write("\033[?25l")  # hide cursor
    try:
        while _screensaver_active:
            # twinkle
            for _ in range(max(1, cols * rows // 200)):
                r = random.randint(0, rows - 1)
                c = random.randint(0, cols - 1)
                if random.random() < 0.3:
                    grid[r][c] = rand_star()
                else:
                    grid[r][c] = (" ", C.RESET)

            # draw frame
            frame = "\033[H"  # home
            for r in range(rows):
                row_str = ""
                for c in range(cols):
                    ch, col = grid[r][c]
                    row_str += f"{col}{ch}{C.RESET}"
                frame += row_str + "\r\n"

            # draw comets
            comet_overlays = []
            for comet in comets[:]:
                comet["tick"] += 1
                if comet["tick"] % comet["speed"] == 0:
                    comet["col"] += 1
                if comet["col"] >= cols:
                    comets.remove(comet)
                    comets.append(rand_comet())
                    continue
                for i in range(comet["len"]):
                    cc = comet["col"] - i
                    if 0 <= cc < cols:
                        brightness = max(0, 255 - i * 30)
                        ch = COMET_CHARS[0] if i == 0 else "·" if i < 3 else " "
                        comet_overlays.append((comet["row"], cc, ch, comet["color"] if i < 3 else C.DIM + C.WHITE))

            sys.stdout.write("\033[H")
            sys.stdout.write(frame)
            for r, c, ch, col in comet_overlays:
                sys.stdout.write(f"\033[{r+1};{c+1}H{col}{ch}{C.RESET}")

            # watermark
            wm = "  ✦ SMVF — Made by SuperMaxVF ✦  "
            sys.stdout.write(f"\033[{rows};1H{C.BOLD}{C.NEBULA}{wm}{C.RESET}")
            sys.stdout.flush()
            time.sleep(0.08)
    finally:
        sys.stdout.write("\033[?25h")  # show cursor
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()


def start_screensaver():
    global _screensaver_active, _screensaver_thread
    _screensaver_active = True
    _screensaver_thread = threading.Thread(target=_screensaver_loop, daemon=True)
    _screensaver_thread.start()


def stop_screensaver():
    global _screensaver_active
    _screensaver_active = False
    if _screensaver_thread:
        _screensaver_thread.join(timeout=1)


def progress_bar(current: int, total: int, width: int = 30, label: str = "") -> str:
    pct = current / total if total else 0
    filled = int(width * pct)
    bar = "█" * filled + "░" * (width - filled)
    return f"{C.NEBULA}[{C.STAR}{bar}{C.NEBULA}]{C.RESET} {C.BCYAN}{int(pct*100):3d}%{C.RESET} {label}"


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def format_uptime(seconds: float) -> str:
    s = int(seconds)
    d, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    if d:
        return f"{d}д {h}ч {m}м {s}с"
    if h:
        return f"{h}ч {m}м {s}с"
    return f"{m}м {s}с"
