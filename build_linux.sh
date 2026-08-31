#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
step(){ printf '\n[%s/7] %s\n' "$1" "$2"; }

step 1 "Checking Linux environment"
[[ "$(uname -s)" == "Linux" ]] || { echo "This build must run on Linux." >&2; exit 69; }

step 2 "Preparing Python environment"
./setup_linux.sh
./validate_source.sh

step 3 "Installing build dependency"
shopt -s nullglob
cached=(packages/linux/*.whl packages/linux/*.tar.gz packages/linux/*.zip)
if ((${#cached[@]})); then
  .venv/bin/python -m pip install --disable-pip-version-check --no-index --find-links packages/linux -r requirements-build.txt
else
  .venv/bin/python -m pip install --disable-pip-version-check -r requirements-build.txt
fi

step 4 "Building standalone application"
rm -rf build dist codecafe-lab-records.spec
DATA_ARGS=()
while IFS= read -r -d '' file; do
  rel="${file#./}"; dest="$(dirname "$rel")"; DATA_ARGS+=(--add-data "$rel:$dest")
done < <(find ./templates ./static -type f -print0)
DATA_ARGS+=(--add-data "$PWD/ocr/tessdata/eng.traineddata:tessdata")
DATA_ARGS+=(--add-data "$PWD/ocr/tessdata/spa.traineddata:tessdata")
.venv/bin/python -m PyInstaller --noconfirm --clean --windowed --onedir \
  --name "codecafe-lab-records" --collect-all webview --collect-all pypdf --collect-all pymupdf "${DATA_ARGS[@]}" desktop_window.py
APP_DIR="dist/codecafe-lab-records"
[[ -x "$APP_DIR/codecafe-lab-records" ]] || { echo "Expected executable not found: $APP_DIR/codecafe-lab-records" >&2; exit 70; }

# Keep the standalone Linux build byte-for-byte as produced by PyInstaller.
# Native package builders may create staging copies for distro-specific adjustments.

step 5 "Creating self-contained Linux installer"
PKGROOT="dist/CodeCafe_Lab_Records_Linux_Installer"
rm -rf "$PKGROOT"
mkdir -p "$PKGROOT/payload" 
cp -a "$APP_DIR/." "$PKGROOT/payload/"
cp AUTHORSHIP.md "$PKGROOT/AUTHORSHIP.txt"

cat > "$PKGROOT/install.sh" <<'INSTALL'
#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
APPDIR="/opt/codecafe-lab-records"
BIN="/usr/local/bin/codecafe-lab-records"
DESKTOP="/usr/share/applications/codecafe-lab-records.desktop"

echo "Installing Registros Clínicos by CodeCafe..."
[[ -x "$ROOT/payload/codecafe-lab-records" ]] || { echo "Installer payload is incomplete." >&2; exit 70; }

sudo rm -rf "$APPDIR"
sudo install -d -m 755 "$APPDIR"
sudo cp -a "$ROOT/payload/." "$APPDIR/"
sudo chmod +x "$APPDIR/codecafe-lab-records"

sudo tee "$BIN" >/dev/null <<'WRAPPER'
#!/usr/bin/env bash
exec /opt/codecafe-lab-records/codecafe-lab-records "$@"
WRAPPER
sudo chmod 755 "$BIN"

sudo tee "$DESKTOP" >/dev/null <<'DESKTOPFILE'
[Desktop Entry]
Type=Application
Version=1.0
Name=Clinical Records
Name[es]=Registros Clínicos
Comment=Clinical records organizer by CodeCafe
Comment[es]=Registros clínicos by CodeCafe
Exec=/usr/local/bin/codecafe-lab-records
Terminal=false
Categories=Office;Utility;
StartupNotify=true
DESKTOPFILE
sudo chmod 644 "$DESKTOP"

command -v update-desktop-database >/dev/null 2>&1 && sudo update-desktop-database /usr/share/applications || true
command -v kbuildsycoca6 >/dev/null 2>&1 && kbuildsycoca6 >/dev/null 2>&1 || true
command -v kbuildsycoca5 >/dev/null 2>&1 && kbuildsycoca5 >/dev/null 2>&1 || true

if [[ ! -x "$APPDIR/codecafe-lab-records" ]]; then
  echo "Installation validation failed: executable missing." >&2
  exit 71
fi
if [[ ! -x "$BIN" ]]; then
  echo "Installation validation failed: launcher missing." >&2
  exit 72
fi

echo
echo "✓ Registros Clínicos by CodeCafe is installed."
echo "Open it from the normal application menu."
echo "The extracted installer/source folder can now be deleted."
echo "Personal medical data is stored separately under your user profile."
INSTALL
chmod +x "$PKGROOT/install.sh"

cat > "$PKGROOT/uninstall.sh" <<'UNINSTALL'
#!/usr/bin/env bash
set -Eeuo pipefail
sudo rm -rf /opt/codecafe-lab-records
sudo rm -f /usr/local/bin/codecafe-lab-records /usr/share/applications/codecafe-lab-records.desktop
command -v update-desktop-database >/dev/null 2>&1 && sudo update-desktop-database /usr/share/applications || true
command -v kbuildsycoca6 >/dev/null 2>&1 && kbuildsycoca6 >/dev/null 2>&1 || true
command -v kbuildsycoca5 >/dev/null 2>&1 && kbuildsycoca5 >/dev/null 2>&1 || true
echo "Application removed. Personal medical data was left untouched."
UNINSTALL
chmod +x "$PKGROOT/uninstall.sh"

step 6 "Packaging Linux installer"
( cd dist && tar -czf CodeCafe_Lab_Records_Linux_Installer.tar.gz CodeCafe_Lab_Records_Linux_Installer )

step 7 "Done"
printf 'Installer: %s/dist/CodeCafe_Lab_Records_Linux_Installer.tar.gz\n' "$PWD"
printf 'Extract it and run ./install.sh once. After installation the extracted folder may be deleted.\n'
