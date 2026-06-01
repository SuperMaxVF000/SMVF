# Определение платформы запуска: RPi / Termux / UserLand / Ubuntu
# psutil — опциональная зависимость, работает без неё

import os
import platform
import sys
from typing import Optional


def detect_platform() -> str:
    if _is_rpi():      return "rpi"
    if _is_termux():   return "termux"
    if _is_userland(): return "userland"
    if sys.platform.startswith("linux"): return "linux"
    return "unknown"


def _is_rpi() -> bool:
    if os.path.exists("/etc/rpi-issue"): return True
    try:
        with open("/proc/cpuinfo") as f:
            c = f.read().lower()
            if "raspberry pi" in c or "bcm2" in c: return True
    except Exception: pass
    try:
        with open("/proc/device-tree/model") as f:
            if "raspberry" in f.read().lower(): return True
    except Exception: pass
    return False


def _is_termux() -> bool:
    return (
        "TERMUX_VERSION" in os.environ
        or "com.termux" in os.environ.get("PREFIX", "")
        or os.path.exists("/data/data/com.termux")
    )


def _is_userland() -> bool:
    if os.path.exists("/proc/version"):
        try:
            with open("/proc/version") as f:
                if "android" in f.read().lower() and not _is_termux():
                    return True
        except Exception: pass
    return os.path.exists("/etc/userland")


def get_platform_info() -> dict:
    info = {
        "platform_key": detect_platform(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "os": platform.system(),
        "os_release": platform.release(),
        "machine": platform.machine(),
        "cpu_count": os.cpu_count() or 1,
        "ram_total_mb": 0,
        "ram_used_mb": 0,
    }
    try:
        import psutil
        mem = psutil.virtual_memory()
        info["ram_total_mb"] = round(mem.total / 1024 / 1024)
        info["ram_used_mb"]  = round(mem.used  / 1024 / 1024)
    except Exception: pass
    return info


def get_cpu_usage() -> float:
    try:
        import psutil
        return psutil.Process().cpu_percent(interval=0.1)
    except Exception: return 0.0


def get_ram_usage_mb() -> float:
    try:
        import psutil
        return round(psutil.Process().memory_info().rss / 1024 / 1024, 1)
    except Exception:
        # Fallback через /proc/self/status (работает на Android без psutil)
        try:
            with open("/proc/self/status") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        return round(int(line.split()[1]) / 1024, 1)
        except Exception: pass
        return 0.0
