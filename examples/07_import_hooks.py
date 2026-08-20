"""Импорт идёт через sys.meta_path. Можно поставить свой finder (как pytest)."""

from __future__ import annotations

import importlib.abc
import importlib.machinery
import sys
import types
from typing import Sequence


class ConstantLoader(importlib.abc.Loader):
    def create_module(self, spec: importlib.machinery.ModuleSpec) -> types.ModuleType | None:
        return None

    def exec_module(self, module: types.ModuleType) -> None:
        module.ANSWER = 42  # type: ignore[attr-defined]


class ConstantFinder(importlib.abc.MetaPathFinder):
    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None,
        target: types.ModuleType | None = None,
    ) -> importlib.machinery.ModuleSpec | None:
        if fullname == "synthetic_const_module":
            return importlib.machinery.ModuleSpec(
                fullname, ConstantLoader(), origin="synthetic"
            )
        return None


def import_via_custom_finder() -> None:
    finder = ConstantFinder()
    sys.meta_path.insert(0, finder)
    try:
        sys.modules.pop("synthetic_const_module", None)
        mod = __import__("synthetic_const_module")
        assert mod.ANSWER == 42
        assert "synthetic_const_module" in sys.modules
    finally:
        sys.meta_path.remove(finder)
        sys.modules.pop("synthetic_const_module", None)


def cached_import_returns_same_object() -> None:
    import json

    again = __import__("json")
    assert json is again


if __name__ == "__main__":
    import_via_custom_finder()
    cached_import_returns_same_object()
    print("07_import_hooks: ok")
