# 📦 SMVF — Документация по написанию модулей

> *✦ Made by SuperMaxVF ✦*  
> 📡 [t.me/MadeBySuperMaxVF](https://t.me/MadeBySuperMaxVF) | 👨‍💻 [t.me/Mad3BySuperMaxVF](https://t.me/Mad3BySuperMaxVF)

---

## Структура модуля

Каждый SMVF-модуль — это `.py` файл с обязательной функцией `register(client)`.

```python
from telethon import events

def register(client):
    """SMVF вызывает эту функцию при загрузке модуля."""
    
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.моякоманда$"))
    async def handler(event):
        await event.edit("Привет!")
```

Помести файл в папку `modules/` — он загрузится автоматически при следующем запуске,  
либо сразу через `.mod load <url>`.

---

## Паттерны команд

```python
# Команда без аргументов
pattern=r"^\.ping$"

# Команда с необязательными аргументами
pattern=r"^\.say(?: (.+))?$"
# event.pattern_match.group(1) → текст или None

# Команда с обязательным аргументом
pattern=r"^\.say (.+)$"
# event.pattern_match.group(1) → текст

# Несколько слов аргументов
pattern=r"^\.cmd (\w+)(?: (.+))?$"
# group(1) → первое слово, group(2) → остаток
```

---

## Методы event

```python
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.пример (.+)$"))
async def handler(event):
    args = event.pattern_match.group(1)   # аргументы команды
    
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
        print(reply.sender)     # отправитель
    
    # ID чата и отправителя
    print(event.chat_id)
    print(event.sender_id)
    
    # Исходный текст сообщения
    print(event.raw_text)
    print(event.message.text)
```

---

## Отправка медиа

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

# Стикер
await client.send_file(event.chat_id, "sticker.webp")

# Скачать медиа из ответа
reply = await event.message.get_reply_message()
if reply and reply.media:
    path = await client.download_media(reply.media, "downloaded_file")
```

---

## Инлайн-кнопки

```python
from telethon import Button

# Одна кнопка-ссылка
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
        [Button.url("Канал", "https://t.me/MadeBySuperMaxVF"),
         Button.url("Dev", "https://t.me/Mad3BySuperMaxVF")],
    ],
)

# Callback-кнопка (только в боте, не в юзерботе напрямую)
# Для юзербота используй только url-кнопки
```

---

## Форматирование текста

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
    "<a href='https://t.me/MadeBySuperMaxVF'>Ссылка</a>",
    parse_mode="html",
)

# Упоминание пользователя
await event.edit(
    f"<a href='tg://user?id={user_id}'>Имя</a>",
    parse_mode="html",
)

# Спойлер
await event.edit("<tg-spoiler>Секрет</tg-spoiler>", parse_mode="html")
```

---

## Premium-эмодзи

```python
from smvf import config as cfg

# Проверить наличие Premium
me = await client.get_me()
if cfg.get("premium_emoji") and me.premium:
    emoji = "<emoji document_id=5449599833973203438>🧡</emoji>"
else:
    emoji = "🧡"

await event.edit(f"Привет {emoji}", parse_mode="html")
```

---

## Работа с конфигом

```python
from smvf import config as cfg

# Получить значение
value = cfg.get("my_module_setting", "default")

# Сохранить значение
cfg.set_value("my_module_setting", "new_value")

# Удобный паттерн для настроек модуля
def get_setting(key, default=None):
    return cfg.get(f"mymodule_{key}", default)

def set_setting(key, value):
    cfg.set_value(f"mymodule_{key}", value)
```

---

## Логирование

```python
from smvf import logger as log

log.info("Инфо сообщение")
log.ok("Успех")
log.warn("Предупреждение")
log.error("Ошибка")
```

Логи попадают в: терминал, файл `logs/`, лог-группу в Telegram.

---

## Утилиты

```python
from smvf.utils import format_uptime, ensure_dir
import time

# Форматировать время работы
uptime = format_uptime(time.time() - start_time)  # "2ч 15м 30с"

# Создать директорию
ensure_dir("my_module_data")
```

---

## Полный пример модуля

```python
"""
Модуль: WeatherMod
Команда: .weather <город>
Автор: Ваш ник
"""

import aiohttp
from telethon import events
from smvf import config as cfg, logger as log


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
                url = f"https://wttr.in/{city}?format=3&lang=ru"
                async with session.get(url) as resp:
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

## Совместимость с Hikka-модулями

SMVF включает базовый shim-слой для Hikka-модулей. Большинство простых модулей работают.  
Помести `.py` файл Hikka-модуля в папку `modules/` — SMVF автоматически определит формат.

Ограничения:
- Hikka Database недоступна — используй `cfg.set_value()`
- Inline-галереи и сложные формы могут не работать
- Переводы (langpacks) не поддерживаются

---

## Совместимость с MCUB-модулями

Полная совместимость. Любой MCUB-модуль с `register(client)` работает без изменений.

---

## Размещение модуля

1. **Локально:** помести `.py` файл в `modules/`
2. **По URL:** `.mod load https://raw.githubusercontent.com/.../mymodule.py`
3. **Файлом:** отправь `.py` файл в любой чат и ответь командой `.mod load`

---

*✦ Made by SuperMaxVF ✦*  
*📡 [t.me/MadeBySuperMaxVF](https://t.me/MadeBySuperMaxVF) | 👨‍💻 [t.me/Mad3BySuperMaxVF](https://t.me/Mad3BySuperMaxVF)*
