# pytest: хуки как операционная система тестов

pytest — не «раннер assert'ов». Это **плагинная машина** (pluggy) + дерево коллекции + стек setup/teardown + переписывание AST. Я читал `src/_pytest/config/__init__.py`, `main.py`, `python.py`, `runner.py`, `fixtures.py`, `assertion/rewrite.py`.

## Вход

`pytest.main` → `_prepareconfig` → `PytestPluginManager` (наследник `pluggy.PluginManager`) грузит builtin plugins, `conftest.py` (отложенно, по директориям), third-party entry points. Дальше хук `pytest_cmdline_main` → `wrap_session` → коллекция → `pytest_runtestloop`.

Ядро pytest — тоже плагин: `add_hookspecs(_pytest.hookspec)` и `self.register(self)`. Расширение = функция с `@hookimpl`. Нет «если plugin_name:». Есть композиция хуков (`firstresult`, wrappers, historic).

## Коллекция — дерево, не список файлов

`Session.perform_collect` → для каждого пути `collect_one_node` → `pytest_collect_file` → `Module`.

`Module.collect`: регистрирует setup_module/function фикстуры, `FixtureManager.parsefactories(self)`, затем `PyCollector.collect` — перебор имён в модуле, хук `pytest_pycollect_makeitem`. Классы → `Class`, функции `test_*` → `Function`. Parametrize (`Metafunc`) размножает Item.

Каждый узел имеет `nodeid` (`tests/test_a.py::TestFoo::test_bar[1]`). Это адрес для селекции, кэша, репортов. Фабрика `from_parent` — нельзя склеить узел без родителя.

Импорт тестового модуля идёт через assertion rewriting hook в `sys.meta_path`: `assert a == b` становится `if not ...: raise AssertionError(explanation)`. Поэтому pytest-assert информативнее unittest. Это import-time компиляция, как у Pydantic, только AST→AST.

## Протокол одного теста

`pytest_runtest_protocol(item, nextitem)`:

1. `call_and_report(item, "setup")` → `SetupState.setup(item)` поднимает цепочку collectors, которых ещё нет на стеке (session → package → module → class → function). `Function.setup` → `_fillfixtures` → `FixtureDef.execute`.
2. Если setup прошёл — `"call"` → `pytest_pyfunc_call` → `testfunction(**fixture_kwargs)`. Сам вызов тривиален.
3. `"teardown"` → `SetupState.teardown_exact(nextitem)`: снимает только то, что не нужно следующему тесту. Поэтому module-scoped фикстура живёт через пачку тестов файла.

Ошибка в setup → call не выполняется. Это state machine, не «просто вызвать функцию».

## Фикстуры

Имя параметра теста = имя фикстуры (не тип, в отличие от FastAPI). `FixtureManager` строит closure зависимостей (`FuncFixtureInfo`) заранее.

Yield-фикстура:

```python
fixture_result = next(generator)
request.addfinalizer(partial(_teardown_yield_fixture, ..., generator))
```

Второй `next` ждёт `StopIteration`. Тот же генераторный contextmanager.

Scopes: function/class/module/package/session. Кеш по scope. Циклы зависимостей — ошибка при resolve, не в рантайме вызова.

conftest.py виден вниз по дереву каталогов: локальные плагины перекрывают. `item.ihook` — хуки, уже отфильтрованные по месту.

## Сложность

`fixtures.py` огромный: видимость, parametrize indirect, cache invalidation. Сам `test_foo()` — нет. Как у Pydantic: сложность на setup.

## Что украсть

1. Именованные хуки вместо `if plugin`.
2. Дерево с nodeid.
3. Инкрементальный setup stack относительно *следующего* элемента — для скорости.
4. Import hook только если без него нельзя (asserts).
5. DI по именам — просто, но плохо стыкуется со статическими типами. FastAPI выбрал типы. pytest — имена. Оба честны в своём мире.

Читать: `runner.py` `runtestprotocol`, `python.py` `pytest_pyfunc_call`, `fixtures.py` `call_fixture_func`, `assertion/rewrite.py` `visit_Assert`.
