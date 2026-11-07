# NOVELIX 7.0 — Root Cause Analysis Report

**Generated:** 2026-11-07  
**Project:** NOVELIX Digital Publishing Platform  
**Firebase App ID:** `novelxa-48f15`  
**Package:** `com.novelix.app`

---

## 1. Problem: Unexpected Reader Startup on Launch

### Investigation
In earlier builds, users observed the app occasionally opening directly into a black screen or the PDF reader modal instead of the primary Home screen. 

### Root Causes
1. **Absence of an Explicit Navigation State Controller:**  
   The application startup sequence in `DOMContentLoaded` relied on static HTML classes (`class="app-page active"` on `#page-home` and no `open` on `#readerModal`). However, when the Android OS or WebView restored session state, or if any background event occurred, lingering modal DOM states were not reset.
2. **Automatic Invocation in `resumeReadingProgressBook`:**  
   The function `resumeReadingProgressBook()` previously executed an automatic `setTimeout(() => launchActiveReader(), 200)` without an explicit user tap on "Start Reading".
3. **Orphan PDF Worker & Canvas State:**  
   If a user previously minimized the app while reading, `APP_STATE.pdfDocument` and `APP_STATE.pdfPageNumber` retained old references.

### Corrective Actions
- Implemented `NavigationController.init()` called as the first step of `DOMContentLoaded`:
  - Force removes `.open` from `.modal-fullscreen`, `.modal-sheet`, and `#devTerminal`.
  - Clears `APP_STATE.pdfDocument`, `APP_STATE.pdfIsRendering`, and cancels `_currentRenderTask`.
  - Resets body scroll lock (`document.body.style.overflow = ''`).
  - Explicitly executes `switchPage('home')` to guarantee the Home view is active.
- Refactored `resumeReadingProgressBook` to safely open `openBookDetail()` and highlight `Continue from Page X` rather than auto-launching the reader.
- Created `directResumeBook(..., event)` for the card "Resume" button with `event.stopPropagation()`.

---

## 2. Problem: PDF Fails to Open When Clicking "Read Book"

### Investigation
When clicking "Read Book", the modal appeared, but the reader either crashed, timed out, or threw a JavaScript error.

### Root Causes
1. **Web Worker Cross-Origin Blocking in Capacitor WebView:**  
   PDF.js attempted to spin up a Web Worker from `https://cdnjs.cloudflare.com/.../pdf.worker.min.js`. Inside the Capacitor WebView running at `https://localhost`, cross-origin workers are blocked by default Content Security Policies and Chrome WebView origin isolation. This produced `Setting up fake worker failed` or silent promise rejection.
2. **Missing Reference `initiateGoogleDriveAuth`:**  
   The reader error overlay button called `initiateGoogleDriveAuth()` instead of `initiateGoogleDriveConnection()`, throwing a fatal `TypeError`.
3. **Expired Firebase Storage Tokens:**  
   Storage download URLs saved at publish time can expire. A direct `fetch(edition.fileUrl)` returned `403 Forbidden` without attempting to refresh the URL using the storage path.
4. **Race Conditions on Fast Page Flips:**  
   Calling `renderPdfPage()` rapidly while an existing page was still drawing caused canvas context collisions.

### Corrective Actions
- Configured `{ disableWorker: true }` in `pdfjsLib.getDocument()`, ensuring single-threaded rendering inside the WebView.
- Renamed all dangling references to `initiateGoogleDriveConnection()`.
- Implemented automatic token refresh fallback using `storage.ref(edition.storagePath).getDownloadURL()` when available.
- Added `APP_STATE._currentRenderTask.cancel()` to cleanly abort obsolete page renders.
- Capped device pixel ratio at `2.5` to prevent canvas memory exhaustion on high-density mobile screens.

---

## 3. Problem: Exposed Third-Party Credentials (Security)

### Investigation
A hardcoded ImgBB API key (`a9985ccf572a0e05bce242e27cf8be33`) was embedded in `generate_4.py`, client HTML, and environment files.

### Root Causes
- An initial prototype used ImgBB as a temporary image host and retained the fallback key in production scripts.

### Corrective Actions
- Completely removed the key from client JavaScript, `.env.local`, `README.md`, and `SETUP.md`.
- Converted all book cover and user profile avatar uploads to use authenticated Firebase Storage (`covers/{bookId}/` and `avatars/{uid}/`).

---

## 4. Problem: Publication Editing & Unpublishing Missing

### Investigation
Authors could publish or delete works, but could not edit existing metadata, add new volumes or language editions, or change a publication status to draft or unlisted.

### Root Causes
- `handlePublishSubmit` lacked an update branch; it always generated a new Firestore document ID.

### Corrective Actions
- Created `openEditPublication(bookId)` in `NavigationController`.
- Prepopulated publishing form fields and set `APP_STATE.editingBookId`.
- Updated `handlePublishSubmit` to execute `db.collection('books').doc(bookId).update(...)` when editing.
- Added an "Edit" button next to "View" and "Delete" in the author's Works tab in Profile.
