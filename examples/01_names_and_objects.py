"""Имена — не коробки. Присваивание не копирует объект."""

from __future__ import annotations


def aliasing() -> None:
    a = [1, 2]
    b = a
    b.append(3)
    assert a is b
    assert a == [1, 2, 3]


def assignment_rebinds() -> None:
    a = [1]
    b = a
    a = [2]
    assert b == [1]
    assert a == [2]
    assert a is not b


def mutable_default_is_one_object() -> None:
    def add(item: int, bucket: list[int] | None = None) -> list[int]:
        if bucket is None:
            bucket = []
        bucket.append(item)
        return bucket

    assert add(1) == [1]
    assert add(2) == [2]

    def broken(item: int, bucket: list[int] = []) -> list[int]:
        bucket.append(item)
        return bucket

    broken.__defaults__[0].clear()  # type: ignore[index]
    assert broken(1) == [1]
    assert broken(2) == [1, 2]
    assert broken.__defaults__[0] is broken(3)  # same list object


def call_by_object_sharing() -> None:
    def bump_int(n: int) -> None:
        n += 1

    def bump_list(xs: list[int]) -> None:
        xs.append(9)

    x = 1
    bump_int(x)
    assert x == 1

    ys = [1]
    bump_list(ys)
    assert ys == [1, 9]


def none_is_singleton() -> None:
    assert (None is None) is True
    x = None
    assert x is None


if __name__ == "__main__":
    aliasing()
    assignment_rebinds()
    mutable_default_is_one_object()
    call_by_object_sharing()
    none_is_singleton()
    print("01_names_and_objects: ok")
