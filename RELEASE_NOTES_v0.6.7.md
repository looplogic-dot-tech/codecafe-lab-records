# CodeCafe Lab Records v0.6.7 — Native Linux Packaging

- Added native `.deb` builder for Debian/Ubuntu-family systems.
- Added native `.rpm` builder for Fedora/RHEL/CentOS/Rocky/Alma families.
- Added auto-detecting `build_native_package.sh`.
- Native packages install the desktop application, launcher, menu entry, icon and authorship documentation.
- Personal clinical data remains outside the application package and survives normal upgrades/removal of the program files.
- Builders refuse to package a PyInstaller payload on the wrong Linux distribution family, reducing accidental glibc/system-library incompatibility.
