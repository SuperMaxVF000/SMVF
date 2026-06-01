# Keepalive — юзербот никогда не засыпает
# Реализует: мониторинг соединения, автоматическое переподключение с backoff,
# периодический healthcheck, защита от системного sleep

import asyncio
import logging
import time
from typing import Optional

try:
    import psutil as _psutil
except ImportError:
    _psutil = None

from ..utils.colors import Colors, cprint
from ..utils.i18n import t

logger = logging.getLogger(__name__)

# Параметры переподключения
_MAX_RECONNECT_ATTEMPTS = 20        # Максимум попыток прежде чем сдаться
_RECONNECT_BASE_DELAY   = 5         # Начальная задержка в секундах
_RECONNECT_MAX_DELAY    = 300       # Максимальная задержка (5 минут)
_HEALTHCHECK_INTERVAL   = 60        # Секунды между healthcheck-ами

# Флаг остановки
_shutdown = False


def request_shutdown() -> None:
    """Запрашиваем корректную остановку keepalive."""
    global _shutdown
    _shutdown = True


async def keepalive_loop(client) -> None:
    """
    Главный keepalive-цикл.
    Запускается как asyncio.Task и работает всё время жизни юзербота.

    :param client: Telethon TelegramClient.
    """
    global _shutdown
    reconnect_attempts = 0

    # Параллельно запускаем healthcheck
    asyncio.create_task(_healthcheck_loop(client))

    while not _shutdown:
        try:
            # Ждём отключения — этот вызов блокируется пока клиент подключён
            await client.run_until_disconnected()

        except asyncio.CancelledError:
            break

        except Exception as e:
            logger.warning("Разрыв соединения: %s", e)

        if _shutdown:
            break

        # Переподключение с exponential backoff
        reconnect_attempts += 1
        if reconnect_attempts > _MAX_RECONNECT_ATTEMPTS:
            logger.critical("Достигнут лимит попыток переподключения. Завершение.")
            break

        delay = min(
            _RECONNECT_BASE_DELAY * (2 ** (reconnect_attempts - 1)),
            _RECONNECT_MAX_DELAY,
        )
        cprint(
            t("reconnecting", attempt=reconnect_attempts, max=_MAX_RECONNECT_ATTEMPTS),
            Colors.YELLOW,
        )
        cprint(f"⏳ Повтор через {delay}с...", Colors.DIM)

        await asyncio.sleep(delay)

        # Попытка переподключения
        connected = await _reconnect(client)
        if connected:
            reconnect_attempts = 0
            cprint(t("reconnect_ok"), Colors.GREEN)
        else:
            cprint(t("reconnect_fail", secs=delay), Colors.RED)


async def _reconnect(client) -> bool:
    """
    Попытка переподключения к Telegram.

    :param client: Telethon TelegramClient.
    :return: True если переподключение успешно.
    """
    try:
        if client.is_connected():
            await client.disconnect()
    except Exception:
        pass

    try:
        await client.connect()
        if await client.is_user_authorized():
            return True
    except Exception as e:
        logger.warning("Ошибка переподключения: %s", e)

    return False


async def _healthcheck_loop(client) -> None:
    """
    Периодический healthcheck: логируем состояние системы.
    Работает параллельно с keepalive_loop.
    """
    from ..core.database import get as cfg_get

    while not _shutdown:
        try:
            interval = cfg_get("healthcheck_interval", 5) * 60  # минуты → секунды
            await asyncio.sleep(interval)

            if _shutdown:
                break

            # Собираем метрики
            if _psutil:
                proc = _psutil.Process()
                cpu  = proc.cpu_percent(interval=0.5)
                ram  = proc.memory_info().rss / 1024 / 1024
            else:
                cpu, ram = 0.0, 0.0
            connected = client.is_connected()

            logger.debug(
                "Healthcheck: connected=%s cpu=%.1f%% ram=%.1fMB",
                connected, cpu, ram,
            )

            # Предупреждение при высокой нагрузке
            if cpu > 80:
                logger.warning("Высокая загрузка CPU: %.1f%%", cpu)
            if ram > 500:
                logger.warning("Высокое потребление RAM: %.1f МБ", ram)

            # Если не подключён — сигнализируем (keepalive_loop восстановит)
            if not connected:
                logger.warning("Healthcheck: соединение потеряно")

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error("Healthcheck ошибка: %s", e)
            await asyncio.sleep(30)


async def safe_connect(client) -> bool:
    """
    Безопасное подключение с повторными попытками.
    Используется при первом старте.

    :param client: Telethon TelegramClient.
    :return: True если подключён и авторизован.
    """
    for attempt in range(1, 6):
        try:
            if not client.is_connected():
                await client.connect()
            if await client.is_user_authorized():
                return True
        except Exception as e:
            logger.warning("Попытка подключения %d/5: %s", attempt, e)
            if attempt < 5:
                await asyncio.sleep(5 * attempt)

    return False
