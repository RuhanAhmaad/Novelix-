# NOVELIX 5.0 — Professional Mobile PDF Reader Report

## 1. Executive Summary

NOVELIX 5.0 introduces a custom, high-performance in-app Mobile PDF Reader designed with a minimalist black and amethyst purple aesthetic. Readers can read published manuscripts directly inside the Android application without being redirected to external browsers or Google Drive. The reader supports high-DPI crisp typography, smooth navigation, portrait and landscape auto-adaptation, reading progress persistence, page bookmarking, customizable reading themes, and secure authenticated proxying for Google Drive files.

---

## 2. Reader Features & Architecture

### A. High-DPI Canvas Rendering
Mobile AMOLED and Retina screens often suffer from blurry canvas rendering if standard CSS pixels are used. The NOVELIX reader queries `window.devicePixelRatio` and renders the PDF page at device physical resolution:
```javascript
const dpr = window.devicePixelRatio || 1;
const viewport = page.getViewport({ scale: targetScale * dpr });
canvas.height = viewport.height;
canvas.width = viewport.width;
canvas.style.width = `${Math.floor(viewport.width / dpr)}px`;
canvas.style.height = `${Math.floor(viewport.height / dpr)}px`;
```
This guarantees pin-sharp typography and crisp illustrations at any zoom level.

### B. Responsive Fit Modes
- **Fit to Width (`fitMode = 'width'`):** Automatically computes the scaling factor required to fit the document width to the viewport width minus padding, ideal for continuous mobile scrolling and reading.
- **Fit to Page (`fitMode = 'page'`):** Scales both width and height to fit entirely within the available screen area, ideal for full-page comic and manga layouts.
- **Custom Zoom (`+` / `-`):** Allows fine-grained zoom adjustment between 0.6x and 3.0x with smooth redraws.

### C. Reading Progress Memory & Auto-Resume
1. As the reader turns pages, `saveReadingProgressDebounced()` persists the current page, total pages, percentage, and timestamp to `users/{uid}/reading_progress/{bookId}`.
2. When reopening the book, the reader retrieves this record:
   - If `savedPage > 1`, the reader automatically jumps to that page and presents a clean toast: `Resumed at page X`.
3. Reading progress is preserved across app sessions, restarts, and updates.

### D. Bookmark System
- A dedicated bookmark toggle button in the top toolbar allows readers to bookmark the active page with one tap.
- Bookmarks are stored in Firestore as an array of page numbers under `users/{uid}/reading_progress/{bookId}`.
- When navigating onto a bookmarked page, the toolbar icon automatically lights up in amethyst purple (`#9270FF`).

### E. Multiple Reading Themes
The reader supports four distinct, eye-friendly color themes switchable via the palette icon:
1. **Dark (Default):** Deep obsidian `#07070A` background with crisp white typography.
2. **Midnight Purple:** Regal twilight `#0E0919` background tailored to the NOVELIX purple brand identity.
3. **Warm Sepia:** Soft parchment `#EFE6CE` background with high-contrast warm charcoal text, optimal for long novel reading sessions.
4. **Paper Light:** Clean `#F6F8FB` daylight mode for bright outdoor reading.

### F. Secure Access for Google Drive Files
When reading books stored on Google Drive:
1. The reader does NOT attempt to fetch the file directly from `drive.google.com` (which would trigger CORS errors and require public file exposure).
2. The reader invokes the backend callable `getReaderPdfData` with the book ID and edition language.
3. The backend validates user authorization, retrieves the PDF from Google Drive using the author's securely stored token, and returns the file buffer.
4. The frontend caches the decoded `Uint8Array` in `APP_STATE._pdfCache` for instantaneous page turning.
5. On user logout, `APP_STATE._pdfCache` is cleared to protect private manuscripts.
