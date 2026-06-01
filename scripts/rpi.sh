#!/bin/bash
# SMVF Userbot — установщик для Raspberry Pi (тест: RPi 5 8GB)
# Использование: bash rpi.sh

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

REPO="https://github.com/SuperMaxVF000/SMVF"
SMVF_DIR="$HOME/smvf"

echo -e "${CYAN}"
echo "  ███████╗███╗   ███╗██╗   ██╗███████╗"
echo "  ██╔════╝████╗ ████║██║   ██║██╔════╝"
echo "  ███████╗██╔████╔██║██║   ██║█████╗  "
echo "  ╚════██║██║╚██╔╝██║╚██╗ ██╔╝██╔══╝  "
echo "  ███████║██║ ╚═╝ ██║ ╚████╔╝ ██║     "
echo "  ╚══════╝╚═╝     ╚═╝  ╚═══╝  ╚═╝     "
echo -e "${NC}  Userbot Installer — Raspberry Pi"
echo ""

# Определяем модель RPi
if [ -f /proc/device-tree/model ]; then
    RPI_MODEL=$(cat /proc/device-tree/model 2>/dev/null | tr -d '\0')
    echo -e "${GREEN}Обнаружено: $RPI_MODEL${NC}"
fi

echo -e "${CYAN}[1/5] Обновление системы...${NC}"
sudo apt-get update -q
sudo apt-get upgrade -y -q

echo -e "${CYAN}[2/5] Установка зависимостей...${NC}"
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    libssl-dev \
    libffi-dev \
    build-essential \
    python3-dev

# Проверяем Python
echo -e "${CYAN}[3/5] Проверка Python...${NC}"
PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"; then
    echo -e "${GREEN}Python $PY_VER — OK${NC}"
else
    echo -e "${RED}Требуется Python 3.10+, установлен $PY_VER${NC}"
    echo "На RPi OS Bookworm уже Python 3.11. Обновите систему:"
    echo "  sudo apt-get install python3.11"
    exit 1
fi

# Клонируем
echo -e "${CYAN}[4/5] Загрузка SMVF...${NC}"
if [ -d "$SMVF_DIR" ]; then
    echo -e "${YELLOW}Обновляем существующую установку...${NC}"
    cd "$SMVF_DIR" && git pull
else
    git clone "$REPO" "$SMVF_DIR"
    cd "$SMVF_DIR"
fi

# Виртуальное окружение
cd "$SMVF_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

# systemd-сервис (рекомендуется для RPi — работает всегда)
echo -e "${CYAN}[5/5] Настройка systemd-сервиса...${NC}"
echo -e "${YELLOW}Рекомендуется для Raspberry Pi: systemd обеспечивает автозапуск после перезагрузки${NC}"
read -p "Создать systemd-сервис? [Y/n] " CREATE_SERVICE
CREATE_SERVICE=${CREATE_SERVICE:-Y}

if [[ "$CREATE_SERVICE" =~ ^[Yy]$ ]]; then
    SERVICE_FILE="/etc/systemd/system/smvf.service"
    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=SMVF Userbot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SMVF_DIR
ExecStart=$SMVF_DIR/.venv/bin/python -m smvf
Restart=always
RestartSec=15
StandardOutput=journal
StandardError=journal
# Не даём системе останавливать процесс при нагрузке
OOMScoreAdjust=-100

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable smvf
    echo -e "${GREEN}Сервис создан и включён (автозапуск при перезагрузке)${NC}"
    echo ""
    echo "Управление:"
    echo -e "  Запуск:   ${CYAN}sudo systemctl start smvf${NC}"
    echo -e "  Стоп:     ${CYAN}sudo systemctl stop smvf${NC}"
    echo -e "  Логи:     ${CYAN}sudo journalctl -u smvf -f${NC}"
    echo -e "  Статус:   ${CYAN}sudo systemctl status smvf${NC}"
fi

echo ""
echo -e "${GREEN}✅ SMVF установлен в $SMVF_DIR${NC}"
echo ""
echo "Первый запуск (настройка):"
echo -e "  ${CYAN}cd $SMVF_DIR${NC}"
echo -e "  ${CYAN}source .venv/bin/activate${NC}"
echo -e "  ${CYAN}python -m smvf${NC}"
echo ""
echo -e "${YELLOW}⚠️  При первом запуске потребуется ввести API_ID, API_HASH и номер телефона${NC}"
echo ""
