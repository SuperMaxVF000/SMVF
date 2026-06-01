# SMVF Module Documentation

> Версия: 1.0beta | [GitHub](https://github.com/SuperMaxVF000) | [Канал](https://t.me/MadeBySuperMaxVF)

SMVF поддерживает **три формата модулей**. Выбирай любой.

---

## Форматы модулей

| Формат | Тип | Описание |
|--------|-----|----------|
| `SMVFNative` 🟢 | Нативный | Новый формат, все возможности SMVF |
| `MCUBCompat` 🔵 | Совместимость | Модули от MCUB — работают без изменений |
| `HikkaCompat` 🟣 | Совместимость | Большинство простых Hikka-модулей |

---

## Формат 1: SMVF Native (рекомендуется)

```python
# my_module.py

from telethon import events
from smvf.core.dispatcher import register_builtin
from smvf.core.database import get as cfg_get, set_value as cfg_set
from smvf.utils.helpers import escape_html


def register(client) -> None:
    """
    Точка входа модуля. Обязательна.
    Вызывается один раз при загрузке.
    """
    register_builtin("hello", hello_handler)
    register_builtin("bye",   bye_handler)


async def hello_handler(event: events.NewMessage.Event) -> None:
    """.hello — приветствие"""
    await event.edit("👋 Привет!")


async def bye_handler(event: events.NewMessage.Event) -> None:
    """.bye — прощание"""
    await event.edit("👋 Пока!")
```

### Доступные утилиты SMVF

```python
from smvf.core.database import get, set_value          # конфиг
from smvf.core.dispatcher import register_builtin       # регистрация команд
from smvf.utils.helpers import escape_html, format_uptime, get_args
from smvf.utils.platform import detect_platform, get_cpu_usage
from smvf.inline.manager import get_bot_username, send_via_inline
```

### Регистрация команд через `client.add_event_handler`

```python
from telethon import events

def register(client) -> None:
    prefix = "."

    @client.on(events.NewMessage(outgoing=True, pattern=rf"^\{prefix}echo(\s|$)"))
    async def echo_cmd(event):
        args = event.raw_text.split(None, 1)
        text = args[1] if len(args) > 1 else "—"
        await event.edit(f"🔊 {escape_html(text)}", parse_mode="html")
```

### Сохранение настроек модуля

```python
from smvf.core.database import get as cfg_get, set_value as cfg_set

def register(client) -> None:
    register_builtin("setgreeting", set_greeting_handler)
    register_builtin("greeting",    greeting_handler)

async def set_greeting_handler(event):
    args = event.raw_text.split(None, 1)
    if len(args) < 2:
        await event.edit("❌ Укажите текст")
        return
    cfg_set("my_module.greeting", args[1])
    await event.edit("✅ Приветствие сохранено!")

async def greeting_handler(event):
    text = cfg_get("my_module.greeting", "Привет!")
    await event.edit(text)
```

### Premium emoji

```python
async def my_cmd(event):
    me = await event.client.get_me()
    if getattr(me, "premium", False):
        icon = '<emoji document_id=5431449001532594346>⚡️</emoji>'
    else:
        icon = "⚡️"
    await event.edit(f"{icon} Команда выполнена!", parse_mode="html")
```

### Отправка через Inline-бот (via @smvfinlineXXXX)

```python
from smvf.core.database import get as cfg_get

async def my_cmd(event):
    bot_username = cfg_get("inline_bot_username", "")
    if bot_username:
        results = await event.client.inline_query(bot_username, "Текст сообщения")
        if results:
            await event.delete()
            await results[0].click(event.chat_id)
```

---

## Формат 2: MCUB Compatible

Если у тебя уже есть MCUB-модуль — просто скопируй файл. Работает без изменений.

```python
# mcub_style.py — оригинальный MCUB-модуль

from telethon import events

def register(client):
    """MCUB-стиль: register(client)"""

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.test$"))
    async def test_cmd(event):
        await event.edit("✅ MCUB-модуль работает!")
```

**Автоопределение:** SMVF видит `def register(` → считает MCUB-форматом.

---

## Формат 3: Hikka Compatible

Простые Hikka-модули работают. Есть ограничения (см. `docs/HIKKA_COMPAT.md`).

```python
# hikka_style.py — оригинальный Hikka-модуль

from .. import loader  # будет заменено на smvf.compat.hikka

@loader.tds
class MyModule(loader.Module):
    """Мой модуль"""

    strings = {"name": "MyModule", "_cmd_doc_hello": "Привет"}
    strings_ru = {"_cmd_doc_hello": "Привет (на русском)"}

    async def hellocmd(self, message):
        """.hello"""
        await message.edit("👋 Привет из Hikka-модуля!")
```

**Автоопределение:** SMVF видит `loader.Module` → считает Hikka-форматом.

---

## Структура файла модуля

```
my_module.py
├── Метаданные (опционально)
│   ├── __name__ = "MyModule"
│   ├── __version__ = (1, 0, 0)
│   └── __doc__ = "Описание"
├── register(client) — точка входа (обязательно для SMVF/MCUB)
└── Функции-обработчики
```

---

## Команды управления модулями

| Команда | Описание |
|---------|----------|
| `.lm <url>` | Загрузить модуль из URL |
| `.dlm` | Загрузить модуль из файла (ответьте на файл) |
| `.ulm <name>` | Выгрузить модуль |
| `.mlm` | Список загруженных модулей |

---

## Ограничения

- Один модуль = один `.py` файл
- Имя файла становится именем модуля (без `.py`)
- Не используй глобальные переменные для хранения состояния между перезапусками — используй `cfg_set/cfg_get`
- Модуль не должен блокировать event loop — только `async` функции

---

## Пример полноценного модуля

```python
# weather.py — пример полноценного SMVF-модуля

"""
Модуль погоды для SMVF Userbot.
Команды: .weather <город>
"""

import aiohttp
import logging
from telethon import events

from smvf.core.dispatcher import register_builtin
from smvf.utils.helpers import escape_html, get_args

logger = logging.getLogger(__name__)

API_URL = "https://wttr.in/{city}?format=3&lang=ru"


def register(client) -> None:
    register_builtin("weather", weather_handler)
    logger.info("Модуль weather загружен")


async def weather_handler(event: events.NewMessage.Event) -> None:
    """.weather <город> — погода в городе"""
    city = get_args(event.raw_text).strip()

    if not city:
        await event.edit("❌ Укажите город. Пример: <code>.weather Москва</code>", parse_mode="html")
        return

    await event.edit("🌍 Загрузка погоды...", parse_mode="html")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                API_URL.format(city=city),
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    await event.edit(f"🌤 {escape_html(text.strip())}", parse_mode="html")
                else:
                    await event.edit("❌ Город не найден.", parse_mode="html")
    except Exception as e:
        logger.error("weather ошибка: %s", e)
        await event.edit(f"❌ Ошибка: {escape_html(str(e))}", parse_mode="html")
```
