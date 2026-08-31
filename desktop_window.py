from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import webbrowser
from pathlib import Path
from typing import Any

DATA_APP_NAME = "CodeCafe Lab Records"  # keep legacy data path for upgrade compatibility
DISPLAY_NAME = "Registros Clínicos"
APP_NAME = DISPLAY_NAME
APP_VERSION = "0.6.12-multi-record-adaptive-ocr"


def platform_data_dir() -> Path:
    override = os.environ.get("CODECAFE_LAB_DATA")
    if override:
        return Path(override).expanduser().resolve()

    home = Path.home()
    if sys.platform == "darwin":
        return (home / "Library" / "Application Support" / DATA_APP_NAME).resolve()
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
        return (base / DATA_APP_NAME).resolve()

    xdg = Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share"))
    return (xdg / DATA_APP_NAME).resolve()


_ACTIVE_QT_PRINT_JOBS: list[tuple[Any, Any]] = []


def _enable_linux_qt_printing(window: Any) -> dict[str, object]:
    """Wire JavaScript window.print() to the native Qt/CUPS print dialog."""
    if not sys.platform.startswith("linux"):
        return {"ok": True, "enabled": False, "reason": "not-linux"}

    try:
        native = window.native
        view = native.webview
        page = view.page()
    except Exception as exc:
        return {"ok": False, "enabled": False, "error": f"native-webview: {exc}"}

    try:
        from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
        from PyQt6.QtWidgets import QDialog
    except Exception as exc:
        return {"ok": False, "enabled": False, "error": f"qt-print-support: {exc}"}

    if getattr(window, "_codecafe_print_handler_installed", False):
        return {"ok": True, "enabled": True, "alreadyInstalled": True}

    def handle_print_request() -> None:
        try:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            dialog = QPrintDialog(printer, native)
            dialog.setWindowTitle(f"{DISPLAY_NAME} — by CodeCafe")
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return

            def finished(_success: bool) -> None:
                try:
                    view.printFinished.disconnect(finished)
                except Exception:
                    pass
                try:
                    _ACTIVE_QT_PRINT_JOBS.remove((printer, finished))
                except ValueError:
                    pass

            _ACTIVE_QT_PRINT_JOBS.append((printer, finished))
            view.printFinished.connect(finished)
            view.print(printer)
        except Exception as exc:
            try:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(native, DISPLAY_NAME, f"Printing failed:\n{exc}")
            except Exception:
                print(f"{DISPLAY_NAME}: printing failed: {exc}", file=sys.stderr)

    page.printRequested.connect(handle_print_request)
    setattr(window, "_codecafe_print_handler_installed", True)
    setattr(window, "_codecafe_print_handler", handle_print_request)
    return {"ok": True, "enabled": True}


class NativeApi:
    """Small native bridge exposed to the HTML/JavaScript interface."""

    def __init__(self) -> None:
        self.window: Any | None = None

    def attach(self, window: Any) -> None:
        self.window = window

    def close_app(self) -> dict[str, bool]:
        window = self.window
        if window is not None:
            threading.Timer(0.08, window.destroy).start()
        return {"ok": True}

    def open_in_browser(self) -> dict[str, object]:
        window = self.window
        if window is None:
            return {"ok": False}
        try:
            url = window.get_current_url()
        except Exception:
            url = ""
        if not url:
            return {"ok": False}
        return {"ok": bool(webbrowser.open(url, new=1)), "url": url}

    def select_pdf_folder(self) -> dict[str, object]:
        window = self.window
        if window is None:
            return {"ok": False, "cancelled": True}
        try:
            import webview
            selected = window.create_file_dialog(webview.FileDialog.FOLDER)
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
        if not selected:
            return {"ok": True, "cancelled": True}
        return {"ok": True, "cancelled": False, "folder": str(selected[0])}

    def environment(self) -> dict[str, object]:
        return {"desktop": True, "version": APP_VERSION, "platform": sys.platform}


def run_desktop(*, debug: bool = False) -> int:
    os.environ.setdefault("CODECAFE_LAB_DATA", str(platform_data_dir()))
    os.environ["CODECAFE_DESKTOP_MODE"] = "1"

    # v0.6.12 layers adaptive multi-record OCR over the stable Flask application.
    import app_v612 as core
    import webview

    core.init_db()
    core.app.debug = False

    api = NativeApi()
    window = webview.create_window(
        f"{DISPLAY_NAME} — by CodeCafe",
        core.app,
        js_api=api,
        width=1360,
        height=860,
        min_size=(960, 680),
        resizable=True,
        confirm_close=True,
        background_color="#f4f7fb",
        text_select=True,
    )
    api.attach(window)

    if sys.platform.startswith("linux") and getattr(window, "events", None) is not None:
        shown_event = getattr(window.events, "shown", None)
        if shown_event is not None:
            shown_event += lambda: _enable_linux_qt_printing(window)

    webview.start(debug=debug)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"{DISPLAY_NAME} — by CodeCafe {APP_VERSION}")
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Developer fallback: run the traditional browser/server interface.",
    )
    parser.add_argument("--port", type=int, default=5000, help="Browser-mode port.")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument(
        "--diagnose-pdf",
        metavar="PDF",
        help="Advanced diagnostic: parse one PDF without opening the desktop window.",
    )
    parser.add_argument(
        "--diagnostic-output",
        metavar="FILE",
        help="Write --diagnose-pdf JSON to this file (useful for windowed macOS builds).",
    )
    # Hidden mode used by disposable OCR helpers in frozen/PyInstaller builds.
    parser.add_argument("--ocr-worker", nargs=2, metavar=("TASK", "OUTPUT"), help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.ocr_worker:
        from multi_record_ocr import worker_task_main
        return int(worker_task_main(args.ocr_worker[0], args.ocr_worker[1]))

    if args.diagnose_pdf:
        from lab_pdf_parser_v612 import parse_lab_pdf
        from lab_pdf_parser import ocr_status

        pdf_path = Path(args.diagnose_pdf).expanduser().resolve()
        result = parse_lab_pdf(pdf_path.read_bytes())
        summary = {
            "file": str(pdf_path),
            "ok": result.get("ok"),
            "engine": result.get("engine"),
            "page_count": result.get("page_count"),
            "records": len(result.get("records", [])),
            "results": len(result.get("observations", [])),
            "metadata": result.get("metadata", {}),
            "warnings": result.get("warnings", []),
            "ocr": ocr_status(),
        }
        payload = json.dumps(summary, ensure_ascii=False, indent=2)
        if args.diagnostic_output:
            Path(args.diagnostic_output).expanduser().write_text(payload + "\n", encoding="utf-8")
        else:
            print(payload)
        return 0

    if args.browser:
        os.environ.setdefault("CODECAFE_LAB_DATA", str(platform_data_dir()))
        import app_v612 as core
        core.main_with_args(host="127.0.0.1", port=args.port, debug=args.debug, open_browser=True)
        return 0
    return run_desktop(debug=args.debug)


if __name__ == "__main__":
    raise SystemExit(main())
