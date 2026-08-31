#!/usr/bin/env bash
cd "$(dirname "$0")"
./run_macos.sh
status=$?
echo
read -r -p "Application stopped. Press Return to close this window." _
exit $status
