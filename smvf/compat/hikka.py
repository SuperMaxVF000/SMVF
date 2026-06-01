# Слой совместимости с Hikka-модулями
# Реализует заглушки для loader.Module, loader.command, ModuleConfig и т.д.

import asyncio
import logging
import inspect
from typing import Any, Callable, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


# ── Validators (заглушки) ─────────────────────────────────────────────────

class _ValidatorBase:
    def __init__(self, *args, **kwargs): pass
    def validate(self, value): return value

class _Validators:
    Boolean   = _ValidatorBase
    String    = _ValidatorBase
    Integer   = _ValidatorBase
    Float     = _ValidatorBase
    TelegramID= _ValidatorBase
    URL       = _ValidatorBase
    RegExp    = _ValidatorBase
    Series    = _ValidatorBase
    Union     = _ValidatorBase
    Hidden    = _ValidatorBase
    def __getattr__(self, _): return _ValidatorBase

validators = _Validators()


# ── utils заглушка ────────────────────────────────────────────────────────

class _Utils:
    """Заглушка для hikka utils / smvf_utils"""

    @staticmethod
    async def answer(message, text: str, **kwargs):
        """Hikka utils.answer → Telethon edit или reply"""
        try:
            await message.edit(text, parse_mode="html", **{
                k: v for k, v in kwargs.items()
                if k in ("parse_mode", "link_preview", "buttons")
            })
        except Exception:
            try:
                chat = getattr(message, "peer_id", None) or getattr(message, "chat_id", None)
                client = getattr(message, "_client", None) or getattr(message, "client", None)
                if client and chat:
                    await client.send_message(chat, text, parse_mode="html")
            except Exception:
                pass

    @staticmethod
    def get_args_raw(message) -> str:
        text = getattr(message, "raw_text", "") or getattr(message, "text", "") or ""
        parts = text.split(None, 1)
        return parts[1].strip() if len(parts) > 1 else ""

    @staticmethod
    def get_args(message) -> list:
        raw = _Utils.get_args_raw(message)
        return raw.split() if raw else []

utils = _Utils()


# ── Декораторы ────────────────────────────────────────────────────────────

def command(*args, **kwargs):
    def decorator(func: Callable) -> Callable:
        func._is_command = True
        func._cmd_kwargs = kwargs
        return func
    # Поддержка @loader.command (без скобок) и @loader.command(...)
    if args and callable(args[0]):
        return decorator(args[0])
    return decorator

def watcher(*args, **kwargs):
    def decorator(func: Callable) -> Callable:
        func._is_watcher = True
        return func
    if args and callable(args[0]):
        return decorator(args[0])
    return decorator

def tds(cls: Type) -> Type:
    cls._hikka_tds = True
    return cls

def inline_handler(**kwargs):
    def decorator(func: Callable) -> Callable:
        func._is_inline_handler = True
        return func
    return decorator

def loop(interval: int, autostart: bool = False, **kwargs):
    def decorator(func: Callable) -> Callable:
        func._is_loop = True
        func._loop_interval = interval
        func._loop_autostart = autostart
        return func
    return decorator


# ── ConfigValue / ModuleConfig ────────────────────────────────────────────

class ConfigValue:
    def __init__(self, option, default=None, doc=None, validator=None, on_change=None):
        self.option    = option
        self.default   = default
        self.value     = default
        self.doc       = doc() if callable(doc) else (doc or "")
        self.validator = validator

    def __repr__(self):
        return f"ConfigValue({self.option}={self.value!r})"


class ModuleConfig(dict):
    def __init__(self, *entries):
        super().__init__()
        self._config: Dict[str, ConfigValue] = {}

        if entries and isinstance(entries[0], ConfigValue):
            for entry in entries:
                self._config[entry.option] = entry
                self[entry.option] = entry.value
        else:
            it = iter(entries)
            for key in it:
                default  = next(it, None)
                doc_item = next(it, None)
                doc      = doc_item() if callable(doc_item) else (doc_item or "")
                cv = ConfigValue(key, default, doc)
                self._config[key] = cv
                self[key] = default

    def get(self, key, default=None):
        return super().get(key, default)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if key in self._config:
            self._config[key].value = value


# ── Strings / DB заглушки ─────────────────────────────────────────────────

class _DBStub:
    def __init__(self):
        self._data: Dict[str, Any] = {}

    def get(self, module: str, key: str, default: Any = None) -> Any:
        return self._data.get(f"{module}.{key}", default)

    def set(self, module: str, key: str, value: Any) -> None:
        self._data[f"{module}.{key}"] = value


# ── Базовый класс модуля ──────────────────────────────────────────────────

class Module:
    """Базовый класс — совместим с Hikka loader.Module"""
    strings:    Dict[str, str] = {"name": "Unknown"}
    strings_ru: Dict[str, str] = {}
    config: Optional[ModuleConfig] = None

    def __init__(self):
        self._client  = None
        self._me      = None
        self._prefix  = "."
        self._db_stub = _DBStub()
        # self.db — назначается при load
        self.db       = self._db_stub
        # self.inline — заглушка
        self.inline   = _InlineStub()

    async def client_ready(self, client=None, db=None):
        pass

    def get_prefix(self) -> str:
        return self._prefix


class _InlineStub:
    async def form(self, *a, **kw):    logger.warning("HikkaCompat: inline.form() не поддерживается")
    async def gallery(self, *a, **kw): logger.warning("HikkaCompat: inline.gallery() не поддерживается")
    async def list(self, *a, **kw):    logger.warning("HikkaCompat: inline.list() не поддерживается")


# Алиас для совместимости
HikkaModule = Module


# ── Загрузчик Hikka-модулей ───────────────────────────────────────────────

def load_hikka_module(client, module_class: Type[Module], prefix: str = ".", lang: str = "ru") -> Optional[Module]:
    try:
        instance = module_class()
        instance._client = client
        instance._prefix = prefix
        instance.client  = client  # некоторые модули используют self.client напрямую

        # Регистрируем команды
        for name, method in inspect.getmembers(instance, predicate=inspect.ismethod):
            # Команды: методы помеченные @loader.command ИЛИ заканчивающиеся на 'cmd'
            is_cmd = getattr(method, "_is_command", False) or (
                name.endswith("cmd") and not name.startswith("_")
            )
            if is_cmd:
                cmd_name = name.removesuffix("cmd")
                _register_hikka_cmd(client, instance, cmd_name, method, prefix)

            # Watchers
            if getattr(method, "_is_watcher", False):
                _register_hikka_watcher(client, instance, method)

            # Loops с autostart
            if getattr(method, "_is_loop", False) and getattr(method, "_loop_autostart", False):
                interval = getattr(method, "_loop_interval", 60)
                asyncio.get_event_loop().create_task(_run_loop(method, interval))

        # client_ready
        asyncio.get_event_loop().create_task(_call_ready(instance, client))
        return instance

    except Exception as e:
        logger.error("HikkaCompat: ошибка загрузки %s: %s", module_class.__name__, e)
        return None


def _register_hikka_cmd(client, instance, cmd_name: str, method: Callable, prefix: str):
    from telethon import events
    pattern = rf"^\{prefix}{cmd_name}(\s|$)"

    async def handler(event):
        try:
            await method(event.message)
        except Exception as e:
            logger.error("HikkaCompat cmd %s: %s", cmd_name, e)
            try:
                await event.edit(f"❌ Ошибка: {e}", parse_mode="html")
            except Exception:
                pass

    client.add_event_handler(handler, events.NewMessage(outgoing=True, pattern=pattern))
    logger.debug("HikkaCompat: .%s зарегистрирован", cmd_name)


def _register_hikka_watcher(client, instance, method: Callable):
    from telethon import events

    async def handler(event):
        try:
            await method(event.message)
        except Exception as e:
            logger.debug("HikkaCompat watcher: %s", e)

    client.add_event_handler(handler, events.NewMessage(incoming=True))


async def _call_ready(instance: Module, client):
    try:
        instance._me = await client.get_me()
        await instance.client_ready(client, instance.db)
    except Exception as e:
        logger.warning("HikkaCompat client_ready: %s", e)


async def _run_loop(func: Callable, interval: int):
    while True:
        try:
            await func()
        except Exception as e:
            logger.warning("HikkaCompat loop: %s", e)
        await asyncio.sleep(interval)


# Экспортируем всё что нужно Hikka-модулям
__all__ = [
    "Module", "HikkaModule", "ModuleConfig", "ConfigValue",
    "validators", "utils",
    "command", "watcher", "tds", "inline_handler", "loop",
    "load_hikka_module",
]
