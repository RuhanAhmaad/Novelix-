# NOVELIX 7.0 — Reader Engine Fix & Verification Report

**Generated:** 2026-11-07  
**Platform:** Capacitor Android / Web SPA  
**Rendering Library:** Mozilla PDF.js 3.11.174  
**Primary Engine File:** `scripts/generate_4.py` (Controller: `launchActiveReader`, `loadPdfDocumentForReader`, `renderPdfPage`)

---

## 1. Architectural Fixes in Reader Engine

### A. Workerless Execution Mode (`disableWorker: true`)
- **Issue:** Web Worker CDN script (`pdf.worker.min.js`) is blocked from executing inside Android Capacitor WebViews (`https://localhost`).
- **Solution:** Configured `pdfDataParam.disableWorker = true`. PDF.js decodes PDF binary streams synchronously on the main UI thread within webview limits, eliminating worker creation failures.

### B. Pre-Fetch Binary Stream & Magic Byte Validation
- **Issue:** Passing a remote URL directly to `pdfjsLib.getDocument({ url })` subjected the PDF request to CORS restrictions inside the WebView.
- **Solution:** Pre-fetch raw array buffers via standard `fetch(url, { credentials: 'omit' })`, cast to `Uint8Array`, and validate `%PDF-` magic bytes (`0x25, 0x50, 0x44, 0x46`) before passing `{ data: bytes }` into PDF.js.

### C. Multi-Provider Source Resolution
The reader resolves manuscripts across four supported storage topologies:
1. **Firebase Storage:** Fetches via authenticated download URL, with automatic token renewal via `storage.ref(edition.storagePath).getDownloadURL()`.
2. **Google Drive:** Calls Cloud Function `getReaderPdfData({ bookId, language })`, decoding returned Base64 directly into `Uint8Array`.
3. **External HTTPS PDFs:** Fetches directly while validating headers and magic bytes to reject HTML error redirects.
4. **Local Uploads:** Read via `FileReader.readAsArrayBuffer()` into `Uint8Array`.

---

## 2. Touch Gestures & UI Navigation

1. **Pinch-to-Zoom:**
   - Listens to 2-finger `touchstart`, `touchmove`, and `touchend` events on `#pdfRenderCanvas`.
   - Computes Euclidean distance between touch points: `dist = sqrt(dx^2 + dy^2)`.
   - Adjusts `APP_STATE.pdfZoomScale` between 50% and 400%, re-rendering canvas on release.
2. **Tap-to-Turn Pages:**
   - Single tap on left 30% of viewport triggers `changeReaderPage(-1)`.
   - Single tap on right 30% triggers `changeReaderPage(1)`.
   - Center 40% preserves touch interactions without page flips.
3. **Hardware Back Button:**
   - Pressing Android Back closes the reader modal, cancels active renders, and restores the Book Detail view.

---

## 3. Reading Progress & Memory Optimization

- **Debounced Firestore Sync:** `saveReadingProgressDebounced(pageNum, totalPages)` persists page number, edition language, and bookmarks array with a 1500ms debounce.
- **Render Task Cancellation:** `if (APP_STATE._currentRenderTask) APP_STATE._currentRenderTask.cancel()` prevents overlapping renders during rapid page navigation.
- **DPR Capping:** `devicePixelRatio` is capped at `2.5` to prevent Out-Of-Memory (OOM) errors on 4K/QHD mobile displays.
