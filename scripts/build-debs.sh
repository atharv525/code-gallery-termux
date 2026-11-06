#!/usr/bin/env bash
# Build every package in packages/ into a Termux .deb under out/pool/main/.
# Usage: scripts/build-debs.sh [package ...]
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
OUT="$ROOT/out/pool/main"
TPREFIX="data/data/com.termux/files/usr"
MAINTAINER="Code Gallery <codegallery-termux@users.noreply.github.com>"
HOMEPAGE="https://github.com/atharv525/code-gallery-termux"
mkdir -p "$OUT"

pkgs=("$@")
if [ ${#pkgs[@]} -eq 0 ]; then
  for d in "$ROOT"/packages/*/; do n=$(basename "$d"); [[ $n == _* ]] || pkgs+=("$n"); done
fi

for name in "${pkgs[@]}"; do
  dir="$ROOT/packages/$name"
  [ -f "$dir/build.conf" ] || { echo "no build.conf in $dir" >&2; exit 1; }
  unset NAME VERSION ARCH DEPENDS RECOMMENDS SUGGESTS CONFLICTS SECTION DESCRIPTION LONG_DESCRIPTION
  # shellcheck disable=SC1091
  . "$dir/build.conf"
  : "${NAME:?}" "${VERSION:?}" "${DESCRIPTION:?}"
  ARCH=${ARCH:-all}; SECTION=${SECTION:-utils}
  for arch in $ARCH; do
    stage=$(mktemp -d)
    mkdir -p "$stage/DEBIAN" "$stage/$TPREFIX"
    if [ -d "$dir/files" ]; then cp -a "$dir/files/." "$stage/$TPREFIX/"; fi
    [ -d "$stage/$TPREFIX/bin" ] && chmod 755 "$stage/$TPREFIX/bin/"* 2>/dev/null || true
    find "$stage" -type d -exec chmod 755 {} +
    size=$(du -sk --exclude=DEBIAN "$stage" | cut -f1)
    {
      echo "Package: $NAME"
      echo "Version: $VERSION"
      echo "Architecture: $arch"
      echo "Maintainer: $MAINTAINER"
      echo "Installed-Size: $size"
      [ -n "${DEPENDS:-}" ] && echo "Depends: $DEPENDS"
      [ -n "${RECOMMENDS:-}" ] && echo "Recommends: $RECOMMENDS"
      [ -n "${SUGGESTS:-}" ] && echo "Suggests: $SUGGESTS"
      [ -n "${CONFLICTS:-}" ] && echo "Conflicts: $CONFLICTS"
      echo "Section: $SECTION"
      echo "Priority: optional"
      echo "Homepage: $HOMEPAGE"
      echo "Description: $DESCRIPTION"
      if [ -n "${LONG_DESCRIPTION:-}" ]; then
        printf '%s\n' "$LONG_DESCRIPTION" | sed -e 's/^$/./' -e 's/^/ /'
      fi
    } > "$stage/DEBIAN/control"
    for s in preinst postinst prerm postrm; do
      if [ -f "$dir/$s" ]; then install -m755 "$dir/$s" "$stage/DEBIAN/$s"; fi
    done
    mkdir -p "$OUT/$NAME"
    deb="$OUT/$NAME/${NAME}_${VERSION}_${arch}.deb"
    dpkg-deb --root-owner-group -Zxz --build "$stage" "$deb" >/dev/null
    rm -rf "$stage"
    echo "built $(basename "$deb")"
  done
done
