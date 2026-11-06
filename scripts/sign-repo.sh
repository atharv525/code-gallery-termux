#!/usr/bin/env bash
# Sign out/dists/codegallery/Release -> InRelease + Release.gpg.
# Needs GPG_PASSPHRASE in the environment (GitHub Actions secret).
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
: "${GPG_PASSPHRASE:?GPG_PASSPHRASE is not set}"
export GNUPGHOME=${GNUPGHOME:-$(mktemp -d)}
chmod 700 "$GNUPGHOME"
echo allow-loopback-pinentry > "$GNUPGHOME/gpg-agent.conf"
pf=$(mktemp); trap 'rm -f "$pf"' EXIT
printf '%s' "$GPG_PASSPHRASE" > "$pf"
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -in "$ROOT/keys/signing-key.enc" -pass file:"$pf" \
  | gpg --batch --pinentry-mode loopback --passphrase-file "$pf" --import 2>/dev/null
KEY=$(gpg --batch --with-colons --list-secret-keys | awk -F: '/^fpr/{print $10; exit}')
REL="$ROOT/out/dists/codegallery"
rm -f "$REL/InRelease" "$REL/Release.gpg"
gpg --batch --yes --pinentry-mode loopback --passphrase-file "$pf" --digest-algo SHA512 \
  -u "$KEY" --clearsign -o "$REL/InRelease" "$REL/Release"
gpg --batch --yes --pinentry-mode loopback --passphrase-file "$pf" --digest-algo SHA512 \
  -u "$KEY" -abs -o "$REL/Release.gpg" "$REL/Release"
echo "signed with $KEY"
