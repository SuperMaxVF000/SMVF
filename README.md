<div align="center">

```
  ███████╗███╗   ███╗██╗   ██╗███████╗
  ██╔════╝████╗ ████║██║   ██║██╔════╝
  ███████╗██╔████╔██║██║   ██║█████╗  
  ╚════██║██║╚██╔╝██║╚██╗ ██╔╝██╔══╝  
  ███████║██║ ╚═╝ ██║ ╚████╔╝ ██║     
  ╚══════╝╚═╝     ╚═╝  ╚═══╝  ╚═╝     
```

**Space-themed Telegram Userbot**

[![Version](https://img.shields.io/badge/version-1.0.0-blueviolet?style=for-the-badge)](https://github.com/SuperMaxVF000/SMVF)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python)](https://python.org)
[![Channel](https://img.shields.io/badge/channel-@MadeBySuperMaxVF-26A5E4?style=for-the-badge&logo=telegram)](https://t.me/MadeBySuperMaxVF)
[![Dev](https://img.shields.io/badge/dev-@Mad3BySuperMaxVF-26A5E4?style=for-the-badge&logo=telegram)](https://t.me/Mad3BySuperMaxVF)

*✦ Made by SuperMaxVF ✦*

[🇬🇧 English](#-english) · [🇷🇺 Русский](#-русский)

</div>

---

## 🇬🇧 English

### About

**SMVF** is a Telegram userbot with a space theme. It supports its own modules as well as modules from **Hikka** and **MCUB**. On first launch it automatically creates an inline bot and a log group.

**Features:**
- 🚀 One-command installation
- 🤖 Auto-creates an inline bot via BotFather
- 📋 Auto-creates a Telegram log group (events, errors, status)
- 📦 Supports SMVF, Hikka and MCUB modules
- 🌌 Animated space screensaver in the terminal (stars, comets)
- ⚡ Never sleeps — runs 24/7, monitors the network
- 💾 All logs saved to a local file
- 📡 Network monitoring and auto-reconnect
- 💎 Telegram Premium emoji support
- ⌨️ Fully terminal-based setup — no web server

---

### Installation

**One-line install (all platforms):**
```bash
curl -sSL https://raw.githubusercontent.com/SuperMaxVF000/SMVF/main/install.sh | bash
```

#### 🟢 Termux (Android)
```bash
pkg update && pkg upgrade -y
pkg install python python-pip git -y
git clone https://github.com/SuperMaxVF000/SMVF ~/SMVF
cd ~/SMVF
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
python -m smvf
```

#### 🟡 UserLand → Ubuntu (Android)
```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y
git clone https://github.com/SuperMaxVF000/SMVF ~/SMVF
cd ~/SMVF
python3 -m venv venv && source venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
python -m smvf
```

#### 🔵 Ubuntu / Debian (PC or VPS)
```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y
git clone https://github.com/SuperMaxVF000/SMVF ~/SMVF
cd ~/SMVF
python3 -m venv venv && source venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
python -m smvf
```

Run in background with **screen**:
```bash
screen -S smvf
cd ~/SMVF && source venv/bin/activate && python -m smvf
# Ctrl+A, D — detach   |   screen -r smvf — reattach
```

#### 🔴 Raspberry Pi (Raspberry Pi OS)
```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y
git clone https://github.com/SuperMaxVF000/SMVF ~/SMVF
cd ~/SMVF
python3 -m venv venv && source venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
python -m smvf
```

Auto-start via **systemd** (`/etc/systemd/system/smvf.service`):
```ini
[Unit]
Description=SMVF Userbot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/SMVF
ExecStart=/home/pi/SMVF/venv/bin/python -m smvf
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable smvf && sudo systemctl start smvf
```

---

### First-Time Setup

On first launch SMVF runs an interactive wizard in the terminal — no web server required. It will ask for:

1. **API ID** and **API Hash** — get them at [my.telegram.org](https://my.telegram.org) → *API development tools*
2. **Phone number** — format `+13371234567`
3. **Command prefix** — default is `.`
4. **Telegram Premium** — do you have a subscription?

All data is saved locally to `smvf_config.json`. After setup SMVF automatically creates an inline bot and a log group.

---

### Built-in Commands

| Command | Description |
|---------|-------------|
| `.info` | Show userbot info card |
| `.info set <text>` | Set custom text for .info |
| `.info media` | Set media — reply to photo/video/gif |
| `.info clear media` | Remove media from .info |
| `.info button Text\|URL` | Add an inline URL button |
| `.ping` | Show ping latency and uptime |
| `.ping media` | Set media for .ping |
| `.ping clear media` | Remove media from .ping |
| `.help` | List all commands |
| `.mod list` | List loaded modules |
| `.mod load <url>` | Load module from URL |
| `.mod load` + reply | Load .py file from a replied message |
| `.mod unload <name>` | Unload a module |
| `.alias add a=cmd` | Add a command alias |
| `.alias del <alias>` | Remove alias |
| `.alias list` | List all aliases |
| `.restart` | Restart the userbot |
| `.update` | Pull latest update from GitHub |

---

### Modules

SMVF supports three module formats: **SMVF**, **Hikka** (via compatibility shim) and **MCUB**. Full documentation: [MODULES.md](MODULES.md)

Load a module:
```
.mod load https://raw.githubusercontent.com/.../mymodule.py
```
Or reply to a `.py` file with `.mod load`.

---

### Links

- 📡 Main channel: [t.me/MadeBySuperMaxVF](https://t.me/MadeBySuperMaxVF)
- 👨‍💻 Dev channel: [t.me/Mad3BySuperMaxVF](https://t.me/Mad3BySuperMaxVF)
- 🔗 GitHub: [github.com/SuperMaxVF000/SMVF](https://github.com/SuperMaxVF000/SMVF)

---

---

## 🇷🇺 Русский

### О проекте

**SMVF** — юзербот для Telegram с космической темой оформления. Поддерживает собственные модули, а также модули от **Hikka** и **MCUB**. При первом запуске автоматически создаёт инлайн-бота и лог-группу.

**Возможности:**
- 🚀 Простая установка одной командой
- 🤖 Автосоздание инлайн-бота через BotFather
- 📋 Автосоздание группы с логами (события, ошибки, статус)
- 📦 Поддержка модулей SMVF, Hikka и MCUB
- 🌌 Космический скринсейвер в терминале (звёзды, кометы)
- ⚡ Никогда не засыпает, работает 24/7
- 💾 Все логи сохраняются в файл
- 📡 Сетевой мониторинг и автовосстановление
- 💎 Поддержка Premium-эмодзи
- ⌨️ Настройка без веб-сервера — всё через терминал

---

### Установка

**Быстрая установка (все платформы):**
```bash
curl -sSL https://raw.githubusercontent.com/SuperMaxVF000/SMVF/main/install.sh | bash
```

#### 🟢 Termux (Android)
```bash
pkg update && pkg upgrade -y
pkg install python python-pip git -y
git clone https://github.com/SuperMaxVF000/SMVF ~/SMVF
cd ~/SMVF
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
python -m smvf
```

#### 🟡 UserLand → Ubuntu (Android)
```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y
git clone https://github.com/SuperMaxVF000/SMVF ~/SMVF
cd ~/SMVF
python3 -m venv venv && source venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
python -m smvf
```

#### 🔵 Ubuntu / Debian (ПК или VPS)
```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y
git clone https://github.com/SuperMaxVF000/SMVF ~/SMVF
cd ~/SMVF
python3 -m venv venv && source venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
python -m smvf
```

Запуск в фоне через **screen**:
```bash
screen -S smvf
cd ~/SMVF && source venv/bin/activate && python -m smvf
# Ctrl+A, D — свернуть   |   screen -r smvf — вернуться
```

#### 🔴 Raspberry Pi (Raspberry Pi OS)
```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y
git clone https://github.com/SuperMaxVF000/SMVF ~/SMVF
cd ~/SMVF
python3 -m venv venv && source venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
python -m smvf
```

Автозапуск через **systemd** (`/etc/systemd/system/smvf.service`):
```ini
[Unit]
Description=SMVF Userbot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/SMVF
ExecStart=/home/pi/SMVF/venv/bin/python -m smvf
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable smvf && sudo systemctl start smvf
```

---

### Первоначальная настройка

При первом запуске SMVF запустит мастер настройки в терминале — веб-сервер не нужен. Потребуются:

1. **API ID** и **API Hash** — получи на [my.telegram.org](https://my.telegram.org) → *API development tools*
2. **Номер телефона** — в формате `+79001234567`
3. **Префикс команд** — по умолчанию `.`
4. **Telegram Premium** — есть ли у тебя подписка?

Данные сохраняются в `smvf_config.json`. После настройки SMVF автоматически создаёт инлайн-бота и лог-группу.

---

### Встроенные команды

| Команда | Описание |
|---------|----------|
| `.info` | Показать карточку юзербота |
| `.info set <текст>` | Установить свой текст в .info |
| `.info media` | Установить медиа (ответь на фото/видео/гиф) |
| `.info clear media` | Удалить медиа из .info |
| `.info button Текст\|URL` | Добавить инлайн-кнопку |
| `.ping` | Показать задержку и аптайм |
| `.ping media` | Установить медиа для .ping |
| `.ping clear media` | Удалить медиа из .ping |
| `.help` | Список всех команд |
| `.mod list` | Список загруженных модулей |
| `.mod load <url>` | Загрузить модуль по URL |
| `.mod load` + reply | Загрузить .py файл из ответа |
| `.mod unload <имя>` | Выгрузить модуль |
| `.alias add к=команда` | Добавить алиас |
| `.alias del <алиас>` | Удалить алиас |
| `.alias list` | Список алиасов |
| `.restart` | Перезапустить юзербот |
| `.update` | Обновить с GitHub |

---

### Модули

SMVF поддерживает три формата: **SMVF**, **Hikka** (через shim) и **MCUB**. Полная документация: [MODULES.md](MODULES.md)

Загрузка модуля:
```
.mod load https://raw.githubusercontent.com/.../mymodule.py
```
Или ответь на `.py` файл командой `.mod load`.

---

### Ссылки

- 📡 Основной канал: [t.me/MadeBySuperMaxVF](https://t.me/MadeBySuperMaxVF)
- 👨‍💻 Dev-канал: [t.me/Mad3BySuperMaxVF](https://t.me/Mad3BySuperMaxVF)
- 🔗 GitHub: [github.com/SuperMaxVF000/SMVF](https://github.com/SuperMaxVF000/SMVF)

---

<div align="center">

*✦ Made by SuperMaxVF ✦*

</div>
