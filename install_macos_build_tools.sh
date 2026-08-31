#!/usr/bin/env bash
set -Eeuo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This helper is intended for macOS." >&2
  exit 69
fi

if xcode-select -p >/dev/null 2>&1 && xcrun --find lipo >/dev/null 2>&1; then
  echo "Apple Command Line Tools are already installed."
  exit 0
fi

echo "Apple Command Line Tools are required only to BUILD the standalone .app."
echo "They are NOT required on Macs that only run the finished application."
echo
echo "macOS will now offer to install them. After installation finishes, run:"
echo "  ./build_macos.sh"
echo
xcode-select --install || true
