#!/usr/bin/env bash
# Create packages/<name> from the template:  scripts/new-package.sh cg-mytool
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
name=${1:?usage: scripts/new-package.sh <name>}
dst="$ROOT/packages/$name"
[ -e "$dst" ] && { echo "$dst already exists" >&2; exit 1; }
cp -r "$ROOT/packages/_template" "$dst"
mv "$dst/files/bin/cg-template" "$dst/files/bin/$name"
sed -i "s/cg-template/$name/g" "$dst/build.conf" "$dst/files/bin/$name"
echo "created $dst - edit build.conf and files/bin/$name, then push"
