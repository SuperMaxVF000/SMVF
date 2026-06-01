# Встроенный модуль SMVF: Loader Commands
# .lm <url>  — загрузить модуль из URL
# .dlm       — загрузить модуль из прикреплённого файла
# .ulm <name>— выгрузить модуль
# .mlm       — список загруженных модулей

import logging
import os
import re
from typing import Optional

import aiohttp
from telethon import events

from ..core.database import get as cfg_get
from ..core.dispatcher import register_builtin
from ..core.loader import (
    get_loaded_modules,
    load_module_file,
    load_module_from_code,
    unload_module,
)
from ..utils.helpers import ensure_dir, escape_html, safe_filename

logger = logging.getLogger(__name__)

MODULES_DIR = "modules"


def register(client) -> None:
    """Регистрируем команды управления модулями."""
    register_builtin("lm",  _lm_handler)
    register_builtin("dlm", _dlm_handler)
    register_builtin("ulm", _ulm_handler)
    register_builtin("mlm", _mlm_handler)
    logger.debug("Модуль loader_cmd зарегистрирован")


async def _lm_handler(event: events.NewMessage.Event) -> None:
    """
    .lm <url> — загружаем модуль по URL.
    """
    prefix = cfg_get("command_prefix", ".")
    args   = (event.raw_text or "").split(None, 1)

    if len(args) < 2:
        await event.edit(
            f"❌ Укажите URL модуля.\nПример: <code>{escape_html(prefix)}lm https://example.com/mod.py</code>",
            parse_mode="html",
        )
        return

    url = args[1].strip()
    if not url.startswith(("http://", "https://")):
        await event.edit("❌ Некорректный URL.", parse_mode="html")
        return

    await event.edit(f"📥 Загрузка модуля из URL...", parse_mode="html")

    # Скачиваем код
    code = await _download_code(url)
    if code is None:
        await event.edit("❌ Не удалось скачать файл.", parse_mode="html")
        return

    # Имя модуля из URL
    module_name = _name_from_url(url)

    ok, mtype = await load_module_from_code(
        event.client, code, module_name, MODULES_DIR,
        prefix=cfg_get("command_prefix", "."),
        lang=cfg_get("language", "ru"),
    )

    if ok:
        await event.edit(
            f"✅ Модуль <b>{escape_html(module_name)}</b> загружен [{mtype}]",
            parse_mode="html",
        )
    else:
        await event.edit(
            f"❌ Ошибка загрузки <b>{escape_html(module_name)}</b>. Смотри логи.",
            parse_mode="html",
        )


async def _dlm_handler(event: events.NewMessage.Event) -> None:
    """
    .dlm — загружаем модуль из прикреплённого .py файла.
    Ответьте на сообщение с файлом командой .dlm
    """
    # Ищем файл в текущем сообщении или в сообщении-ответе
    reply = await event.get_reply_message()
    target = reply or event

    if not target.document:
        await event.edit(
            "❌ Ответьте на сообщение с .py файлом командой <code>.dlm</code>",
            parse_mode="html",
        )
        return

    doc = target.document
    file_name = _get_document_name(doc)

    if not file_name or not file_name.endswith(".py"):
        await event.edit("❌ Файл должен иметь расширение .py", parse_mode="html")
        return

    await event.edit("📥 Загрузка модуля из файла...", parse_mode="html")

    ensure_dir(MODULES_DIR)
    save_path = os.path.join(MODULES_DIR, safe_filename(file_name))

    # Скачиваем файл
    try:
        await event.client.download_media(target.document, file=save_path)
    except Exception as e:
        await event.edit(f"❌ Не удалось скачать файл: {escape_html(str(e))}", parse_mode="html")
        return

    module_name = file_name.removesuffix(".py")
    ok, name, mtype = await load_module_file(
        event.client, save_path,
        prefix=cfg_get("command_prefix", "."),
        lang=cfg_get("language", "ru"),
    )

    if ok:
        await event.edit(
            f"✅ Модуль <b>{escape_html(module_name)}</b> загружен [{mtype}]",
            parse_mode="html",
        )
    else:
        await event.edit(
            f"❌ Ошибка загрузки <b>{escape_html(module_name)}</b>. Смотри логи.",
            parse_mode="html",
        )
        if os.path.exists(save_path):
            os.remove(save_path)


async def _ulm_handler(event: events.NewMessage.Event) -> None:
    """
    .ulm <name> — выгружаем модуль по имени.
    """
    prefix = cfg_get("command_prefix", ".")
    args   = (event.raw_text or "").split(None, 1)

    if len(args) < 2:
        await event.edit(
            f"❌ Укажите имя модуля.\nПример: <code>{escape_html(prefix)}ulm modname</code>",
            parse_mode="html",
        )
        return

    module_name = args[1].strip().lower()
    ok = await unload_module(module_name, MODULES_DIR)

    if ok:
        await event.edit(
            f"✅ Модуль <b>{escape_html(module_name)}</b> выгружен.",
            parse_mode="html",
        )
    else:
        await event.edit(
            f"❌ Модуль <b>{escape_html(module_name)}</b> не найден.",
            parse_mode="html",
        )


async def _mlm_handler(event: events.NewMessage.Event) -> None:
    """
    .mlm — список всех загруженных внешних модулей.
    """
    loaded = get_loaded_modules()

    if not loaded:
        await event.edit("📦 Нет загруженных модулей.", parse_mode="html")
        return

    lines = []
    for name, info in sorted(loaded.items()):
        mtype    = info.get("type", "?")
        fp       = info.get("file_path", "")
        basename = os.path.basename(fp) if fp else "?"

        type_icon = {"smvf": "🟢", "mcub": "🔵", "hikka": "🟣"}.get(mtype, "⚪")
        lines.append(f"{type_icon} <b>{escape_html(name)}</b> [{mtype}] — <code>{escape_html(basename)}</code>")

    text = (
        f"📦 <b>Загруженные модули ({len(loaded)}):</b>\n\n"
        + "\n".join(lines)
        + "\n\n"
        "🟢 SMVF-native  🔵 MCUB  🟣 Hikka"
    )
    await event.edit(text, parse_mode="html")


# ── Утилиты ──────────────────────────────────────────────────────────────

async def _download_code(url: str) -> Optional[str]:
    """Скачиваем текст по URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    return await resp.text(encoding="utf-8", errors="replace")
    except Exception as e:
        logger.error("Ошибка скачивания %s: %s", url, e)
    return None


def _name_from_url(url: str) -> str:
    """Извлекаем имя модуля из URL."""
    path = url.split("?")[0]
    base = os.path.basename(path)
    return safe_filename(base.removesuffix(".py") or "module")


def _get_document_name(doc) -> Optional[str]:
    """Получаем имя файла из Document объекта Telethon."""
    for attr in getattr(doc, "attributes", []):
        name = getattr(attr, "file_name", None)
        if name:
            return name
    return None
