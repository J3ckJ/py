# Django: луковица middleware и ленивый QuerySet

Django — batteries-included. Разбирать «весь Django» бессмысленно. Я читал то, через что проходит каждый HTTP-запрос и каждый ORM-запрос: `django/core/handlers/wsgi.py`, `base.py`, `django/db/models/query.py`.

Django 6.0 (декабрь 2025) добавил встроенные background tasks — это уже не ядро request path, не путайте.

## Старт процесса

WSGI-сервер импортирует `application = get_wsgi_application()` → `django.setup()` (settings, app registry, модели) → `WSGIHandler()`. В `__init__` — `load_middleware()` **один раз на процесс/worker**, не на запрос. Каждый gunicorn worker стартует это заново.

## WSGIHandler.__call__

```python
def __call__(self, environ, start_response):
    set_script_prefix(get_script_name(environ))
    signals.request_started.send(...)
    request = self.request_class(environ)  # WSGIRequest
    response = self.get_response(request)
    start_response(status, headers + Set-Cookie)
    return response  # iterable; file_wrapper отдельная ветка
```

`WSGIRequest` оборачивает environ: `LimitedStream` на `wsgi.input` (нельзя читать больше Content-Length), lazy `GET`/`COOKIES` через `@cached_property`, `POST`/`FILES` при первом доступе парсят тело.

Заголовки из WSGI приходят как latin-1 str; Django кодирует обратно в bytes (`get_bytes_from_wsgi`) — шрам спецификации WSGI.

## Сборка middleware: вложенные callable

`load_middleware` идёт по `settings.MIDDLEWARE` **с конца**:

```python
get_response = self._get_response
handler = convert_exception_to_response(get_response)
for middleware_path in reversed(settings.MIDDLEWARE):
    mw_instance = middleware(adapted_handler)
    handler = convert_exception_to_response(mw_instance)
self._middleware_chain = handler
```

Каждый middleware — фабрика `(get_response) → (request) → response`. Луковица: вход сверху вниз списка, выход обратно. Short-circuit: не вызвал `get_response` — внутренние слои (и view) не увидят запрос.

Отдельно списки `process_view` / `process_template_response` / `process_exception` — старый стиль, вставляется вокруг view внутри `_get_response`.

Sync/async: `adapt_method_mode` через `asgiref` `sync_to_async` / `async_to_sync`. У middleware флаги `sync_capable` / `async_capable`. ASGIHandler — параллельный путь `get_response_async`, не «прогнать WSGI через async» (комментарий в коде: слишком медленно).

## Внутри луковицы: `_get_response`

1. `resolve_request` → `get_resolver().resolve(path_info)` → `request.resolver_match`.
2. view middleware, может вернуть response.
3. `make_view_atomic`: если `ATOMIC_REQUESTS` — обернуть view в `transaction.atomic` (с async views запрещено).
4. Если view coroutine, а мы на sync handler — `async_to_sync`.
5. View обязан вернуть `HttpResponse`, не `None` и не «забытый await» (`check_response`).
6. Если есть `.render()` (TemplateResponse) — template middleware, затем `render()`.

`get_response` после цепочки регистрирует `request.close` в `response._resource_closers`.

## QuerySet: SQL не там, где вы думаете

```python
qs = User.objects.filter(active=True)  # SQL ещё нет
```

`QuerySet` держит объект `sql.Query`, `_result_cache = None`. Методы `filter`/`exclude` **клонируют** queryset (`query.chain()`), не мутируют (кроме внутренних sticky-трюков).

SQL случается при:

- итерации / `list(qs)` / `bool(qs)` / `len(qs)` → `_fetch_all`:
  `_result_cache = list(self._iterable_class(self))`
- `get()`, `first()`, агрегации, `update`/`delete` — свои пути
- pickle queryset — тоже `_fetch_all` (в `__getstate__`)

`iterator()` — без полного кеша, для больших выборок.

Это та же идея, что у PreparedRequest и Dependant: **построить план дёшево, исполнить при необходимости**. Цена: случайный `if queryset:` в шаблоне бьёт в БД; N+1, если в цикле трогаете related без `select_related`/`prefetch_related` (`_prefetch_related_objects` после fetch).

## Что украсть

1. Собрать цепочку middleware на старте, не на запросе.
2. Один и тот же паттерн callable `(request)→response` на каждом слое.
3. Явный мост sync/async, не надежда, что «как-нибудь».
4. Ленивый query object + явная материализация.
5. `check_response`: ловить None на границе, а не через 3 фрейма AttributeError.

Не красть: глобальные `django.conf.settings` как бог-объект — это цена monolith framework, в своей библиотеке лучше явный config.

Читать: `handlers/base.py` целиком (375 строк, сердце), `query.py` `QuerySet.__init__`, `_clone`, `_fetch_all`.
