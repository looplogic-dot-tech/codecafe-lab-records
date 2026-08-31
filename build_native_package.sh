#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
[[ -r /etc/os-release ]] || { echo "Cannot identify this Linux distribution." >&2; exit 69; }
. /etc/os-release
family=" ${ID:-} ${ID_LIKE:-} "
if [[ "$family" == *" debian "* || "$family" == *" ubuntu "* ]]; then
  exec ./build_deb.sh "$@"
elif [[ "$family" == *" fedora "* || "$family" == *" rhel "* || "$family" == *" centos "* ]]; then
  exec ./build_rpm.sh "$@"
else
  echo "Unsupported package family: ${PRETTY_NAME:-unknown}" >&2
  echo "Use build_linux.sh for the generic installer, or build on a Debian/RPM-family system." >&2
  exit 65
fi
