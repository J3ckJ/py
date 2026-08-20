# Типы, аннотации и runtime: две системы, один синтаксис

Python остаётся динамическим. Аннотации — *опциональный* слой. К 2026 он толстый: PEP 484 → 563/649, Protocols, TypeVarTuple, `type` aliases (PEP 695), TypedDict extras (PEP 728), TypeForm (PEP 747), disjoint bases (PEP 800). Но интерпретатор **не проверяет** `def f(x: int)` сам по себе.

## Кто проверяет типы

- **Редактор / CI**: Pyright, mypy, ty (если используете). Это отдельные программы.
- **Runtime**: Pydantic, FastAPI, `beartype`, `typeguard`, ваши `isinstance`.
- **CPython**: почти ничего, кроме того, что само использует аннотации (dataclasses, `typing.get_type_hints` / `annotationlib`).

Путать эти слои — источник ложного спокойствия. `user_id: int` в FastAPI проверяется, потому что FastAPI *читает* аннотацию и валидирует. Та же аннотация в обычной функции — комментарий для анализатора.

## Deferred annotations (3.14)

PEP 649/749: аннотации не вычисляются при `def`. `annotationlib.get_annotations(obj, format=...)`:

- `VALUE` — как раньше, может бросить `NameError`;
- `FORWARDREF` — дырки как маркеры;
- `STRING` — строки.

`from __future__ import annotations` (PEP 563) всё ещё превращает аннотации в строки и *отменяет* часть новой механики для этого модуля. В новом коде на 3.14+ future обычно не нужен.

Pydantic v2 на 3.14 должен получать типы через тот же toolchain; если модель «не видит» forward ref — смотрите `model_rebuild()` и namespace, не «кавычки вокруг типа».

## Что существует в runtime

| Конструкция | Runtime-объект? |
| --- | --- |
| `class Foo` | да, класс |
| `def f(x: int)` | функция; аннотация — отдельно |
| `list[int]` | `types.GenericAlias` |
| `X | Y` | `types.UnionType` |
| `Protocol` | класс, проверка структурная только если `@runtime_checkable` и то ограниченно |
| `TypedDict` | класс; ключи — не enforced без валидатора |
| `NewType` | функция-identity в runtime |
| `TypeVar` | объект, не значение |

`isinstance(x, list[int])` — нет (TypeError или всегда по origin в некоторых API). Для generics используйте `typing.get_origin` / `get_args` или валидатор.

## dataclasses vs pydantic vs namedtuple vs TypedDict

- `namedtuple` / `NamedTuple` — лёгкий иммутабельный кортеж с именами. Мало поведения.
- `dataclass` — генерирует `__init__`, `__repr__`, опционально `__eq__`/`__hash__`/`slots`/`kw_only`. Нет валидации типов. Стандартная библиотека. Отличный внутренний объект.
- `pydantic.BaseModel` — валидация, сериализация, JSON schema. Дороже на определение класса, дёшево на валидации (Rust). Граница системы (API, конфиг, сообщения).
- `TypedDict` — типы для обычных dict. Runtime — dict. Для JSON-объектов, которые не хотите делать классом.

Правило: внутри ядра домена — dataclass (или обычный класс). На краю — Pydantic. Не обмазывайте каждую структуру BaseModel «на всякий случай»: вы заплатите импортом, сложностью ошибок и соблазном держать бизнес-логику в validator'ах.

## `self: Self`, `type[T]`, ParamSpec

Нужны, когда пишете библиотеки (fluent API, декораторы). В прикладном коде 90% ценности — `X | None`, `list[str]`, `TypedDict`, Protocol для утиных зависимостей (репозиторий, часы, отправитель почты).

## Где это в живом коде

- FastAPI: одна `ModelField` = runtime валидация + OpenAPI. Это эталон «аннотация как контракт».
- pytest: почти не использует ваши аннотации для фикстур (имя параметра = имя фикстуры). Две разные вселенные DI.
- SQLAlchemy 2.0 Mapped[] — аннотации для declarative mapping *и* для type checkers; runtime читает их mapper'ом.

`examples/08_typing_is_not_enforced.py`.
