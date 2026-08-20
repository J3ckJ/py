# Стандартная библиотека, которой хватает дольше, чем кажется

Новичок ставит пакет на каждую мелочь. Профессионал знает, что уже есть в stdlib. Ниже — не каталог модулей, а **набор, который встречается в крупных проектах постоянно**.

## Данные и алгоритмы

- `collections.deque`, `Counter`, `defaultdict`, `ChainMap` (слои конфига).
- `collections.abc` — Iterable, Mapping, Callable, Buffer (3.12+).
- `dataclasses` — внутренние структуры.
- `enum.Enum` / `StrEnum` / `IntFlag` — статусы. Не сравнивайте enum с сырой строкой в новую сторону без `.value`.
- `heapq`, `bisect`, `array`, `graphlib.TopologicalSorter` — SQLAlchemy UoW сортирует зависимости; тот же класс задач.
- `itertools` — `chain`, `islice`, `groupby`, `product`. Память vs CPU: itertools ленив.
- `functools.lru_cache`, `cache`, `cached_property`, `partial`, `singledispatch`, `wraps`.
- `operator.itemgetter`, `attrgetter` — ключи сортировки без лямбд в горячих местах.

## Файлы, пути, процессы

- `pathlib.Path` — канон. `os.path` жив в старом коде.
- `os` / `stat` — то, чего pathlib не закрывает.
- `subprocess.run(..., check=True, capture_output=True, text=True)` — не `os.system`.
- `tempfile.TemporaryDirectory`, `NamedTemporaryFile`.
- `shutil` — copy/rmtree/which.
- `io.BytesIO` / `StringIO` — тесты и адаптеры.

## Текст, байты, время

- `json` — стандарт. `orjson`/`msgspec` — когда профилировщик сказал.
- `re` / `regex` (третья сторона) — не парсите HTML регулярками.
- `datetime` *aware* (UTC) vs naive. 3.11+ `UTC` константа. `zoneinfo`.
- `decimal` для денег, не `float`.
- `uuid` (в 3.14 — версии 6–8).
- `base64`, `hashlib`, `hmac`, `secrets` — `secrets` для токенов, не `random`.
- `html`, `urllib.parse` — FastAPI/Starlette всё равно обёртывают, но знать parse_qs полезно.

## Конкурентность

- `threading` + `queue.Queue` + `Lock`/`RLock`/`Event`.
- `multiprocessing` / `concurrent.futures`.
- `asyncio` + `contextvars`.
- `signal` — осторожно, только главный поток.
- 3.14: `concurrent.interpreters`.
- 3.14: `compression.zstd`.

## Наблюдаемость и корректность

- `logging` — единственный нормальный логгер. `getLogger(__name__)`. Конфиг на входе приложения, не в библиотеке.
- `warnings` — библиотеки предупреждают, приложения фильтруют. 3.14t: context-aware warnings.
- `unittest.mock` — даже если тесты на pytest.
- `doctest` — для маленьких утилит и README, не для системы.
- `timeit`, `cProfile` / `profile`, `tracemalloc`, `dis`, `pdb`, `faulthandler`.
- 3.15: пакет профилирования + Tachyon.

## Система типов в stdlib

- `typing` / `collections.abc` / `types`.
- `annotationlib` (3.14).
- `inspect.signature` — сердце FastAPI и pytest. Научитесь читать Parameter.kind (POSITIONAL_ONLY, KEYWORD_ONLY, VAR_POSITIONAL).

## Импорт и упаковка внутри языка

- `importlib.import_module`, `resources` (файлы внутри пакета), `metadata` (версию пакета не хардкодьте).

## Чего в stdlib нет — и это нормально

HTTP-сервер для прода — не `http.server`. HTTP-клиент прода — не только `urllib.request` (он есть, но requests/httpx честнее). ORM — нет. Валидация JSON schema — нет (есть `json`, дальше pydantic). Это не дыры, это граница «язык» vs «экосистема».

## Где это в живом коде

Werkzeug и Django написаны почти на чистом stdlib + свои структуры. requests — stdlib cookiejar + urllib3. pytest — stdlib ast + importlib + pluggy. Когда тянете зависимость, спросите: это stdlib на 20 строк или настоящий домен (HTTP/2, PostgreSQL, DataFrame)?
