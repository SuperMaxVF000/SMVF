# MCUB → SMVF: Гайд совместимости

> MCUB-модули работают в SMVF **без изменений**.  
> Формат `def register(client)` — нативный для SMVF.

## Автоопределение

SMVF автоматически определяет MCUB-модуль по наличию `def register(` в файле.

## Что работает

✅ `def register(client)` — без изменений  
✅ `@client.on(events.NewMessage(...))` — без изменений  
✅ Все стандартные Telethon события  
✅ `client.send_message()`, `event.edit()` и т.д.

## Что нужно убрать

❌ Импорты из `userbot.*` — специфичны для MCUB, нужно заменить

**Было:**
```python
from userbot import OWNER_ID
from userbot.utils import helpers
```

**Стало:**
```python
from smvf.core.database import get as cfg_get
# OWNER_ID получаем через: (await client.get_me()).id
```

## Пример совместимого модуля

```python
# simple_mcub.py — работает в SMVF без изменений

from telethon import events

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.hi$"))
    async def hi_handler(event):
        await event.edit("👋 Привет! (MCUB-модуль в SMVF)")
```

## Установка MCUB-модуля в SMVF

```
.lm https://raw.githubusercontent.com/.../module.py
```
или ответить на .py файл командой `.dlm`
