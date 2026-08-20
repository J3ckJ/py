# CPython как проект: куда смотреть, не читая 2 миллиона строк

Полный разбор CPython — не цель этого репозитория. Ниже — карта, достаточная, чтобы связать главы runtime с деревом https://github.com/python/cpython.

## Карта каталогов

| Путь | Что там |
| --- | --- |
| `Python/` | eval loop, compile, import, GIL, jit.c, ceval |
| `Objects/` | типы: list, dict, typeobject, funcobject |
| `Include/` | публичные заголовки C API |
| `Lib/` | стандартная библиотека на Python (читается легче C) |
| `Modules/` | builtin extensions (`_asyncio`, `posix`, …) |
| `InternalDocs/` | JIT, QSBR, GC — человеческий текст |
| `Doc/` | Language Reference sources |
| `Tools/jit/` | генерация stencils |

## Что менялось на глазах (3.13–3.15)

- Специализирующий интерпретатор + uops + experimental JIT (`InternalDocs/jit.md`: stencils из `bytecodes.c` через LLVM).
- Free-threaded layout объекта, biased refcount, mimalloc, QSBR (`Doc/howto/free-threading-python.rst`).
- Incremental GC (3.14).
- `concurrent.interpreters` (3.14).
- Deferred annotations, t-strings (3.14).
- `lazy import`, `frozendict`, `sentinel`, UTF-8 default, Tachyon profiler (3.15).

## Как читать изменение языка

Не с коммита в `ceval.c`. С PEP → `Doc/whatsnew` → тесты в `Lib/test` → затем C. Тесты — спецификация поведения, которую core devs боятся ломать.

## Связь с экосистемой

Pydantic-core, numpy, cryptography — живут в слотах C API. Free-threading заставляет их объявлять `Py_mod_gil`. Когда «Python 3.14t медленный на моём приложении», часто виноват не eval loop, а включившийся обратно GIL после импорта одного колеса.

Дальше, если пойдёте в CPython всерьёз: книга «CPython internals» устаревает каждый релиз; якорь — `InternalDocs/` и What's New текущего.
