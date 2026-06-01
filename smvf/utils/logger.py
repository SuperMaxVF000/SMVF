# Логгер SMVF
# Пишет одновременно: в терминал (с цветами), в файл логов, в лог-группу Telegram
# Уровни: DEBUG / INFO / WARNING / ERROR / CRITICAL

import asyncio
import logging
import os
import time
from logging.handlers import RotatingFileHandler
from typing import Optional

from .colors import Colors, cprint, strip_ansi
from .helpers import ensure_dir, now_str, today_str

# ── Константы ──────────────────────────────────────────────────────────────

LOGS_DIR = "logs"
MAX_LOG_SIZE = 5 * 1024 * 1024   # 5 МБ на файл
LOG_BACKUP_COUNT = 7              # Храним 7 дней логов


# ── Telegram-хендлер ──────────────────────────────────────────────────────

class TelegramLogHandler(logging.Handler):
    """
    Хендлер, отправляющий логи в Telegram-группу через inline-бота.
    Буферизует сообщения и отправляет батчами чтобы не флудить.
    """

    def __init__(self) -> None:
        super().__init__()
        self._client = None        # Telethon клиент юзербота
        self._log_chat_id: Optional[int] = None
        self._queue: asyncio.Queue = asyncio.Queue()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._task: Optional[asyncio.Task] = None
        self._running = False

    def install(self, client, log_chat_id: int) -> None:
        """
        Подключаем хендлер к клиенту.

        :param client: Telethon TelegramClient юзербота.
        :param log_chat_id: ID лог-группы.
        """
        self._client = client
        self._log_chat_id = log_chat_id

    def start_sender(self, loop: asyncio.AbstractEventLoop) -> None:
        """Запускаем фоновую задачу отправки логов в Telegram."""
        self._loop = loop
        self._running = True
        self._task = loop.create_task(self._sender_loop())

    def emit(self, record: logging.LogRecord) -> None:
        """Принимаем запись лога и кладём в очередь."""
        if not self._running or self._log_chat_id is None:
            return
        try:
            msg = self.format(record)
            # Кладём в очередь без блокировки
            if self._loop and self._loop.is_running():
                self._loop.call_soon_threadsafe(
                    self._queue.put_nowait, (record.levelno, msg)
                )
        except Exception:
            pass

    async def _sender_loop(self) -> None:
        """Фоновая задача: батчевая отправка логов в Telegram."""
        batch = []
        while self._running:
            try:
                # Ждём первое сообщение до 2 секунд
                try:
                    item = await asyncio.wait_for(self._queue.get(), timeout=2.0)
                    batch.append(item)
                except asyncio.TimeoutError:
                    pass

                # Забираем остальное что накопилось (не ждём)
                while not self._queue.empty() and len(batch) < 10:
                    try:
                        batch.append(self._queue.get_nowait())
                    except asyncio.QueueEmpty:
                        break

                if batch and self._client and self._log_chat_id:
                    await self._send_batch(batch)
                    batch = []

            except Exception:
                batch = []
                await asyncio.sleep(5)

    async def _send_batch(self, batch: list) -> None:
        """Отправляем батч логов в группу."""
        if not batch:
            return

        # Форматируем каждую запись
        lines = []
        for level, msg in batch:
            icon = {
                logging.DEBUG:    "🔍",
                logging.INFO:     "ℹ️",
                logging.WARNING:  "⚠️",
                logging.ERROR:    "❌",
                logging.CRITICAL: "🔴",
            }.get(level, "📝")
            # Убираем ANSI из текста для Telegram
            clean = strip_ansi(msg)
            lines.append(f"{icon} <code>{clean[:300]}</code>")

        text = "\n".join(lines)
        # Обрезаем если слишком длинное
        if len(text) > 4000:
            text = text[:3990] + "\n..."

        try:
            await self._client.send_message(
                self._log_chat_id,
                text,
                parse_mode="html",
            )
        except Exception:
            pass  # Не падаем если Telegram недоступен

    async def stop(self) -> None:
        """Останавливаем хендлер."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass


# ── Форматтер ─────────────────────────────────────────────────────────────

class SMVFFormatter(logging.Formatter):
    """Форматтер с цветами для терминала."""

    LEVEL_COLORS = {
        logging.DEBUG:    Colors.DIM,
        logging.INFO:     Colors.BRIGHT_GREEN,
        logging.WARNING:  Colors.BRIGHT_YELLOW,
        logging.ERROR:    Colors.BRIGHT_RED,
        logging.CRITICAL: Colors.BG_RED + Colors.WHITE,
    }

    def __init__(self, use_colors: bool = True) -> None:
        super().__init__()
        self._use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        ts = time.strftime("%H:%M:%S")
        level = record.levelname[:4].upper()
        name  = record.name.replace("smvf.", "")
        msg   = record.getMessage()

        if record.exc_info:
            msg += "\n" + self.formatException(record.exc_info)

        line = f"[{ts}] [{level}] {name}: {msg}"

        if self._use_colors:
            color = self.LEVEL_COLORS.get(record.levelno, "")
            return f"{color}{line}{Colors.RESET}"
        return line


# ── Глобальный хендлер для Telegram ──────────────────────────────────────

_tg_handler = TelegramLogHandler()


def setup_logging(logs_dir: str = LOGS_DIR) -> None:
    """
    Настраиваем логирование: терминал + ротируемый файл.
    Вызывать один раз при старте до подключения к Telegram.

    :param logs_dir: Директория для файлов логов.
    """
    ensure_dir(logs_dir)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Убираем стандартные хендлеры
    root.handlers.clear()

    # Терминал — INFO и выше, с цветами
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(SMVFFormatter(use_colors=True))
    root.addHandler(console)

    # Файл — DEBUG и выше, без цветов, с ротацией
    log_file = os.path.join(logs_dir, f"{today_str()}.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=MAX_LOG_SIZE,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(SMVFFormatter(use_colors=False))
    root.addHandler(file_handler)

    # Telegram хендлер — WARNING и выше (настраивается позже через install_tg_log)
    _tg_handler.setLevel(logging.WARNING)
    _tg_handler.setFormatter(SMVFFormatter(use_colors=False))
    root.addHandler(_tg_handler)

    # Приглушаем шумные библиотеки
    for noisy in ("telethon", "aiogram", "aiohttp", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def install_tg_log(client, log_chat_id: int) -> None:
    """
    Подключаем Telegram-логгер после создания лог-группы.

    :param client: Telethon TelegramClient.
    :param log_chat_id: ID лог-группы.
    """
    _tg_handler.install(client, log_chat_id)
    loop = asyncio.get_event_loop()
    _tg_handler.start_sender(loop)


async def stop_tg_log() -> None:
    """Останавливаем Telegram-логгер при завершении."""
    await _tg_handler.stop()


def get_log_files(logs_dir: str = LOGS_DIR) -> list[str]:
    """
    Возвращаем список файлов логов (от новых к старым).

    :param logs_dir: Директория логов.
    :return: Список путей к файлам.
    """
    ensure_dir(logs_dir)
    files = [
        os.path.join(logs_dir, f)
        for f in os.listdir(logs_dir)
        if f.endswith(".log")
    ]
    return sorted(files, reverse=True)


def get_all_logs_text(logs_dir: str = LOGS_DIR, max_bytes: int = 500_000) -> str:
    """
    Читаем все логи в одну строку (для .logstxt).

    :param logs_dir: Директория логов.
    :param max_bytes: Максимальный размер в байтах.
    :return: Текст всех логов.
    """
    files = get_log_files(logs_dir)
    if not files:
        return "Логи пусты."

    parts = []
    total = 0
    for fpath in files:
        try:
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            parts.append(f"=== {os.path.basename(fpath)} ===\n{content}")
            total += len(content)
            if total >= max_bytes:
                parts.append("\n[...обрезано...]")
                break
        except Exception:
            continue

    return "\n\n".join(parts)
