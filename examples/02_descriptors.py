"""Дескриптор хранит имя на классе и значение в __dict__ экземпляра."""

from __future__ import annotations


class BoundedInt:
    def __init__(self, min_value: int, max_value: int) -> None:
        self.min_value = min_value
        self.max_value = max_value
        self.public_name = ""
        self.private_name = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, obj: object | None, owner: type | None = None) -> int | BoundedInt:
        if obj is None:
            return self
        return getattr(obj, self.private_name)

    def __set__(self, obj: object, value: object) -> None:
        if not isinstance(value, int):
            raise TypeError(f"{self.public_name} must be int")
        if not self.min_value <= value <= self.max_value:
            raise ValueError(
                f"{self.public_name}={value} not in "
                f"[{self.min_value}, {self.max_value}]"
            )
        setattr(obj, self.private_name, value)


class Player:
    hp = BoundedInt(0, 100)

    def __init__(self, hp: int) -> None:
        self.hp = hp

    def ping(self) -> str:
        return "pong"


def methods_are_descriptors() -> None:
    p = Player(10)
    bound = p.ping
    assert bound.__func__ is Player.ping  # type: ignore[attr-defined]
    assert bound() == "pong"


def per_instance_storage() -> None:
    a = Player(10)
    b = Player(20)
    assert a.hp == 10
    assert b.hp == 20
    a.hp = 50
    assert b.hp == 20
    try:
        a.hp = 500
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")


if __name__ == "__main__":
    methods_are_descriptors()
    per_instance_storage()
    print("02_descriptors: ok")
