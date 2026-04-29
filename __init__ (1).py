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
[![Telegram](https://img.shields.io/badge/channel-@MadeBySuperMaxVF-26A5E4?style=for-the-badge&logo=telegram)](https://t.me/MadeBySuperMaxVF)
[![Dev Channel](https://img.shields.io/badge/dev-@Mad3BySuperMaxVF-26A5E4?style=for-the-badge&logo=telegram)](https://t.me/Mad3BySuperMaxVF)

*✦ Made by SuperMaxVF ✦*

</div>

---

## 🌌 О проекте

**SMVF** — это юзербот для Telegram с космической темой оформления. Поддерживает собственные модули, а также модули от **Hikka** и **MCUB**. При первом запуске автоматически создаёт инлайн-бота и лог-группу.

### Возможности
- 🚀 Простая установка одной командой
- 🤖 Автосоздание инлайн-бота через BotFather
- 📋 Автосоздание группы с логами (время, ошибки, статус)
- 📦 Поддержка модулей SMVF, Hikka и MCUB
- 🌌 Космический скринсейвер в терминале (звёзды, кометы)
- ⚡ Никогда не засыпает, работает 24/7
- 💾 Все логи сохраняются в файл
- 📡 Сетевой мониторинг и автовосстановление соединения
- 💎 Поддержка Premium-эмодзи
- ⌨️ Настройка без веб-сервера — всё через терминал

---

## 📥 Установка

### Быстрая установка (все платформы)

```bash
curl -sSL https://raw.githubusercontent.com/SuperMaxVF000/SMVF/main/install.sh | bash
```

---

### 🟢 Termux (Android)

```bash
# 1. Обнови пакеты
pkg update && pkg upgrade -y

# 2. Установи зависимости
pkg install python python-pip git -y

# 3. Клонируй репозиторий
git clone https://github.com/SuperMaxVF000/SMVF ~/SMVF
cd ~/SMVF

# 4. Установи Python-зависимости
pip install -r requirements.txt

# 5. Запусти
python -m smvf
```

---

### 🟡 UserLand → Ubuntu (Android)

```bash
# В терминале Ubuntu внутри UserLand:
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y

git clone https://github.com/SuperMaxVF000/SMVF ~/SMVF
cd ~/SMVF

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python -m smvf
```

---

### 🔵 Ubuntu / Debian (ПК или VPS)

```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y

git clone https://github.com/SuperMaxVF000/SMVF ~/SMVF
cd ~/SMVF

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python -m smvf
```

#### Запуск в фоне через screen:
```bash
screen -S smvf
cd ~/SMVF && source venv/bin/activate && python -m smvf
# Ctrl+A, D — свернуть
# screen -r smvf — вернуться
```

---

### 🔴 Raspberry Pi (Raspberry Pi OS)

```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y

git clone https://github.com/SuperMaxVF000/SMVF ~/SMVF
cd ~/SMVF

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python -m smvf
```

#### Автозапуск при старте системы (systemd):
```bash
sudo nano /etc/systemd/system/smvf.service
```

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
sudo systemctl enable smvf
sudo systemctl start smvf
sudo systemctl status smvf
```

---

## 🛠 Первоначальная настройка

При первом запуске SMVF запустит мастер настройки в терминале:

1. **API ID** и **API Hash** — получи на [my.telegram.org](https://my.telegram.org) → *API development tools*
2. **Номер телефона** — в формате `+79001234567`
3. **Префикс команд** — по умолчанию `.`
4. **Telegram Premium** — есть ли у тебя подписка?

Данные сохраняются в `smvf_config.json` — **никакого веб-сервера**.

После настройки SMVF автоматически:
- Создаст инлайн-бота через BotFather
- Создаст группу с логами и добавит туда бота
- Загрузит все модули из папки `modules/`

---

## ⌨️ Встроенные команды

| Команда | Описание |
|---------|----------|
| `.info` | Показать информацию о юзерботе |
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

## 📦 Модули

SMVF поддерживает три формата модулей:

### Формат SMVF (рекомендуется)
```python
from telethon import events

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.mycommand$"))
    async def handler(event):
        await event.edit("Привет! ✦ Made by SuperMaxVF")
```

### Модули от MCUB
Полностью совместимы — помести `.py` файл в папку `modules/`.

### Модули от Hikka
Частичная совместимость через shim-слой. Большинство простых модулей работают.

### Установка модуля
```
.mod load https://example.com/mymodule.py
```
Или ответь на `.py` файл командой `.mod load`.

---

## 🌌 Скринсейвер

После запуска в терминале автоматически активируется анимированный космический скринсейвер:
- Разноцветные звёзды (`★ ☆ ✦ ✧ ✩`)
- Летящие кометы
- Анимация 12 FPS
- Защищает экран от выгорания

Для выхода нажми **Ctrl+C**.

---

## 📋 Логи

- **В Telegram:** все события отправляются в лог-группу (инлайн-бот)
- **В файле:** `logs/smvf_YYYYMMDD_HHMMSS.log`
- Логируются: запуск, ошибки, загрузка модулей, проблемы с сетью

---

## 🔗 Ссылки

- 📡 Основной канал: [t.me/MadeBySuperMaxVF](https://t.me/MadeBySuperMaxVF)
- 👨‍💻 Dev-канал: [t.me/Mad3BySuperMaxVF](https://t.me/Mad3BySuperMaxVF)
- 🔗 GitHub: [github.com/SuperMaxVF000/SMVF](https://github.com/SuperMaxVF000/SMVF)

---

<div align="center">

*✦ Made by SuperMaxVF ✦*

</div>
