# SQLAlchemy ORM: Session как Unit of Work

SQLAlchemy — не «Django ORM с другой стороны». Core — SQL compiler + DBAPI. ORM поверх — identity map и unit of work. Я читал `lib/sqlalchemy/orm/session.py` и `unitofwork.py` (версия ветки 2025–2026, копирайты до 2026).

Документация класса буквальная:

> The Session is **not safe for use in concurrent threads.**

Один Session — одна логическая транзакция работы, обычно один request / одна job. Для веб: session per request, закрыть в ExitStack / middleware / FastAPI yield-dependency.

## Состояния объекта

- **transient** — Python-объект, Session не знает.
- **pending** — `add()`, ещё нет строки; после flush станет persistent.
- **persistent** — в identity map, есть PK.
- **detached** — был persistent, Session закрыли / expunge; `add()` вернёт в persistent.

`Session.add`:

```python
state = attributes.instance_state(instance)
self._save_or_update_state(state)
```

Каждый mapped instance несёт `InstanceState` (instrumentation). Session работает со state, не «с полями как с dict» напрямую.

`identity_map`: ключ идентичности → объект. Повторный SELECT той же PK возвращает **тот же** Python-объект. Это инвариант UoW: две «версии» одной строки в памяти не живут, пока вы не сделаете expire/refresh.

## flush ≠ commit

`flush()` пишет INSERT/UPDATE/DELETE в **текущую транзакцию БД**, не коммитит её:

```python
if self._is_clean():
    return
self._flushing = True
self._flush(objects)
```

`_flush` создаёт `UOWTransaction(self)`, считает dirty/new/deleted, топологически сортирует зависимости (FK: сначала parent), шлёт SQL. `unitofwork.py`: «assembles flush tasks … organizes them in order of dependency, and executes».

`commit()` делает flush (если нужно) и коммит транзакции. `expire_on_commit=True` по умолчанию: после commit атрибуты протухают, следующий доступ — новый SELECT. Это защита от stale data, и сюрприз для тех, кто трогает объект после commit без refresh.

`autoflush=True`: перед query Session сам flush, чтобы SELECT видел ваши INSERT. Отключить можно, но тогда «я add, почему query не видит» — ваш выбор.

## execute в 2.0 стиле

`session.execute(select(User).where(...))` — не ленивый QuerySet Django. Вы получаете `Result`, надо `.scalars().all()` и т.д. Ленивость SQLAlchemy — в loaded attributes / lazy relationships (отдельные SELECT при доступе к `user.addresses`), не в объекте запроса как в Django.

N+1 здесь такой же враг: `selectinload` / `joinedload`.

## Почему Session не потокобезопасен

Identity map, `_new`/`_deleted`, текущая транзакция, `_flushing` — мутабельное состояние без внутренних замков «на каждый атрибут объекта». Два потока в одном Session — гонки и порча UoW. Паттерн: thread-local / contextvar session factory (`scoped_session` исторически; в 2.0 чаще явный lifespan).

## Что украсть

1. Identity map, если у вас граф объектов и БД.
2. Разделение flush (синхронизация с транзакцией) и commit (граница работы).
3. Явный запрет на шаринг между потоками в docstring класса — честность API.
4. Instrumentation (state рядом с объектом), когда нужно следить за dirty fields.

Не копируйте целиком: компилятор SQL и 5000 строк session.py — это 20 лет краевых случаев драйверов.

Читать: `Session.add`, `Session.flush` / `_flush`, класс `UOWTransaction`, доку `orm/session.html` (концепции лучше кода в первые 30 минут).
