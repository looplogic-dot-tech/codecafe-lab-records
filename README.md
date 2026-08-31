# Registros Clínicos by CodeCafe — Python v0.6.11 Desktop Window


## v0.6.6 uroculture robustness + folder/bulk import

- Uroculture/culture results are recovered across all available PDF text layouts, not only the layout selected for numeric chemistry tables.
- Multiline qualitative values such as `CULTIVO → Sin / desarrollo / microbiano` are reconstructed without inventing missing data.
- Prefix duplicates from different PDF engines (for example `Sin desarrollo` versus `Sin desarrollo microbiano`) are collapsed to the more specific source-supported value.
- Desktop mode adds a native **Select folder / Seleccionar carpeta** Bulk importer with optional subfolders, duplicate detection, patient-compatibility review, per-document result counts, and selection before saving.
- Browser/developer mode still supports selecting multiple PDFs even though native folder selection is desktop-only.
- The macOS compiled-app self-test now includes an uroculture fixture in addition to embedded-text and scanned chemistry PDFs.

## v0.6.5 structured microbiology / culture results

Culture and microbiology reports can contain valid qualitative findings without numeric reference columns. v0.6.5 recognizes these results (for example, `CULTIVO → Sin desarrollo microbiano`), preserves them as structured observations, and keeps them linked to the original report. It also supports organism/isolate labels and colony counts such as UFC/mL without inventing missing reference ranges.

The cross-platform and self-contained OCR behavior from v0.6.4 is preserved.

## v0.6.4 self-contained macOS PDF extraction

This release fixes the compiled macOS `.app` path where scanned PDFs and some embedded-text PDFs could produce `0 results` even though Linux parsed them correctly. English/Spanish OCR language data is now part of the source and always bundled into the desktop app. The macOS builder also tests both embedded-text and scanned PDF extraction **inside the compiled `.app`** before it creates the installer.

## v0.6.3 cross-platform PDF parser parity

This release fixes a macOS regression where a PDF could expose header metadata but yield zero structured results even though the same document parsed correctly on Linux. The importer now retries independent layout engines when the primary text layout yields no usable rows, reconstructs table columns from PyMuPDF word coordinates, accepts split table headers, supports both unit/reference column orders, and uses OCR only as a last structural fallback.

Exact runtime dependency versions remain pinned in `requirements.txt` for Linux, macOS, and Windows.


## Purpose

CodeCafe Lab Records remains primarily a family clinical-laboratory record organizer. It preserves original reports, extracts and normalizes laboratory results, tracks trends and daily measurements, and keeps other clinical documents easy to find.


## v0.6.1 integrated PDF viewer

The normal desktop interface now renders preserved PDF pages **inside CodeCafe Lab Records** using PyMuPDF-generated page images. This avoids system/browser PDF plug-ins that may open an external browser from pywebview. The exact original PDF remains preserved and linked to the record; opening it externally is an Advanced Mode action only.

## v0.6 desktop change

The default interface is now a dedicated desktop window powered by **pywebview**. The existing Flask/HTML/CSS/JavaScript application is reused inside that window; the user no longer needs to understand browsers, localhost, ports or server processes. Closing the desktop window closes the application.

A browser mode remains available only as an advanced/developer fallback.

## Permanent authorship

The application includes a visible **Configuración / Settings → Acerca de / About** panel:

- Developed by **Jaime Sánchez Sáenz**
- **CodeCafe.io**
- **contacto@codecafe.io**
- © 2026 Jaime Sánchez Sáenz

This attribution is a permanent distribution requirement.

## Run from source

Linux:
```bash
./setup_linux.sh
./run_linux.sh
```

macOS:
```bash
./setup_macos.sh
./run_macos.sh
```

Windows:
```bat
setup_windows.bat
run_windows.bat
```

### Browser fallback

Linux/macOS include `run_browser_*.sh`; Windows includes `run_browser_windows.bat`. This is for advanced diagnostics and is not the normal family-facing interface.

## Build end-user distributions

Linux:
```bash
./build_linux.sh
```
Produces `dist/CodeCafe_Lab_Records_Linux_Installer.tar.gz`.

macOS:
```bash
./build_macos.sh
```
Produces an `.app` and `dist/CodeCafe_Lab_Records_macOS_Installer.zip`. Build must run on macOS.

Windows:
```bat
build_windows.bat
```
Produces `dist\CodeCafe_Lab_Records_Windows_Installer.zip`. Build must run on Windows.

## Data locations

The application data is deliberately separate from the installed program so upgrades do not erase medical records.

- Linux: `~/.local/share/CodeCafe Lab Records/`
- macOS: `~/Library/Application Support/CodeCafe Lab Records/`
- Windows: `%APPDATA%\CodeCafe Lab Records\`

## Offline caches

Use the `download_packages_*` helper on each target platform to populate `packages/<platform>/`. The source package intentionally does not mix packages across operating systems or architectures.

## OCR

Native-text PDFs work without Tesseract. Scanned/image PDFs require local Tesseract OCR. The existing OCR helper scripts remain included.

## Privacy

Real family PDFs, databases, profile data, credentials and backups must never be committed into the source package.

## Native Linux packages (.deb / .rpm) — v0.6.8

For a family/friend-friendly installation, build a native package instead of sharing the source folder:

```bash
./build_native_package.sh
```

On Debian/Ubuntu-family systems this produces a `.deb`; on Fedora/RHEL/CentOS-family systems it produces an `.rpm`.
See `PACKAGING_LINUX.md` for details and the important rule that each package must be built on the matching Linux family.


## v0.6.11 native printing

On Linux Desktop Window mode, the Doctor View print button now opens the native Qt/CUPS print dialog.
