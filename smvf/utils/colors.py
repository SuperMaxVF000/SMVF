# ANSI-цвета для вывода в терминал
# Используются во всём проекте через cprint()

import sys


class Colors:
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

    # Яркие варианты
    BRIGHT_RED     = "\033[91m"
    BRIGHT_GREEN   = "\033[92m"
    BRIGHT_YELLOW  = "\033[93m"
    BRIGHT_BLUE    = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN    = "\033[96m"
    BRIGHT_WHITE   = "\033[97m"

    # Фоны
    BG_RED    = "\033[41m"
    BG_GREEN  = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE   = "\033[44m"


def _supports_color() -> bool:
    """Проверяем, поддерживает ли терминал цвета."""
    if not hasattr(sys.stdout, "isatty"):
        return False
    if not sys.stdout.isatty():
        return False
    # Windows без ANSI-поддержки
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32  # type: ignore
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False
    return True


_COLOR_ENABLED = _supports_color()


def cprint(text: str, color: str = "", bold: bool = False) -> None:
    """
    Вывод цветного текста в терминал.

    :param text: Текст для вывода.
    :param color: Цвет из Colors.*
    :param bold: Жирный текст.
    """
    if _COLOR_ENABLED:
        prefix = (Colors.BOLD if bold else "") + color
        print(f"{prefix}{text}{Colors.RESET}")
    else:
        print(text)


def strip_ansi(text: str) -> str:
    """Убираем ANSI-коды из строки (для записи в файл)."""
    import re
    return re.sub(r"\033\[[0-9;]*m", "", text)
