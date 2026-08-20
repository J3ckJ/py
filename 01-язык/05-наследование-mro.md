# Наследование, MRO, миксины, метаклассы

Наследование в Python — не «скопировать методы предка». Это **поиск атрибута по линейному списку классов** (MRO) плюс кооперативный `super()`.

## C3 linearization

У класса один MRO: `Class.__mro__`. Он строится алгоритмом C3 (как в Dylan). Интуиция:

- Ребёнок раньше родителей.
- Порядок баз в `class C(A, B)` сохраняется: `A` перед `B`.
- Монотонность: если в каком-то предке `X` раньше `Y`, так же будет везде.

Если построить нельзя — `TypeError: Cannot create a consistent method resolution order`. Это не баг интерпретатора, это противоречивые базы.

```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass
# D.__mro__ = (D, B, C, A, object)
```

`super()` без аргументов в методе использует `__class__` и `self`, чтобы найти *следующий* класс в MRO, не «родителя в тексте». Поэтому `super()` работает с миксинами.

## Кооперативный `super()`

Миксин, который вызывает `super().foo()`, обязан предполагать, что *следующий* в MRO тоже примет те же `*args, **kwargs` (или вы аккуратно глотаете лишнее). Стиль:

```python
class Mixin:
    def save(self, **kwargs):
        kwargs.setdefault("touched", True)
        return super().save(**kwargs)
```

Не вызывайте `Parent.save(self)` по имени, если участвуете в множественном наследовании: вы пропустите соседей по MRO.

Django class-based views, SQLAlchemy declarative, pydantic конфиг — всё это миксины + MRO. Если `dispatch()` «не вызывается», нарисуйте `__mro__` до того, как винить фреймворк.

## `object` и `type`

Каждый новый класс в 3.x наследует `object`. У `object` есть `__init__`, `__new__`, `__eq__` по идентичности, `__hash__`. Метакласс по умолчанию — `type`.

`type(name, bases, dict)` создаёт класс. `class` statement — синтаксис для этого вызова. Можно создать класс в рантайме (Django `type("NewModel", (Model,), attrs)` в миграциях и `modelform_factory`).

## Метаклассы: когда они оправданы

Метакласс перехватывает **создание класса**, не экземпляра.

```python
class Meta(type):
    def __new__(mcls, name, bases, namespace, **kw):
        cls = super().__new__(mcls, name, bases, namespace)
        # cls уже существует, можно заполнить реестр
        return cls
```

Оправдания, которые встречаются в природе:

1. **Реестр**: все подклассы попадают в dict (ABC, плагины, модели ORM).
2. **Компиляция схемы**: Pydantic `ModelMetaclass` собирает поля, валидаторы, строит CoreSchema.
3. **Запрет**: ABC помечает абстрактные методы, инстанцирование падает.

Неоправданно: «хочу, чтобы класс сам логировал». Для этого хватает `__init_subclass__` (3.6+):

```python
class Plugin:
    registry = []
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Plugin.registry.append(cls)
```

`__init_subclass__` проще метакласса и композируется через `super()`. Берите его, пока не нужно менять *способ создания* класса (имя, базы, сам тип метакласса).

Конфликт метаклассов (`metaclass conflict`) возникает, когда базы требуют разные метаклассы без общего потомка. Лечится явным общим метаклассом, не «удалю metaclass=».

## ABC и `isinstance`

`abc.ABC` + `@abstractmethod` — runtime-проверка при создании экземпляра. `ABCMeta.register(cls)` позволяет сказать, что сторонний класс «является» Sequence, не наследуясь. `typing.Protocol` с `@runtime_checkable` проверяет *наличие методов*, не родство.

Для публичных API предпочтителен Protocol (структурная типизация). Для «обязан реализовать или не инстанцируешь» — ABC. Для плагинов — реестр через `__init_subclass__`.

## Миксины в проде: правила, которые не написаны в туториалах

1. Миксин не инстанцируют. Имя часто с суффиксом `Mixin`.
2. Миксин стоит **слева** в списке баз, если должен перебивать методы: `class View(LoginRequiredMixin, View)`.
3. Миксин не хранит своё обязательное состояние в `__init__` без `super().__init__`.
4. Документируйте, какой метод вы ожидаете следующим в MRO.

## Где это в живом коде

- `pydantic._internal._model_construction.ModelMetaclass` — компилятор модели.
- Flask `AppContext` не про наследование, а Django CBV — сплошной MRO.
- `collections.abc.Iterable` — `isinstance(x, Iterable)` после register/наследования.

Запустите `examples/03_mro.py`.
