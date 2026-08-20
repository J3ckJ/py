"""Аннотации не проверяются интерпретатором. Проверяет тот, кто их читает."""

from __future__ import annotations


def tagged(x: int) -> str:
    return f"{x}"


def interpreter_does_not_care() -> None:
    # This is allowed at runtime. A type checker would complain.
    assert tagged("not-an-int") == "not-an-int"  # type: ignore[arg-type]


def annotations_are_data() -> None:
    hints = tagged.__annotations__
    # With from __future__ import annotations these are strings.
    assert "x" in hints
    assert "return" in hints


if __name__ == "__main__":
    interpreter_does_not_care()
    annotations_are_data()
    print("08_typing_is_not_enforced: ok")
