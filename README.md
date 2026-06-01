<div align="center">

```
███████╗███╗   ███╗██╗   ██╗███████╗
██╔════╝████╗ ████║██║   ██║██╔════╝
███████╗██╔████╔██║██║   ██║█████╗
╚════██║██║╚██╔╝██║╚██╗ ██╔╝██╔══╝
███████║██║ ╚═╝ ██║ ╚████╔╝ ██║
╚══════╝╚═╝     ╚═╝  ╚═══╝  ╚═╝
```

**SMVF Userbot** — v1.0beta

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Telegram](https://img.shields.io/badge/Channel-@MadeBySuperMaxVF-blue.svg)](https://t.me/MadeBySuperMaxVF)

[Telegram Channel](https://t.me/MadeBySuperMaxVF) • [YouTube](https://www.youtube.com/@SuperMaxVF) • [GitHub](https://github.com/SuperMaxVF000)

</div>

---

# 🇬🇧 English

## Features

- **Three module formats**: SMVF Native, Hikka-compatible, MCUB-compatible
- **Auto inline bot**: creates `@smvfinlineXXXX_bot` via BotFather automatically
- **Log group**: creates a Telegram group, sends all logs there
- **Never sleeps**: auto-reconnect with exponential backoff, healthcheck loop
- **Platform support**: Raspberry Pi, Ubuntu, Termux, Android UserLand
- **Premium emoji**: auto-detects Telegram Premium and uses custom emoji
- **Built-in modules**: `info`, `ping`, `help`, `logs`
- **Module manager**: install from URL or file, unload, list

## Supported Platforms

| Platform | Installer |
|----------|-----------|
| 🐧 Ubuntu / Debian | `scripts/install.sh` |
| 📱 Android (Termux) | `scripts/termux.sh` |
| 📱 Android (UserLand) | `scripts/install.sh` |
| 🍓 Raspberry Pi (tested on RPi 5 8GB) | `scripts/rpi.sh` |

## Requirements

- Python 3.10+
- Telegram API credentials from [my.telegram.org](https://my.telegram.org)

---

## Installation

### 🐧 Ubuntu / Debian / UserLand

```bash
# One-line install
curl -sSL https://raw.githubusercontent.com/SuperMaxVF000/SMVF/main/scripts/install.sh | bash
```

Or manually:
```bash
# 1. Clone
git clone https://github.com/SuperMaxVF000/SMVF.git
cd SMVF

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run (setup wizard on first launch)
python -m smvf
```

### 📱 Android — Termux

```bash
# Install Termux from F-Droid (NOT Google Play!)
# https://f-droid.org/packages/com.termux/

# Open Termux and run:
curl -sSL https://raw.githubusercontent.com/SuperMaxVF000/SMVF/main/scripts/termux.sh | bash
```

Or manually:
```bash
pkg update -y
pkg install python git openssl

git clone https://github.com/SuperMaxVF000/SMVF.git
cd SMVF
pip install -r requirements.txt
python -m smvf
```

**Background mode (Termux):**
```bash
pkg install tmux
tmux new-session -s smvf 'cd ~/smvf && python -m smvf'
# Detach: Ctrl+B, D
# Reattach: tmux attach -t smvf
```

### 📱 Android — UserLand (Ubuntu)

```bash
# Install UserLand app, set up Ubuntu session
# Then in UserLand terminal:
curl -sSL https://raw.githubusercontent.com/SuperMaxVF000/SMVF/main/scripts/install.sh | bash
```

### 🍓 Raspberry Pi (tested on RPi 5 8GB)

```bash
# SSH into your Pi or open terminal
curl -sSL https://raw.githubusercontent.com/SuperMaxVF000/SMVF/main/scripts/rpi.sh | bash
```

The installer will offer to create a **systemd service** — recommended for RPi (auto-start after reboot).

```bash
# After service creation:
sudo systemctl start smvf      # start
sudo systemctl stop smvf       # stop
sudo systemctl status smvf     # status
sudo journalctl -u smvf -f     # live logs
```

---

## First Launch

On first run, the setup wizard starts in terminal:

```
Choose language / Выберите язык:
  [1] Русский
  [2] English
> 2

🔧 SMVF Initial Setup

📌 Get API_ID and API_HASH at https://my.telegram.org

Enter API_ID: 12345678
Enter API_HASH: abc123...
Enter phone number: +1234567890
Enter command prefix (Enter = '.'): .

✅ Settings saved to config.json
```

After that SMVF:
1. Connects to Telegram
2. Creates inline bot `@smvfinlineXXXX_bot` via BotFather
3. Creates a log group and invites the bot
4. Sends a startup message to the log group
5. Loads all modules and starts

---

## Built-in Commands

| Command | Description |
|---------|-------------|
| `.ping` | Check latency and uptime |
| `.pingset <url>` | Set custom image for ping |
| `.pingreset` | Reset ping image |
| `.info` | Show userbot info card |
| `.setbanner <url>` | Set info banner image |
| `.setbtn Name \| url` | Set info button |
| `.setinfo <text>` | Set custom info text |
| `.resetinfo` | Reset all info settings |
| `.help` | List all commands |
| `.help <cmd>` | Help for specific command |
| `.lm <url>` | Load module from URL |
| `.dlm` | Load module from file (reply to file) |
| `.ulm <name>` | Unload module |
| `.mlm` | List loaded modules |
| `.logstxt` | Send all logs as text file |
| `.logs` | Show last 30 log lines |

---

## Module System

SMVF supports 3 module formats. See [docs/MODULES.md](docs/MODULES.md) for full docs.

**Quick example (SMVF Native):**
```python
# my_module.py
from telethon import events
from smvf.core.dispatcher import register_builtin

def register(client) -> None:
    register_builtin("hello", hello_handler)

async def hello_handler(event: events.NewMessage.Event) -> None:
    await event.edit("👋 Hello!")
```

Install: `.lm https://raw.githubusercontent.com/.../my_module.py`

---

## Project Structure

```
SMVF/
├── smvf/
│   ├── core/           # Database, loader, dispatcher, keepalive
│   ├── inline/         # Inline bot manager & BotFather automation
│   ├── modules/        # Built-in modules (ping, info, help, logs)
│   ├── compat/         # Hikka & MCUB compatibility layers
│   └── utils/          # Logger, i18n, platform detect, helpers
├── modules/            # Your installed modules go here
├── logs/               # Auto-created log files
├── docs/               # Documentation
├── scripts/            # Platform-specific installers
├── requirements.txt
└── config.json         # Auto-created, never commit this!
```

---

---

# 🇷🇺 Русский

## Возможности

- **Три формата модулей**: SMVF Native, совместимость с Hikka, совместимость с MCUB
- **Автосоздание inline-бота**: создаёт `@smvfinlineXXXX_bot` через BotFather автоматически
- **Лог-группа**: создаёт Telegram-группу, отправляет туда все логи
- **Никогда не засыпает**: автопереподключение с backoff, healthcheck каждые N минут
- **Поддержка платформ**: Raspberry Pi, Ubuntu, Termux, Android UserLand
- **Premium emoji**: автоматически определяет Telegram Premium и использует кастомные эмодзи
- **Встроенные модули**: `info`, `ping`, `help`, `logs`
- **Менеджер модулей**: установка по URL или из файла, выгрузка, список

## Поддерживаемые платформы

| Платформа | Установщик |
|-----------|------------|
| 🐧 Ubuntu / Debian | `scripts/install.sh` |
| 📱 Android (Termux) | `scripts/termux.sh` |
| 📱 Android (UserLand) | `scripts/install.sh` |
| 🍓 Raspberry Pi (тест: RPi 5 8GB) | `scripts/rpi.sh` |

## Требования

- Python 3.10+
- Данные Telegram API с [my.telegram.org](https://my.telegram.org)

---

## Установка

### 🐧 Ubuntu / Debian / UserLand

```bash
# Одна команда
curl -sSL https://raw.githubusercontent.com/SuperMaxVF000/SMVF/main/scripts/install.sh | bash
```

Или вручную:
```bash
# 1. Клонируем репозиторий
git clone https://github.com/SuperMaxVF000/SMVF.git
cd SMVF

# 2. Виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

# 3. Зависимости
pip install -r requirements.txt

# 4. Запуск (при первом запуске — мастер настройки)
python -m smvf
```

### 📱 Android — Termux

```bash
# Установи Termux из F-Droid (НЕ из Google Play!)
# https://f-droid.org/packages/com.termux/

# Открой Termux и запусти:
curl -sSL https://raw.githubusercontent.com/SuperMaxVF000/SMVF/main/scripts/termux.sh | bash
```

Или вручную:
```bash
pkg update -y
pkg install python git openssl

git clone https://github.com/SuperMaxVF000/SMVF.git
cd SMVF
pip install -r requirements.txt
python -m smvf
```

**Работа в фоне (Termux):**
```bash
pkg install tmux
tmux new-session -s smvf 'cd ~/smvf && python -m smvf'
# Отключиться: Ctrl+B, D
# Подключиться снова: tmux attach -t smvf
```

### 📱 Android — UserLand (Ubuntu)

```bash
# Установи UserLand, настрой Ubuntu-сессию
# В терминале UserLand:
curl -sSL https://raw.githubusercontent.com/SuperMaxVF000/SMVF/main/scripts/install.sh | bash
```

### 🍓 Raspberry Pi (проверено на RPi 5 8GB)

```bash
# SSH или терминал на RPi:
curl -sSL https://raw.githubusercontent.com/SuperMaxVF000/SMVF/main/scripts/rpi.sh | bash
```

Установщик предложит создать **systemd-сервис** — рекомендуется для RPi (автозапуск после перезагрузки).

```bash
# После создания сервиса:
sudo systemctl start smvf      # запуск
sudo systemctl stop smvf       # остановка
sudo systemctl status smvf     # статус
sudo journalctl -u smvf -f     # логи в реальном времени
```

---

## Первый запуск

При первом запуске в терминале запускается мастер настройки:

```
Выберите язык / Choose language:
  [1] Русский
  [2] English
> 1

🔧 Первоначальная настройка SMVF

📌 Получите API_ID и API_HASH на https://my.telegram.org

Введите API_ID: 12345678
Введите API_HASH: abc123...
Введите номер телефона: +79001234567
Введите префикс команд (Enter = '.'): .

✅ Настройки сохранены в config.json
```

После этого SMVF:
1. Подключается к Telegram
2. Создаёт inline-бота `@smvfinlineXXXX_bot` через BotFather
3. Создаёт лог-группу и добавляет туда бота
4. Отправляет стартовое сообщение в лог-группу
5. Загружает все модули и запускается

---

## Встроенные команды

| Команда | Описание |
|---------|----------|
| `.ping` | Проверка задержки и аптайм |
| `.pingset <url>` | Кастомное изображение для ping |
| `.pingreset` | Сброс изображения ping |
| `.info` | Карточка информации о юзерботе |
| `.setbanner <url>` | Баннер для info |
| `.setbtn Название \| url` | Кнопка под info |
| `.setinfo <текст>` | Кастомный текст info |
| `.resetinfo` | Сброс всех настроек info |
| `.help` | Список всех команд |
| `.help <команда>` | Помощь по конкретной команде |
| `.lm <url>` | Загрузить модуль из URL |
| `.dlm` | Загрузить модуль из файла (ответ на файл) |
| `.ulm <имя>` | Выгрузить модуль |
| `.mlm` | Список загруженных модулей |
| `.logstxt` | Отправить все логи текстовым файлом |
| `.logs` | Последние 30 строк логов в чате |

---

## Система модулей

SMVF поддерживает 3 формата. Полная документация: [docs/MODULES.md](docs/MODULES.md)

**Быстрый пример (SMVF Native):**
```python
# my_module.py
from telethon import events
from smvf.core.dispatcher import register_builtin

def register(client) -> None:
    register_builtin("hello", hello_handler)

async def hello_handler(event: events.NewMessage.Event) -> None:
    await event.edit("👋 Привет!")
```

Установка: `.lm https://raw.githubusercontent.com/.../my_module.py`

---

## Документация

| Файл | Описание |
|------|----------|
| [docs/MODULES.md](docs/MODULES.md) | Написание SMVF-модулей |
| [docs/HIKKA_COMPAT.md](docs/HIKKA_COMPAT.md) | Переписка Hikka → SMVF |
| [docs/MCUB_COMPAT.md](docs/MCUB_COMPAT.md) | Совместимость с MCUB |
| [docs/AI_PROMPT.md](docs/AI_PROMPT.md) | Промпт для AI-конвертации модулей |

---

## Ссылки

- 📢 Telegram-канал: [@MadeBySuperMaxVF](https://t.me/MadeBySuperMaxVF)
- 🎬 YouTube: [@SuperMaxVF](https://www.youtube.com/@SuperMaxVF)
- 💻 GitHub: [SuperMaxVF000](https://github.com/SuperMaxVF000)

---

## Лицензия

MIT License — делай что хочешь, упоминание автора приветствуется.
