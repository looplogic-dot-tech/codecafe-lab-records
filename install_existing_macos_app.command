#!/bin/bash
set -Eeuo pipefail
APP_NAME="Registros Clínicos.app"
DEST="/Applications/$APP_NAME"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE=""
for candidate in "$SCRIPT_DIR/$APP_NAME" "$SCRIPT_DIR/dist/$APP_NAME" "$PWD/$APP_NAME" "$PWD/dist/$APP_NAME"; do
  if [[ -d "$candidate" ]]; then SOURCE="$candidate"; break; fi
done
if [[ -z "$SOURCE" ]]; then
  SOURCE="$(osascript <<'APPLESCRIPT'
try
  set pickedApp to choose application with prompt "Select Registros Clínicos.app"
  return POSIX path of pickedApp
on error number -128
  return ""
end try
APPLESCRIPT
)"
fi
[[ -n "$SOURCE" && -d "$SOURCE" && -f "$SOURCE/Contents/Info.plist" ]] || { echo "No valid Registros Clínicos.app selected." >&2; read -r -p "Press Enter to close..."; exit 1; }

echo "Installing existing build to /Applications..."
osascript - "$SOURCE" "$DEST" <<'APPLESCRIPT'
on run argv
  set sourcePath to item 1 of argv
  set destPath to item 2 of argv
  set cmd to "/bin/rm -rf " & quoted form of destPath & " && /usr/bin/ditto " & quoted form of sourcePath & " " & quoted form of destPath
  do shell script cmd with administrator privileges
end run
APPLESCRIPT
[[ -d "$DEST" && -f "$DEST/Contents/Info.plist" ]] || { echo "Installation validation failed." >&2; read -r -p "Press Enter to close..."; exit 2; }
touch "$DEST" 2>/dev/null || true
echo "✓ Installed. The source/build folder may now be deleted after confirming the app opens."
open "$DEST"
sleep 2
