"""
SMVF Config Manager — Made by SuperMaxVF
Reads/writes data/config.json. No web server, no env vars.
"""
import os
import json
from typing import Any, Optional

# Config stored inside data/ next to session
_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(_BASE, "data", "config.json")
os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

DEFAULTS: dict = {
    "api_id": None,
    "api_hash": None,
    "phone": None,
    "bot_token": None,
    "log_group_id": None,
    "owner_id": None,
    "prefix": ".",
    "version": "1.0",
    "premium": False,
    "language": "ru",
    # .info module
    "info_text": (
        "🌌 <b>SMVF Userbot</b> <code>v1.0</code>\n"
        "✦ <i>Made by SuperMaxVF</i>\n\n"
        "📡 <a href='https://t.me/MadeBySuperMaxVF'>Channel</a> · "
        "<a href='https://t.me/Mad3BySuperMaxVF'>Dev</a> · "
        "<a href='https://github.com/SuperMaxVF000/SMVF'>GitHub</a>"
    ),
    "info_media": None,
    "info_buttons": [],
    # .ping module
    "ping_media": None,
    # modules
    "enabled_modules": [],
    "disabled_modules": [],
    # inline bot
    "inline_bot_username": None,
    # connection
    "healthcheck_interval": 30,
    "db_version": 1,
}


class Config:
    def __init__(self):
        self._data: dict = {}
        self._load()

    def _load(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._data = dict(DEFAULTS)
        else:
            self._data = dict(DEFAULTS)

    def save(self):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        val = self._data.get(key)
        if val is None:
            val = DEFAULTS.get(key, default)
        return val

    def set(self, key: str, value: Any):
        self._data[key] = value
        self.save()

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any):
        self.set(key, value)

    def is_configured(self) -> bool:
        """True if api_id is already set (not first run)."""
        return bool(self._data.get("api_id"))

    def as_dict(self) -> dict:
        return dict(self._data)


_cfg: Optional[Config] = None


def get_config() -> Config:
    global _cfg
    if _cfg is None:
        _cfg = Config()
    return _cfg
