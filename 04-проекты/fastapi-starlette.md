# FastAPI на Starlette: ASGI, DI, аннотации как контракт

FastAPI **не** конкурирует со Starlette в HTTP. Он наследует `Starlette` и подменяет узкий шов: как из функции пользователя получается ASGI-app. Я читал `fastapi/routing.py`, `dependencies/utils.py`, `starlette/applications.py`.

## Контракт: ASGI

```python
async def __call__(self, scope, receive, send):
    ...
    await super().__call__(scope, receive, send)
```

Сервер (uvicorn) передаёт `scope` (dict: тип, путь, заголовки), канал `receive` (тело), канал `send` (ответ). Starlette ставит `scope["app"]`, лениво собирает middleware stack, вызывает его.

## Луковица middleware (FastAPI чуть другая)

FastAPI **переопределяет** `build_middleware_stack`, чтобы внутрь, после user middleware и `ExceptionMiddleware`, вставить `AsyncExitStackMiddleware` — per-request стек для закрытия uploaded files (`scope["fastapi_middleware_astack"]`).

Снаружи внутрь:

1. `ServerErrorMiddleware` — 500
2. Пользовательский middleware (CORS, …)
3. `ExceptionMiddleware` — `HTTPException` и ваши handlers
4. `AsyncExitStackMiddleware`
5. `Router`

Порядок не косметика: AnyIO task groups копируют contextvars; ExitStack для yield-зависимостей должен быть **внутри** пользовательского middleware, иначе teardown и context разъезжаются.

## Роутер Starlette

Цикл по `self.routes`, `route.matches(scope)`, при FULL — `scope.update(child_scope)`, `route.handle`. Обычный `Route` оборачивает `endpoint` в `request_response`: создать `Request`, вызвать `f(request)`, `await response(scope, receive, send)`.

## То, что добавляет FastAPI

`APIRoute` ставит `self.app = request_response(self.get_route_handler())`, но свой `request_response`:

- `Request(scope, receive, send)`
- два вложенных `AsyncExitStack`: `fastapi_inner_astack` (request-scope yield) и `fastapi_function_astack` (function-scope, закрывается **до** стрима ответа)
- `wrap_app_handling_exceptions`

Пользовательская функция **никогда** не получает сырой `Request` как единственный аргумент (если сама его не запросила). Её вызывает `run_endpoint_function(**solved_values)`.

### Компиляция маршрута (один раз)

`get_dependant` + `inspect.signature` + `analyze_param`:

- `Depends` / `Security` → рекурсивный подграф `Dependant`
- `Request`, `Response`, `BackgroundTasks` — особые слоты
- иначе: path / query / header / cookie / body по эвристике (скаляр → query, нескаляр → body, имя из URL → path)
- каждый вход → Pydantic `ModelField`

Return annotation → `response_field` в режиме serialization. Тот же объект поля кормит OpenAPI (`openapi/utils.py` не парсит функции заново — читает уже собранное).

### Горячий путь запроса

1. Прочитать body (`request.body()` / `form()`, файлы закрыть через middleware stack).
2. `solve_dependencies` — DFS по подзависимостям, кеш `(callable, oauth_scopes, scope)` на запрос.
3. Генераторы → `asynccontextmanager` + `enter_async_context` на нужный стек. Sync callable → `run_in_threadpool`.
4. `run_endpoint_function`.
5. `serialize_response` — валидация ответа, иначе `ResponseValidationError`.
6. Starlette `Response.__call__` шлёт `http.response.start` / `body`.

`dependency_overrides` в тестах: подмена callable → **пересборка** `Dependant` на лету.

## Что делегировано Starlette

Request/Response/WebSocket, Router/Mount, middleware infrastructure, `run_in_threadpool`, lifespan, exception wrapper. FastAPI добавляет граф зависимостей, валидацию, OpenAPI, security schemes, streaming JSONL/SSE с валидацией элементов.

## Урок дизайна (самый важный в этом репозитории)

**Скомпилируй контракт при регистрации, исполняй дешёвый граф на запросе.** Аннотации — данные. Pydantic — один источник истины для проверки, сериализации и документации. Не держите отдельно «валидацию» и «Swagger».

Три ExitStack — образец, как развести lifetime: файл, сессия БД до конца ответа, временный объект только на время вызова функции.

Читать: `fastapi/routing.py` (`get_request_handler`, `request_response`), `fastapi/dependencies/utils.py` (`solve_dependencies`, `analyze_param`), `starlette/routing.py` (match loop), `starlette/responses.py` `__call__`.
