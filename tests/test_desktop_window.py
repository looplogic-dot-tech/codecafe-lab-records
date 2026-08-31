import os
import sys
import types
import unittest
from unittest import mock

import desktop_window


class FakeWindow:
    def __init__(self):
        self.destroyed = False

    def destroy(self):
        self.destroyed = True

    def get_current_url(self):
        return "http://127.0.0.1:43210/"

    def create_file_dialog(self, dialog_type, **kwargs):
        return ("/tmp/Synthetic Labs",)


class DesktopWindowTest(unittest.TestCase):
    def test_platform_data_directory_override(self):
        with mock.patch.dict(os.environ, {"CODECAFE_LAB_DATA": "/tmp/codecafe-test-data"}, clear=False):
            self.assertEqual(str(desktop_window.platform_data_dir()), "/tmp/codecafe-test-data")

    def test_native_api_closes_attached_window(self):
        window = FakeWindow()
        api = desktop_window.NativeApi()
        api.attach(window)
        with mock.patch.object(desktop_window.threading, "Timer") as timer:
            response = api.close_app()
            self.assertTrue(response["ok"])
            callback = timer.call_args.args[1]
            callback()
        self.assertTrue(window.destroyed)

    def test_native_api_selects_pdf_folder(self):
        window = FakeWindow()
        api = desktop_window.NativeApi()
        api.attach(window)
        fake_webview = types.ModuleType("webview")
        class FileDialog:
            FOLDER = "folder"
        fake_webview.FileDialog = FileDialog
        with mock.patch.dict(sys.modules, {"webview": fake_webview}):
            result = api.select_pdf_folder()
        self.assertTrue(result["ok"])
        self.assertFalse(result["cancelled"])
        self.assertEqual(result["folder"], "/tmp/Synthetic Labs")

    def test_run_desktop_passes_flask_wsgi_app_to_webview(self):
        calls = []
        window = FakeWindow()

        fake_webview = types.ModuleType("webview")

        def create_window(*args, **kwargs):
            calls.append(("create_window", args, kwargs))
            return window

        def start(**kwargs):
            calls.append(("start", kwargs))

        fake_webview.create_window = create_window
        fake_webview.start = start

        class FakeFlaskApp:
            debug = True

        fake_core = types.ModuleType("app")
        fake_core.app = FakeFlaskApp()
        fake_core.init_db = lambda: calls.append(("init_db",))

        with mock.patch.dict(sys.modules, {"webview": fake_webview, "app": fake_core}):
            rc = desktop_window.run_desktop(debug=False)

        self.assertEqual(rc, 0)
        self.assertEqual(calls[0], ("init_db",))
        self.assertEqual(calls[1][0], "create_window")
        self.assertEqual(calls[1][1][0], "Registros Clínicos — by CodeCafe")
        self.assertIs(calls[1][1][1], fake_core.app)
        self.assertTrue(calls[1][2]["confirm_close"])
        self.assertEqual(calls[-1], ("start", {"debug": False}))


if __name__ == "__main__":
    unittest.main()
