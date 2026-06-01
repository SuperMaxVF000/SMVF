# Встроенный модуль SMVF v1.2beta: Help
# .help — список всех команд с кратким описанием
# .help <команда> — подробное описание

import logging
from telethon import events

from ..core.database import get as cfg_get
from ..core.dispatcher import register_builtin
from ..core.loader import get_loaded_modules
from ..utils.helpers import escape_html

logger = logging.getLogger(__name__)

# Краткое описание (для .help списка) и подробное (для .help <команда>)
_HELP: dict = {
    "ping": {
        "short": "Пинг и аптайм",
        "full":  "Проверяет задержку редактирования и показывает аптайм юзербота.\n"
                 "Если установлено изображение — отправляется через inline-бота.\n\n"
                 "Связанные команды:\n"
                 "• <code>.pingset &lt;url&gt;</code> — установить картинку\n"
                 "• <code>.pingreset</code> — сбросить картинку",
    },
    "pingset": {
        "short": "Установить картинку для .ping",
        "full":  "Устанавливает кастомное изображение для команды .ping.\n\n"
                 "Пример: <code>.pingset https://i.imgur.com/xxx.jpg</code>\n"
                 "Без аргументов — показывает текущее изображение.",
    },
    "pingreset": {
        "short": "Сбросить картинку .ping",
        "full":  "Сбрасывает кастомное изображение для .ping до стандартного вида.",
    },
    "info": {
        "short": "Карточка информации о боте",
        "full":  "Отображает карточку с информацией о юзерботе.\n"
                 "Отправляется через inline-бота (via @smvfinlineXXXX).\n\n"
                 "Кастомизация:\n"
                 "• <code>.setbanner &lt;url&gt;</code> — установить баннер\n"
                 "• <code>.setbanner</code> (ответ на фото/гиф/видео) — скачать и установить\n"
                 "• <code>.setbtn Название | url</code> — добавить кнопку\n"
                 "• <code>.setinfo &lt;текст&gt;</code> — кастомный текст\n"
                 "• <code>.resetinfo</code> — сбросить всё",
    },
    "setbanner": {
        "short": "Установить баннер для .info",
        "full":  "Устанавливает баннер для команды .info.\n\n"
                 "Варианты:\n"
                 "• <code>.setbanner &lt;url&gt;</code> — из прямой ссылки\n"
                 "• Ответить на фото/гиф/видео → <code>.setbanner</code> — скачает и сохранит\n"
                 "• <code>.setbanner</code> без аргументов — сброс баннера",
    },
    "setbtn": {
        "short": "Кнопка под .info",
        "full":  "Добавляет кнопку-ссылку под карточку .info.\n\n"
                 "Пример: <code>.setbtn Мой канал | https://t.me/...</code>\n"
                 "Без аргументов — сброс кнопки.",
    },
    "setinfo": {
        "short": "Кастомный текст .info",
        "full":  "Устанавливает кастомный текст для .info.\n"
                 "Без аргументов — сброс к стандартному.\n\n"
                 "Доступные переменные:\n"
                 "<code>{name}</code> — имя | <code>{version}</code> — версия\n"
                 "<code>{prefix}</code> — префикс | <code>{uptime}</code> — аптайм\n"
                 "<code>{cpu}</code> — CPU | <code>{ram}</code> — RAM\n"
                 "<code>{platform}</code> — платформа | <code>{modules}</code> — модулей\n"
                 "<code>{lang}</code> — язык | <code>{python}</code> — Python",
    },
    "resetinfo": {
        "short": "Сбросить все настройки .info",
        "full":  "Сбрасывает баннер, текст и кнопку .info к стандартным значениям.",
    },
    "help": {
        "short": "Список команд",
        "full":  "Показывает список всех доступных команд.\n\n"
                 "<code>.help</code> — полный список\n"
                 "<code>.help &lt;команда&gt;</code> — подробная справка по команде",
    },
    "lm": {
        "short": "Загрузить модуль из URL",
        "full":  "Скачивает и загружает модуль по прямой ссылке.\n\n"
                 "Поддерживает форматы: SMVF Native, MCUB, Hikka.\n"
                 "Пример: <code>.lm https://raw.githubusercontent.com/.../mod.py</code>",
    },
    "dlm": {
        "short": "Загрузить модуль из файла",
        "full":  "Загружает модуль из прикреплённого .py файла.\n\n"
                 "Ответьте на сообщение с .py файлом командой <code>.dlm</code>",
    },
    "ulm": {
        "short": "Выгрузить модуль",
        "full":  "Выгружает модуль по имени.\n\n"
                 "Пример: <code>.ulm modname</code>\n"
                 "Имена модулей смотри в <code>.mlm</code>",
    },
    "mlm": {
        "short": "Список загруженных модулей",
        "full":  "Показывает все загруженные внешние модули с типами.\n\n"
                 "🟢 SMVF Native  🔵 MCUB  🟣 Hikka",
    },
    "logstxt": {
        "short": "Логи текстовым файлом",
        "full":  "Отправляет все логи текстовым документом в текущий чат.\n"
                 "Полезно для отладки и отправки отчётов об ошибках.",
    },
    "logs": {
        "short": "Последние 30 строк логов",
        "full":  "Показывает последние 30 строк текущего лог-файла прямо в сообщении.",
    },
}


def register(client) -> None:
    register_builtin("help", _help_handler)
    logger.debug("Модуль help зарегистрирован")


async def _help_handler(event: events.NewMessage.Event) -> None:
    prefix = cfg_get("command_prefix", ".")
    args   = (event.raw_text or "").split(None, 1)

    # .help <команда> — подробная справка
    if len(args) == 2:
        cmd = args[1].strip().lower().lstrip(prefix)
        if cmd in _HELP:
            text = (
                f"📖 <b>{escape_html(prefix + cmd)}</b>\n\n"
                f"{_HELP[cmd]['full']}"
            )
        else:
            text = f"❌ Команда <code>{escape_html(prefix + cmd)}</code> не найдена."
        await event.edit(text, parse_mode="html")
        return

    # .help — полный список
    loaded  = get_loaded_modules()
    p       = escape_html(prefix)

    lines = []
    for cmd, info in sorted(_HELP.items()):
        lines.append(f"  <code>{p}{escape_html(cmd)}</code> — {info['short']}")

    text = f"📋 <b>SMVF v1.2beta — команды</b>\n\n" + "\n".join(lines)

    if loaded:
        ext = []
        for name, info in sorted(loaded.items()):
            icon = {"smvf": "🟢", "mcub": "🔵", "hikka": "🟣"}.get(info.get("type",""), "⚪")
            ext.append(f"  {icon} <b>{escape_html(name)}</b>")
        text += "\n\n📦 <b>Загруженные модули:</b>\n" + "\n".join(ext)

    text += f"\n\n💡 <code>{p}help &lt;команда&gt;</code> — подробнее"
    await event.edit(text, parse_mode="html")
