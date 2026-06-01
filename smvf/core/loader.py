# Загрузчик модулей SMVF
# Поддерживает три типа модулей:
#   smvf  — нативные (SMVFModule)
#   mcub  — MCUB-совместимые (register(client))
#   hikka — Hikka-совместимые (loader.Module)

import importlib.util
import logging
import os
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..compat.mcub import detect_module_type, patch_mcub_module
from ..utils.colors import Colors, cprint
from ..utils.helpers import ensure_dir
from ..utils.i18n import t

logger = logging.getLogger(__name__)

# ── Реестр загруженных модулей ────────────────────────────────────────────

# name -> {instance, type, file_path}
_loaded: Dict[str, Dict[str, Any]] = {}

MODULES_DIR = "modules"


def get_loaded_modules() -> Dict[str, Dict[str, Any]]:
    """Возвращаем копию реестра загруженных модулей."""
    return dict(_loaded)


def is_loaded(name: str) -> bool:
    """Проверяем загружен ли модуль."""
    return name in _loaded


# ── Загрузка одного файла ─────────────────────────────────────────────────

async def load_module_file(
    client,
    file_path: str,
    prefix: str = ".",
    lang: str = "ru",
    send_message_func: Optional[Callable] = None,
) -> Tuple[bool, str, str]:
    """
    Загружаем модуль из файла. Автоопределяем тип.

    :param client: Telethon TelegramClient.
    :param file_path: Путь к .py файлу.
    :param prefix: Префикс команд.
    :param lang: Язык интерфейса.
    :param send_message_func: Функция для отправки сообщений (не обязательна).
    :return: (успех, имя_модуля, тип_модуля)
    """
    file_name = os.path.basename(file_path)
    module_name = file_name.removesuffix(".py")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        logger.error("Не удалось прочитать %s: %s", file_path, e)
        return False, module_name, "unknown"

    mod_type = detect_module_type(code)

    # MCUB-модули патчим перед загрузкой
    if mod_type == "mcub":
        code = patch_mcub_module(code)

    # Hikka-модули требуют патча импортов
    if mod_type == "hikka":
        code = _patch_hikka_imports(code)

    # Если уже загружен — выгружаем старую версию
    if module_name in _loaded:
        _unregister(module_name)

    # Загружаем через importlib
    try:
        spec = importlib.util.spec_from_file_location(
            f"smvf_modules.{module_name}", file_path
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules[f"smvf_modules.{module_name}"] = mod
        spec.loader.exec_module(mod)
    except Exception as e:
        logger.error("Ошибка компиляции %s: %s", file_name, e)
        sys.modules.pop(f"smvf_modules.{module_name}", None)
        return False, module_name, mod_type

    # Регистрируем по типу
    try:
        if mod_type == "smvf":
            instance = await _load_smvf(client, mod, module_name, prefix, lang)
        elif mod_type == "mcub":
            instance = _load_mcub(client, mod, module_name)
        elif mod_type == "hikka":
            instance = _load_hikka(client, mod, module_name, prefix, lang)
        else:
            logger.warning(t("module_incompatible", name=file_name))
            return False, module_name, mod_type
    except Exception as e:
        logger.error(t("module_failed", name=file_name, error=str(e)))
        return False, module_name, mod_type

    if instance is None:
        return False, module_name, mod_type

    _loaded[module_name] = {
        "instance": instance,
        "type": mod_type,
        "file_path": file_path,
        "module": mod,
    }

    logger.info(t("module_loaded", name=module_name, type=mod_type))
    return True, module_name, mod_type


def _load_mcub(client, mod, module_name: str):
    """Загрузка MCUB-модуля через register(client)."""
    if not hasattr(mod, "register"):
        logger.warning("MCUB модуль %s не имеет register()", module_name)
        return None
    mod.register(client)
    return mod  # Сам модуль как instance


async def _load_smvf(client, mod, module_name: str, prefix: str, lang: str):
    """Загрузка нативного SMVF-модуля."""
    # Ищем класс-наследник SMVFModule
    import inspect
    for name, obj in inspect.getmembers(mod, inspect.isclass):
        if hasattr(obj, "_is_smvf_module") and obj._is_smvf_module:
            instance = obj()
            instance._client = client
            instance._prefix = prefix
            instance._lang = lang
            await instance._setup(client)
            return instance
    # Если нет SMVFModule — пробуем как MCUB (register)
    if hasattr(mod, "register"):
        return _load_mcub(client, mod, module_name)
    return None


def _load_hikka(client, mod, module_name: str, prefix: str, lang: str):
    """Загрузка Hikka-модуля через compat-слой."""
    import inspect
    from ..compat.hikka import HikkaModule, load_hikka_module

    for name, obj in inspect.getmembers(mod, inspect.isclass):
        # Hikka-классы наследуют HikkaModule (через наш compat) или имеют strings dict
        if (
            hasattr(obj, "strings")
            and isinstance(getattr(obj, "strings", None), dict)
            and name not in ("HikkaModule", "Module")
        ):
            return load_hikka_module(client, obj, prefix, lang)

    logger.warning("Hikka модуль %s: не найден подходящий класс", module_name)
    return None


def _patch_hikka_imports(code: str) -> str:
    """
    Патчим импорты Hikka-модулей для работы с SMVF.
    Порядок важен — сначала более специфичные паттерны.
    """
    replacements = [
        # hikkatl → telethon
        ("from hikkatl", "from telethon"),
        ("import hikkatl", "import telethon"),
        # Варианты from .. import loader, utils (с разными пробелами)
        ("from .. import loader, utils", "from smvf.compat import hikka as loader; from smvf.compat.hikka import utils"),
        ("from .. import loader,utils",  "from smvf.compat import hikka as loader; from smvf.compat.hikka import utils"),
        # Только loader
        ("from .. import loader", "from smvf.compat import hikka as loader"),
        # Только utils
        ("from .. import utils", "from smvf.compat.hikka import utils"),
        # Прямой import loader (BoysNSFW стиль: import loader)
        ("import loader\n", "from smvf.compat import hikka as loader\n"),
        # import utils as smvf_utils
        ("import utils as smvf_utils", "from smvf.compat.hikka import utils as smvf_utils"),
        ("import utils\n", "from smvf.compat.hikka import utils\n"),
        # Inline types
        ("from ..inline.types import", "# from ..inline.types import"),
        ("from ..inline", "# from ..inline"),
        # version
        ("from .. import version", ""),
        # MCUB-специфичные
        ("from userbot import", "# from userbot import"),
        ("from userbot.", "# from userbot."),
    ]
    for old, new in replacements:
        code = code.replace(old, new)
    return code


# ── Выгрузка модуля ───────────────────────────────────────────────────────

def _unregister(module_name: str) -> None:
    """Внутренняя выгрузка — убираем из реестра и sys.modules."""
    _loaded.pop(module_name, None)
    sys.modules.pop(f"smvf_modules.{module_name}", None)


async def unload_module(module_name: str, modules_dir: str = MODULES_DIR) -> bool:
    """
    Выгружаем модуль по имени.

    :param module_name: Имя модуля (без .py).
    :param modules_dir: Директория модулей.
    :return: True если выгружен.
    """
    if module_name not in _loaded:
        return False

    entry = _loaded[module_name]

    # Вызываем on_unload если есть
    instance = entry.get("instance")
    if hasattr(instance, "on_unload"):
        try:
            await instance.on_unload()
        except Exception as e:
            logger.warning("on_unload ошибка в %s: %s", module_name, e)

    # Удаляем файл
    file_path = entry.get("file_path", "")
    if file_path and os.path.exists(file_path):
        # Не удаляем встроенные модули из пакета
        if modules_dir in file_path:
            os.remove(file_path)

    _unregister(module_name)
    logger.info("Модуль выгружен: %s", module_name)
    return True


# ── Загрузка всех модулей из директории ─────────────────────────────────

async def load_all_modules(
    client,
    modules_dir: str = MODULES_DIR,
    prefix: str = ".",
    lang: str = "ru",
) -> int:
    """
    Загружаем все .py файлы из директории модулей.

    :param client: Telethon TelegramClient.
    :param modules_dir: Директория с модулями.
    :param prefix: Префикс команд.
    :param lang: Язык.
    :return: Количество успешно загруженных модулей.
    """
    ensure_dir(modules_dir)
    count = 0

    for file_name in sorted(os.listdir(modules_dir)):
        if not file_name.endswith(".py") or file_name.startswith("_"):
            continue

        file_path = os.path.join(modules_dir, file_name)
        ok, name, mtype = await load_module_file(client, file_path, prefix, lang)
        if ok:
            count += 1
        else:
            cprint(t("module_failed", name=file_name, error="см. логи"), Colors.YELLOW)

    return count


# ── Загрузка модуля из исходного кода (строки) ───────────────────────────

async def load_module_from_code(
    client,
    code: str,
    module_name: str,
    modules_dir: str = MODULES_DIR,
    prefix: str = ".",
    lang: str = "ru",
) -> Tuple[bool, str]:
    """
    Сохраняем код как файл и загружаем.

    :param client: Telethon TelegramClient.
    :param code: Исходный код модуля.
    :param module_name: Имя модуля (без .py).
    :param modules_dir: Директория для сохранения.
    :param prefix: Префикс команд.
    :param lang: Язык.
    :return: (успех, тип_модуля)
    """
    ensure_dir(modules_dir)
    file_path = os.path.join(modules_dir, f"{module_name}.py")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    ok, name, mtype = await load_module_file(client, file_path, prefix, lang)
    if not ok and os.path.exists(file_path):
        os.remove(file_path)

    return ok, mtype
