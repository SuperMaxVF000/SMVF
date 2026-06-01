# Диспетчер команд SMVF
# Принимает все исходящие сообщения, определяет команды и передаёт в обработчики

import logging
from typing import Callable, Dict, Optional

from telethon import events

from ..core.database import get, runtime_get
from ..utils.i18n import t

logger = logging.getLogger(__name__)

# Реестр встроенных команд (устанавливается в __init__)
_builtin_handlers: Dict[str, Callable] = {}


def register_builtin(command: str, handler: Callable) -> None:
    """
    Регистрируем встроенную команду.

    :param command: Имя команды без префикса.
    :param handler: Асинхронная функция-обработчик(event).
    """
    _builtin_handlers[command] = handler


def setup_dispatcher(client) -> None:
    """
    Устанавливаем главный хендлер на все исходящие сообщения.
    Вызывается один раз при старте.

    :param client: Telethon TelegramClient.
    """

    @client.on(events.NewMessage(outgoing=True))
    async def _dispatch(event: events.NewMessage.Event) -> None:
        text = event.raw_text or ""
        prefix = get("command_prefix", ".")

        # Проверяем что сообщение начинается с префикса
        if not text.startswith(prefix):
            return

        # Извлекаем команду
        body = text[len(prefix):]
        parts = body.split(None, 1)
        if not parts:
            return
        cmd = parts[0].lower().strip()

        # Проверяем алиасы
        aliases: dict = get("aliases", {})
        if cmd in aliases:
            cmd = aliases[cmd]

        # Ищем в реестре встроенных команд
        if cmd in _builtin_handlers:
            try:
                await _builtin_handlers[cmd](event)
            except Exception as e:
                logger.error("Ошибка в команде .%s: %s", cmd, e)
                try:
                    await event.edit(f"❌ Ошибка: <code>{e}</code>", parse_mode="html")
                except Exception:
                    pass
            return

        # Команда не найдена — молча игнорируем
        # (модули сами регистрируют свои хендлеры через client.add_event_handler)

    logger.debug("Диспетчер команд установлен")
