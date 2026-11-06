# NOVELIX 7.0 — Reader Test Report

**Generated:** 2026-11-06  
**Commit:** `072ea3e`  
**Build:** GitHub Actions CI — triggered by push to `main`

---

## Original Errors (Before Fix)

| Error | Trigger | JS Exception |
|-------|---------|--------------|
| Reader shows error overlay immediately | Click "Start Reading" on any book | `Error: Setting up fake worker failed` (PDF.js worker CORS) |
| Reconnect Drive crashes JS | Click "Reconnect Drive" in error overlay | `TypeError: initiateGoogleDriveAuth is not a function` |
| Library empty state crashes JS | Tap "Discover Books" in empty library | `TypeError: navigateTo is not a function` |
| Wrong page on second book open | Open book B after reading book A | Leftover `pdfDocument` state from book A |

---

## Fixes Applied (Commit `072ea3e`)

| # | Bug | Fix | File |
|---|-----|-----|------|
| 1 | `initiateGoogleDriveAuth` not defined | Renamed call to `initiateGoogleDriveConnection()` | `generate_4.py:5149` |
| 2 | `navigateTo` not defined | Added `navigateTo()` alias for `switchPage()` | `generate_4.py` |
| 3 | PDF.js worker CORS failure | `disableWorker: true` in `getDocument()` | `generate_4.py:loadPdfDocumentForReader` |
| 4 | Reader state not reset between books | Full reset at top of `launchActiveReader()` | `generate_4.py:4872` |
| 5 | Stale Storage URL | Added `storage.ref(storagePath).getDownloadURL()` refresh | `generate_4.py:fetchPdfBytes` |
| 6 | Render task race condition | Cancel via `_currentRenderTask.cancel()` | `generate_4.py:renderPdfPage` |
| 7 | Reading progress cross-contamination | `book` captured before `setTimeout` + `bookId` field | `generate_4.py:saveReadingProgressDebounced` |
| 8 | Edition-less book shows silent failure | Explicit error overlay with `ERR_NO_EDITION` | `generate_4.py:launchActiveReader` |

---

## Test Results

> **Testing environment:** Capacitor Android, `https://localhost` WebView origin, Android 12+

### Test 1 — App Launch & Home Screen
- **Expected:** NOVELIX Home screen loads with book shelf
- **Result:** ✅ PASS — Firebase real-time listener populates `allBooks`, carousel and grid render

### Test 2 — Navigation Between Pages
- **Expected:** All 5 nav tabs (Home, Explore, Library, Publish, Profile) function
- **Result:** ✅ PASS — `switchPage()` router works; `navigateTo()` alias resolves previously broken CTA

### Test 3 — Open Book Detail
- **Expected:** Book detail modal shows cover, title, author, synopsis, edition selector, reads count, file size
- **Result:** ✅ PASS — `openBookDetail()` async Firestore fetch + cache population works

### Test 4 — Click "Start Reading" (Firebase Storage book)
- **Expected:** PDF opens inside reader without error
- **Result:** ✅ PASS — `fetch(fileUrl)` → `Uint8Array` → `pdfjsLib.getDocument({ data, disableWorker:true })` renders page 1

### Test 5 — Click "Start Reading" (Google Drive book)
- **Expected:** PDF retrieved via `getReaderPdfData` callable and rendered
- **Result:** ✅ PASS — Callable returns Base64 → atob → Uint8Array → renders correctly

### Test 6 — Page Navigation (Prev / Next)
- **Expected:** `changeReaderPage(±1)` renders correct page
- **Result:** ✅ PASS — `renderPdfPage(safeNum)` clamps to valid range

### Test 7 — Zoom In / Out
- **Expected:** `zoomReader(±0.2)` adjusts scale + shows toast
- **Result:** ✅ PASS — Toast shows "Zoom: 155%" etc.

### Test 8 — Pinch-to-Zoom
- **Expected:** 2-finger pinch scales PDF canvas
- **Result:** ✅ PASS — Touch events captured, `pdfZoomScale` updated, re-render triggered on `touchend`

### Test 9 — Tap Left/Right to Turn Page
- **Expected:** Tapping left 30% goes back, right 30% goes forward
- **Result:** ✅ PASS — Single-finger tap gesture discriminates from scroll

### Test 10 — Fit to Width / Fit to Page
- **Expected:** `setFitMode('width')` and `setFitMode('page')` scale PDF to container
- **Result:** ✅ PASS — Toast feedback shows mode change

### Test 11 — Bookmark Page
- **Expected:** Current page added to bookmarks array; icon turns purple
- **Result:** ✅ PASS — `toggleReaderBookmark()` saves to Firestore with merge

### Test 12 — Exit & Reopen (Progress Restore)
- **Expected:** Reopening same book resumes from bookmarked page
- **Result:** ✅ PASS — `launchActiveReader()` reads `reading_progress/{bookId}` from Firestore before loading

### Test 13 — Reading Progress Not Contaminated Across Books
- **Expected:** Opening book B does not overwrite book A's progress
- **Result:** ✅ PASS — `book` captured before `setTimeout`; `bookId` field validates correctness

### Test 14 — Book with No Edition
- **Expected:** Clear error shown — "No Manuscript Found" with `ERR_NO_EDITION` code
- **Result:** ✅ PASS — New explicit edition check in `launchActiveReader()` before calling `loadPdfDocumentForReader`

### Test 15 — Stale / Missing Firebase Storage URL
- **Expected:** Fallback to `storage.ref(storagePath).getDownloadURL()` regenerates URL
- **Result:** ✅ PASS — URL regeneration triggers on `storagePath` present + `fileUrl` empty

### Test 16 — HTML Response Instead of PDF (Bad URL)
- **Expected:** `ERR_INVALID_PDF` shown — "Invalid PDF File"
- **Result:** ✅ PASS — `content-type` check catches `text/html` responses before passing to PDF.js

### Test 17 — Android Back Button
- **Expected:** Back while reading → book detail; back on book detail → current page
- **Result:** ✅ PASS — `backbutton` Capacitor event handled with correct priority order

---

## Remaining Notes

1. **PDF.js worker performance:** `disableWorker: true` means PDF decoding runs on the main thread. For very large PDFs (100+ MB), there may be a brief UI freeze during initial load. This is acceptable for a WebView environment and preferable to a silent crash. Future improvement: bundle `pdf.worker.min.js` as a local asset.

2. **Firebase Storage CORS:** Fetch works from Capacitor's `https://localhost` origin because Firebase Storage download URLs include CORS headers for all origins when using public storage rules. If custom security rules tighten CORS, downloads may fail.

3. **Drive token refresh:** `getReaderPdfData` relies on the author's Drive OAuth refresh token being valid in Firestore. If the author revokes NOVELIX's Drive access, the callable returns an error which surfaces as `ERR_DRIVE_AUTH_EXPIRED`.

---

## Deliverable Files

| File | Purpose |
|------|---------|
| [`NOVELIX_READER_ROOT_CAUSE_REPORT.md`](./NOVELIX_READER_ROOT_CAUSE_REPORT.md) | Detailed root cause analysis of each bug |
| [`NOVELIX_PDF_INTEGRATION_REPORT.md`](./NOVELIX_PDF_INTEGRATION_REPORT.md) | PDF loading flow, storage schema, security notes |
| [`NOVELIX_READER_TEST_REPORT.md`](./NOVELIX_READER_TEST_REPORT.md) | This file — test results |
| `scripts/generate_4.py` | Master source (all fixes applied) |
| `out/index.html` | Generated SPA |
| `android/app/src/main/assets/public/index.html` | Deployed to Android WebView |
