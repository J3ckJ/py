# Первичные источники

Снимок сделан **20 августа 2026**. Ссылки ведут на актуальные документы; номера строк в разборах проектов соответствуют shallow-clone репозиториев на эту дату и могут чуть съехать на `main`.

## Язык и реализация

- [The Python Language Reference — Data model](https://docs.python.org/3.14/reference/datamodel.html)
- [The import system](https://docs.python.org/3.14/reference/import.html)
- [What's New in Python 3.14](https://docs.python.org/3.14/whatsnew/3.14.html) — релиз 7 октября 2025, патч 3.14.7 от 5 августа 2026
- [What's New in Python 3.15](https://docs.python.org/3.15/whatsnew/3.15.html) — 3.15.0rc1 от 4 августа 2026
- [PEP 790 — Python 3.15 Release Schedule](https://peps.python.org/pep-0790/)
- [PEP 703 — Making the GIL Optional](https://peps.python.org/pep-0703/)
- [PEP 779 — Criteria for supported status for free-threaded Python](https://peps.python.org/pep-0779/)
- [Free-threading howto](https://docs.python.org/3.14/howto/free-threading-python.html)
- [Python Free-Threading Guide](https://py-free-threading.github.io/)
- [CPython InternalDocs/jit.md](https://github.com/python/cpython/blob/main/InternalDocs/jit.md)

Ключевые PEP, без которых современный Python не читается: 8, 20, 228, 255, 311, 343, 380, 3155, 3119, 362, 484, 492, 525, 526, 544, 567, 572, 584, 617, 634, 649, 654, 667, 695, 701, 703, 734, 750, 779, 810, 814.

## Проекты (код)

| Проект | Репозиторий | Что смотрели |
| --- | --- | --- |
| requests | https://github.com/psf/requests | `src/requests/{api,sessions,adapters,models,auth,hooks}.py` |
| httpx | https://github.com/encode/httpx | `httpx/{_api,_client,_models,_auth,_config,_transports}` |
| Flask | https://github.com/pallets/flask | `src/flask/{app,ctx,globals,wrappers,sansio}` |
| Werkzeug | https://github.com/pallets/werkzeug | `wrappers`, `routing/map.py`, `local.py`, `serving.py` |
| FastAPI | https://github.com/fastapi/fastapi | `applications.py`, `routing.py`, `dependencies/` |
| Starlette | https://github.com/encode/starlette | `applications.py`, `routing.py`, `requests.py`, `responses.py` |
| Pydantic | https://github.com/pydantic/pydantic | `main.py`, `_internal/_model_construction.py`, `_generate_schema.py`, `pydantic-core` |
| pytest | https://github.com/pytest-dev/pytest | `_pytest/{config,main,python,runner,fixtures,assertion}` |
| Django | https://github.com/django/django | `django/core/handlers/{base,wsgi}.py`, `db/models/query.py` |
| SQLAlchemy | https://github.com/sqlalchemy/sqlalchemy | `orm/session.py`, `orm/unitofwork.py` |

## Презентационный веб (август 2026)

Живые страницы, HTML снят 2026-08-20:

- https://www.apple.com/
- https://www.apple.com/iphone-17-pro/ — `data-anim-scroll-group`, `lotus.min.js`, USDZ AR, InlineMedia
- https://www.apple.com/v/home/a/scripts/inline-media.built.js — load/play кейфреймы
- https://stripe.com/ — Next.js + canvas
- https://linear.app/ — Next App Router, Cloudflare Images

Разборы и спецификации:

- [web.dev Rendering performance](https://web.dev/articles/rendering-performance)
- [RenderingNG architecture](https://developer.chrome.com/docs/chromium/renderingng-architecture)
- [Stick to compositor-only properties](https://web.dev/articles/stick-to-compositor-only-properties-and-manage-layer-count)
- [CSS-Tricks: Apple-style scroll sequence](https://css-tricks.com/lets-make-one-of-those-fancy-scrolling-animations-used-on-apple-product-pages/)
- [Flow: Apple's Animation Secret Weapon](https://graydonpleasants.com/posts/flow-apples-secret-weapon/)
- [iPhone 13 Flow compression](https://dev.to/tetra2000/compression-algorithm-for-iphone-13s-product-page-3gde)
- [Stripe gradient reverse-engineering](https://kevinhufnagl.com/how-to-stripe-website-gradient-effect/)
- [Linear vaporwave Three.js](https://blog.maximeheckel.com/posts/vaporwave-3d-scene-with-threejs/)
- [Trionn: GSAP + Three + Lenis](https://tympanus.net/codrops/2026/07/15/the-architecture-behind-trionn-coordinating-gsap-three-js-lenis-and-web-audio/)
- [Immersive stack 2026](https://adamarant.com/en/blog/immersive-web-stack-in-2026-lenis-gsap-and-what-to-skip)

## Экосистема (обзоры, не истина в последней инстанции)

- [Python 3.14.7 / 3.13.15 — Python Insider](https://blog.python.org/2026/08/python-3147-31315/)
- Обзоры экосистемы 2026 (FastAPI / Django / uv / Ruff / Polars) полезны как *карта популярности*, не как доказательство качества. Для качества всегда возвращайтесь к коду.
