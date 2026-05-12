# 📦 SMVF Module Development Guide

> **SMVF Userbot v1.0** · Made by SuperMaxVF
> [GitHub](https://github.com/SuperMaxVF000/SMVF) · [t.me/MadeBySuperMaxVF](https://t.me/MadeBySuperMaxVF) · [t.me/Mad3BySuperMaxVF](https://t.me/Mad3BySuperMaxVF)

---

## English

### Quick Start

Create `modules/external/my_module.py`:

```python
from smvf.core.module import SMVFModule, cmd

class MyModule(SMVFModule):
    strings = {
        "name": "MyModule",
        "doc":  "My cool SMVF module",
    }

    async def on_load(self):
        self.log.ok("MyModule loaded!")

    @cmd("hello")
    async def hello_cmd(self, event):
        await self.edit(event, "👋 <b>Hello from SMVF!</b>")
```

Done — `.hello` is now available.

---

### Supported Module Formats

SMVF loads three formats automatically, no configuration needed:

#### 1. SMVF Native (recommended)

```python
from smvf.core.module import SMVFModule, cmd

class WeatherModule(SMVFModule):
    strings = {"name": "Weather", "doc": "Shows weather."}

    @cmd("weather")
    async def weather_cmd(self, event):
        city = self.args(event) or "Moscow"
        await self.edit(event, f"🌤 Checking weather for {city}...")
```

#### 2. Hikka-compatible

```python
# Hikka modules work as-is. SMVF detects strings + commands automatically.
# client_ready() is called after load, same as Hikka.

class HikkaStyleModule:
    strings = {"name": "HikkaModule", "doc": "Ported from Hikka"}

    async def client_ready(self):
        pass  # called on load

    async def examplecmd(self, message):
        # In Hikka, handlers are named <command>cmd
        await message.edit("Works in SMVF!")
```

#### 3. Mku-compatible

```python
# Mku modules use register(client) — works unchanged.
from telethon import events

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.dice$'))
    async def handler(event):
        import random
        await event.edit(f"🎲 {random.randint(1, 6)}")
```

---

### SMVFModule Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `self.client` | `TelegramClient` | User session (Telethon) |
| `self.bot` | `TelegramClient` | Inline bot session |
| `self.cfg` | `Config` | Config — read and write |
| `self.db` | `Config` | Hikka alias for cfg |
| `self.log` | `SMVFLogger` | Logger |
| `self.core` | `SMVFCore` | Core instance |
| `self.prefix` | `str` | Current prefix (`.`) |
| `self.owner_id` | `int` | Owner Telegram ID |
| `self.premium` | `bool` | Owner has Telegram Premium |
| `self.uptime` | `str` | Bot uptime string |

---

### strings Dictionary

```python
strings = {
    "name":  "MyModule",       # required — shown in .help
    "doc":   "Does stuff.",    # required — module description
    "done":  "✅ Done!",       # optional — your custom reply strings
    "error": "❌ Error: {}",
}
```

Access: `self.strings["done"]`

---

### Registering Commands

```python
@cmd("mycommand")
async def my_cmd(self, event):
    args = self.args(event)   # text after command word
    await self.edit(event, f"You wrote: {args}")
```

`@cmd("name")` auto-registers the handler. No manual wiring.

---

### Helper Methods

```python
await self.edit(event, "<b>Bold</b> text")      # edit the message (HTML)
await self.reply(event, "<i>Italic</i>")         # reply to message
await self.send(chat_id, "Text")                 # send anywhere
text = self.args(event)                          # args after command
self.is_owner(event.sender_id)                   # True if owner
```

---

### HTML Formatting

```python
await self.edit(event, """
<b>Bold</b>
<i>Italic</i>
<u>Underline</u>
<s>Strikethrough</s>
<code>Monospace</code>
<pre>Code block</pre>
<blockquote>Quote</blockquote>
<a href="https://t.me/MadeBySuperMaxVF">Link</a>
""")
```

---

### Inline Buttons

```python
from telethon import Button

buttons = [
    [Button.url("📡 Channel", "https://t.me/MadeBySuperMaxVF")],
    [Button.url("💻 GitHub",  "https://github.com/SuperMaxVF000/SMVF")],
]
await self.client.send_message(
    event.chat_id, "<b>Title</b>",
    buttons=buttons, parse_mode="html"
)
```

---

### Working with Media

```python
# Download media from a replied message
if event.is_reply:
    reply = await event.get_reply_message()
    if reply.media:
        path = await reply.download_media(file="data/saved.jpg")

# Send a file with caption
await self.client.send_file(event.chat_id, "data/image.jpg", caption="Text")

# Auto-detect format (photo vs gif vs video)
import mimetypes, os
if hasattr(reply.media, "photo"):
    ext = ".jpg"
elif hasattr(reply.media, "document"):
    mime = reply.media.document.mime_type or "video/mp4"
    ext  = mimetypes.guess_extension(mime) or ".mp4"
```

---

### Premium Emoji

```python
if self.premium:
    header = "🌌 "   # or use a real custom emoji ID from Telegram
else:
    header = "✦ "

await self.edit(event, header + "<b>My Module</b>")
```

---

### Storing Data

```python
# Read
value = self.cfg.get("mymod.setting", "default")

# Write (auto-saves to data/config.json)
self.cfg.set("mymod.setting", "new_value")

# Complex data (dict/list)
data = self.cfg.get("mymod.data") or {}
data["key"] = "value"
self.cfg.set("mymod.data", data)
```

---

### Logging

```python
self.log.ok("Everything fine")
self.log.info("Info message")
self.log.warn("Warning")
self.log.error("Error description", exc)   # exc is optional
self.log.network("Network problem")
```

All logs go to `logs/smvf.log` and the Telegram log group automatically.

---

### Lifecycle Hooks

```python
class MyModule(SMVFModule):
    async def on_load(self):
        """Called once when module is loaded. Use for init and background tasks."""
        import asyncio
        asyncio.ensure_future(self._loop())

    async def on_unload(self):
        """Called before unload or reload."""
        pass

    async def _loop(self):
        import asyncio
        while True:
            await asyncio.sleep(60)
            # runs every minute in background
```

---

### Full Example Module

```python
"""
WeatherModule for SMVF — Made by SuperMaxVF
Usage: .weather Moscow
"""
import aiohttp
from smvf.core.module import SMVFModule, cmd


class WeatherModule(SMVFModule):
    strings = {
        "name": "Weather",
        "doc":  "Shows weather. Usage: .weather <city>",
        "no_city": "❌ Specify city: <code>.weather Moscow</code>",
        "error":   "❌ Could not fetch weather.",
    }

    async def on_load(self):
        self.log.ok("Weather module loaded")

    @cmd("weather")
    async def weather_cmd(self, event):
        city = self.args(event)
        if not city:
            return await self.edit(event, self.strings["no_city"])

        await self.edit(event, f"🌍 Fetching weather for <b>{city}</b>...")
        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.get(f"https://wttr.in/{city}?format=3") as r:
                    text = await r.text()
            await self.edit(event, f"🌤 <b>Weather</b>\n\n<code>{text}</code>")
        except Exception as e:
            self.log.error("Weather fetch failed", e)
            await self.edit(event, self.strings["error"])
```

---

### Installing Modules

```
.mod install https://raw.githubusercontent.com/you/repo/main/module.py
```

Or drop the `.py` file directly into `modules/external/` and run `.restart`.

---

## Русский

### Быстрый старт

Создай `modules/external/my_module.py`:

```python
from smvf.core.module import SMVFModule, cmd

class MyModule(SMVFModule):
    strings = {
        "name": "MyModule",
        "doc":  "Мой крутой SMVF-модуль",
    }

    async def on_load(self):
        self.log.ok("MyModule загружен!")

    @cmd("hello")
    async def hello_cmd(self, event):
        await self.edit(event, "👋 <b>Привет из SMVF!</b>")
```

Готово — команда `.hello` появляется автоматически.

---

### Форматы модулей

#### 1. SMVF Native (рекомендуется)

```python
from smvf.core.module import SMVFModule, cmd

class MyModule(SMVFModule):
    strings = {"name": "MyModule", "doc": "Описание"}

    @cmd("example")
    async def example_cmd(self, event):
        await self.edit(event, "Работает!")
```

#### 2. Hikka-совместимый

```python
# Hikka-модули работают без изменений.
# SMVF автоматически распознаёт strings + commands.
class HikkaModule:
    strings = {"name": "HikkaModule", "doc": "Портировано из Hikka"}

    async def client_ready(self):
        pass

    async def mycmd(self, message):
        await message.edit("Hikka-модуль работает в SMVF!")
```

#### 3. Mku-совместимый

```python
from telethon import events

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.mku$'))
    async def handler(event):
        await event.edit("Mku-модуль работает!")
```

---

### Атрибуты SMVFModule

| Атрибут | Тип | Описание |
|---------|-----|----------|
| `self.client` | `TelegramClient` | Пользовательская сессия |
| `self.bot` | `TelegramClient` | Inline-бот |
| `self.cfg` | `Config` | Конфиг — чтение/запись |
| `self.db` | `Config` | Hikka-алиас для cfg |
| `self.log` | `SMVFLogger` | Логгер |
| `self.core` | `SMVFCore` | Ядро юзербота |
| `self.prefix` | `str` | Текущий префикс (`.`) |
| `self.owner_id` | `int` | Telegram ID владельца |
| `self.premium` | `bool` | Есть ли Telegram Premium |
| `self.uptime` | `str` | Аптайм юзербота |

---

### Словарь strings

```python
strings = {
    "name":  "MyModule",         # обязательно
    "doc":   "Делает вещи.",     # обязательно
    "done":  "✅ Готово!",       # опционально
    "error": "❌ Ошибка: {}",
}
```

Доступ: `self.strings["done"]`

---

### Регистрация команд

```python
@cmd("mycommand")
async def my_cmd(self, event):
    args = self.args(event)
    await self.edit(event, f"Ты написал: {args}")
```

---

### Хелперы

```python
await self.edit(event, "<b>Жирный</b>")      # редактировать (HTML)
await self.reply(event, "<i>Курсив</i>")     # ответить
await self.send(chat_id, "Текст")            # отправить куда угодно
text = self.args(event)                      # аргументы после команды
self.is_owner(event.sender_id)               # True если владелец
```

---

### HTML-форматирование

```python
await self.edit(event, """
<b>Жирный</b>   <i>Курсив</i>   <u>Подчёрк</u>
<s>Зачёрк</s>   <code>Моно</code>   <pre>Блок кода</pre>
<blockquote>Цитата</blockquote>
<a href="https://t.me/MadeBySuperMaxVF">Ссылка</a>
""")
```

---

### Инлайн-кнопки

```python
from telethon import Button

buttons = [
    [Button.url("📡 Канал", "https://t.me/MadeBySuperMaxVF")],
]
await self.client.send_message(
    event.chat_id, "Текст",
    buttons=buttons, parse_mode="html"
)
```

---

### Работа с медиа

```python
if event.is_reply:
    reply = await event.get_reply_message()
    if reply.media:
        path = await reply.download_media(file="data/saved.jpg")

await self.client.send_file(event.chat_id, "data/image.jpg", caption="Текст")
```

---

### Premium Emoji

```python
if self.premium:
    header = "🌌 "
else:
    header = "✦ "
await self.edit(event, header + "<b>Мой модуль</b>")
```

---

### Хранение данных

```python
value = self.cfg.get("mymod.setting", "default")  # читать
self.cfg.set("mymod.setting", "new_value")          # писать (авто-сохранение)
```

---

### Логирование

```python
self.log.ok("Всё хорошо")
self.log.info("Информация")
self.log.warn("Предупреждение")
self.log.error("Ошибка", exc)
self.log.network("Проблема с сетью")
```

Логи пишутся в `logs/smvf.log` и в TG-группу логов.

---

### Жизненный цикл

```python
class MyModule(SMVFModule):
    async def on_load(self):
        """Вызывается при загрузке."""
        import asyncio
        asyncio.ensure_future(self._loop())

    async def on_unload(self):
        """Вызывается перед выгрузкой."""
        pass

    async def _loop(self):
        import asyncio
        while True:
            await asyncio.sleep(60)
            # что-то каждую минуту
```

---

### Установка модулей

```
.mod install https://raw.githubusercontent.com/you/repo/main/module.py
```

Или просто положи `.py`-файл в `modules/external/` и напиши `.restart`.

---

> SMVF Userbot v1.0 · Made by SuperMaxVF
> [t.me/MadeBySuperMaxVF](https://t.me/MadeBySuperMaxVF) · [github.com/SuperMaxVF000/SMVF](https://github.com/SuperMaxVF000/SMVF)
