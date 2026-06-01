# Реэкспорт утилит для удобного импорта
from .colors import Colors, cprint, strip_ansi
from .helpers import (
    ensure_dir,
    escape_html,
    format_uptime,
    get_args,
    is_premium_emoji,
    now_str,
    progress_bar,
    strip_html,
    today_str,
    truncate,
)
from .i18n import get_lang, set_lang, t
from .logger import (
    get_all_logs_text,
    get_log_files,
    install_tg_log,
    setup_logging,
    stop_tg_log,
)
from .platform import (
    detect_platform,
    get_cpu_usage,
    get_platform_info,
    get_ram_usage_mb,
)

__all__ = [
    "Colors", "cprint", "strip_ansi",
    "ensure_dir", "escape_html", "format_uptime", "get_args",
    "is_premium_emoji", "now_str", "progress_bar", "strip_html",
    "today_str", "truncate",
    "get_lang", "set_lang", "t",
    "get_all_logs_text", "get_log_files", "install_tg_log",
    "setup_logging", "stop_tg_log",
    "detect_platform", "get_cpu_usage", "get_platform_info", "get_ram_usage_mb",
]
