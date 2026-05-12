"""
SMVF Built-in: Info — Made by SuperMaxVF
"""
import os, mimetypes
from telethon import Button
from smvf.core.module import SMVFModule, cmd

_BASE      = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_MEDIA_DIR = os.path.join(_BASE, "data", "info_media")
os.makedirs(_MEDIA_DIR, exist_ok=True)

_DEFAULT = (
    "🌌 <b>SMVF Userbot</b> <code>v1.0</code>\n"
    "✦ <i>Made by SuperMaxVF</i>\n\n"
    "📡 <a href='https://t.me/MadeBySuperMaxVF'>Channel</a>  "
    "💻 <a href='https://t.me/Mad3BySuperMaxVF'>Dev</a>  "
    "🔗 <a href='https://github.com/SuperMaxVF000/SMVF'>GitHub</a>"
)


class InfoModule(SMVFModule):
    strings = {
        "name": "Info",
        "doc":  "Userbot info card with media, inline buttons and HTML formatting.",
    }

    async def on_load(self):
        self.log.ok("Info module loaded")

    @cmd("info")
    async def info_cmd(self, event):
        """
        🌌 <b>Info Card</b>

        <code>.info</code> — show the info card

        <b>Customisation:</b>
        <code>.info set</code> — reply to a photo/gif/video to attach it
        <code>.info clear</code> — remove attached media
        <code>.info text &lt;html&gt;</code> — set card text (supports HTML tags)
        <code>.info btn Label | https://url</code> — add an inline button
        <code>.info btnclear</code> — remove all buttons

        <b>HTML tags you can use:</b>
        &lt;b&gt;bold&lt;/b&gt;  &lt;i&gt;italic&lt;/i&gt;  &lt;code&gt;mono&lt;/code&gt;
        &lt;u&gt;underline&lt;/u&gt;  &lt;s&gt;strike&lt;/s&gt;
        &lt;a href='url'&gt;link&lt;/a&gt;  &lt;blockquote&gt;quote&lt;/blockquote&gt;
        """
        args = self.args(event).strip()

        if args == "set":
            if not event.is_reply:
                return await self.edit(event,
                    "⚠️ Reply to a photo, gif or video with <code>.info set</code>"
                )
            reply = await event.get_reply_message()
            if not reply.media:
                return await self.edit(event, "⚠️ That message has no media.")
            path = await self._save_media(reply, _MEDIA_DIR, "info")
            self.cfg.set("info_media", path)
            return await self.edit(event, "✅ Info media saved!")

        if args == "clear":
            self.cfg.set("info_media", None)
            return await self.edit(event, "✅ Info media cleared.")

        if args == "btnclear":
            self.cfg.set("info_buttons", [])
            return await self.edit(event, "✅ Buttons cleared.")

        if args.startswith("btn "):
            rest = args[4:].strip()
            if "|" not in rest:
                return await self.edit(event,
                    "❌ Format: <code>.info btn Label | https://url</code>"
                )
            label, url = rest.split("|", 1)
            btns = self.cfg.get("info_buttons") or []
            btns.append({"text": label.strip(), "url": url.strip()})
            self.cfg.set("info_buttons", btns)
            return await self.edit(event, "✅ Button added.")

        if args.startswith("text "):
            self.cfg.set("info_text", args[5:].strip())
            return await self.edit(event, "✅ Info text updated.")

        await event.delete()
        text  = self.cfg.get("info_text") or _DEFAULT
        if self.premium:
            text = "🌌 " + text
        media = self.cfg.get("info_media")
        btns  = self._build_buttons()
        kw    = {"parse_mode": "html", "link_preview": False}
        if btns:
            kw["buttons"] = btns
        if media and os.path.exists(media):
            await self.client.send_file(event.chat_id, media, caption=text, **kw)
        else:
            await self.client.send_message(event.chat_id, text, **kw)

    async def _save_media(self, message, directory, prefix):
        if hasattr(message.media, "photo"):
            ext = ".jpg"
        elif hasattr(message.media, "document"):
            mime = getattr(message.media.document, "mime_type", "video/mp4")
            ext  = mimetypes.guess_extension(mime) or ".mp4"
        else:
            ext = ".bin"
        path = os.path.join(directory, f"{prefix}{ext}")
        await message.download_media(file=path)
        return path

    def _build_buttons(self):
        raw = self.cfg.get("info_buttons") or []
        if not raw:
            return None
        rows, row = [], []
        for i, b in enumerate(raw):
            row.append(Button.url(b["text"], b["url"]))
            if len(row) == 2 or i == len(raw) - 1:
                rows.append(row); row = []
        return rows
