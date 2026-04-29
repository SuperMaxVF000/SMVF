#!/bin/bash
# ✦ SMVF Userbot Installer ✦
# Made by SuperMaxVF
# https://github.com/SuperMaxVF000/SMVF

set -e

RED='\033[91m'; GREEN='\033[92m'; YELLOW='\033[93m'; CYAN='\033[96m'
MAGENTA='\033[95m'; BOLD='\033[1m'; RESET='\033[0m'
STAR='\033[38;5;226m'; NEBULA='\033[38;5;93m'; COMET='\033[38;5;51m'

banner() {
  echo -e "${BOLD}${NEBULA}"
  echo "  ███████╗███╗   ███╗██╗   ██╗███████╗"
  echo "  ██╔════╝████╗ ████║██║   ██║██╔════╝"
  echo "  ███████╗██╔████╔██║██║   ██║█████╗  "
  echo "  ╚════██║██║╚██╔╝██║╚██╗ ██╔╝██╔══╝  "
  echo "  ███████║██║ ╚═╝ ██║ ╚████╔╝ ██║     "
  echo "  ╚══════╝╚═╝     ╚═╝  ╚═══╝  ╚═╝     "
  echo -e "${STAR}        ✦ Made by SuperMaxVF ✦         ${RESET}"
  echo -e "${COMET}  t.me/MadeBySuperMaxVF | t.me/Mad3BySuperMaxVF${RESET}"
  echo ""
}

info()  { echo -e "${CYAN}[INFO]${RESET} $1"; }
ok()    { echo -e "${GREEN}[OK]${RESET} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${RESET} $1"; }
err()   { echo -e "${RED}[ERR]${RESET} $1"; exit 1; }
step()  { echo -e "\n${BOLD}${MAGENTA}▶ $1${RESET}"; }

banner

# ── Detect platform ────────────────────────────────────────────────────────
step "Определяю платформу..."
PLATFORM="unknown"
if [ -f /data/data/com.termux/files/usr/bin/bash ]; then
  PLATFORM="termux"
elif grep -qi "raspberry" /proc/device-tree/model 2>/dev/null; then
  PLATFORM="raspberrypi"
elif [ -f /etc/os-release ]; then
  . /etc/os-release
  PLATFORM="${ID:-linux}"
fi
ok "Платформа: $PLATFORM"

# ── Install system deps ────────────────────────────────────────────────────
step "Устанавливаю системные зависимости..."
case "$PLATFORM" in
  termux)
    pkg update -y && pkg install -y python python-pip git
    ;;
  raspberrypi|debian|ubuntu|linuxmint)
    sudo apt-get update -y && sudo apt-get install -y python3 python3-pip python3-venv git curl
    ;;
  *)
    warn "Неизвестная платформа — попробую стандартный apt"
    command -v apt-get >/dev/null && sudo apt-get install -y python3 python3-pip git || true
    ;;
esac
ok "Зависимости установлены"

# ── Clone / update ─────────────────────────────────────────────────────────
step "Скачиваю SMVF с GitHub..."
SMVF_DIR="$HOME/SMVF"
if [ -d "$SMVF_DIR/.git" ]; then
  info "Директория уже существует, обновляю..."
  cd "$SMVF_DIR" && git pull origin main
else
  git clone https://github.com/SuperMaxVF000/SMVF "$SMVF_DIR"
  cd "$SMVF_DIR"
fi
ok "SMVF скачан в $SMVF_DIR"

# ── Python venv ────────────────────────────────────────────────────────────
step "Настраиваю Python окружение..."
if [ "$PLATFORM" = "termux" ]; then
  pip install --upgrade pip
  pip install -r requirements.txt
else
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
fi
ok "Python зависимости установлены"

# ── Done ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${STAR}╔══════════════════════════════════════╗${RESET}"
echo -e "${BOLD}${STAR}║  ✅  SMVF УСПЕШНО УСТАНОВЛЕН!        ║${RESET}"
echo -e "${BOLD}${STAR}╚══════════════════════════════════════╝${RESET}"
echo ""
echo -e "${CYAN}Запуск:${RESET}"
if [ "$PLATFORM" = "termux" ]; then
  echo -e "  ${BOLD}cd ~/SMVF && python -m smvf${RESET}"
else
  echo -e "  ${BOLD}cd ~/SMVF && source venv/bin/activate && python -m smvf${RESET}"
fi
echo ""
echo -e "${MAGENTA}📡 Канал: https://t.me/MadeBySuperMaxVF${RESET}"
echo -e "${MAGENTA}👨‍💻 Dev:   https://t.me/Mad3BySuperMaxVF${RESET}"
echo -e "${MAGENTA}🔗 GitHub: https://github.com/SuperMaxVF000/SMVF${RESET}"
echo ""
echo -e "${NEBULA}✦ Made by SuperMaxVF ✦${RESET}"
