# Flask и Werkzeug: WSGI, контекст, «магия» request

Flask 3.2, который я читал, уже не тот Flask 1.x из старых книг: **RequestContext слит с AppContext**, стек `LocalStack` заменён на `contextvars.ContextVar`. Идея та же: глобальные имена `request`/`g`/`current_app` — прокси к объекту текущего запроса.

Werkzeug — toolkit. Flask без Werkzeug не существует. Jinja2 — только шаблоны.

## Контракт: Flask — WSGI-приложение

`Flask.__call__` → `wsgi_app(environ, start_response)` в `flask/app.py`.

Dev-сервер (`werkzeug.serving`) собирает `environ` из HTTP и вызывает `app(environ, start_response)`. В проде то же делает gunicorn. `app.run()` — не прод.

`Response` Werkzeug **сам** является WSGI-приложением: `__call__` делает `start_response` и отдаёт итератор байт. Flask в конце `return response(environ, start_response)`.

## Жизнь одного запроса

1. `ctx = AppContext.from_environ(app, environ)` — создаётся `app.request_class(environ)` (Flask Request ⊆ Werkzeug Request).
2. `ctx.push()`: `_cv_app.set(self)` — с этого момента `from flask import request` начинает работать. Лениво открывается session. `match_request()` → `url_adapter.match()`.
3. `full_dispatch_request(ctx)`:
   - сигнал `request_started`
   - `preprocess_request` (`before_request`)
   - `dispatch_request`: `view_functions[rule.endpoint](**view_args)`
   - `finalize_request`: `make_response` + `after_request`
4. `response(environ, start_response)`
5. `finally: ctx.pop(error)` — teardown_request, `request.close()`, teardown_appcontext, `ContextVar.reset`.

Если view бросил — контекст всё равно снимется. Это правильный `try/finally`, не магия.

## Откуда берётся `request.args`

`flask/globals.py`:

```python
_cv_app: ContextVar[AppContext] = ContextVar("flask.app_ctx")
request = LocalProxy(_cv_app, "request", unbound_message=_no_req_msg)
```

`LocalProxy` (Werkzeug) на каждый доступ делает `ContextVar.get()` и `getattr(obj, "request")`. Вне `wsgi_app` / `app.app_context()` — `RuntimeError: Working outside of request context`. Это не баг, это незапушенный контекст.

`g` — экземпляр `_AppCtxGlobals` на этот `AppContext`, namespace «на время запроса». Не кладите туда то, что должно пережить запрос.

## Роутинг: Werkzeug находит, Flask вызывает

`@app.route("/u/<id>")` → `add_url_rule` → `url_map.add(Rule)` + `view_functions[endpoint] = f`.

При запросе `Map.bind_to_environ` + `MapAdapter.match` (конечный автомат по path/method). Результат: `Rule` + `view_args`. Flask **не** вызывает функцию из Rule; он индексирует свой dict. Разделение: toolkit не знает про ваши декораторы `login_required`.

OPTIONS часто автоматический (`provide_automatic_options`).

## `make_response` — полиморфный return

View может вернуть `str`, `bytes`, iterator, `dict`/`list` (JSON), tuple `(body, status, headers)`, или уже `Response`. Это часть DX Flask. Цена: скрытый тип возврата. FastAPI пошёл другим путём: аннотация + валидация.

## Blueprint — отложенная регистрация

`@bp.route` не пишет в `url_map` приложения. Кладёт lambda в `deferred_functions`. `app.register_blueprint` создаёт `BlueprintSetupState` и прогоняет deferred: URL prefix, endpoint `admin.index`. Хуки мержатся с ключом имени blueprint.

Паттерн: декораторы на «ещё не примонтированном» объекте. Тот же приём у FastAPI `APIRouter`.

## Почему это «микро»

Flask не даёт ORM, admin, users. Даёт: WSGI-оркестрацию, контекст, роутинг, сессии, сигналы, Jinja. Всё остальное — расширения. Это честная граница. Django честен в другую сторону: batteries included.

## Что украсть

1. Контекст как `ContextVar` + тонкий proxy, не threadlocal 2005 года.
2. `try/finally pop` обязателен.
3. Роутинг отдельно от dispatch.
4. Deferred registration для модульности.
5. Response как callable того же контракта, что и app (композиция WSGI).

Читать: `flask/app.py` `wsgi_app` / `full_dispatch_request` / `dispatch_request`, `flask/ctx.py` `push`/`pop`, `werkzeug/local.py`, `werkzeug/routing/map.py` `match`.
