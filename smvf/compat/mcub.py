# Слой совместимости с MCUB-модулями
# MCUB-модули используют паттерн: def register(client): ...
# Это нативный формат и поддерживается без адаптеров.
# Данный модуль содержит утилиты для проверки и загрузки таких модулей.

import logging
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


def is_mcub_module(code: str) -> bool:
    """
    Проверяем является ли код MCUB-модулем.
    MCUB-модуль содержит функцию register(client) или register(bot).

    :param code: Исходный код модуля.
    :return: True если модуль MCUB-совместим.
    """
    return "def register(" in code


def is_hikka_module(code: str) -> bool:
    """
    Проверяем является ли код Hikka-модулем.
    Hikka-модуль содержит loader.Module как базовый класс.

    :param code: Исходный код модуля.
    :return: True если модуль Hikka-совместим.
    """
    return (
        "loader.Module" in code
        or "class " in code and "loader.tds" in code
        or "from .. import loader" in code
    )


def is_smvf_native(code: str) -> bool:
    """
    Проверяем является ли код нативным SMVF-модулем.
    SMVF-модуль содержит SMVFModule как базовый класс.

    :param code: Исходный код модуля.
    :return: True если модуль нативный SMVF.
    """
    return "SMVFModule" in code or "smvf_module" in code.lower()


def detect_module_type(code: str) -> str:
    """
    Определяем тип модуля по исходному коду.

    :param code: Исходный код.
    :return: 'smvf' | 'hikka' | 'mcub' | 'unknown'
    """
    if is_smvf_native(code):
        return "smvf"
    if is_hikka_module(code):
        return "hikka"
    if is_mcub_module(code):
        return "mcub"
    return "unknown"


def patch_mcub_module(code: str) -> str:
    """
    Минимальные патчи для MCUB-модулей.
    Некоторые MCUB-модули используют специфичные импорты или функции.

    :param code: Исходный код модуля.
    :return: Пропатченный код.
    """
    # Заменяем специфичные для MCUB импорты если нужно
    patches = [
        # Если MCUB-модуль импортирует что-то из userbot — убираем
        ("from userbot import ", "# from userbot import "),
        ("from userbot.", "# from userbot."),
    ]
    for old, new in patches:
        code = code.replace(old, new)
    return code
