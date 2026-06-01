#!/bin/bash
# SMVF Userbot — установщик для Ubuntu / UserLand (Android)
# Использование: bash install.sh

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

REPO="https://github.com/SuperMaxVF000/SMVF"
SMVF_DIR="$HOME/smvf"
PYTHON_MIN="3.10"

echo -e "${CYAN}"
echo "  ███████╗███╗   ███╗██╗   ██╗███████╗"
echo "  ██╔════╝████╗ ████║██║   ██║██╔════╝"
echo "  ███████╗██╔████╔██║██║   ██║█████╗  "
echo "  ╚════██║██║╚██╔╝██║╚██╗ ██╔╝██╔══╝  "
echo "  ███████║██║ ╚═╝ ██║ ╚████╔╝ ██║     "
echo "  ╚══════╝╚═╝     ╚═╝  ╚═══╝  ╚═╝     "
echo -e "${NC}  Userbot Installer — Ubuntu / UserLand"
echo ""

# Проверяем Python
echo -e "${CYAN}[1/5] Проверка Python...${NC}"
if ! command -v python3 &>/dev/null; then
    echo -e "${YELLOW}Python3 не найден. Устанавливаем...${NC}"
    sudo apt-get update -q
    sudo apt-get install -y python3 python3-pip python3-venv
fi

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"; then
    echo -e "${GREEN}Python $PY_VER — OK${NC}"
else
    echo -e "${RED}Требуется Python 3.10+, установлен $PY_VER${NC}"
    echo "Установите Python 3.10+: sudo apt install python3.10"
    exit 1
fi

# Зависимости системы
echo -e "${CYAN}[2/5] Установка системных зависимостей...${NC}"
sudo apt-get update -q
sudo apt-get install -y git python3-pip python3-venv libssl-dev libffi-dev

# Клонируем репо
echo -e "${CYAN}[3/5] Загрузка SMVF...${NC}"
if [ -d "$SMVF_DIR" ]; then
    echo -e "${YELLOW}Директория $SMVF_DIR уже существует. Обновляем...${NC}"
    cd "$SMVF_DIR"
    git pull
else
    git clone "$REPO" "$SMVF_DIR"
    cd "$SMVF_DIR"
fi

# Виртуальное окружение
echo -e "${CYAN}[4/5] Создание виртуального окружения...${NC}"
python3 -m venv .venv
source .venv/bin/activate
# Обновляем pip только если это не контейнер без полноценного pip (UserLand)
if pip install --upgrade pip -q 2>/dev/null; then
    :
fi
pip install -r requirements.txt -q

# systemd-сервис (опционально, только если systemd запущен как init)
echo -e "${CYAN}[5/5] Настройка автозапуска...${NC}"
if ! systemctl is-system-running &>/dev/null 2>&1 && ! pidof systemd &>/dev/null; then
    echo -e "${YELLOW}⚠️  systemd не обнаружен (UserLand/контейнер). Автозапуск через systemd недоступен.${NC}"
    echo -e "    Для фонового запуска используйте: ${CYAN}tmux new-session -s smvf 'cd $SMVF_DIR && source .venv/bin/activate && python -m smvf'${NC}"
else
    read -p "Создать systemd-сервис для автозапуска? [y/N] " CREATE_SERVICE
    if [[ "$CREATE_SERVICE" =~ ^[Yy]$ ]]; then
        SERVICE_FILE="/etc/systemd/system/smvf.service"
        sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=SMVF Userbot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SMVF_DIR
ExecStart=$SMVF_DIR/.venv/bin/python -m smvf
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
        sudo systemctl daemon-reload
        sudo systemctl enable smvf
        echo -e "${GREEN}Сервис создан. Запуск: sudo systemctl start smvf${NC}"
    fi
fi

echo ""
echo -e "${GREEN}✅ SMVF установлен в $SMVF_DIR${NC}"
echo ""
echo "Запуск:"
echo -e "  ${CYAN}cd $SMVF_DIR${NC}"
echo -e "  ${CYAN}source .venv/bin/activate${NC}"
echo -e "  ${CYAN}python -m smvf${NC}"
echo ""
