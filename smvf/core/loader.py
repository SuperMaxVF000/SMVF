"""
SMVF Module Loader — Made by SuperMaxVF
Supports SMVF native, Hikka-style, and Mku register() modules.
"""
import asyncio, importlib.util, os, re, sys, traceback
from typing import Dict, List
from telethon import events

_BASE        = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUILTIN_DIR  = os.path.join(_BASE, "modules", "built_in")
EXTERNAL_DIR = os.path.join(_BASE, "modules", "external")


class ModuleLoader:
    def __init__(self, client, bot, cfg, log, core):
        self.client = client
        self.bot    = bot
        self.cfg    = cfg
        self.log    = log
        self.core   = core
        self._modules: Dict[str, object] = {}

    async def load_all(self):
        self.log.info("📦 Loading modules...")
        os.makedirs(BUILTIN_DIR,  exist_ok=True)
        os.makedirs(EXTERNAL_DIR, exist_ok=True)
        await self._load_dir(BUILTIN_DIR,  builtin=True)
        await self._load_dir(EXTERNAL_DIR, builtin=False)
        self.log.ok(f"Modules loaded: {len(self._modules)}")

    async def install(self, url: str) -> bool:
        import aiohttp
        os.makedirs(EXTERNAL_DIR, exist_ok=True)
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, timeout=aiohttp.ClientTimeout(total=30)) as r:
                    if r.status != 200:
                        return False
                    code = await r.text()
            fname = url.rstrip("/").split("/")[-1]
            if not fname.endswith(".py"):
                fname += ".py"
            path = os.path.join(EXTERNAL_DIR, fname)
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
            await self._load_file(path, builtin=False)
            return True
        except Exception as e:
            self.log.error(f"Install failed: {e}")
            return False

    def get_loaded(self) -> List[str]:
        return sorted(self._modules.keys())

    async def _load_dir(self, directory, builtin):
        for fname in sorted(os.listdir(directory)):
            if not fname.endswith(".py") or fname.startswith("_"):
                continue
            await self._load_file(os.path.join(directory, fname), builtin=builtin)

    async def _load_file(self, path, builtin=False):
        name = os.path.splitext(os.path.basename(path))[0]
        if name in (self.cfg.get("disabled_modules") or []):
            self.log.info(f"  ⊘ Disabled: {name}")
            return
        try:
            spec = importlib.util.spec_from_file_location(f"smvf_mod_{name}", path)
            mod  = importlib.util.module_from_spec(spec)
            mod.client = self.client
            mod.bot    = self.bot
            mod.cfg    = self.cfg
            mod.log    = self.log
            mod.core   = self.core
            sys.modules[f"smvf_mod_{name}"] = mod
            spec.loader.exec_module(mod)

            if not await self._try_class(mod, name):
                if not await self._try_register(mod, name):
                    self.log.warn(f"  ⚠ No interface found in: {name}")
                    return

            tag = "[built-in] " if builtin else ""
            self.log.ok(f"  ✦ {tag}Loaded: {name}")
        except Exception as e:
            self.log.error(f"Error loading '{name}': {e}\n{traceback.format_exc()}")

    async def _try_class(self, mod, name) -> bool:
        from smvf.core.module import SMVFModule
        for attr_name in dir(mod):
            if attr_name.startswith("_"):
                continue
            cls = getattr(mod, attr_name, None)
            if not isinstance(cls, type):
                continue
            if cls is SMVFModule:
                continue
            if not (hasattr(cls, "strings") or hasattr(cls, "commands") or hasattr(cls, "client_ready")):
                continue
            try:
                if issubclass(cls, SMVFModule):
                    inst = cls(self.client, self.bot, self.cfg, self.log, self.core)
                else:
                    # Hikka bare class
                    inst = object.__new__(cls)
                    inst.client = self.client
                    inst._client = self.client
                    inst.bot = self.bot
                    inst.cfg = self.cfg
                    inst.db  = self.cfg
                    inst.log = self.log
                    inst.core = self.core
                    inst.inline = None
                    inst.commands = {}
                    for mname in dir(type(inst)):
                        m = getattr(inst, mname, None)
                        if callable(m) and hasattr(m, "_smvf_cmd"):
                            inst.commands[m._smvf_cmd] = m

                # Only call on_load once
                if hasattr(inst, "on_load"):
                    await inst.on_load()
                elif hasattr(inst, "client_ready"):
                    await inst.client_ready()

                self._register_handlers(inst)
                self._modules[name] = inst
                return True
            except Exception as e:
                self.log.error(f"  Error in {attr_name}: {e}")
        return False

    async def _try_register(self, mod, name) -> bool:
        if hasattr(mod, "register") and callable(mod.register):
            try:
                r = mod.register(self.client)
                if asyncio.iscoroutine(r):
                    await r
                self._modules[name] = mod
                return True
            except Exception as e:
                self.log.error(f"  register() failed for {name}: {e}")
        return False

    def _register_handlers(self, inst):
        prefix = re.escape(self.cfg.get("prefix", "."))
        for cmd_name, handler in inst.commands.items():
            self.client.add_event_handler(
                _wrap(handler),
                events.NewMessage(pattern=rf"^{prefix}{re.escape(cmd_name)}(\s|$)", outgoing=True),
            )


def _wrap(handler):
    async def wrapper(event):
        try:
            await handler(event)
        except Exception as e:
            print(f"[SMVF] Handler error: {e}\n{traceback.format_exc()}")
    return wrapper
