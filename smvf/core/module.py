"""
SMVF Module Base — Made by SuperMaxVF
Base class compatible with Hikka (strings/commands/client_ready)
and Mku (register(client) pattern).
"""
import re
from typing import Dict, Callable, Optional


def cmd(name: str):
    """Decorator to register a command on a method."""
    def decorator(func: Callable) -> Callable:
        func._smvf_cmd = name
        return func
    return decorator


class SMVFModule:
    """
    Base class for all SMVF modules.

    Hikka compatibility:
      - strings dict with 'name' and 'doc'
      - commands dict auto-populated by @cmd() decorator
      - async client_ready() / async on_load() lifecycle hooks
      - self.client, self.db (config acts as db), self.inline

    Mku compatibility:
      - Loader also recognizes register(client) function modules

    Usage:
        from smvf.core.module import SMVFModule, cmd

        class MyModule(SMVFModule):
            strings = {"name": "MyModule", "doc": "Does things."}

            @cmd("hello")
            async def hello_cmd(self, event):
                await self.edit(event, "Hello!")
    """

    strings: Dict[str, str] = {
        "name": "SMVFModule",
        "doc": "Base SMVF module",
    }
    commands: Dict[str, Callable] = {}

    def __init__(self, client, bot, cfg, log, core):
        self.client = client
        self._client = client          # Hikka alias
        self.bot = bot
        self.cfg = cfg
        self.db = cfg                  # Hikka alias — db.get/set maps to cfg
        self._db = cfg
        self.log = log
        self.core = core
        self.inline = None             # populated by core after inline bot connects
        self.commands = {}             # fresh per-instance dict
        self._collect_commands()

    def _collect_commands(self):
        for name in dir(type(self)):
            method = getattr(self, name, None)
            if callable(method) and hasattr(method, "_smvf_cmd"):
                self.commands[method._smvf_cmd] = method

    # ── Hikka lifecycle hooks ──────────────────────────────────────

    async def on_load(self):
        """Called once when the module is loaded."""

    async def client_ready(self):
        """Hikka alias — same as on_load."""
        await self.on_load()

    async def on_unload(self):
        """Called before unload/reload."""

    async def config_complete(self):
        """Called after config is populated (Hikka hook)."""

    # ── Message helpers ────────────────────────────────────────────

    async def edit(self, event, text: str, **kwargs):
        kwargs.setdefault("parse_mode", "html")
        return await event.edit(text, **kwargs)

    async def reply(self, event, text: str, **kwargs):
        kwargs.setdefault("parse_mode", "html")
        return await event.reply(text, **kwargs)

    async def send(self, chat_id, text: str, **kwargs):
        kwargs.setdefault("parse_mode", "html")
        return await self.client.send_message(chat_id, text, **kwargs)

    def args(self, event) -> str:
        """Return everything after the command word."""
        text = getattr(event.message, "text", "") or ""
        parts = text.split(maxsplit=1)
        return parts[1].strip() if len(parts) > 1 else ""

    # ── Properties ────────────────────────────────────────────────

    @property
    def prefix(self) -> str:
        return self.cfg.get("prefix", ".")

    @property
    def owner_id(self) -> Optional[int]:
        return self.cfg.get("owner_id")

    @property
    def premium(self) -> bool:
        return bool(self.cfg.get("premium", False))

    @property
    def uptime(self) -> str:
        return self.core.uptime if self.core else "—"

    def is_owner(self, user_id: int) -> bool:
        return user_id == self.owner_id

    # ── Hikka db shim ─────────────────────────────────────────────

    def get(self, module: str, key: str, default=None):
        """Hikka-style db.get(module, key)."""
        return self.cfg.get(f"{module}.{key}", default)

    def set_db(self, module: str, key: str, value):
        """Hikka-style db.set(module, key, value)."""
        self.cfg.set(f"{module}.{key}", value)
