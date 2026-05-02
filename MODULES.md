# 📦 SMVF — Module Development Docs / Документация по модулям

> *✦ Made by SuperMaxVF ✦*
> 📡 [t.me/MadeBySuperMaxVF](https://t.me/MadeBySuperMaxVF) | 👨‍💻 [t.me/Mad3BySuperMaxVF](https://t.me/Mad3BySuperMaxVF)

[🇬🇧 English](#-english) · [🇷🇺 Русский](#-русский)

---

## 🇬🇧 English

### Module structure

Every SMVF module is a `.py` file with a required `register(client)` function.

```python
from telethon import events

def register(client):
    """SMVF calls this function when loading the module."""

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.mycommand$"))
    async def handler(event):
        await event.edit("Hello from my module! ✦ Made by SuperMaxVF")
```

Place the file in the `modules/` folder — it loads automatically on next start,
or immediately via `.mod load <url>`.

---

### Command patterns

```python
# No arguments
pattern=r"^\.ping$"

# Optional argument
pattern=r"^\.say(?: (.+))?$"
# event.pattern_match.group(1) → text or None

# Required argument
pattern=r"^\.say (.+)$"
# event.pattern_match.group(1) → text

# Two arguments
pattern=r"^\.cmd (\w+)(?: (.+))?$"
# group(1) → first word, group(2) → rest
```

---

### Event methods

```python
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.example (.+)$"))
async def handler(event):
    args = event.pattern_match.group(1)

    # Edit the current message
    await event.edit("New text")
    await event.edit("<b>HTML</b>", parse_mode="html")

    # Delete the current message
    await event.delete()

    # Send a new message to the same chat
    await client.send_message(event.chat_id, "Hello!")

    # Get the message being replied to
    reply = await event.message.get_reply_message()
    if reply:
        print(reply.raw_text)   # text
        print(reply.sender)     # sender object

    # Chat and sender IDs
    print(event.chat_id)
    print(event.sender_id)

    # Raw message text
    print(event.raw_text)
```

---

### Sending media

```python
# Photo
await client.send_file(event.chat_id, "path/to/photo.jpg", caption="Caption")

# Video (with streaming support)
await client.send_file(
    event.chat_id,
    "path/to/video.mp4",
    caption="Video",
    supports_streaming=True,
)

# Document
await client.send_file(event.chat_id, "file.zip")

# Download media from a replied message
reply = await event.message.get_reply_message()
if reply and reply.media:
    path = await client.download_media(reply.media, "downloaded_file")
```

---

### Inline URL buttons

```python
from telethon import Button

# Single button
await client.send_message(
    event.chat_id,
    "Text with button",
    buttons=[Button.url("Click me!", "https://t.me/MadeBySuperMaxVF")],
)

# Multiple buttons in a row
await client.send_message(
    event.chat_id,
    "Choose:",
    buttons=[
        [
            Button.url("Channel", "https://t.me/MadeBySuperMaxVF"),
            Button.url("Dev", "https://t.me/Mad3BySuperMaxVF"),
        ],
    ],
)
```

---

### Text formatting

```python
# HTML (recommended)
await event.edit(
    "<b>Bold</b>\n"
    "<i>Italic</i>\n"
    "<u>Underline</u>\n"
    "<s>Strikethrough</s>\n"
    "<code>Monospace</code>\n"
    "<pre>Code block</pre>\n"
    "<blockquote>Quote</blockquote>\n"
    "<tg-spoiler>Spoiler</tg-spoiler>\n"
    "<a href='https://t.me/MadeBySuperMaxVF'>Link</a>",
    parse_mode="html",
)

# User mention
await event.edit(
    f"<a href='tg://user?id={user_id}'>Name</a>",
    parse_mode="html",
)
```

---

### Premium emoji

```python
from smvf import config as cfg

me = await client.get_me()
if cfg.get("premium_emoji") and me.premium:
    emoji = "<emoji document_id=5449599833973203438>🧡</emoji>"
else:
    emoji = "🧡"

await event.edit(f"Hello {emoji}", parse_mode="html")
```

---

### Config storage

```python
from smvf import config as cfg

# Read a value
value = cfg.get("my_module_key", "default")

# Save a value (persists to smvf_config.json)
cfg.set_value("my_module_key", "new_value")

# Namespaced helpers to avoid collisions
def get_opt(key, default=None):
    return cfg.get(f"mymodule_{key}", default)

def set_opt(key, value):
    cfg.set_value(f"mymodule_{key}", value)
```

---

### Logging

```python
from smvf import logger as log

log.info("Info message")
log.ok("Success")
log.warn("Warning")
log.error("Error")
```

Logs go to: terminal, `logs/` file, and the Telegram log group.

---

### Full module example

```python
"""
Module : WeatherMod
Command: .weather <city>
Author : YourNick
"""

import aiohttp
from telethon import events
from smvf import logger as log


def register(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.weather(?: (.+))?$"))
    async def weather_handler(event):
        city = event.pattern_match.group(1)

        if not city:
            await event.edit(
                "❌ <b>Specify a city:</b> <code>.weather London</code>",
                parse_mode="html",
            )
            return

        await event.edit(f"🌍 Fetching weather for <b>{city}</b>...", parse_mode="html")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://wttr.in/{city}?format=3") as resp:
                    if resp.status == 200:
                        data = await resp.text()
                        await event.edit(
                            f"🌤 <b>Weather:</b>\n<code>{data}</code>\n\n"
                            f"<i>✦ Made by SuperMaxVF ✦</i>",
                            parse_mode="html",
                        )
                    else:
                        await event.edit("❌ City not found")
        except Exception as e:
            log.error(f"WeatherMod error: {e}")
            await event.edit(f"❌ Error: <code>{e}</code>", parse_mode="html")
```

---

### Module compatibility

| Format | How to detect | Notes |
|--------|--------------|-------|
| **SMVF** | has `def register(client)` | Native format, full support |
| **MCUB** | has `def register(client)` + `add_event_handler` | Full support |
| **Hikka** | has `loader.Module` or `loader.tds` | Partial — basic commands work, inline galleries may not |

---

### Publishing your module

1. **Local:** place the `.py` file in `modules/`
2. **By URL:** `.mod load https://raw.githubusercontent.com/.../mymodule.py`
3. **By file:** send a `.py` file to any chat and reply with `.mod load`

---

---

## 🇷🇺 Русский

### Структура модуля

Каждый SMVF-модуль — это `.py` файл с обязательной функцией `register(client)`.

```python
from telethon import events

def register(client):
    """SMVF вызывает эту функцию при загрузке модуля."""

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.моякоманда$"))
    async def handler(event):
        await event.edit("Привет от модуля! ✦ Made by SuperMaxVF")
```

Помести файл в папку `modules/` — он загрузится автоматически при следующем запуске,
либо сразу через `.mod load <url>`.

---

### Паттерны команд

```python
# Команда без аргументов
pattern=r"^\.ping$"

# Необязательный аргумент
pattern=r"^\.say(?: (.+))?$"
# event.pattern_match.group(1) → текст или None

# Обязательный аргумент
pattern=r"^\.say (.+)$"
# event.pattern_match.group(1) → текст

# Два аргумента
pattern=r"^\.cmd (\w+)(?: (.+))?$"
# group(1) → первое слово, group(2) → остаток
```

---

### Методы event

```python
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.пример (.+)$"))
async def handler(event):
    args = event.pattern_match.group(1)

    # Редактировать текущее сообщение
    await event.edit("Новый текст")
    await event.edit("<b>HTML</b>", parse_mode="html")

    # Удалить текущее сообщение
    await event.delete()

    # Отправить новое сообщение в тот же чат
    await client.send_message(event.chat_id, "Привет!")

    # Получить сообщение на которое ответили
    reply = await event.message.get_reply_message()
    if reply:
        print(reply.raw_text)   # текст
        print(reply.sender)     # объект отправителя

    # ID чата и отправителя
    print(event.chat_id)
    print(event.sender_id)

    # Исходный текст сообщения
    print(event.raw_text)
```

---

### Отправка медиа

```python
# Фото
await client.send_file(event.chat_id, "path/to/photo.jpg", caption="Подпись")

# Видео (с поддержкой стриминга)
await client.send_file(
    event.chat_id,
    "path/to/video.mp4",
    caption="Видео",
    supports_streaming=True,
)

# Документ
await client.send_file(event.chat_id, "file.zip")

# Скачать медиа из ответа
reply = await event.message.get_reply_message()
if reply and reply.media:
    path = await client.download_media(reply.media, "downloaded_file")
```

---

### Инлайн-кнопки (URL)

```python
from telethon import Button

# Одна кнопка
await client.send_message(
    event.chat_id,
    "Текст с кнопкой",
    buttons=[Button.url("Нажми!", "https://t.me/MadeBySuperMaxVF")],
)

# Несколько кнопок в ряд
await client.send_message(
    event.chat_id,
    "Выбери:",
    buttons=[
        [
            Button.url("Канал", "https://t.me/MadeBySuperMaxVF"),
            Button.url("Dev", "https://t.me/Mad3BySuperMaxVF"),
        ],
    ],
)
```

---

### Форматирование текста

```python
# HTML (рекомендуется)
await event.edit(
    "<b>Жирный</b>\n"
    "<i>Курсив</i>\n"
    "<u>Подчёркнутый</u>\n"
    "<s>Зачёркнутый</s>\n"
    "<code>Моноширинный</code>\n"
    "<pre>Блок кода</pre>\n"
    "<blockquote>Цитата</blockquote>\n"
    "<tg-spoiler>Спойлер</tg-spoiler>\n"
    "<a href='https://t.me/MadeBySuperMaxVF'>Ссылка</a>",
    parse_mode="html",
)

# Упоминание пользователя
await event.edit(
    f"<a href='tg://user?id={user_id}'>Имя</a>",
    parse_mode="html",
)
```

---

### Premium-эмодзи

```python
from smvf import config as cfg

me = await client.get_me()
if cfg.get("premium_emoji") and me.premium:
    emoji = "<emoji document_id=5449599833973203438>🧡</emoji>"
else:
    emoji = "🧡"

await event.edit(f"Привет {emoji}", parse_mode="html")
```

---

### Хранение настроек

```python
from smvf import config as cfg

# Получить значение
value = cfg.get("my_module_key", "default")

# Сохранить значение (записывается в smvf_config.json)
cfg.set_value("my_module_key", "new_value")

# Вспомогательные функции с неймспейсом (чтобы не конфликтовать с другими модулями)
def get_opt(key, default=None):
    return cfg.get(f"mymodule_{key}", default)

def set_opt(key, value):
    cfg.set_value(f"mymodule_{key}", value)
```

---

### Логирование

```python
from smvf import logger as log

log.info("Инфо сообщение")
log.ok("Успех")
log.warn("Предупреждение")
log.error("Ошибка")
```

Логи попадают в: терминал, файл `logs/`, лог-группу в Telegram.

---

### Полный пример модуля

```python
"""
Модуль : WeatherMod
Команда: .weather <город>
Автор  : ВашНик
"""

import aiohttp
from telethon import events
from smvf import logger as log


def register(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.weather(?: (.+))?$"))
    async def weather_handler(event):
        city = event.pattern_match.group(1)

        if not city:
            await event.edit(
                "❌ <b>Укажи город:</b> <code>.weather Москва</code>",
                parse_mode="html",
            )
            return

        await event.edit(f"🌍 Получаю погоду для <b>{city}</b>...", parse_mode="html")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://wttr.in/{city}?format=3&lang=ru") as resp:
                    if resp.status == 200:
                        data = await resp.text()
                        await event.edit(
                            f"🌤 <b>Погода:</b>\n<code>{data}</code>\n\n"
                            f"<i>✦ Made by SuperMaxVF ✦</i>",
                            parse_mode="html",
                        )
                    else:
                        await event.edit("❌ Город не найден")
        except Exception as e:
            log.error(f"WeatherMod ошибка: {e}")
            await event.edit(f"❌ Ошибка: <code>{e}</code>", parse_mode="html")
```

---

### Совместимость форматов

| Формат | Признак | Поддержка |
|--------|---------|-----------|
| **SMVF** | есть `def register(client)` | Полная — нативный формат |
| **MCUB** | есть `def register(client)` + `add_event_handler` | Полная |
| **Hikka** | есть `loader.Module` или `loader.tds` | Частичная — базовые команды работают, сложные inline могут не работать |

---

### Публикация модуля

1. **Локально:** помести `.py` файл в `modules/`
2. **По URL:** `.mod load https://raw.githubusercontent.com/.../mymodule.py`
3. **Файлом:** отправь `.py` файл в любой чат и ответь командой `.mod load`

---

*✦ Made by SuperMaxVF ✦*
*📡 [t.me/MadeBySuperMaxVF](https://t.me/MadeBySuperMaxVF) | 👨‍💻 [t.me/Mad3BySuperMaxVF](https://t.me/Mad3BySuperMaxVF)*
