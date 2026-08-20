# GIL и free-threaded Python

GIL (Global Interpreter Lock) — mutex, который в классической сборке CPython держит один поток, исполняющий байткод. Это не часть языка. Это 30 лет инженерного компромисса: простой refcount + не надо делать каждый `list.append` lock-free.

## Что GIL даёт и что забирает

Даёт: простую модель памяти для C-расширений, дешёвый single-thread, предсказуемые гонки *внутри* одного объекта stdlib (на практике — «почти безопасно мутировать dict из одного потока, пока другой только читает» — это всё равно не контракт).

Забирает: CPU-параллелизм на потоках. `threading` отлично прячет latency I/O (GIL отпускается на I/O, в C-расширениях на длинных вычислениях, если автор сделал `Py_BEGIN_ALLOW_THREADS`). Для CPU-bound Python-кода потоки **не ускоряют** классический CPython. Отсюда multiprocessing, subprocess, и «вынеси в Rust/C/numpy».

## Обходные пути, которые никуда не делись

| Задача | Инструмент |
| --- | --- |
| Много I/O | `threading`, `asyncio`, `httpx.AsyncClient` |
| Много CPU на чистом Python | `multiprocessing`, отдельные процессы, или 3.14t |
| Много CPU на массивах | numpy/polars/pyarrow — GIL часто отпущен |
| Изоляция + своя память | процессы |
| Акцент на latency одного запроса | asyncio, не 200 потоков |

`concurrent.futures.ThreadPoolExecutor` и `ProcessPoolExecutor` — правильные фасады. Не собирайте пулы руками, пока не нужно.

## PEP 703 → PEP 779: GIL стал опциональным

- **3.13**: экспериментальная сборка `--disable-gil`.
- **3.14**: free-threaded build **официально поддержан**, но не default (фаза II). Бинарь с суффиксом `t`: `python3.14t`.
- Дальше по дорожной карте: сначала GIL выключается флажком в одной ABI, затем default off. Это годы, не «уже в 3.15».

Проверки:

```python
import sys, sysconfig
sysconfig.get_config_var("Py_GIL_DISABLED")  # 1 если сборка free-threaded
sys._is_gil_enabled()  # фактически включён ли сейчас
```

Импорт неподготовленного C-extension может **включить GIL обратно**. Плюс `PYTHON_GIL=1` / `-X gil=1`.

## Цена free-threading

Документация 3.14 честна:

- Single-thread overhead порядка единиц процентов (зависит от платформы; на pyperformance ~1% aarch64 macOS … ~8% x86-64 Linux).
- Больше память: другой заголовок объекта, mimalloc вместо pymalloc, QSBR откладывает free, immortal interned strings, biased / deferred / per-thread refcount.
- `sys.intern` делает строку бессмертной до конца интерпретатора.
- Итераторы и `frame.f_locals` чужого потока — не трогать.
- Встроенные `dict`/`list`/`set` имеют внутренние замки, поведение «похоже на GIL», но **не гарантия языка**. Для инвариантов приложения — свой `threading.Lock`.

## Что это меняет в вашем коде 2026 года

1. Не переписывайте всё на потоки. Сначала измерьте: ваш bottleneck — GIL или диск/сеть/SQL?
2. Если CPU-bound и данные плохо pickle'ятся — попробуйте 3.14t на нагрузочном стенде. Проверьте научный стек на compatibility tracker.
3. Глобальные мутабельные кеши без замка, которые «работали» из-за GIL, станут багами. Это главный скрытый долг.
4. `contextvars` в новых потоках на 3.14t копируются по умолчанию.

## asyncio и GIL — разные оси

Async не отменяет GIL и не даёт CPU-параллелизма. Async даёт **concurrency на одном потоке**: пока одна корутина ждёт сокет, другая бежит. CPU-тяжёлую работу из async всё равно выносите в `asyncio.to_thread` / process pool (Starlette `run_in_threadpool` так и делает для sync FastAPI endpoints).

Free-threading + asyncio в одном процессе — возможно, но вы смешиваете две модели. Имеет смысл, если event loop один, а CPU-куски идут в native библиотеки без GIL. Не запускайте два конкурирующих event loop в двух потоках «потому что можно».

## Где это в живом коде

- httpx/anyio: async I/O, не потоки.
- FastAPI: sync endpoint → thread pool, чтобы не блокировать loop.
- numpy/pydantic-core: тяжёлая работа вне eval loop.
- Ваш `lru_cache` на функции с мутабельным глобальным dict — место, которое стоит пересмотреть перед включением 3.14t.
