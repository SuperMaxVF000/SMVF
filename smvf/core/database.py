# База данных SMVF
# Хранит конфиг в config.json (только локально, никуда не отправляется)
# Runtime-данные хранятся в памяти и не сбрасываются между перезапусками модулей

import json
import os
import sys
import getpass
from typing import Any, Dict, Optional, Tuple

from ..utils.colors import Colors, cprint
from ..utils.helpers import ensure_dir
from ..utils.i18n import t
from ..version import DB_SCHEMA_VERSION

# ── Константы ──────────────────────────────────────────────────────────────

CONFIG_FILE = "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "api_id": 0,
    "api_hash": "",
    "phone": "",
    "language": "ru",
    "command_prefix": ".",
    "aliases": {},
    "inline_bot_token": "",
    "inline_bot_username": "",
    "log_chat_id": None,
    "log_chat_hash": None,
    "healthcheck_interval": 5,        # минуты
    "db_schema_version": DB_SCHEMA_VERSION,
}

# ── Текущий конфиг (глобальный) ───────────────────────────────────────────

_config: Dict[str, Any] = {}

# ── Runtime-словарь (для модулей, хранится только в памяти) ──────────────

_runtime: Dict[str, Any] = {}


# ── Загрузка / сохранение ─────────────────────────────────────────────────

def load_config() -> Dict[str, Any]:
    """
    Загружаем конфиг из config.json.
    Если файл не найден — запускаем интерактивный мастер настройки.

    :return: Загруженный конфиг.
    """
    global _config

    if not os.path.exists(CONFIG_FILE):
        cprint(t("config_not_found"), Colors.YELLOW)
        _config = dict(DEFAULT_CONFIG)
        _run_setup_wizard()
        save_config()
    else:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        # Заполняем отсутствующие ключи дефолтами
        _config = {**DEFAULT_CONFIG, **loaded}
        _migrate_schema()

    return _config


def save_config() -> None:
    """Сохраняем конфиг в config.json."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(_config, f, ensure_ascii=False, indent=2)


def _migrate_schema() -> None:
    """Мигрируем схему конфига если версия устарела."""
    global _config
    current = _config.get("db_schema_version", 0)
    if current < DB_SCHEMA_VERSION:
        cprint(f"🔄 Миграция конфига {current} → {DB_SCHEMA_VERSION}...", Colors.YELLOW)
        _config["db_schema_version"] = DB_SCHEMA_VERSION
        # Добавляем отсутствующие ключи из DEFAULT_CONFIG
        for key, val in DEFAULT_CONFIG.items():
            if key not in _config:
                _config[key] = val
        save_config()
        cprint("✅ Миграция завершена", Colors.GREEN)


def _run_setup_wizard() -> None:
    """
    Интерактивный мастер первоначальной настройки.
    Всё вводится в терминале, никуда не отправляется.
    """
    global _config

    # Выбор языка (до загрузки i18n, поэтому выводим сырым текстом)
    print("\n" + "=" * 50)
    print("  Выберите язык / Choose language:")
    print("  [1] Русский")
    print("  [2] English")
    print("=" * 50)

    while True:
        choice = input("  > ").strip()
        if choice == "1":
            _config["language"] = "ru"
            from ..utils.i18n import set_lang
            set_lang("ru")
            break
        elif choice == "2":
            _config["language"] = "en"
            from ..utils.i18n import set_lang
            set_lang("en")
            break
        else:
            print("  Введите 1 или 2 / Enter 1 or 2")

    print()
    cprint(t("setup_header"), Colors.BRIGHT_CYAN, bold=True)
    print()
    cprint(
        "📌 Получите API_ID и API_HASH на https://my.telegram.org" if _config["language"] == "ru"
        else "📌 Get API_ID and API_HASH at https://my.telegram.org",
        Colors.CYAN,
    )
    print()

    # API_ID
    while True:
        raw = input(t("setup_api_id")).strip()
        try:
            api_id = int(raw)
            if api_id > 0:
                _config["api_id"] = api_id
                break
        except ValueError:
            pass
        cprint(t("setup_error_api_id"), Colors.RED)

    # API_HASH
    while True:
        api_hash = input(t("setup_api_hash")).strip()
        if len(api_hash) >= 10:
            _config["api_hash"] = api_hash
            break
        cprint("❌ API_HASH слишком короткий. / API_HASH too short.", Colors.RED)

    # Телефон
    while True:
        phone = input(t("setup_phone")).strip()
        if phone.startswith("+") and len(phone) >= 8:
            _config["phone"] = phone
            break
        cprint("❌ Формат: +79001234567 / Format: +79001234567", Colors.RED)

    # Префикс (опционально)
    prefix_raw = input(t("setup_prefix")).strip()
    _config["command_prefix"] = prefix_raw if prefix_raw else "."

    print()
    cprint(t("setup_saved"), Colors.GREEN)
    print()


# ── Геттер / сеттер ──────────────────────────────────────────────────────

def get(key: str, default: Any = None) -> Any:
    """
    Получаем значение из конфига.

    :param key: Ключ.
    :param default: Значение по умолчанию.
    :return: Значение из конфига.
    """
    return _config.get(key, default)


def set_value(key: str, value: Any) -> None:
    """
    Устанавливаем значение в конфиге и сохраняем.

    :param key: Ключ.
    :param value: Значение.
    """
    _config[key] = value
    save_config()


def get_credentials() -> Tuple[int, str, str]:
    """
    Возвращаем учётные данные из конфига.

    :return: (api_id, api_hash, phone)
    :raises SystemExit: Если данные не заполнены.
    """
    api_id   = _config.get("api_id", 0)
    api_hash = _config.get("api_hash", "")
    phone    = _config.get("phone", "")

    if not api_id or not api_hash or not phone:
        cprint("❌ Незаполнены api_id, api_hash или phone в config.json", Colors.RED)
        sys.exit(1)

    return int(api_id), str(api_hash), str(phone)


# ── Runtime-хранилище ─────────────────────────────────────────────────────

def runtime_set(key: str, value: Any) -> None:
    """Сохраняем значение в runtime (только в памяти)."""
    _runtime[key] = value


def runtime_get(key: str, default: Any = None) -> Any:
    """Читаем значение из runtime."""
    return _runtime.get(key, default)


def runtime_del(key: str) -> None:
    """Удаляем значение из runtime."""
    _runtime.pop(key, None)
