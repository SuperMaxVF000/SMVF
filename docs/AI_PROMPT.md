# AI Prompt: Конвертация Hikka → SMVF

Скопируй этот промпт в любой AI-чат (ChatGPT, Claude, Gemini и др.)  
и вставь после него исходный код Hikka-модуля.

---

## Промпт (копировать целиком)

```
Ты конвертируешь Hikka Userbot модуль в формат SMVF Userbot.

ПРАВИЛА КОНВЕРТАЦИИ:

1. ИМПОРТЫ:
   - Убери все импорты из `.. import loader`, `hikkatl`, `..inline.types`
   - Добавь:
     from telethon import events
     from smvf.core.dispatcher import register_builtin
     from smvf.core.database import get as cfg_get, set_value as cfg_set
     from smvf.utils.helpers import escape_html, get_args
     import logging
     logger = logging.getLogger(__name__)

2. КЛАСС → ФУНКЦИИ:
   - Удали `@loader.tds` декоратор
   - Удали класс (class XyzModule(loader.Module):)
   - Каждый метод `*cmd(self, message)` стань функцией `*_handler(event)`
   - `self.client` → `event.client`
   - `message.edit()` → `event.edit()`
   - `message.reply()` → `event.reply()`

3. ТОЧКА ВХОДА:
   Добавь в начало файла (после импортов):
   
   def register(client) -> None:
       register_builtin("cmd1", cmd1_handler)
       register_builtin("cmd2", cmd2_handler)
       # ... все команды модуля

4. КОНФИГ (ModuleConfig):
   - `self.config["key"]` → `cfg_get("MODULENAME.key", default)`
   - `self.db.get(self.strings["name"], "key")` → `cfg_get("MODULENAME.key")`
   - `self.db.set(...)` → `cfg_set("MODULENAME.key", value)`

5. INLINE (self.inline.form / gallery / list):
   - Замени на Telethon кнопки:
     from telethon import Button
     buttons=[[Button.inline("Текст", b"callback_data")]]
   - Callback: @client.on(events.CallbackQuery(data=b"callback_data"))
   - ВАЖНО: проверяй что нажал владелец: if event.sender_id != (await client.get_me()).id: return

6. LOOP (@loader.loop):
   - Добавь в register():
     asyncio.get_event_loop().create_task(_your_loop(client))
   - Создай:
     async def _your_loop(client):
         while True:
             await your_logic(client)
             await asyncio.sleep(INTERVAL_SECONDS)

7. STRINGS:
   - strings dict → константы или f-строки прямо в коде
   - Не нужны

8. CLIENT_READY:
   - Логику из client_ready перенеси в конец register()

9. PREMIUM EMOJI:
   - Оставь как есть, но оберни в проверку:
     me = await event.client.get_me()
     if getattr(me, "premium", False):
         # используй premium emoji

10. РЕЗУЛЬТАТ:
    - Верни только готовый Python-код без объяснений
    - Добавь docstring к файлу с описанием модуля
    - Добавь logger.debug("Модуль X загружен") в register()

Вот Hikka-модуль для конвертации:
[ВСТАВЬ КОД ЗДЕСЬ]
```

---

## Пример использования

**Вопрос к AI:**
```
[промпт выше]

from .. import loader

@loader.tds
class PingModule(loader.Module):
    strings = {"name": "Ping", "_cmd_doc_ping": "Пинг"}

    async def pingcmd(self, message):
        await message.edit("🏓 Pong!")
```

**Ответ AI (готовый SMVF-модуль):**
```python
"""Модуль пинга для SMVF Userbot."""

import logging
from telethon import events
from smvf.core.dispatcher import register_builtin

logger = logging.getLogger(__name__)


def register(client) -> None:
    register_builtin("ping", ping_handler)
    logger.debug("Модуль ping загружен")


async def ping_handler(event: events.NewMessage.Event) -> None:
    """.ping — проверка связи"""
    await event.edit("🏓 Pong!")
```
