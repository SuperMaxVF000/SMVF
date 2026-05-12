"""
SMVF Built-in: Utils — Made by SuperMaxVF
.help, .mod, .restart — with detailed Hikka-style guides
"""
import os, sys, inspect
from smvf.core.module import SMVFModule, cmd


class UtilsModule(SMVFModule):
    strings = {
        "name": "Utils",
        "doc":  "System commands: help, mod, restart.",
    }

    async def on_load(self):
        self.log.ok("Utils module loaded")

    @cmd("help")
    async def help_cmd(self, event):
        """
        🌌 <b>SMVF Help</b>

        <code>.help</code> — show all loaded modules and their commands
        <code>.help &lt;module&gt;</code> — detailed help for a specific module

        <b>Examples:</b>
        <code>.help</code>
        <code>.help Info</code>
        <code>.help ping</code>
        """
        args = self.args(event).strip()
        p    = self.prefix
        mods = self.core.loader._modules

        if args:
            # find by module name or command name
            mod = mods.get(args) or mods.get(args.lower())
            if not mod:
                # search by command name
                for mn, m in mods.items():
                    if args.lower() in (getattr(m, "commands", {}) or {}):
                        mod = m; break
            if not mod:
                return await self.edit(event,
                    f"❌ Module or command <code>{args}</code> not found.\n"
                    f"Use <code>{p}help</code> to see all modules."
                )
            name = getattr(mod, "strings", {}).get("name", args)
            doc  = getattr(mod, "strings", {}).get("doc", "No description.")
            cmds = getattr(mod, "commands", {}) or {}

            lines = [f"🌌 <b>{name}</b>\n<i>{doc}</i>\n"]
            for cname, handler in cmds.items():
                hdoc = inspect.getdoc(handler) or "No description."
                lines.append(f"<code>{p}{cname}</code>\n<i>{hdoc}</i>\n")

            return await self.edit(event, "\n".join(lines))

        # Full help
        lines = [
            "🌌 <b>SMVF v1.0 — All Modules</b>",
            f"<i>Made by SuperMaxVF · prefix: <code>{p}</code></i>\n",
        ]
        for mname, mod in sorted(mods.items()):
            mstrings = getattr(mod, "strings", {})
            name   = mstrings.get("name", mname)
            doc    = mstrings.get("doc", "")
            cmds   = list((getattr(mod, "commands", {}) or {}).keys())
            cmds_s = "  ".join(f"<code>{p}{c}</code>" for c in cmds[:6])
            lines.append(f"<b>{name}</b> — <i>{doc}</i>\n{cmds_s}\n")

        lines += [
            f"<i>Total modules: {len(mods)}</i>",
            f"\n<code>{p}help &lt;module&gt;</code> — detailed help for a module",
        ]
        await self.edit(event, "\n".join(lines))

    @cmd("mod")
    async def mod_cmd(self, event):
        """
        📦 <b>Module Manager</b>

        <code>.mod install &lt;url&gt;</code>
        Install a module from a direct URL to a .py file.
        Supports SMVF, Hikka and Mku module formats.

        <code>.mod list</code>
        Show all currently loaded modules.

        <b>Examples:</b>
        <code>.mod install https://raw.githubusercontent.com/user/repo/main/module.py</code>
        <code>.mod list</code>
        """
        args = self.args(event).strip()

        if args.startswith("install "):
            url = args[8:].strip()
            if not url.startswith("http"):
                return await self.edit(event, "❌ Provide a full URL starting with https://")
            await self.edit(event, f"📦 Installing module...\n<code>{url}</code>")
            ok = await self.core.loader.install(url)
            if ok:
                await self.edit(event, "✅ Module installed and loaded!")
            else:
                await self.edit(event,
                    "❌ Installation failed.\n"
                    "Check that the URL points to a valid .py file."
                )
            return

        if args == "list":
            names = self.core.loader.get_loaded()
            return await self.edit(event,
                f"📦 <b>Loaded modules ({len(names)}):</b>\n"
                + "\n".join(f"  • <code>{n}</code>" for n in names)
            )

        await self.edit(event,
            "📦 <b>Module Manager</b>\n\n"
            f"<code>{self.prefix}mod install &lt;url&gt;</code>\n"
            "<i>Install a module from URL (.py file)</i>\n\n"
            f"<code>{self.prefix}mod list</code>\n"
            "<i>Show all loaded modules</i>\n\n"
            "<b>Supported formats:</b> SMVF, Hikka, Mku"
        )

    @cmd("restart")
    async def restart_cmd(self, event):
        """
        🔄 Restart the userbot process.
        All modules will be reloaded.
        """
        await self.edit(event, "🔄 Restarting SMVF...")
        self.log.info("Restart requested by owner")
        os.execv(sys.executable, [sys.executable] + sys.argv)
