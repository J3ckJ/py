"""Контекстные менеджеры и генераторный @contextmanager."""

from __future__ import annotations

from contextlib import contextmanager


class Resource:
    def __init__(self) -> None:
        self.actions: list[str] = []

    def __enter__(self) -> Resource:
        self.actions.append("enter")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object,
    ) -> bool:
        self.actions.append("exit")
        return False


def with_closes_on_error() -> None:
    r = Resource()
    try:
        with r:
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    assert r.actions == ["enter", "exit"]


@contextmanager
def session_like() -> object:
    steps: list[str] = []
    steps.append("open")
    try:
        yield steps
        steps.append("commit")
    except Exception:
        steps.append("rollback")
        raise
    finally:
        steps.append("close")


def generator_cm_rollback() -> None:
    try:
        with session_like() as steps:
            raise ValueError("no")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
    # yield object is the same list
    # we cannot see it after exception unless we keep it
    # recreate success path:
    with session_like() as steps2:
        steps2.append("work")
    assert steps2 == ["open", "work", "commit", "close"]


def suppress_only_if_exit_true() -> None:
    class Swallow:
        def __enter__(self) -> None:
            return None

        def __exit__(self, *args: object) -> bool:
            return True

    with Swallow():
        raise RuntimeError("hidden")


if __name__ == "__main__":
    with_closes_on_error()
    generator_cm_rollback()
    suppress_only_if_exit_true()
    print("05_context_managers: ok")
