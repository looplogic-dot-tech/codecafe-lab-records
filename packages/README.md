# Offline dependency caches

This source tree keeps platform-specific package caches, following the same reproducible-build philosophy used for CodeCafe Atlas.

- `packages/linux/` — populate on the target Linux architecture with `./download_packages_linux.sh`
- `packages/macos/` — populate on the target Mac architecture with `./download_packages_macos.sh`
- `packages/windows/` — populate on Windows with `download_packages_windows.bat`

The download helpers cache both runtime dependencies and build dependencies (PyInstaller). Setup/build scripts prefer the local cache when it is populated. Do not mix wheels from different operating systems or CPU architectures.
