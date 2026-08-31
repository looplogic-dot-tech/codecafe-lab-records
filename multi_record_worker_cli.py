from __future__ import annotations

import sys

from multi_record_ocr import worker_task_main


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: multi_record_worker_cli.py TASK.json OUTPUT.jsonl")
    raise SystemExit(worker_task_main(sys.argv[1], sys.argv[2]))
