#!/data/data/com.termux/files/usr/bin/bash
# Code Gallery Termux repo installer
#   curl -sL https://atharv525.github.io/code-gallery-termux/install.sh | bash
set -e
REPO_URL="https://atharv525.github.io/code-gallery-termux"
P="${PREFIX:-/data/data/com.termux/files/usr}"
if [ ! -d "$P/etc/apt" ]; then
  echo "This installer is for the Termux app only."; exit 1
fi
echo "[*] Adding Code Gallery repo..."
mkdir -p "$P/etc/apt/sources.list.d" "$P/etc/apt/trusted.gpg.d"
curl -fsSL "$REPO_URL/codegallery.gpg" -o "$P/etc/apt/trusted.gpg.d/codegallery.gpg"
echo "deb $REPO_URL codegallery main" > "$P/etc/apt/sources.list.d/codegallery.list"
echo "[*] Updating package lists..."
apt update
apt install -y code-gallery-keyring >/dev/null 2>&1 || true
cat <<MSG

[+] Code Gallery repo added!
    pkg install cg-setup      # toolkit installer menu
    pkg install cg-devkit     # full coding toolkit in one go
    pkg install cg-run cg-new cg-serve cg-push cg-backup cg-info cg-clean
    apt list 2>/dev/null | grep codegallery   # everything in the repo
MSG
