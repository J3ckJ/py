---
name: deep-source-map
description: Deep analysis of a language, ecosystem, or product by reading primary sources and real code, then writing a layered map plus runnable demos. Use when Eugene asks to разобрать, проанализировать, понять как устроено, or to cover a topic from basics to large projects without a formal tutorial.
color: blue
---

# Карта по первичным источникам

Не пиши учебник и не обещай «весь интернет». Сделай конечную карту.

## Метод

1. Зафиксируй снимок (дата, версии).
2. Найди контракт: CLI, WSGI/ASGI, HTML-документ, метакласс.
3. Проследи **один горячий путь** по реальному коду (clone/fetch), с именами файлов.
4. Отдели язык от реализации, документ от приложения, DOM от canvas/WebGL.
5. Сложи в слои папок + короткие исполняемые примеры. Чужой код не вендорить.

## Качество

- Цитаты короткие, со ссылкой на файл/URL.
- Если разобрать «как Apple» — смотри живой HTML, не статью 2019 года как истину.
- В конце честно перечисли, что не вошло.

Образец структуры: репозиторий `J3ckJ/py` (`01-язык/`, `04-проекты/`, `06-сайты/`, `sites/`, `examples/`).
