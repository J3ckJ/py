# Stripe, Linear и «крутые, но не Apple»

Apple — вертикально интегрированный маркетинг. Остальные чаще живут в Next и берут **один фирменный эффект**.

## Stripe.com (HTML августа 2026)

- Next.js: `__NEXT_DATA__`, `/_next/static/chunks/...` с `b.stripecdn.com`.
- 74 внешних скрипта чанков — цена универсальной платформы.
- Есть `<canvas>` (герой-градиент).
- `picture` есть, srcset в HTML почти нет — изображения часто через их CDN-компоненты.

Исторический градиент (реверс Kevin Hufnagl / Whatamesh):

- свой **minigl**, не Three.js;
- плоскость ~30×20;
- vertex displacement (3D simplex noise);
- цвет с вершин, fragment почти пустой;
- отсюда «ткань», не «кисель шейдера на весь экран»;
- ScrollObserver: не считать GPU, когда блок вне вьюпорта;
- PNG fallback.

Урок: **мало вершин + движение меша** дешевле fullscreen `sin(uv*time)` в fragment на 4K.

Демо идеи: [`../sites/06-cloth-gradient.html`](../sites/06-cloth-gradient.html).

## Linear.app (HTML августа 2026)

- Next App Router: `ppr-fallback-shell`, `app-router-scroll`, 258 `modulepreload`.
- Картинки: `linear.app/cdn-cgi/imagedelivery/.../f=auto,fit=scale-down` — Cloudflare, формат выбирает CDN.
- Главная сейчас тяжелее текстом/UI-иллюстрациями, чем WebGL.
- Старый vaporwave-релиз 2021 — Three.js plane + RGBShift (разбор Maxime Heckel): отдельная кампания, не вечный движок сайта.

Урок: эффект **разовой кампании** не обязан жить в дизайн-системе. Флагманский продукт может быть CSS-сеткой, а «вау» — на `/releases/2021-06`.

Путают «сайт Linear» и «один шейдер, который видели в твиттере». Смотрите текущий HTML.

## Award-tier (Trionn и подобные, Codrops 2026)

Типичный клей:

```
Lenis.progress → gsap.ticker → ScrollTrigger + Three.js + Web Audio
```

Один clock. `gsap.matchMedia()` для desktop/mobile и `prefers-reduced-motion`. Idle scheduling, чтобы не считать шейдер, пока вкладка в фоне.

Это **игра**. Штат: WebGL engineer + motion + sound. Копировать на корпоративный лендинг = неподдерживаемый зоопарк.

## Другие ориентиры (паттерны, не культ)

| Кто | Паттерн |
| --- | --- |
| Vercel / Next marketing | документ + точечный WebGL/canvas, App Router |
| PlayStation / Nike кампании | видеополные, часто WebGL только в hero |
| Figma marketing | CSS + лёгкий motion, продукт сам 3D |
| Awwwards SOTD | максимализм; учитесь у них композиции, не архитектуре прод-маркетинга |

## Общее у «взрослых»

1. Один фирменный GPU-эффект, не пять.
2. Фоллбэк картинкой.
3. Медиа не грузится ниже фолда без нужды.
4. Текст в DOM, не в канве (SEO, перевод, a11y).
5. Motion выключается по `prefers-reduced-motion`.
