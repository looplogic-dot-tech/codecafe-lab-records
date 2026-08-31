#!/usr/bin/env bash
set -Eeuo pipefail

if command -v tesseract >/dev/null 2>&1; then
  echo "Tesseract already installed: $(tesseract --version 2>/dev/null | head -n1)"
else
  if ! command -v dnf >/dev/null 2>&1; then
    echo "Tesseract is not installed and this helper currently supports DNF-based Linux systems." >&2
    echo "Install Tesseract OCR with Spanish and English language data, then rerun ./setup_linux.sh." >&2
    exit 69
  fi
  echo "Installing Tesseract OCR..."
  sudo dnf install -y tesseract
fi

if tesseract --list-langs 2>/dev/null | grep -qx 'spa'; then
  echo "Spanish OCR language data: available"
else
  echo "Spanish OCR language data is missing. Trying common DNF package names..."
  installed=0
  for pkg in tesseract-langpack-spa tesseract-langpack-spa.noarch; do
    if sudo dnf -q list --available "$pkg" >/dev/null 2>&1; then
      sudo dnf install -y "$pkg"
      installed=1
      break
    fi
  done
  if (( ! installed )); then
    echo "Could not locate a Spanish Tesseract language package automatically." >&2
    echo "OCR will still try English, but Spanish medical reports will be less accurate." >&2
  fi
fi

printf '\nAvailable OCR languages:\n'
tesseract --list-langs 2>/dev/null || true
