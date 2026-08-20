"""Байткод — реализация CPython, не язык. Но его полезно увидеть."""

from __future__ import annotations

import dis
import io


def add(a: int, b: int) -> int:
    return a + b


def bytecode_contains_add() -> None:
    buf = io.StringIO()
    dis.dis(add, file=buf)
    text = buf.getvalue()
    assert "RESUME" in text or "LOAD" in text
    assert "RETURN" in text


def names_live_on_code_object() -> None:
    code = add.__code__
    assert "a" in code.co_varnames and "b" in code.co_varnames
    assert isinstance(code.co_code, bytes)
    assert len(code.co_code) > 0


if __name__ == "__main__":
    bytecode_contains_add()
    names_live_on_code_object()
    print("04_bytecode: ok")
    print("--- dis.dis(add) ---")
    dis.dis(add)
