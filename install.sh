#!/bin/bash
# ╔══════════════════════════════════════════════════════╗
# ║       SMVF Userbot Installer v1.0                   ║
# ║       Made by SuperMaxVF                            ║
# ║       github.com/SuperMaxVF000/SMVF                 ║
# ╚══════════════════════════════════════════════════════╝
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'
MAGENTA='\033[0;35m'; YELLOW='\033[1;33m'; NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

banner(){
cat << 'EOF'
  ███████╗███╗   ███╗██╗   ██╗███████╗
  ██╔════╝████╗ ████║██║   ██║██╔════╝
  ███████╗██╔████╔██║██║   ██║█████╗
  ╚════██║██║╚██╔╝██║╚██╗ ██╔╝██╔══╝
  ███████║██║ ╚═╝ ██║ ╚████╔╝ ██║
  ╚══════╝╚═╝     ╚═╝  ╚═══╝  ╚═╝
         Made by SuperMaxVF   v1.0
EOF
}

step(){ echo -e "${CYAN}[✦]${NC} $1"; }
ok(){   echo -e "${GREEN}[✓]${NC} $1"; }
err(){  echo -e "${RED}[✗]${NC} $1"; exit 1; }
warn(){ echo -e "${YELLOW}[⚠]${NC} $1"; }

detect_platform(){
    if [ -n "$TERMUX_VERSION" ]; then
        PLATFORM="termux"
    elif [ -f /proc/cpuinfo ] && grep -qi "raspberry" /proc/cpuinfo 2>/dev/null; then
        PLATFORM="raspberry"
    elif [ -f /etc/os-release ]; then
        . /etc/os-release
        PLATFORM="${ID:-unknown}"
    else
        PLATFORM="unknown"
    fi
    echo -e "${MAGENTA}[✦] Platform: ${PLATFORM}${NC}"
}

is_proot(){
    uname -r 2>/dev/null | grep -qi "android\|userland\|proot" && return 0
    grep -qa "proot" /proc/1/cmdline 2>/dev/null && return 0
    [ -f /etc/userland ] && return 0
    return 1
}

# ══════════════════════════════════════════════════════
# TERMUX — все C-пакеты через pkg, не pip
# ══════════════════════════════════════════════════════
install_termux(){
    step "Updating pkg..."
    pkg update -y 2>/dev/null || true

    step "Installing system packages via pkg..."
    pkg install -y python python-pip git libffi openssl \
        python-psutil python-pillow || \
    pkg install -y python python-pip git libffi openssl python-psutil
    ok "System packages installed"

    step "Installing Python packages via pip (pure-Python only)..."
    # cryptg — pure Python fallback (no Rust needed for telethon, cryptg is optional speedup)
    pip install \
        "telethon>=1.34.0" \
        "aiohttp>=3.9.0" \
        "aiofiles>=23.0.0" \
        "colorama>=0.4.6" \
        "rich>=13.0.0" \
        "requests>=2.31.0" \
        -q
    ok "Python packages installed"
}

# ══════════════════════════════════════════════════════
# USERLAND / proot-Ubuntu
# pyaes падает из-за proot-ограничений на rename().
# Единственный надёжный способ: поставить telethon
# через apt (python3-telethon если есть) или
# через pip с --no-deps + зависимости вручную.
# ══════════════════════════════════════════════════════
install_userland(){
    step "Installing apt packages..."
    sudo apt-get update -y -qq
    sudo apt-get install -y -qq \
        python3 python3-pip python3-dev \
        git libffi-dev libssl-dev build-essential \
        python3-aiohttp python3-requests python3-colorama \
        python3-pil python3-psutil

    # Try system telethon first
    if sudo apt-get install -y -qq python3-telethon 2>/dev/null; then
        ok "telethon installed via apt"
    else
        step "Installing telethon via pip --no-deps (bypasses pyaes build)..."
        # --no-deps skips pyaes build entirely, we install deps separately
        pip3 install --user --no-deps "telethon>=1.34.0" -q
        # pyaes pure python — install from pre-built wheel directly
        pip3 install --user \
            "pyaes" \
            "pyasn1" \
            "rsa" \
            -q --only-binary :all: 2>/dev/null || \
        pip3 install --user "pyaes" "pyasn1" "rsa" -q --no-build-isolation
        ok "telethon installed via pip"
    fi

    pip3 install --user \
        "aiofiles>=23.0.0" \
        "rich>=13.0.0" \
        -q --only-binary :all: 2>/dev/null || \
    pip3 install --user "aiofiles>=23.0.0" "rich>=13.0.0" -q

    ok "All packages installed"
}

# ══════════════════════════════════════════════════════
# STANDARD Ubuntu/Debian/Raspberry
# ══════════════════════════════════════════════════════
install_apt(){
    step "Installing apt dependencies..."
    sudo apt-get update -y -qq
    sudo apt-get install -y \
        python3 python3-pip python3-dev \
        git libffi-dev libssl-dev build-essential \
        libjpeg-dev zlib1g-dev
    ok "apt packages installed"

    step "Installing Python packages..."
    pip3 install --user -r requirements.txt -q
    ok "Python packages installed"
}

# ── Autostart ──────────────────────────────────────────
autostart_termux(){
    mkdir -p ~/.termux/boot
    printf '#!/data/data/com.termux/files/usr/bin/bash\ncd "%s"\npython main.py &\n' \
        "$SCRIPT_DIR" > ~/.termux/boot/smvf.sh
    chmod +x ~/.termux/boot/smvf.sh
    ok "Termux:Boot script created"
    warn "Install Termux:Boot from F-Droid to enable boot autostart."
}

autostart_systemd(){
    SVC="$HOME/.config/systemd/user/smvf.service"
    mkdir -p "$(dirname "$SVC")"
    PYBIN=$(command -v python3 2>/dev/null || command -v python)
    cat > "$SVC" << SVCEOF
[Unit]
Description=SMVF Userbot - Made by SuperMaxVF
After=network.target

[Service]
Type=simple
WorkingDirectory=$SCRIPT_DIR
ExecStart=$PYBIN main.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target
SVCEOF
    if command -v systemctl &>/dev/null; then
        systemctl --user daemon-reload
        systemctl --user enable smvf 2>/dev/null || true
        ok "systemd service created"
        echo -e "${CYAN}  Start: systemctl --user start smvf${NC}"
    else
        warn "systemd unavailable. Use tmux:"
        echo -e "${YELLOW}  sudo apt install tmux -y && tmux new -s smvf${NC}"
        echo -e "${YELLOW}  python3 main.py${NC}"
        echo -e "${YELLOW}  Detach: Ctrl+B then D  |  Reattach: tmux attach -t smvf${NC}"
    fi
}

main(){
    clear; banner; echo ""
    detect_platform

    case "$PLATFORM" in
        termux)
            install_termux
            autostart_termux
            ;;
        ubuntu|debian|raspbian|raspberry|linuxmint|pop|kali)
            if is_proot; then
                echo -e "${MAGENTA}[✦] Detected proot/UserLand environment${NC}"
                install_userland
            else
                install_apt
                autostart_systemd
            fi
            ;;
        *)
            warn "Unknown platform '$PLATFORM', trying apt..."
            if is_proot; then install_userland
            else install_apt; autostart_systemd; fi
            ;;
    esac

    echo ""
    echo -e "${MAGENTA}╔══════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║  SMVF installed!  Run: python3 main.py  ║${NC}"
    echo -e "${MAGENTA}║  Made by SuperMaxVF                     ║${NC}"
    echo -e "${MAGENTA}╚══════════════════════════════════════════╝${NC}"
    echo ""
}

main "$@"
