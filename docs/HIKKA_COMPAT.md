# Hikka → SMVF: Гайд совместимости

> [GitHub](https://github.com/SuperMaxVF000) | [Канал](https://t.me/MadeBySuperMaxVF)

## Что работает автоматически

✅ Простые команды (`*cmd` методы)  
✅ `strings` / `strings_ru` (локализация)  
✅ `ModuleConfig` / `ConfigValue`  
✅ `client_ready`  
✅ `@loader.loop` с `autostart=True`  
✅ `self.db.get/set` (в памяти)

## Что НЕ работает

❌ `self.inline.form()` — inline-меню Hikka  
❌ `self.inline.gallery()` — галереи  
❌ Web-панель Hikka  
❌ `hikka-tl-new` специфичные API  
❌ `@loader.inline_handler` — Hikka inline query  
❌ `InlineManager`, `InlineCall`

---

## Переписка шаг за шагом

### Шаг 1: Импорты

**Было (Hikka):**
```python
from .. import loader, utils
from ..inline.types import InlineQuery, InlineCall
```

**Стало (SMVF):**
```python
from telethon import events
from smvf.core.dispatcher import register_builtin
from smvf.core.database import get as cfg_get, set_value as cfg_set
from smvf.utils.helpers import escape_html
```

---

### Шаг 2: Класс модуля → функции

**Было (Hikka):**
```python
@loader.tds
class GreetModule(loader.Module):
    strings = {"name": "Greet", "_cmd_doc_hello": "Привет"}

    async def hellocmd(self, message):
        await message.edit("👋 Привет!")

    async def byecmd(self, message):
        await message.edit("👋 Пока!")
```

**Стало (SMVF):**
```python
from telethon import events
from smvf.core.dispatcher import register_builtin

def register(client) -> None:
    register_builtin("hello", hello_handler)
    register_builtin("bye",   bye_handler)

async def hello_handler(event: events.NewMessage.Event) -> None:
    await event.edit("👋 Привет!")

async def bye_handler(event: events.NewMessage.Event) -> None:
    await event.edit("👋 Пока!")
```

---

### Шаг 3: ModuleConfig → cfg_set/cfg_get

**Было (Hikka):**
```python
class MyModule(loader.Module):
    strings = {"name": "My"}
    config = loader.ModuleConfig(
        loader.ConfigValue("api_key", "", "API ключ"),
    )

    async def mycmd(self, message):
        key = self.config["api_key"]
```

**Стало (SMVF):**
```python
from smvf.core.database import get as cfg_get, set_value as cfg_set

def register(client) -> None:
    register_builtin("mysetkey", setkey_handler)
    register_builtin("my",       my_handler)

async def setkey_handler(event):
    args = event.raw_text.split(None, 1)
    cfg_set("mymodule.api_key", args[1] if len(args) > 1 else "")
    await event.edit("✅ Ключ сохранён")

async def my_handler(event):
    key = cfg_get("mymodule.api_key", "")
    # ... используем key
```

---

### Шаг 4: self.inline.form() → кнопки Telethon

**Было (Hikka):**
```python
async def mycmd(self, message):
    await self.inline.form(
        text="Подтвердить?",
        message=message,
        reply_markup=[{"text": "✅ Да", "callback": self._confirm}],
    )

async def _confirm(self, call):
    await call.edit("Подтверждено!")
```

**Стало (SMVF):**
```python
from telethon import Button

async def my_handler(event):
    await event.client.send_message(
        event.chat_id,
        "Подтвердить?",
        buttons=[[Button.inline("✅ Да", b"confirm_yes"),
                  Button.inline("❌ Нет", b"confirm_no")]],
    )
    await event.delete()

# Регистрируем callback в register():
from telethon import events as tl_events

def register(client) -> None:
    register_builtin("my", my_handler)

    @client.on(tl_events.CallbackQuery(data=b"confirm_yes"))
    async def on_confirm(event):
        me = await client.get_me()
        if event.sender_id != me.id:
            return
        await event.edit("✅ Подтверждено!")
```

---

### Шаг 5: @loader.loop → asyncio

**Было (Hikka):**
```python
@loader.loop(interval=60, autostart=True)
async def poller(self):
    await self._check_updates()
```

**Стало (SMVF):**
```python
import asyncio

def register(client) -> None:
    asyncio.get_event_loop().create_task(_poller_loop(client))

async def _poller_loop(client) -> None:
    while True:
        await _check_updates(client)
        await asyncio.sleep(60)

async def _check_updates(client) -> None:
    pass  # ваша логика
```

---

## Таблица замен

| Hikka | SMVF |
|-------|------|
| `loader.Module` | `register(client)` функция |
| `self.client` | `event.client` или `client` |
| `message.edit()` | `event.edit()` |
| `self.config["key"]` | `cfg_get("mod.key")` |
| `self.db.get/set` | `cfg_get/cfg_set` |
| `self.inline.form()` | `Button.inline()` + `@client.on(CallbackQuery)` |
| `@loader.loop` | `asyncio.create_task` + `while True` |
| `strings["key"]` | f-строки или константы |
| `loader.tds` | не нужен |
| `client_ready` | логика в `register(client)` |
