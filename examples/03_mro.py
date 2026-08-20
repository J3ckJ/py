"""C3 MRO и кооперативный super()."""

from __future__ import annotations


class A:
    def who(self) -> list[str]:
        return ["A"]


class B(A):
    def who(self) -> list[str]:
        return ["B"] + super().who()


class C(A):
    def who(self) -> list[str]:
        return ["C"] + super().who()


class D(B, C):
    def who(self) -> list[str]:
        return ["D"] + super().who()


def diamond_mro() -> None:
    assert D.__mro__ == (D, B, C, A, object)
    assert D().who() == ["D", "B", "C", "A"]


class Left:
    def save(self, **kwargs: object) -> dict[str, object]:
        kwargs["left"] = True
        return super().save(**kwargs)  # type: ignore[misc]


class Right:
    def save(self, **kwargs: object) -> dict[str, object]:
        kwargs["right"] = True
        return dict(kwargs)


class Combined(Left, Right):
    pass


def cooperative_super() -> None:
    assert Combined().save(n=1) == {"n": 1, "left": True, "right": True}


if __name__ == "__main__":
    diamond_mro()
    cooperative_super()
    print("03_mro: ok")
