# ✦ SMVF Module Example ✦
# Made by SuperMaxVF
# https://github.com/SuperMaxVF000/SMVF
#
# Это пример SMVF-модуля. Скопируй этот файл, измени и помести в папку modules/

from telethon import events


# ── Обязательная функция register(client) ─────────────────────────────────

def register(client):
    """SMVF вызывает эту функцию при загрузке модуля."""

    # ── Простая команда ────────────────────────────────────────────────────
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.hello$"))
    async def hello_handler(event):
        """Отвечает на .hello"""
        await event.edit("👋 Привет! Это SMVF модуль. Made by SuperMaxVF ✦")

    # ── Команда с аргументами ──────────────────────────────────────────────
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.say (.+)$"))
    async def say_handler(event):
        """Повторяет текст: .say <текст>"""
        text = event.pattern_match.group(1)
        await event.edit(f"🗣 {text}")

    # ── Команда с ответом на сообщение ────────────────────────────────────
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.quote$"))
    async def quote_handler(event):
        """Цитирует сообщение на которое ответили"""
        reply = await event.message.get_reply_message()
        if not reply:
            await event.edit("❌ Ответь на сообщение!")
            return
        name = getattr(reply.sender, "first_name", "Аноним")
        text = reply.raw_text or "[медиа]"
        await event.edit(f"💬 <b>{name}:</b>\n<i>{text}</i>", parse_mode="html")

    # ── Команда с инлайн-медиа ────────────────────────────────────────────
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.sticker$"))
    async def sticker_handler(event):
        """Отвечает стикером-заглушкой"""
        await event.delete()
        await client.send_message(event.chat_id, "🌌 Космический стикер!")
