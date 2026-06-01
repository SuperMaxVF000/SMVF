# Встроенный модуль SMVF: Logs
# .logstxt — отправить все логи текстовым файлом в текущий чат

import logging
import os
import time

from telethon import events

from ..core.dispatcher import register_builtin
from ..utils.helpers import today_str
from ..utils.logger import get_all_logs_text, get_log_files

logger = logging.getLogger(__name__)

LOGS_DIR = "logs"


def register(client) -> None:
    """Регистрируем команду логов."""
    register_builtin("logstxt", _logstxt_handler)
    register_builtin("logs",    _logs_handler)
    logger.debug("Модуль logs зарегистрирован")


async def _logstxt_handler(event: events.NewMessage.Event) -> None:
    """
    .logstxt — отправляем все логи текстовым файлом.
    """
    await event.edit("📋 Сбор логов...", parse_mode="html")

    content = get_all_logs_text(LOGS_DIR)
    tmp_path = f"/tmp/smvf_logs_{int(time.time())}.txt"

    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)

        await event.delete()
        await event.client.send_file(
            event.chat_id,
            tmp_path,
            caption=f"📋 <b>SMVF Logs</b> — {today_str()}",
            parse_mode="html",
            force_document=True,
        )
    except Exception as e:
        await event.edit(f"❌ Ошибка: {e}", parse_mode="html")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


async def _logs_handler(event: events.NewMessage.Event) -> None:
    """
    .logs — показываем последние 30 строк логов прямо в сообщении.
    """
    files = get_log_files(LOGS_DIR)
    if not files:
        await event.edit("📋 Логи пусты.", parse_mode="html")
        return

    lines = []
    try:
        with open(files[0], "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception:
        pass

    last = "".join(lines[-30:]).strip()
    if not last:
        await event.edit("📋 Логи пусты.", parse_mode="html")
        return

    # Обрезаем до 3800 символов (лимит Telegram)
    if len(last) > 3800:
        last = "...\n" + last[-3800:]

    await event.edit(
        f"📋 <b>Последние логи:</b>\n<pre>{last}</pre>",
        parse_mode="html",
    )
