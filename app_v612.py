from __future__ import annotations

"""v0.6.12 application bridge.

This module intentionally layers the new adaptive parser on top of the validated
v0.6.11 Flask application instead of duplicating the application and database code.
All existing routes, data migrations, printing, backups and multi-laboratory logic
remain in app.py; only the parser entrypoint and visible version are replaced.
"""

import app as core
from lab_pdf_parser_v612 import parse_lab_pdf

APP_VERSION = "0.6.12-multi-record-adaptive-ocr"

# Route functions in app.py resolve these globals at request time, so replacing them
# here upgrades analysis/import flows without forking the stable application module.
core.APP_VERSION = APP_VERSION
core.parse_lab_pdf = parse_lab_pdf

app = core.app
init_db = core.init_db
main_with_args = core.main_with_args
current_state = core.current_state


def main() -> None:
    core.main()


def __getattr__(name: str):
    return getattr(core, name)


if __name__ == "__main__":
    main()
