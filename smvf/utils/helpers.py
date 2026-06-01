# Общие утилиты SMVF

import os
import re
import time
from typing import Optional


def ensure_dir(path: str) -> None:
    """Создаём директорию если не существует."""
    os.makedirs(path, exist_ok=True)


def format_uptime(seconds: float) -> str:
    """
    Форматируем аптайм в читаемый вид.

    :param seconds: Секунды аптайма.
    :return: Строка вида '2д 3ч 14м 5с'
    """
    seconds = int(seconds)
    days    = seconds // 86400
    hours   = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs    = seconds % 60

    parts = []
    if days:    parts.append(f"{days}д")
    if hours:   parts.append(f"{hours}ч")
    if minutes: parts.append(f"{minutes}м")
    parts.append(f"{secs}с")
    return " ".join(parts)


def progress_bar(current: int, total: int, width: int = 10) -> str:
    """
    Текстовый прогресс-бар.

    :param current: Текущее значение.
    :param total: Максимальное значение.
    :param width: Ширина в символах.
    :return: Строка '[████░░░░] 45%'
    """
    if total == 0:
        return f"[{'░' * width}] 0%"
    percent = max(0.0, min(1.0, current / total))
    filled = int(width * percent)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {int(percent * 100)}%"


def escape_html(text: str) -> str:
    """Экранируем HTML-спецсимволы."""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def strip_html(text: str) -> str:
    """Убираем HTML-теги из строки."""
    return re.sub(r"<[^>]+>", "", text)


def get_args(text: str, prefix: str = ".") -> str:
    """
    Извлекаем аргументы из команды.

    Пример: '.info hello world' -> 'hello world'

    :param text: Текст сообщения.
    :param prefix: Префикс команды.
    :return: Аргументы или пустая строка.
    """
    parts = text.split(maxsplit=1)
    return parts[1].strip() if len(parts) > 1 else ""


def now_str() -> str:
    """Текущее время в формате для логов: 2024-01-15 14:30:00"""
    return time.strftime("%Y-%m-%d %H:%M:%S")


def today_str() -> str:
    """Текущая дата: 2024-01-15"""
    return time.strftime("%Y-%m-%d")


def safe_filename(name: str) -> str:
    """Убираем из имени файла недопустимые символы."""
    return re.sub(r'[<>:"/\\|?*]', "_", name)


def truncate(text: str, max_len: int = 200, suffix: str = "...") -> str:
    """Обрезаем текст до max_len символов."""
    if len(text) <= max_len:
        return text
    return text[: max_len - len(suffix)] + suffix


def is_premium_emoji(doc_id: int) -> str:
    """
    Возвращаем HTML-тег премиум-эмодзи.
    Использовать только если me.premium == True.

    :param doc_id: ID документа эмодзи.
    :return: HTML-тег.
    """
    return f'<emoji document_id={doc_id}>⭐</emoji>'
