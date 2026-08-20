# Анатомия Apple.com (август 2026)

Читал живой HTML `https://www.apple.com/` и `https://www.apple.com/iphone-17-pro/` плюс их `inline-media.built.js` и `AnimSystemModel`. Это не слухи 2019 года про canvas-sequence — текущий стек.

## Это не React

Главная: 254 КБ HTML, 13 скриптов, 0 `__NEXT_DATA__`, 0 modulepreload. Скрипты вида `/v/home/a/scripts/inline-media.built.js`. Продуктовая: `/v/iphone-17-pro/h/built/scripts/overview/main.built.js`.

`<html class="no-js">`. Компоненты вешаются декларативно:

```html
<body data-component-list="FocusManager DeepLink">
<section data-anim-scroll-group="Welcome" data-component-list="Welcome">
<div data-component-list="InlineMediaDefault">
<div data-component-list="ProductViewerCore ProductViewer ...">
```

Свой registry (`ComponentMap`). Похоже на мини-фреймворк маркетинга («Marcom»), не на SPA.

Страницы продуктов **слабо шарятся**: independent templates + общий header/footer. Поэтому iPhone 17 Pro весит 860 КБ HTML — контент и `picture` встроены.

## Anim System — сердце «яблочного» скролла

Из `AnimSystemModel`:

- брейкпоинты **S / M / L**: `max-width 734px`, `1068px`, `min-width 1069px`;
- кейфреймы с `start`/`end` выражениями, easing, `breakpointMask: "SMLX"`;
- типы: Interpolation, CSSClass, Event;
- pageMetrics: scrollX/Y, window size, breakpoint;
- события групп и таймлайна (`ON_TIMELINE_UPDATE`, `ON_CHAPTER_*`).

`InlineMedia` (расшифрованный бандл с домашней):

1. `createScrollGroup(el, { name: "Inline Media" })`
2. Load keyframe → `video.load()` один раз (`onEnterOnce`)
3. Play keyframe → `play()` / на exit `pause()` если loop
4. Таймаут 4с на play, иначе `destroy()`
5. `requestVideoFrameCallback` чтобы снять класс `loading` когда кадр реально на экране
6. Смена breakpoint с другим viewport-ассетом → destroy и не enhanced

Это **медиа-оркестратор**, привязанный к скроллу, не плеер.

Выражения (`HpViewport` + парсер): `t - (100vh - 70h)` — геометрия, не магические пиксели. Меняете заголовок — кейфрейм жив.

## Видео на home

```html
<video id="bts-2026" muted preload="none" playsinline
  data-inline-media-basepath="/105/media/us/home/2026/.../anim/hero/"
  data-inline-media-type="webm"
  data-inline-media-play-kf='{"start":"t - (100vh - 70h)","end":"b"}'
  role="img">
```

База путь + тип: скрипт сам соберёт URL под retina/tall viewport. `role="img"` — для AT это картинка, не видеоконтролы.

## iPhone 17 Pro: главы и 3D

`data-anim-scroll-group`: Welcome, Highlights, Design, Product Viewer, …

Highlights gallery: `data-preload-strategy="keyframe, prior-section"` — грузить медиа, когда близко, с учётом предыдущей главы.

Product viewer:

```html
data-library-path="/v/iphone-17-pro/h/static/libs/lotus.min.js"
data-mode="3d"
data-rt-scenes='{"large":"iPhone17Pro_US_L","medium":"..._M","small":"..._S"}'
data-rt-scenes-path="/v/iphone-17-pro/h/static/"
```

AR: `<a rel="ar" href=".../iphone-17-pro-e-sim.usdz">` — нативный iOS Quick Look, не WebXR для всех.

Фоллбэк: `tour-3d-fallback` + color gallery, если 3D не взлетел.

Итого 2026: **не один Flow на всю страницу**, а стек слоёв:

1. Документ + picture.
2. Anim System (кейфреймы, главы).
3. InlineMedia (webm lifecycle).
4. Lotus 3D viewer + USDZ.
5. StaggeredFadeIn / SlideGallery / HardwareZoom как локальные компоненты.

## Почему ощущается цельно

- Одна сетка брейкпоинтов на всю marcom.
- Одна система времени (scroll groups).
- Ассеты режутся под S/M/L **на этапе продакшена**, не `srcset` от бедра.
- Local nav меняет тему по скроллу (`theme-reveal-on-scroll`, `data-reveal-keyframe="a0b"`).
- Если enhanced умер — класс `no-enhanced`, видео вычищаются (`src=""`).

## Честный вывод инженеру

Чтобы «сделать как Apple», нужна не GSAP-подписка. Нужны:

1. раскадровка глав;
2. язык интервалов относительно layout;
3. оркестр загрузки медиа;
4. фоллбэки;
5. пайплайн 3D/видео (киношники + USD).

Библиотека — 5% репозитория. Остальное — контент и дисциплина пайплайна. Демо 1–5 в `/sites` закрывают инженерные 5% без украденных ассетов.
