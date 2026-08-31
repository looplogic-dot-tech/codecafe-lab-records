#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"

APP_ID="codecafe-lab-records"
APP_NAME="Registros Clínicos"
PKG_VERSION="${CODECAFE_PACKAGE_VERSION:-0.6.11}"
MAINTAINER="Jaime Sánchez Sáenz <contacto@codecafe.io>"

usage() {
  cat <<USAGE
Usage: ./build_deb.sh [--reuse-build]

Builds a native .deb for Debian/Ubuntu-family Linux systems.
By default it first runs ./build_linux.sh. Use --reuse-build only when
./dist/codecafe-lab-records already contains a build created on THIS Debian/
Ubuntu-family system and architecture.
USAGE
}

REUSE=0
case "${1:-}" in
  "") ;;
  --reuse-build) REUSE=1 ;;
  -h|--help) usage; exit 0 ;;
  *) usage >&2; exit 64 ;;
esac

[[ "$(uname -s)" == "Linux" ]] || { echo "DEB packages must be built on Linux." >&2; exit 69; }
if [[ -r /etc/os-release ]]; then
  . /etc/os-release
  family=" ${ID:-} ${ID_LIKE:-} "
  if [[ "$family" != *" debian "* && "$family" != *" ubuntu "* ]]; then
    echo "Refusing to build a DEB from a non-Debian-family host (${PRETTY_NAME:-unknown})." >&2
    echo "Build the DEB on Debian/Ubuntu/Mint so the bundled Linux binary targets that family." >&2
    exit 65
  fi
fi
command -v dpkg-deb >/dev/null 2>&1 || { echo "dpkg-deb is required (normally provided by dpkg)." >&2; exit 69; }
command -v dpkg >/dev/null 2>&1 || { echo "dpkg is required." >&2; exit 69; }

if (( ! REUSE )); then
  ./build_linux.sh
fi
APP_DIR="dist/$APP_ID"
[[ -x "$APP_DIR/$APP_ID" ]] || { echo "Missing Linux build: $APP_DIR/$APP_ID" >&2; exit 70; }

ARCH="$(dpkg --print-architecture)"
OUTDIR="$PWD/dist/packages"
STAGE="$PWD/build/deb-root"
rm -rf "$STAGE"
mkdir -p \
  "$STAGE/DEBIAN" \
  "$STAGE/opt/$APP_ID" \
  "$STAGE/usr/bin" \
  "$STAGE/usr/share/applications" \
  "$STAGE/usr/share/icons/hicolor/scalable/apps" \
  "$STAGE/usr/share/doc/$APP_ID"
chmod 0755 "$STAGE/DEBIAN" "$STAGE/opt" "$STAGE/usr"
chmod g-s "$STAGE/DEBIAN" "$STAGE/opt" "$STAGE/usr" 2>/dev/null || true

cp -a "$APP_DIR/." "$STAGE/opt/$APP_ID/"
cp AUTHORSHIP.md "$STAGE/usr/share/doc/$APP_ID/AUTHORSHIP.md"
[[ -f README.md ]] && cp README.md "$STAGE/usr/share/doc/$APP_ID/README.md"

cat > "$STAGE/usr/bin/$APP_ID" <<'WRAPPER'
#!/usr/bin/env bash
exec /opt/codecafe-lab-records/codecafe-lab-records "$@"
WRAPPER
chmod 755 "$STAGE/usr/bin/$APP_ID"

cat > "$STAGE/usr/share/applications/$APP_ID.desktop" <<'DESKTOP'
[Desktop Entry]
Type=Application
Version=1.0
Name=Clinical Records
Name[es]=Registros Clínicos
Comment=Clinical laboratory records organizer
Comment[es]=Organizador de análisis y registros clínicos
Exec=/usr/bin/codecafe-lab-records
Icon=codecafe-lab-records
Terminal=false
Categories=Office;Science;Utility;
StartupNotify=true
DESKTOP

cat > "$STAGE/usr/share/icons/hicolor/scalable/apps/$APP_ID.svg" <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">
  <rect x="8" y="8" width="112" height="112" rx="26" fill="#2557a7"/>
  <path d="M39 35h50v11H39zm0 23h50v11H39zm0 23h32v11H39z" fill="white"/>
  <circle cx="91" cy="87" r="18" fill="#ffffff" opacity=".96"/>
  <path d="M91 76v22M80 87h22" stroke="#2557a7" stroke-width="7" stroke-linecap="round"/>
</svg>
SVG

INSTALLED_SIZE="$(du -sk "$STAGE/opt/$APP_ID" | awk '{print $1}')"
cat > "$STAGE/DEBIAN/control" <<CONTROL
Package: $APP_ID
Version: $PKG_VERSION
Section: science
Priority: optional
Architecture: $ARCH
Maintainer: $MAINTAINER
Installed-Size: $INSTALLED_SIZE
Depends: libgl1, libdbus-1-3, libfontconfig1, libxkbcommon-x11-0, libxcb-cursor0, libxcb-icccm4, libxcb-image0, libxcb-keysyms1, libxcb-render-util0
Recommends: tesseract-ocr, tesseract-ocr-spa, tesseract-ocr-eng
Description: Registros Clínicos by CodeCafe
 Registros Clínicos organizes laboratory PDFs, structured results, trends,
 daily measurements including blood pressure, glucose and weight, and related clinical documents in an elder-friendly desktop
 interface. Original source documents and personal clinical data are kept in the
 user's profile and are not removed during application upgrades.
CONTROL

cat > "$STAGE/DEBIAN/postinst" <<'POSTINST'
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database /usr/share/applications >/dev/null 2>&1 || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor >/dev/null 2>&1 || true
fi
exit 0
POSTINST
chmod 755 "$STAGE/DEBIAN/postinst"

cat > "$STAGE/DEBIAN/postrm" <<'POSTRM'
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database /usr/share/applications >/dev/null 2>&1 || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor >/dev/null 2>&1 || true
fi
exit 0
POSTRM
chmod 755 "$STAGE/DEBIAN/postrm"

mkdir -p "$OUTDIR"
OUT="$OUTDIR/${APP_ID}_${PKG_VERSION}_${ARCH}.deb"
rm -f "$OUT"
dpkg-deb --build --root-owner-group "$STAGE" "$OUT"

echo
echo "DEB created: $OUT"
echo "Install test: sudo apt install ./$(basename "$OUT")"
echo "End users can normally double-click the .deb in their graphical file manager/software installer."
