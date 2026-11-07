# NOVELIX 7.0 — Performance & Memory Optimization Report

**Generated:** 2026-11-07  
**Target:** Android Mobile Devices (Capacitor WebView)  
**Evaluated Areas:** Canvas Rendering, Memory Footprint, Asset Bundling, Firestore Queries

---

## 1. Canvas Rendering & Memory Conservation

### Device Pixel Ratio (DPR) Clamping
- **Challenge:** High-DPI mobile devices (e.g. 1080p to 1440p displays) report a `window.devicePixelRatio` of 3.0 or 4.0. Rendering a 200-page PDF page at 4x scaling creates huge canvas bitmaps (e.g. 4000x6000 px), exceeding mobile WebView texture limits and triggering silent crashes or OOM reboots.
- **Optimization:** Capped DPR at `2.5` maximum:
  ```javascript
  const dpr = Math.min(window.devicePixelRatio || 1, 2.5);
  ```
  This delivers crisp, legible typography on retina displays while cutting canvas memory usage by up to 60%.

### Render Task Cancellation
- **Challenge:** Turning pages quickly spawned concurrent asynchronous `page.render()` tasks on the same canvas context.
- **Optimization:** Tracked active task in `APP_STATE._currentRenderTask`. Calling `changeReaderPage()` immediately executes `_currentRenderTask.cancel()`, eliminating thread contention.

---

## 2. Firestore Query Performance

- **Pagination & Bounds:** Queries on `books` use `.limit(60)` for home feeds and `.limit(30)` for fallback categories.
- **Debounced Progress Updates:** Reading progress updates are throttled with a 1500ms debounce timer to prevent continuous Firestore document writes during fast page scrubbing.
- **Single Master Listener:** One real-time snapshot listener monitors public published books, updating all in-memory shelf views without duplicate queries.

---

## 3. Asset Loading & Shimmer Animations

- **Hardware Acceleration:** Modal backdrops and drawer elements use `transform: translateZ(0)` and `will-change: transform` to force GPU compositing.
- **Skeleton Shimmer:** Uses pure CSS gradients (`#0F0F18` to `#2B2B3F`) running at 60 FPS without JavaScript animation timers.
