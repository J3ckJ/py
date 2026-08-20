# Pydantic v2: метакласс-компилятор и Rust на горячем пути

Pydantic выглядит как «классы с типами». Внутри это **двуязычный компилятор**. Python строит `CoreSchema` (словарь-IR). `pydantic-core` (Rust) компилирует дерево валидаторов и гоняет его на каждом `model_validate`.

Я читал `pydantic/main.py`, `_internal/_model_construction.py`, `_generate_schema.py` и Rust `validators/mod.rs` / `model.rs` в том же репозитории.

## Определение класса — компиляция

`class User(BaseModel):` → `ModelMetaclass.__new__`:

1. Слить `model_config` с баз (`ConfigWrapper.for_model`).
2. Разобрать namespace: поля vs class vars vs private.
3. Собрать `FieldInfo` (алиасы validation/serialization, default, constraints).
4. Собрать декораторы: `@field_validator`, `@model_validator`, `@computed_field`, serializers (`DecoratorInfos`).
5. `complete_model_class`:
   - `GenerateSchema.generate_schema(cls)` → `model_fields_schema` + computed + inner/outer validators
   - `cls.__pydantic_core_schema__ = schema`
   - `cls.__pydantic_validator__ = SchemaValidator(...)`  # Rust
   - `cls.__pydantic_serializer__ = SchemaSerializer(...)`

Если модель ссылается на ещё не определённую — `model_rebuild()`, моки, `defer_build`.

`_generate_schema.py` — ~тысячи строк и **самое сложное место**: вся система типов Python должна стать IR. Горячий путь после этого простой.

## `__init__` почти пустой

```python
def __init__(self, /, **data: Any) -> None:
    __tracebackhide__ = True
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
```

`model_validate(obj)` — тот же валидатор без `self_instance` (Rust делает `tp_new` и пишет `__dict__`). Ветвление `__init__` vs validate — в Rust (`validate_init` vs `validate_construct`), не в Python-цикле по полям.

`__tracebackhide__` — вежливость к pytest: этот кадр не засоряет traceback.

## Почему быстро

- Обход дерева в Rust, не Python for-по полях.
- Схема один раз; nested models переиспользуют prebuilt validator.
- Прямая запись в `__dict__`, минуя `__setattr__`, если политика позволяет.
- Python `@field_validator` — callback обратно в Python, главный тормоз. Держите их тонкими.

## Алиасы и computed

Алиасы запекаются в `core_schema.model_field(..., validation_alias=..., serialization_alias=...)`. Computed fields — узлы сериализации, не вход валидации.

`model_validator(mode='before'|'after')` оборачивает схему wrapper-нодами. Комбинаторика mode × field/model × info — причина, почему API валидаторов кажется большим.

## Урок

Если у вас горячая валидация — **IR + нативный движок**. Если нет — dataclass. Не копируйте метакласс Pydantic «для красоты»: вы получите сложность `_generate_schema` без выигрыша.

Граница системы (JSON с улицы, конфиг, очередь) — да, BaseModel. Внутренний домен — нет.

Читать: `pydantic/main.py` `__init__` / `model_validate`, `_model_construction.py` `complete_model_class`, docs `internals/architecture.md` в репозитории pydantic.
