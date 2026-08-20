# Карта конкурентности

В Python четыре разных «одновременно», и они не взаимозаменяемы.

## 1. Прерывания внутри одного потока: asyncio

Event loop крутит готовую корутину, пока та не упрётся в `await` I/O. Подходит: веб, вебсокеты, много исходящих HTTP, чат. Не подходит: тяжёлый CPU без offload.

Стек 2026: `asyncio` + **anyio** (Starlette/httpx так и живут: бэкенд asyncio или trio). Пишите `async with` / TaskGroup, не забывайте отменять задачи. Исключения в фоне без `await` — потерянные ошибки: всегда собирайте задачи.

Паттерн FastAPI: endpoint async → не блокируйте loop (`time.sleep` запрещён, `asyncio.sleep` / I/O библиотеки — да). Sync endpoint → `run_in_threadpool`.

## 2. Потоки: latency hiding, не параллелизм байткода

Пока GIL на месте, потоки = параллельный I/O и native extensions. Очереди `queue.Queue` — канон producer/consumer. Не делите список между потоками «потому что append атомарный» — это не спецификация.

На 3.14t потоки начинают давать CPU. Тогда гонки, которые прятал GIL, вылезают. Перед включением: аудит глобальных кешей, синглтонов, `lru_cache` с мутабельными значениями.

## 3. Процессы: настоящая изоляция

`multiprocessing` / ProcessPoolExecutor: pickle аргументов, отдельная память, отдельный интерпретатор. Цена старта высока. Имеет смысл для CPU и для «этот кусок может упасть».

Gunicorn/Uvicorn workers — это процессы. Django `ATOMIC_REQUESTS` и соединения с БД — **на процесс и на поток** (`django.db.connections`). Не шарьте SQLAlchemy `Session` между потоками: в исходнике прямо написано *not safe for concurrent threads*.

## 4. Несколько интерпретаторов в процессе (3.14)

`concurrent.interpreters`: меньше, чем процесс, строже, чем поток. Экосистема библиотек ещё не вся готова. Рассматривайте, если вы пишете платформу, не CRUD.

## Практическая схема выбора

```
есть ли ожидание сети/диска?
  да → asyncio (много соединений) или потоки (простое, blocking SDK)
нет, только CPU Python?
  да → процессы или 3.14t + потоки (после измерений)
есть нативный код без GIL (numpy)?
  → потоки могут хватить даже на классическом CPython
нужна изоляция сбоя / другая память?
  → процессы
```

## Синхронизация

- `Lock` вокруг инварианта, не вокруг «всего».
- `asyncio.Lock` нельзя смешивать с threading.Lock.
- `contextvars` для request-id, не `threading.local` в ASGI (таски — не потоки).
- Транзакция БД — тоже синхронизация: один Session / один request.

## Тупики, которые все ловят

1. `async def` вызывает sync ORM без `sync_to_async` — блокировка loop.
2. `sync_to_async` + снова async внутри (Django `async_to_sync` вложенность) — deadlock thread-sensitive.
3. Два lock в разном порядке.
4. `ProcessPool` с лямбдой / локальной функцией — не pickle.
5. Создали `Client()`/`Session()` на каждый запрос в цикле — исчерпали сокеты. Держите пул.

## Где это в живом коде

- Starlette `run_in_threadpool` = anyio.to_thread.
- Django `adapt_method_mode` = мост sync/async middleware.
- httpx: две параллельные иерархии Client / AsyncClient, не «один класс с if async».
- pytest-asyncio / anyio plugins — иначе pytest не умеет await.

`examples/06_concurrency_map.py`.
