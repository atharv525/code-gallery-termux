#!/data/data/com.termux/files/usr/bin/bash
# Remove the Code Gallery Termux repo (installed tools stay unless you remove them)
#   curl -sL https://atharv525.github.io/code-gallery-termux/uninstall.sh | bash
P="${PREFIX:-/data/data/com.termux/files/usr}"
apt remove -y code-gallery-keyring >/dev/null 2>&1 || true
rm -f "$P/etc/apt/sources.list.d/codegallery.list" "$P/etc/apt/trusted.gpg.d/codegallery.gpg"
apt update
echo "[+] Code Gallery repo removed."
echo "    To also remove its tools: apt remove cg-setup cg-devkit cg-run cg-new cg-serve cg-push cg-backup cg-info cg-clean"
