# CSS-движение: что браузер умеет сам

До JS. Если эффект выражается кривой между двумя computed-стилями — CSS дешевле GSAP.

## Transition vs animation vs WAAPI

- **transition** — из A в B по событию (hover, класс). Идеал кнопок, меню.
- **animation / @keyframes** — цикл или вход. Можно повесить на `animation-timeline`.
- **Web Animations API** — то же в JS, без библиотеки: `el.animate([{transform:'...'}], {duration, easing})`.

Easing: `cubic-bezier`. Линейный scrub скролла (`ease: none`) + внутренний easing персонажа. Двойной easing (скролл ease + анимация ease) ощущается как масло.

## Только compositor-свойства

```css
.card {
  transition: transform 500ms cubic-bezier(.22,1,.36,1), opacity 400ms;
}
.card:hover {
  transform: translateY(-4px) scale(1.02);
}
```

Не анимируйте `margin`, `top`, `width` для «премиума». Исключение: FLIP (First-Last-Invert-Play) — вы один раз считаете дельту layout и дальше играете `transform`. Framer Motion так делает.

## Scroll-driven animations (натив)

```css
.progress {
  animation: grow linear;
  animation-timeline: scroll();
}
@keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }

.reveal {
  animation: fade-up linear both;
  animation-timeline: view();
  animation-range: entry 0% cover 40%;
}
```

- `scroll()` — прогресс скролла контейнера.
- `view()` — насколько элемент в вьюпорте.
- Живут на compositor, **0 байт JS**, не бьют INP.

К 2026: Chromium давно, Safari 18+, Firefox догоняет (флаг/релиз — проверяйте caniuse на день сборки). Для универсального Firefox-фоллбэка либо `@supports (animation-timeline: scroll())`, либо GSAP.

`animation-trigger` (Chrome 145, 2026) — старт анимации по появлению, не scrub. Это «wow once», не «фильм».

Демо: [`../sites/02-scroll-css.html`](../sites/02-scroll-css.html).

## Sticky как дешёвый pin

```css
.scene {
  height: 300vh; /* время скролла */
}
.scene-sticky {
  position: sticky;
  top: 0;
  height: 100vh;
}
```

Пока родитель 300vh едет, ребёнок приклеен. Это **не** ScrollTrigger.pin, но закрывает 70% «яблоко-секций». Дальше scrub внутри sticky — CSS timeline или JS.

Демо: [`../sites/03-pin-story.html`](../sites/03-pin-story.html).

## View Transitions API

Многостраничные сайты (Apple — классические полные загрузки) начинают делать cross-fade без SPA. `document.startViewTransition`. Для маркетинга 2026 — опция, не база. Не путать с Barba.js page transitions award-сайтов.

## Что CSS не умеет (сюда зовут JS)

- `video.currentTime = progress * duration`
- canvas `drawImage(frame)`
- WebGL camera
- сложный pin + snap + callbacks (`onEnterOnce` у Apple)
- измерение velocity скролла
- оркестр из 40 элементов с labels

Правило 2026: CSS — высокий fps дешёвых эффектов. JS — оркестр и не-DOM выход.
