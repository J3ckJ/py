"""Запуск всех примеров без pytest (достаточно stdlib)."""

from __future__ import annotations

import pathlib
import runpy
import sys

ROOT = pathlib.Path(__file__).resolve().parent
SKIP = {"run_all.py"}


def main() -> int:
    failed = 0
    for path in sorted(ROOT.glob("*.py")):
        if path.name in SKIP or path.name.startswith("test_"):
            continue
        print(f">>> {path.name}")
        try:
            runpy.run_path(str(path), run_name="__main__")
        except Exception as exc:
            failed += 1
            print(f"FAIL {path.name}: {exc!r}")
    if failed:
        print(f"{failed} example(s) failed")
        return 1
    print("all examples passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
