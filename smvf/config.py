"""SMVF Configuration Manager. Made by SuperMaxVF"""

import json
import os
import sys
from typing import Any, Optional

CONFIG_FILE = "smvf_config.json"

DEFAULT_CONFIG: dict = {
    "api_id": 0,
    "api_hash": "",
    "phone": "",
    "command_prefix": ".",
    "inline_bot_token": "",
    "inline_bot_username": "",
    "log_group_id": None,
    "log_group_invite": "",
    "aliases": {},
    "version": "1.0.0",
    "premium_emoji": False,
    "info_media": None,
    "info_media_type": None,
    "info_text": "",
    "info_button_text": "",
    "info_button_url": "",
    "ping_media": None,
    "ping_media_type": None,
    "loaded_modules": [],
    "db_version": 1,
}

config: dict = {}


def load_config() -> dict:
    global config
    if not os.path.exists(CONFIG_FILE):
        config = dict(DEFAULT_CONFIG)
        return config
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    config = dict(DEFAULT_CONFIG)
    config.update(loaded)
    return config


def save_config() -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get(key: str, default: Any = None) -> Any:
    return config.get(key, default)


def set_value(key: str, value: Any) -> None:
    config[key] = value
    save_config()


set = set_value


def is_configured() -> bool:
    return bool(
        config.get("api_id")
        and config.get("api_hash")
        and config.get("phone")
        and config["api_id"] != 0
    )
