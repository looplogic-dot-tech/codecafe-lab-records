#!/bin/bash
cd "$(dirname "$0")"
./build_macos.sh
status=$?
echo
if [[ $status -eq 0 ]]; then
  echo "Build finished. Finder will open the dist folder."
  open dist
else
  echo "Build stopped with status $status. Read the message above."
fi
echo
read -n 1 -s -r -p "Press any key to close this window..."
exit $status
