# Четыре движка картинки

Любой «вау» сводится к тому, **кто рисует пиксели героя**.

## A. DOM + CSS

Текст, кнопки, сетка, sticky. Плюс: доступность, SEO, выделение. Минус: не 4K-материал с motion blur. Linear homepage glow — часто CSS radial + сетка точек с `@keyframes` opacity. Нулевой WebGL.

## B. `<video>` / `<img>` / `<picture>`

Пререндер. Apple кладёт webm рядом с `data-inline-media-basepath="/105/media/.../anim/hero/"`. `preload="none"`, `playsinline`, `muted`, `role="img"` (анимация как изображение, не как медиаплеер).

Lifecycle на 17 Pro: `load` / `play` / `pause` / `reset-on-exit` / `unload-at-end` кейфреймы. Не держать декодер, когда секция уехала.

`<picture>` + `srcset` + media — основной объём DOM. На `/iphone-17-pro/` сотни picture. Это не лень: разные кропы под S/M/L и 1x/2x.

## C. Canvas 2D, последовательность кадров

Классика CSS-Tricks: `drawImage(img[index])`, index из scroll progress. Плотно к жесту, дорого по сети (N jpeg). Sprite sheet упирается в лимит размера текстуры.

rAF обязателен: не `img.src =` на каждый scroll event (мигание, декод на main).

Демо: [`../sites/04-canvas-scrub.html`](../sites/04-canvas-scrub.html) — кадры **рисуются процедурно** (не ассеты Apple).

### Apple Flow (исторический движок ~2018–2023)

Reverse-engineering (Graydon Pleasants, Takahiko Inayama, не исходники Apple):

- не `<video>`;
- keyframes + **diff-кадры** (jpeg с дельтами блоков 8×8);
- manifest + BitSet + worker (`marcom-flow-worker.js`);
- сборка кадра → WebGL texture;
- отдельная ч/б последовательность как alpha mask;
- De Bruijn-подобная упаковка повторяющихся блоков.

Зачем огород: sequence высокого разрешения не влезает в бюджет страницы; video seek неточный. Flow — **свой видеокодек в браузере**, заточенный под скролл.

К 2025–2026 на флагманских страницах Apple сместился к **webm + 3D (USDZ / lotus viewer)**. Flow не «отменён вселенной», но на iPhone 17 Pro в HTML доминируют video wrappers и `data-mode="3d"`, не flow-manifest. Имеет смысл знать Flow, чтобы понимать, *какую задачу* решают кодеки.

## D. WebGL / Three.js / собственные движки

Realtime 3D или шейдерный фон.

| Пример | Что на самом деле |
| --- | --- |
| Stripe gradient | minigl: плоскость ~30×20 вершин, simplex displacement, дешёвый fragment. Не fullscreen shader. PNG fallback `wave-fallback-desktop.png` |
| Linear 2021 release | Three.js terrain + RGBShift (реконструкция Maxime Heckel) |
| Linear 2026 marketing | часто CSS, не шейдер |
| Apple Product Viewer | `lotus.min.js` + `data-rt-scenes` JSON имён сцен large/medium/small + USDZ для AR (`rel="ar"`) |
| Award sites | Three + postprocessing + Lenis |

Цена: GPU, батарея, сложность фоллбэка, a11y (нужен текстовый эквивалент). DPR обычно `min(devicePixelRatio, 1.5–2)`.

Демо cloth-плоскости без Three: [`../sites/06-cloth-gradient.html`](../sites/06-cloth-gradient.html).

## Lottie / Rive

Векторная анимация из After Effects (Lottie/bodymovin) или Rive (стейт-машина). Отлично для иконок и микромоушена. Плохо как замена киношному герою iPhone: нет фотореализма, CPU на сложных шейпах.

## Выбор за 30 секунд

Нужен фотореализм без интерактива → видео/`picture`.  
Нужен кадр-в-кадр скролл → canvas sequence / Flow-подобное / видео с кучей I-frames.  
Нужно крутить продукт руками → 3D (glTF + drei / lotus).  
Нужно «живое поле цвета» → маленькая vertex-mesh, не 1080p fragment noise на весь экран.
