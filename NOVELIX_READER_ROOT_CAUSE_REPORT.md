# NOVELIX 7.0 — Reader Root Cause Report

**Generated:** 2026-11-06  
**Commit:** `072ea3e`  
**Branch:** `main`

---

## Summary of Root Causes

NOVELIX exhibited **two categories of failure**: a hard JavaScript crash that prevented the reader from opening at all, and a PDF rendering failure that caused a blank/error screen even when the reader launched. Below is the precise diagnosis of every defect.

---

## Root Cause 1 — `initiateGoogleDriveAuth` Called but Never Defined (JS TypeError)

**Location:** `scripts/generate_4.py`, `reconnectDriveFromReader()` function  
**Error produced:** `TypeError: initiateGoogleDriveAuth is not a function`  
**Symptom:** Clicking "Reconnect Drive" inside the reader error overlay crashes the entire JS context.

**Root cause:**  
The function `reconnectDriveFromReader()` calls `initiateGoogleDriveAuth()`, but this function was never defined. The correct function name throughout the entire codebase is `initiateGoogleDriveConnection()`. This was introduced when the reader error overlay was added in a previous session but the wrong function name was used.

**Fix:** Renamed the call from `initiateGoogleDriveAuth()` → `initiateGoogleDriveConnection()`.

---

## Root Cause 2 — `navigateTo` Called but Never Defined (JS TypeError)

**Location:** `scripts/generate_4.py`, library empty-state HTML  
**Error produced:** `TypeError: navigateTo is not a function`  
**Symptom:** Tapping "Discover Books" in an empty library crashes JavaScript, leaving the app unresponsive.

**Root cause:**  
The library page's empty state used `onclick="navigateTo('home')"` but the routing function in NOVELIX is named `switchPage()`. No `navigateTo` alias existed anywhere.

**Fix:** Added a `navigateTo(pageId)` alias function that calls `switchPage(pageId)`.

---

## Root Cause 3 — PDF.js Worker CORS Failure in Capacitor Android WebView (Primary Reader Failure)

**Location:** `loadPdfDocumentForReader()`, line `pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs…'`  
**Error produced:** `Error: Setting up fake worker failed` or `WorkerMessageHandler is not defined`  
**Symptom:** Reader loading overlay spins, then shows an error state. PDF never renders.

**Root cause:**  
PDF.js uses a Web Worker to decode PDFs off the main thread. When the worker script URL is external (CDN), the Capacitor Android WebView blocks the cross-origin worker instantiation from `https://localhost` due to Content Security Policy and cross-origin restrictions. The worker fails silently or throws, and PDF.js falls back to synchronous mode — but only if `disableWorker: true` is explicitly set in `getDocument()` options.

**Fix:** Added `disableWorker: true` to the `getDocument()` call options. PDF.js gracefully falls back to main-thread rendering. This is correct for WebView environments and handles all PDF files without a worker.

---

## Root Cause 4 — Reader State Not Reset Between Book Opens

**Location:** `launchActiveReader()`  
**Symptom:** Opening a second book after closing the reader resumed from the wrong page or showed a previous book's render artifact.

**Root cause:**  
`APP_STATE.pdfDocument`, `APP_STATE.pdfIsRendering`, `APP_STATE.pdfPageNumber`, and `APP_STATE.readerFitMode` were never reset when launching the reader for a new book. If the previous reader session ended without calling `closeReaderModal`, the state would leak into the new session.

**Fix:** Added a full state reset block at the top of `launchActiveReader()` that clears all reader state before proceeding.

---

## Root Cause 5 — Firebase Storage URLs May Expire (Silent Download Failure)

**Location:** `loadPdfDocumentForReader()`, Storage branch  
**Symptom:** Books that previously worked stop loading after Firebase Storage download tokens expire (default: 7 days for public rules; shorter for signed URLs).

**Root cause:**  
The `fileUrl` stored in Firestore at publish time is a signed Firebase Storage download URL. These URLs can expire. The code called `fetch(edition.fileUrl)` directly with no fallback mechanism.

**Fix:** Added a `storagePath`-based URL regeneration path using `storage.ref(edition.storagePath).getDownloadURL()` when the initial fetch fails or when `storagePath` is present and `fileUrl` is empty.

---

## Root Cause 6 — Render Task Race Condition on Fast Page Turns

**Location:** `renderPdfPage()`  
**Symptom:** Rapidly pressing next/prev page could cause multiple canvas renders to overlap, corrupting the display.

**Root cause:**  
No cancellation of an in-progress render task before starting a new one. PDF.js's `page.render()` returns a cancellable task object, but the previous implementation ignored it.

**Fix:** Stored the current render task in `APP_STATE._currentRenderTask` and cancelled it before starting any new render.

---

## Root Cause 7 — Reading Progress Cross-Contamination Between Books

**Location:** `saveReadingProgressDebounced()`  
**Symptom:** Opening a new book could overwrite a different book's reading progress in Firestore.

**Root cause:**  
The debounced save wrote to `users/{uid}/reading_progress/{book.id}` but the `book` reference came from `APP_STATE.selectedBook` — read inside the `setTimeout` callback 1500ms later. If the user quickly switched to another book within that window, the wrong book's data would be saved.

**Fix:** Captured `book` reference at the start of the debounce function (before `setTimeout`), and added a `bookId` field to the saved document for cross-validation.

---

## Files Changed

| File | Changes |
|------|---------|
| `scripts/generate_4.py` | 8 reader fixes + 9 UI improvements (see commit message) |
| `scripts/patch_reader_fix.py` | Automated patch script (reference) |
| `scripts/patch_ui_premium.py` | Automated UI patch script (reference) |
| `out/index.html` | Regenerated output |
| `android/app/src/main/assets/public/index.html` | Deployed to Android |
