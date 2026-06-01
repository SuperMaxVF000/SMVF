#!/data/data/com.termux/files/usr/bin/bash
# SMVF Userbot — установщик для Termux (Android)
# Использование: bash termux.sh

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
echo -e "${NC}  SMVF Userbot v1.2beta — Termux Installer"
echo ""

echo -e "${CYAN}[1/4] Обновление пакетов Termux...${NC}"
pkg update -y -q
pkg install -y python git openssl libffi

echo -e "${CYAN}[2/4] Проверка Python...${NC}"
PY_VER=$(python -c "import sys; print(str(sys.version_info.major) + '.' + str(sys.version_info.minor))")
python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"
if test $? -eq 0; then
    echo -e "${GREEN}Python $PY_VER — OK${NC}"
else
    echo -e "${RED}Требуется Python 3.10+, установлен $PY_VER${NC}"
    exit 1
fi

echo -e "${CYAN}[3/4] Загрузка SMVF...${NC}"
if test -d "$SMVF_DIR"; then
    echo -e "${YELLOW}Обновляем существующую установку...${NC}"
    cd "$SMVF_DIR"
    git pull
else
    git clone "$REPO" "$SMVF_DIR"
    cd "$SMVF_DIR"
fi

echo -e "${CYAN}[4/4] Установка зависимостей...${NC}"
cd "$SMVF_DIR"
# psutil не поддерживает Android официально — пропускаем, он опциональный
pip install telethon aiohttp tgcrypto -q

echo ""
echo -e "${GREEN}✅ SMVF v1.2beta установлен в $SMVF_DIR${NC}"
echo ""
echo "Запуск:"
echo -e "  ${CYAN}cd $SMVF_DIR && python -m smvf${NC}"
echo ""
echo "Фоновый режим:"
echo -e "  ${CYAN}pkg install tmux${NC}"
echo -e "  ${CYAN}tmux new-session -s smvf 'cd $SMVF_DIR && python -m smvf'${NC}"
echo -e "  Отключиться: Ctrl+B затем D  |  Вернуться: tmux attach -t smvf"
echo ""
