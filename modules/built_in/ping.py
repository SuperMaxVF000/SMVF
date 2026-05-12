"""
SMVF Built-in: Ping — Made by SuperMaxVF
"""
import mimetypes, os, time
from smvf.core.module import SMVFModule, cmd

_BASE      = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_MEDIA_DIR = os.path.join(_BASE, "data", "ping_media")
os.makedirs(_MEDIA_DIR, exist_ok=True)


class PingModule(SMVFModule):
    strings = {
        "name": "Ping",
        "doc":  "Shows Telegram latency and bot uptime. Supports media attachment.",
    }

    async def on_load(self):
        self.log.ok("Ping module loaded")

    @cmd("ping")
    async def ping_cmd(self, event):
        """
        🛰 <b>Ping</b>

        <code>.ping</code> — show latency and uptime

        <b>Media attachment:</b>
        <code>.ping set</code> — reply to a photo/gif/video to attach it
        <code>.ping clear</code> — remove attached media
        """
        args = self.args(event).strip()

        if args == "set":
            if not event.is_reply:
                return await self.edit(event,
                    "⚠️ Reply to a photo, gif or video with <code>.ping set</code>"
                )
            reply = await event.get_reply_message()
            if not reply.media:
                return await self.edit(event, "⚠️ No media in that message.")
            path = await self._save_media(reply)
            self.cfg.set("ping_media", path)
            return await self.edit(event, "✅ Ping media saved!")

        if args == "clear":
            self.cfg.set("ping_media", None)
            return await self.edit(event, "✅ Ping media cleared.")

        t1  = time.monotonic()
        msg = await self.edit(event, "🌌 Pinging...")
        ms  = round((time.monotonic() - t1) * 1000, 1)

        star = "⭐" if self.premium else "✦"
        text = (
            f"🛰 <b>SMVF Ping</b>\n\n"
            f"{star} Latency: <code>{ms} ms</code>\n"
            f"⏱ Uptime: <code>{self.uptime}</code>\n\n"
            f"<i>Made by SuperMaxVF</i>"
        )

        media = self.cfg.get("ping_media")
        if media and os.path.exists(media):
            await event.delete()
            await self.client.send_file(event.chat_id, media, caption=text, parse_mode="html")
        else:
            await msg.edit(text, parse_mode="html")

    async def _save_media(self, message):
        if hasattr(message.media, "photo"):
            ext = ".jpg"
        elif hasattr(message.media, "document"):
            mime = getattr(message.media.document, "mime_type", "video/mp4")
            ext  = mimetypes.guess_extension(mime) or ".mp4"
        else:
            ext = ".bin"
        path = os.path.join(_MEDIA_DIR, f"ping{ext}")
        await message.download_media(file=path)
        return path
