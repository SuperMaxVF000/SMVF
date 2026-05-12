<div align="center">

```
  ███████╗███╗   ███╗██╗   ██╗███████╗
  ██╔════╝████╗ ████║██║   ██║██╔════╝
  ███████╗██╔████╔██║██║   ██║█████╗
  ╚════██║██║╚██╔╝██║╚██╗ ██╔╝██╔══╝
  ███████║██║ ╚═╝ ██║ ╚████╔╝ ██║
  ╚══════╝╚═╝     ╚═╝  ╚═══╝  ╚═╝
         Made by SuperMaxVF   v1.0
```

**Made by SuperMaxVF** · v1.0

[![Telegram](https://img.shields.io/badge/Telegram-MadeBySuperMaxVF-blue?logo=telegram)](https://t.me/MadeBySuperMaxVF)
[![Dev](https://img.shields.io/badge/Dev-Mad3BySuperMaxVF-purple?logo=telegram)](https://t.me/Mad3BySuperMaxVF)
[![GitHub](https://img.shields.io/badge/GitHub-SuperMaxVF000-black?logo=github)](https://github.com/SuperMaxVF000/SMVF)

</div>

---

# 🌌 SMVF Userbot

## English

### Features

- 🌌 **Space UI** — star/comet screensaver in terminal, cosmic styled messages in TG
- 🤖 **Inline bot** — auto-created on first launch, sends messages `via @bot`
- 📋 **Log group** — all events go to a private TG group + saved to `logs/smvf.log`
- 📦 **Module system** — supports SMVF, Hikka and Mku module formats
- ⚡ **Watchdog** — never sleeps, monitors network, CPU/RAM/disk
- 🔧 **No web server** — pure terminal setup, config saved to `data/config.json`
- 🖼 **Startup logo** — sends `assets/smvf_logo.png` to log group on every launch

### Supported Platforms

| Platform | Status |
|----------|--------|
| Termux (Android) | ✅ |
| UserLand → Ubuntu (Android) | ✅ |
| Ubuntu / Debian | ✅ |
| Raspberry Pi OS | ✅ |

---

### Install — Termux (Android)

```bash
pkg update && pkg install git python -y
git clone https://github.com/SuperMaxVF000/SMVF.git
cd SMVF
bash install.sh
python main.py
```

For auto-start on Android boot — install [Termux:Boot](https://f-droid.org/packages/com.termux.boot/) from F-Droid. The installer sets the boot script automatically.

---

### Install — UserLand → Ubuntu (Android)

Open Ubuntu session in UserLand, then:

```bash
sudo apt update && sudo apt install git python3 python3-pip -y
git clone https://github.com/SuperMaxVF000/SMVF.git
cd SMVF
bash install.sh
python3 main.py
```

**Keep running after closing UserLand** — use tmux:

```bash
sudo apt install tmux -y
tmux new -s smvf
python3 main.py
# Detach session: Ctrl+B, then D
# Reattach later:  tmux attach -t smvf
```

---

### Install — Ubuntu / Debian

```bash
sudo apt update && sudo apt install git python3 python3-pip -y
git clone https://github.com/SuperMaxVF000/SMVF.git
cd SMVF
bash install.sh
```

The installer sets up a systemd user service. Start it:

```bash
systemctl --user start smvf
```

Or run manually:

```bash
python3 main.py
```

---

### Install — Raspberry Pi OS

```bash
sudo apt update && sudo apt install git python3 python3-pip -y
git clone https://github.com/SuperMaxVF000/SMVF.git
cd SMVF
bash install.sh
systemctl --user start smvf
```

---

### First Launch

On first run SMVF asks in the terminal (no web server):

| Prompt | Description |
|--------|-------------|
| API ID | Integer — get at [my.telegram.org](https://my.telegram.org) |
| API Hash | 32-char string — same page |
| Phone number | Your Telegram account (+79...) |
| Bot token | Create via [@BotFather](https://t.me/BotFather) (optional) |
| Prefix | Command prefix, default `.` |
| Telegram Premium | Enables custom emoji |

SMVF then automatically:
- Connects the inline bot
- Creates a private log group, adds you + bot to it
- Loads all modules
- Sends the startup logo to the log group

---

### Built-in Commands

| Command | Description |
|---------|-------------|
| `.info` | Show info card |
| `.info set` | Reply to media → attach to info card |
| `.info text <html>` | Set info card text (HTML) |
| `.info btn Label \| https://url` | Add inline button |
| `.info btnclear` | Clear all buttons |
| `.info clear` | Remove media from card |
| `.ping` | Latency + uptime |
| `.ping set` | Reply to media → attach to ping |
| `.ping clear` | Remove ping media |
| `.help` | List all modules and commands |
| `.help <module>` | Help for a specific module |
| `.mod install <url>` | Install module from URL |
| `.mod list` | List loaded modules |
| `.restart` | Restart the userbot |

---

### Project Structure

```
SMVF/
├── install.sh                 ← Run this to install
├── main.py                    ← Entry point
├── requirements.txt
├── assets/
│   └── smvf_logo.png          ← Startup logo (sent to log group)
├── smvf/
│   ├── core/
│   │   ├── config.py          ← Config manager (data/config.json)
│   │   ├── core.py            ← Main lifecycle
│   │   ├── loader.py          ← Module loader (SMVF / Hikka / Mku)
│   │   ├── logger.py          ← Terminal + file + TG logging
│   │   ├── module.py          ← Base module class
│   │   ├── screensaver.py     ← Space screensaver (anti-burn)
│   │   ├── setup.py           ← First-run terminal wizard
│   │   └── watchdog.py        ← Network + resource monitor
│   └── inline/
│       └── bot.py             ← Inline bot + log group manager
├── modules/
│   ├── built_in/              ← Built-in modules (info, ping, utils)
│   └── external/              ← Drop your modules here
├── data/                      ← Runtime data (gitignored)
│   ├── config.json
│   ├── smvf_user.session
│   ├── info_media/
│   └── ping_media/
└── logs/
    └── smvf.log               ← All logs with timestamps
```

---

## Русский

### Возможности

- 🌌 **Космический UI** — заставка звёздами/кометами в терминале, космическое оформление в TG
- 🤖 **Inline-бот** — создаётся автоматически при первом запуске, пишет `via @бот`
- 📋 **Группа логов** — все события в приватную TG-группу + файл `logs/smvf.log`
- 📦 **Модульная система** — поддержка форматов SMVF, Hikka и Mku
- ⚡ **Watchdog** — не засыпает, следит за сетью, CPU/RAM/диском
- 🔧 **Без веб-сервера** — настройка в терминале, конфиг в `data/config.json`
- 🖼 **Стартовый логотип** — отправляет `assets/smvf_logo.png` в группу логов при каждом запуске

### Поддерживаемые платформы

| Платформа | Статус |
|-----------|--------|
| Termux (Android) | ✅ |
| UserLand → Ubuntu (Android) | ✅ |
| Ubuntu / Debian | ✅ |
| Raspberry Pi OS | ✅ |

---

### Установка — Termux (Android)

```bash
pkg update && pkg install git python -y
git clone https://github.com/SuperMaxVF000/SMVF.git
cd SMVF
bash install.sh
python main.py
```

Для автозапуска при включении телефона — установи [Termux:Boot](https://f-droid.org/packages/com.termux.boot/) из F-Droid. Скрипт настроит автозапуск автоматически.

---

### Установка — UserLand → Ubuntu (Android)

Открой сессию Ubuntu в UserLand, затем:

```bash
sudo apt update && sudo apt install git python3 python3-pip -y
git clone https://github.com/SuperMaxVF000/SMVF.git
cd SMVF
bash install.sh
python3 main.py
```

**Чтобы бот работал после закрытия UserLand** — используй tmux:

```bash
sudo apt install tmux -y
tmux new -s smvf
python3 main.py
# Отключиться: Ctrl+B затем D
# Вернуться:   tmux attach -t smvf
```

---

### Установка — Ubuntu / Debian

```bash
sudo apt update && sudo apt install git python3 python3-pip -y
git clone https://github.com/SuperMaxVF000/SMVF.git
cd SMVF
bash install.sh
```

Скрипт создаёт systemd-сервис. Запусти его:

```bash
systemctl --user start smvf
```

Или вручную:

```bash
python3 main.py
```

---

### Установка — Raspberry Pi OS

```bash
sudo apt update && sudo apt install git python3 python3-pip -y
git clone https://github.com/SuperMaxVF000/SMVF.git
cd SMVF
bash install.sh
systemctl --user start smvf
```

---

### Первый запуск

При первом запуске SMVF спросит в терминале (никакого веб-сервера):

| Вопрос | Описание |
|--------|----------|
| API ID | Число — получи на [my.telegram.org](https://my.telegram.org) |
| API Hash | 32 символа — там же |
| Номер телефона | Твой аккаунт Telegram (+79...) |
| Токен бота | Создай через [@BotFather](https://t.me/BotFather) (необязательно) |
| Префикс | Символ команд, по умолчанию `.` |
| Telegram Premium | Включает кастомные emoji |

SMVF автоматически:
- Подключит inline-бота
- Создаст приватную группу логов, добавит тебя и бота
- Загрузит все модули
- Отправит стартовый логотип в группу логов

---

### Встроенные команды

| Команда | Описание |
|---------|----------|
| `.info` | Карточка юзербота |
| `.info set` | Ответь на медиа → прикрепить к .info |
| `.info text <html>` | Изменить текст карточки (HTML) |
| `.info btn Текст \| https://url` | Добавить инлайн-кнопку |
| `.info btnclear` | Убрать все кнопки |
| `.info clear` | Убрать медиа |
| `.ping` | Задержка + аптайм |
| `.ping set` | Ответь на медиа → прикрепить к .ping |
| `.ping clear` | Убрать медиа |
| `.help` | Список всех модулей и команд |
| `.help <модуль>` | Справка по модулю |
| `.mod install <url>` | Установить модуль из URL |
| `.mod list` | Список загруженных модулей |
| `.restart` | Перезапустить юзербот |

---

### Структура проекта

```
SMVF/
├── install.sh                 ← Запусти для установки
├── main.py                    ← Точка входа
├── requirements.txt
├── assets/
│   └── smvf_logo.png          ← Стартовый логотип
├── smvf/
│   ├── core/
│   │   ├── config.py          ← Конфиг (data/config.json)
│   │   ├── core.py            ← Жизненный цикл
│   │   ├── loader.py          ← Загрузчик модулей
│   │   ├── logger.py          ← Логи (терминал + файл + TG)
│   │   ├── module.py          ← Базовый класс модуля
│   │   ├── screensaver.py     ← Космическая заставка
│   │   ├── setup.py           ← Мастер первого запуска
│   │   └── watchdog.py        ← Мониторинг сети и ресурсов
│   └── inline/
│       └── bot.py             ← Inline-бот + группа логов
├── modules/
│   ├── built_in/              ← Встроенные модули
│   └── external/              ← Сюда кладёшь свои модули
├── data/                      ← Рантайм-данные (в .gitignore)
│   ├── config.json
│   ├── smvf_user.session
│   ├── info_media/
│   └── ping_media/
└── logs/
    └── smvf.log               ← Все логи с временными метками
```

---

> SMVF Userbot v1.0 · Made by SuperMaxVF
> [t.me/MadeBySuperMaxVF](https://t.me/MadeBySuperMaxVF) · [github.com/SuperMaxVF000/SMVF](https://github.com/SuperMaxVF000/SMVF)
