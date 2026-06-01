# Автоматическое создание inline-бота через @BotFather
# Приоритет: автосоздание → ручной ввод токена → работа без бота

import asyncio
import logging
import random
import re
import time
from typing import Optional, Tuple

from ..utils.colors import Colors, cprint
from ..utils.i18n import t
from ..version import INLINE_BOT_PREFIX

logger = logging.getLogger(__name__)

# Таймауты для общения с BotFather
_BF_STEP_DELAY  = 2.5   # Секунды между командами BotFather
_BF_WAIT_REPLY  = 8.0   # Секунды ожидания ответа BotFather
_BF_MAX_RETRIES = 3     # Попыток создания


async def auto_create_bot(client) -> Optional[Tuple[str, str]]:
    """
    Создаём inline-бота через BotFather автоматически.

    :param client: Telethon TelegramClient (авторизованный).
    :return: (token, username) или None если не удалось.
    """
    cprint(t("inline_creating"), Colors.YELLOW)

    for attempt in range(1, _BF_MAX_RETRIES + 1):
        try:
            result = await _create_via_botfather(client)
            if result:
                return result
            logger.warning("Попытка %d/%d создания бота не удалась", attempt, _BF_MAX_RETRIES)
        except Exception as e:
            logger.warning("BotFather попытка %d: %s", attempt, e)

        if attempt < _BF_MAX_RETRIES:
            await asyncio.sleep(5)

    return None


async def _create_via_botfather(client) -> Optional[Tuple[str, str]]:
    """
    Одна попытка создания бота через BotFather.

    :return: (token, username) или None.
    """
    # Генерируем уникальный username: smvfinlineXXXX_bot
    suffix = "".join([str(random.randint(0, 9)) for _ in range(4)])
    bot_username = f"{INLINE_BOT_PREFIX}{suffix}_bot"
    bot_display_name = f"SMVF Inline {suffix}"

    try:
        botfather = await client.get_entity("BotFather")
    except Exception as e:
        logger.error("Не удалось получить BotFather: %s", e)
        return None

    # Шаг 1: /newbot
    await client.send_message(botfather, "/newbot")
    await asyncio.sleep(_BF_STEP_DELAY)

    # Шаг 2: Отображаемое имя
    await client.send_message(botfather, bot_display_name)
    reply_1 = await _wait_bf_reply(client, botfather)
    if not reply_1:
        return None

    # BotFather просит username
    if "username" not in reply_1.lower() and "name" in reply_1.lower():
        # Иногда BotFather говорит "Sorry, that name is taken" — генерируем новый
        logger.warning("BotFather не принял имя, пробуем другое")
        return None

    # Шаг 3: Username
    await client.send_message(botfather, bot_username)
    reply_2 = await _wait_bf_reply(client, botfather, timeout=10.0)
    if not reply_2:
        return None

    # Ищем токен в ответе
    token_match = re.search(r"(\d{8,12}:[A-Za-z0-9_-]{35,})", reply_2)
    if not token_match:
        # Username занят или ошибка
        logger.warning("BotFather: токен не найден в ответе. Ответ: %s", reply_2[:200])
        return None

    token = token_match.group(1)

    # Шаг 4: Включаем inline mode
    await asyncio.sleep(_BF_STEP_DELAY)
    await client.send_message(botfather, "/setinline")
    await asyncio.sleep(_BF_STEP_DELAY)

    # BotFather просит выбрать бота
    await client.send_message(botfather, f"@{bot_username}")
    await asyncio.sleep(_BF_STEP_DELAY)

    # Placeholder для inline
    await client.send_message(botfather, "query")
    await asyncio.sleep(_BF_STEP_DELAY)

    cprint(t("inline_created", username=bot_username), Colors.GREEN)
    return token, bot_username


async def _wait_bf_reply(
    client,
    botfather_entity,
    timeout: float = _BF_WAIT_REPLY,
) -> Optional[str]:
    """
    Ждём ответа от BotFather.

    :param client: Telethon TelegramClient.
    :param botfather_entity: Entity BotFather.
    :param timeout: Максимальное время ожидания.
    :return: Текст последнего сообщения или None.
    """
    deadline = time.time() + timeout
    last_msg_id: Optional[int] = None

    # Запоминаем последнее ID до отправки
    try:
        msgs = await client.get_messages(botfather_entity, limit=1)
        if msgs:
            last_msg_id = msgs[0].id
    except Exception:
        pass

    # Ждём нового сообщения
    while time.time() < deadline:
        await asyncio.sleep(1.0)
        try:
            msgs = await client.get_messages(botfather_entity, limit=1)
            if msgs and msgs[0].id != last_msg_id:
                return msgs[0].text or ""
        except Exception as e:
            logger.debug("_wait_bf_reply: %s", e)

    return None


async def verify_token(token: str) -> Optional[str]:
    """
    Проверяем токен бота через Telegram Bot API.

    :param token: Токен бота.
    :return: Username бота или None если токен неверный.
    """
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.telegram.org/bot{token}/getMe",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("ok"):
                        return data["result"]["username"]
    except Exception as e:
        logger.debug("verify_token: %s", e)
    return None
