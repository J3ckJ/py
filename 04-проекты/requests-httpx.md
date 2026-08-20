# requests и httpx: два поколения HTTP-клиента

Оба решают одну задачу: сделать HTTP удобным для человека. Архитектуры разные. Я читал `psf/requests` и `encode/httpx` целиком по горячему пути GET.

## requests: фасад → одноразовая Session → Adapter → urllib3

`requests.get(url)` **не** держит глобальное соединение. В `src/requests/api.py`:

```python
with sessions.Session() as session:
    return session.request(method=method, url=url, **kwargs)
```

Каждый «голый» `get()` создаёт Session, отправляет, закрывает пул. Для многих запросов к одному хосту это расточительно — держите `Session()` сами. Это первый урок API: удобный модульный фасад ≠ правильный способ в проде.

### Подготовка запроса — отдельная фаза

`Session.request` собирает `Request` (пользовательские данные), затем `prepare_request` → `PreparedRequest.prepare()`:

`prepare_method` → `prepare_url` → `prepare_headers` → `prepare_cookies` → `prepare_body` → **`prepare_auth` последним** → `prepare_hooks`.

Комментарий в коде буквальный: auth должен видеть уже готовый URL/body (OAuth подпись). Порядок side effects — часть контракта, не деталь реализации.

`PreparedRequest` — «то, что уйдёт в провод». `Request` — то, что удобно собирать человеку. Двухфазность позволяет подписать, залогировать, повторить.

### Session.send

1. `get_adapter(url)` — `OrderedDict` префиксов, по умолчанию `https://` и `http://` → `HTTPAdapter`.
2. `adapter.send` → `urllib3` `urlopen(..., redirect=False, preload_content=False)`. Редиректы **намеренно выключены** на транспорте: ими владеет Session (`resolve_redirects` — генератор, до 30 прыжков, 302/303 → GET, Authorization снимается при смене хоста).
3. `dispatch_hook("response", ...)`.
4. cookies в `RequestsCookieJar` (обёртка stdlib `http.cookiejar` через MockRequest/MockResponse).
5. Если не `stream` — читает `r.content`.

Timeout по умолчанию — **None**. Зависший сокет — это не баг библиотеки, это ваш непереданный timeout. Исторический долг, который httpx исправил.

### Auth как callable + hooks

`HTTPDigestAuth.__call__(prepared)` ставит response-hook `handle_401`: при 401 пересобирает заголовок и **повторяет** через `r.connection.send`. Потоки: nonce в `threading.local`. Паттерн: стратегия `__call__` + наблюдатель на ответ, потому что digest — двухкруговый.

## httpx: один Request, транспорт, generator-auth

`httpx.get` аналогично создаёт временный `Client`. Но:

- Default **timeout 5 секунд**.
- Default **`follow_redirects=False`**.
- Есть `AsyncClient` — зеркало sync-пути, не `if is_async` внутри одного класса.
- Нижний слой — **httpcore**, не urllib3. HTTP/2 опционален (`h2`).
- `Request` сразу wire-ready, без Prepared.

### Оркестрация send

`Client.request` → `build_request` (слияние URL/headers/cookies/query с клиента) → `send`:

- `_send_handling_auth` крутит `auth.sync_auth_flow(request)` — **генератор**: `yield request`, клиент шлёт, `send(response)` обратно в генератор. Digest/OAuth refresh описываются одним протоколом для sync и async (`async_auth_flow`).
- `_send_handling_redirects` — цикл `while True`, max 20.
- `_send_single_request` → `_transport_for_url` → `HTTPTransport.handle_request` → `httpcore.ConnectionPool`.

Тестовые транспорты: `MockTransport`, `WSGITransport`, `ASGITransport` — in-process без сети. Adapter pattern доведён до конца.

### Headers как байты

`Headers` хранит `List[Tuple[bytes, bytes, bytes]]` (raw, lower, value). HTTP на проводе — байты; str — удобная проекция. `CaseInsensitiveDict` в requests — str-уровень. Оба решают «регистр заголовка не значим», httpx ближе к спецификации.

### `USE_CLIENT_DEFAULT`

Третье значение помимо «передали X» и `None`. `None` значит «выключить timeout/auth», а не «как у клиента». Это урок API: не overloaded `None`.

## Сравнение одной таблицей

| | requests | httpx |
| --- | --- | --- |
| I/O | sync | sync + async |
| Транспорт | urllib3 Adapter | httpcore Transport |
| HTTP/2 | нет | опционально |
| Редиректы | включены для GET | выключены |
| Timeout | нет | 5s |
| Auth | callable + hooks | generator flow |
| Тело ответа | `.content` кеш | stream-first, `.read()` |

## Что украсть для своей библиотеки

1. Фасад `get()` закрывает ресурс (`with Session`).
2. Редиректы и auth — **над** сокетом, не внутри.
3. `mount(prefix, transport)` для подмены I/O в тестах.
4. Явные дефолты, которые не убивают прод (timeout).
5. Generator как протокол многошагового диалога (auth), а не callback hell.

Читать: `src/requests/sessions.py` (`send`, `resolve_redirects`), `httpx/_client.py` (`_send_handling_redirects`), `httpx/_auth.py` (`auth_flow`).
