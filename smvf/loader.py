"""SMVF Module Loader — supports SMVF / Hikka-compat / MCUB modules. Made by SuperMaxVF"""

import importlib
import importlib.util
import inspect
import os
import re
import sys
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from telethon import TelegramClient

from .utils import C, cprint, ensure_dir
from . import logger as log

MODULES_DIR = "modules"

# Registry: module_name -> module object
_loaded: Dict[str, Any] = {}

# Command registry: prefix+cmd -> (handler, module_name)
_commands: Dict[str, tuple] = {}


# ── Module format detection ──────────────────────────────────────────────────

def _detect_format(code: str) -> str:
    """Return 'smvf', 'hikka', 'mcub' or 'unknown'."""
    if "loader.Module" in code or "loader.tds" in code:
        return "hikka"
    if 'def register(client)' in code and ('add_event_handler' in code or 'events.NewMessage' in code):
        return "mcub"
    if "SMVFModule" in code or "smvf_module" in code.lower():
        return "smvf"
    # try mcub generic
    if "add_event_handler" in code:
        return "mcub"
    return "unknown"


# ── Hikka compatibility shim ──────────────────────────────────────────────────

class _FakeLoader:
    """Minimal shim so Hikka modules don't crash on import."""

    class Module:
        strings = {}
        async def client_ready(self, client, db): pass

    class ModuleConfig(dict):
        def __init__(self, *args): pass

    class ConfigValue:
        def __init__(self, key, default=None, doc=None, validator=None):
            self.key = key; self.default = default

    @staticmethod
    def tds(cls): return cls

    class validators:
        @staticmethod
        def Union(*a, **kw): return None
        @staticmethod
        def Series(*a, **kw): return None
        @staticmethod
        def NoneType(): return None
        @staticmethod
        def Link(): return None

    @staticmethod
    def command(func):
        func._is_command = True
        return func

    @staticmethod
    def loop(*a, **kw):
        def wrapper(func): return func
        return wrapper


def _install_hikka_shim():
    """Inject fake 'loader' module so hikka modules can be imported."""
    import types
    fake = types.ModuleType("loader")
    for attr in dir(_FakeLoader):
        if not attr.startswith("__"):
            setattr(fake, attr, getattr(_FakeLoader, attr))
    sys.modules.setdefault("loader", fake)
    # also hikka.loader
    sys.modules.setdefault("hikka.loader", fake)


# ── Core loader ────────────────────────────────────────────────────────────────

async def load_module(
    client: "TelegramClient",
    file_path: str,
) -> bool:
    """Load a single module file."""
    name = os.path.basename(file_path)[:-3]

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    fmt = _detect_format(code)
    log.info(f"Загружаю [{fmt.upper()}] {name}")

    try:
        if fmt == "hikka":
            return await _load_hikka(client, name, file_path, code)
        elif fmt in ("mcub", "smvf", "unknown"):
            return await _load_mcub_style(client, name, file_path, code)
        else:
            return await _load_mcub_style(client, name, file_path, code)
    except Exception as e:
        log.error(f"Ошибка загрузки {name}: {e}")
        return False


async def _load_hikka(client, name, path, code):
    """Try to load a Hikka-style module with shim."""
    _install_hikka_shim()

    if name in sys.modules:
        del sys.modules[name]

    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod

    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        log.warn(f"Hikka модуль {name} не смог загрузиться полностью: {e}")
        return False

    # find loader.Module subclasses
    loaded_any = False
    for attr_name in dir(mod):
        cls = getattr(mod, attr_name)
        if not inspect.isclass(cls):
            continue
        if attr_name == "Module":
            continue
        try:
            # check it has commands registered
            instance = cls()
            if hasattr(instance, "client_ready"):
                instance._client = client
                try:
                    await instance.client_ready(client, None)
                except Exception:
                    pass
            # register event handlers decorated with @loader.command
            for mname in dir(instance):
                meth = getattr(instance, mname)
                if getattr(meth, "_is_command", False) and callable(meth):
                    cmd = mname.replace("_cmd", "").replace("cmd", "")
                    _commands[cmd] = (meth, name)
            _loaded[name] = mod
            loaded_any = True
        except Exception:
            pass

    if loaded_any:
        log.ok(f"Hikka-модуль {name} загружен")
    return loaded_any


async def _load_mcub_style(client, name, path, code):
    """Load MCUB/SMVF style module with register(client)."""
    if name in sys.modules:
        del sys.modules[name]

    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)

    if hasattr(mod, "register"):
        mod.register(client)
        _loaded[name] = mod
        log.ok(f"Модуль {name} загружен (MCUB/SMVF)")
        return True

    log.warn(f"Модуль {name}: нет функции register(client)")
    return False


async def load_all(client: "TelegramClient") -> int:
    ensure_dir(MODULES_DIR)
    count = 0
    files = sorted(f for f in os.listdir(MODULES_DIR) if f.endswith(".py"))
    for fname in files:
        path = os.path.join(MODULES_DIR, fname)
        if await load_module(client, path):
            count += 1
    return count


async def load_module_from_code(client: "TelegramClient", code: str, name: str) -> bool:
    ensure_dir(MODULES_DIR)
    path = os.path.join(MODULES_DIR, f"{name}.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    return await load_module(client, path)


async def unload_module(name: str) -> bool:
    path = os.path.join(MODULES_DIR, f"{name}.py")
    if os.path.exists(path):
        os.remove(path)
    if name in sys.modules:
        del sys.modules[name]
    if name in _loaded:
        del _loaded[name]
    # remove commands
    to_del = [k for k, v in _commands.items() if v[1] == name]
    for k in to_del:
        del _commands[k]
    return True


def get_loaded() -> Dict[str, Any]:
    return dict(_loaded)


def get_commands() -> Dict[str, tuple]:
    return dict(_commands)
