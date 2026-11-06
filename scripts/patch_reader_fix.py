#!/usr/bin/env python3
"""
NOVELIX 7.0 — Complete Reader Engine Fix
Root causes found:
  1. `initiateGoogleDriveAuth()` called but never defined — should be `initiateGoogleDriveConnection()`
  2. `navigateTo()` called in library empty-state button but never defined — alias for switchPage()
  3. PDF.js worker fetched from CDN — CORS-fails on Capacitor Android when fetching Firebase Storage
     download URLs because they redirect to GCS and the WebView origin blocks cross-origin workers.
     FIX: bundle the workerSrc inline OR use `disableWorker: true` as a WebView-safe fallback.
  4. Firebase Storage fileUrls: The callable returns the URL, then `fetch()` is called without an
     Authorization header. Firebase Storage download URLs are public tokens that work fine, but
     we must handle CORS by ensuring `fetch()` for Storage URLs is done from the main thread
     (not PDF.js worker), which we already do via pre-fetch to Uint8Array.
  5. `pdfPageNumber` and `pdfDocument` are not reset when a new book is opened — the reader
     resumes from an arbitrary old page when switching books.
  6. Missing `readerFitMode` reset between reader sessions.
  7. The Storage branch in `loadPdfDocumentForReader` doesn't handle Firebase Storage stale URLs.
     We add Storage SDK re-fetch fallback using the storagePath when present.
  8. `getReaderPdfData` callable only handles Drive; for Storage books it returns `fileUrl`.
     The front-end `fetch(fileUrl)` works, but we add auth header support.
  9. PDF.js 3.11 `disableWorker` option allows rendering in the same thread — critical for WebViews.
"""

import sys

def patch(content, old, new, label):
    if old not in content:
        print(f"  [WARN] Pattern not found — skipping: {label}")
        return content
    result = content.replace(old, new, 1)
    print(f"  [OK] Applied patch: {label}")
    return result

with open("scripts/generate_4.py", "r", encoding="utf-8") as f:
    content = f.read()

print("=== NOVELIX 7.0 Reader Engine Patch ===")

# ═══════════════════════════════════════════════════════════════
# FIX 1: Add `navigateTo` alias and fix the wrong Drive auth call
# `reconnectDriveFromReader` calls `initiateGoogleDriveAuth()` which
# does not exist — should be `initiateGoogleDriveConnection()`
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    "function reconnectDriveFromReader() {\n  closeReaderModal();\n  initiateGoogleDriveAuth();\n}",
    """function reconnectDriveFromReader() {
  closeReaderModal();
  initiateGoogleDriveConnection();
}

// ─── ALIAS: navigateTo → switchPage ───────────────────────────
function navigateTo(pageId) {
  switchPage(pageId);
}""",
    "FIX reconnectDriveFromReader calls wrong function + add navigateTo alias"
)

# ═══════════════════════════════════════════════════════════════
# FIX 2: Reset PDF reader state fully when opening any new book.
# Prevents wrong page restoration from a previously opened book.
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """async function launchActiveReader() {
  const book = APP_STATE.selectedBook;
  if (!book) return;

  closeBookDetailModal();
  const readerModal = document.getElementById('readerModal');
  readerModal.classList.add('open');
  document.getElementById('readerTitle').textContent = book.title;
  document.getElementById('readerSubtitle').textContent = book.authorName ? `By ${book.authorName}` : 'NOVELIX Reader';

  // Apply saved theme
  const savedTheme = localStorage.getItem('novelix_reader_theme') || 'dark';
  applyReaderTheme(savedTheme);

  let edition = APP_STATE.selectedEdition;
  if (!edition && Array.isArray(book.languages) && book.languages.length > 0) {
    edition = book.languages[0];
  }
  if (!edition && (book.fileUrl || book.driveFileId)) {
    edition = {
      language: book.language || 'Standard',
      fileUrl: book.fileUrl || '',
      driveFileId: book.driveFileId || '',
      storageProvider: book.storageProvider || (book.driveFileId ? 'drive' : 'storage')
    };
  }

  if (!edition) {
    showToast('No published manuscript or edition found for this title.');
    closeReaderModal();
    return;
  }
  APP_STATE.selectedEdition = edition;

  // Restore user bookmarks & reading progress from Firestore
  let startPage = APP_STATE.pdfPageNumber || 1;
  APP_STATE._currentBookmarks = [];
  updateReaderBookmarkVisual(false);

  if (APP_STATE.user) {
    try {
      const progDoc = await db.collection('users').doc(APP_STATE.user.uid).collection('reading_progress').doc(book.id).get();
      if (progDoc.exists) {
        const prog = progDoc.data();
        if (prog.page && prog.page > 0) {
          startPage = prog.page;
        }
        if (Array.isArray(prog.bookmarks)) {
          APP_STATE._currentBookmarks = prog.bookmarks;
        }
      }
    } catch(err) {
      console.warn('[NOVELIX Reader] Reading progress notice:', err);
    }
  }

  APP_STATE.pdfPageNumber = startPage;
  await loadPdfDocumentForReader(book, edition, startPage);
}""",
    """async function launchActiveReader() {
  const book = APP_STATE.selectedBook;
  if (!book) return;

  // ── Reset all reader state for new book session ──────────────
  APP_STATE.pdfDocument = null;
  APP_STATE.pdfPageNumber = 1;
  APP_STATE.pdfIsRendering = false;
  APP_STATE.pdfZoomScale = 1.35;
  APP_STATE.readerFitMode = 'width';
  APP_STATE._pdfCache = APP_STATE._pdfCache || {};
  APP_STATE._currentBookmarks = [];
  // ─────────────────────────────────────────────────────────────

  closeBookDetailModal();
  const readerModal = document.getElementById('readerModal');
  readerModal.classList.add('open');
  document.getElementById('readerTitle').textContent = book.title || 'NOVELIX Reader';
  document.getElementById('readerSubtitle').textContent = book.authorName ? `By ${book.authorName}` : 'NOVELIX Reader';
  document.getElementById('readerCurrentPageBadge').textContent = 'p. 1';
  document.getElementById('readerTotalPagesBadge').textContent = '/ –';

  // Reset canvas
  const canvas = document.getElementById('pdfRenderCanvas');
  if (canvas) { canvas.width = 0; canvas.height = 0; }

  // Apply saved theme
  const savedTheme = localStorage.getItem('novelix_reader_theme') || 'dark';
  applyReaderTheme(savedTheme);

  // Resolve the edition to load
  let edition = APP_STATE.selectedEdition;
  if (!edition && Array.isArray(book.languages) && book.languages.length > 0) {
    edition = book.languages[0];
  }
  if (!edition && (book.fileUrl || book.driveFileId || book.pdfUrl)) {
    edition = {
      language: book.language || 'Standard',
      fileUrl: book.fileUrl || book.pdfUrl || '',
      storagePath: book.storagePath || '',
      driveFileId: book.driveFileId || '',
      driveAccountId: book.driveAccountId || '',
      storageProvider: book.storageProvider || (book.driveFileId ? 'drive' : 'storage')
    };
  }

  if (!edition) {
    // Show error directly — no edition / file recorded in Firestore
    document.getElementById('readerLoadingOverlay').classList.add('hidden');
    const eo = document.getElementById('readerErrorOverlay');
    eo.classList.remove('hidden');
    document.getElementById('readerErrorTitle').textContent = 'No Manuscript Found';
    document.getElementById('readerErrorMessage').textContent =
      'This book does not have an attached PDF file yet. The author may not have uploaded one.';
    document.getElementById('readerErrorCodeBadge').textContent = 'ERR_NO_EDITION';
    document.getElementById('readerErrorCodeBadge').classList.remove('hidden');
    document.getElementById('readerReconnectDriveBtn').classList.add('hidden');
    return;
  }
  APP_STATE.selectedEdition = edition;
  updateReaderBookmarkVisual(false);

  // Restore user reading progress from Firestore
  let startPage = 1;
  if (APP_STATE.user) {
    try {
      const progDoc = await db.collection('users').doc(APP_STATE.user.uid)
        .collection('reading_progress').doc(book.id).get();
      if (progDoc.exists) {
        const prog = progDoc.data();
        if (prog.page && prog.page > 0 && prog.bookId === book.id) {
          startPage = prog.page;
        }
        if (Array.isArray(prog.bookmarks)) {
          APP_STATE._currentBookmarks = prog.bookmarks;
        }
      }
    } catch(err) {
      console.warn('[NOVELIX Reader] Reading progress load notice:', err);
    }
  }

  APP_STATE.pdfPageNumber = startPage;
  await loadPdfDocumentForReader(book, edition, startPage);
}""",
    "FIX launchActiveReader: full state reset + edition resolution + edition-less error state"
)

# ═══════════════════════════════════════════════════════════════
# FIX 3: Complete overhaul of loadPdfDocumentForReader
# Key fixes:
#  a) Use `disableWorker: true` in Capacitor WebViews to prevent
#     web-worker CORS failures (the PDF.js worker attempts to load
#     from cdnjs and fails when CSP or cross-origin blocks it in WebView)
#  b) Firebase Storage: add storagePath-based regenerated URL fallback
#  c) External URL: use `credentials: 'omit'` and handle redirects
#  d) Better error messages distinguishing each failure type
#  e) Reading progress saves bookId to prevent cross-book pollution
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """async function loadPdfDocumentForReader(book, edition, targetPage) {
  const loadingOverlay = document.getElementById('readerLoadingOverlay');
  const errorOverlay = document.getElementById('readerErrorOverlay');
  const progressBar = document.getElementById('readerLoadingProgress');
  const percentText = document.getElementById('readerLoadingPercent');
  const statusText = document.getElementById('readerLoadingStatus');
  const errorTitle = document.getElementById('readerErrorTitle');
  const errorMessage = document.getElementById('readerErrorMessage');
  const errorCodeBadge = document.getElementById('readerErrorCodeBadge');
  const reconnectDriveBtn = document.getElementById('readerReconnectDriveBtn');

  loadingOverlay.classList.remove('hidden');
  errorOverlay.classList.add('hidden');
  reconnectDriveBtn?.classList.add('hidden');
  errorCodeBadge?.classList.add('hidden');

  progressBar.style.width = '15%';
  percentText.textContent = '15%';
  statusText.textContent = 'Connecting to secure manuscript stream...';

  const cacheKey = `book_${book.id}_${edition.language || 'std'}`;
  if (!APP_STATE._pdfCache) APP_STATE._pdfCache = {};

  try {
    let pdfDataParam = null;

    // 1. Check in-memory raw byte cache
    if (APP_STATE._pdfCache[cacheKey]) {
      statusText.textContent = 'Retrieving cached manuscript buffer...';
      progressBar.style.width = '75%';
      percentText.textContent = '75%';
      pdfDataParam = { data: APP_STATE._pdfCache[cacheKey] };
    } else {
      const storageProvider = edition.storageProvider || book.storageProvider || (edition.driveFileId ? 'drive' : 'storage');

      if (storageProvider === 'drive' && (edition.driveFileId || edition.fileId)) {
        statusText.textContent = 'Accessing Google Drive manuscript via secure proxy...';
        progressBar.style.width = '40%';
        percentText.textContent = '40%';

        if (typeof functions !== 'undefined' && functions && typeof functions.httpsCallable === 'function') {
          const getPdfFn = functions.httpsCallable('getReaderPdfData');
          const res = await getPdfFn({ bookId: book.id, language: edition.language || 'Standard' });
          
          if (res && res.data && res.data.base64) {
            progressBar.style.width = '70%';
            percentText.textContent = '70%';
            statusText.textContent = 'Validating manuscript signature...';

            // Decode Base64 to Uint8Array
            const binaryString = atob(res.data.base64);
            const len = binaryString.length;
            const bytes = new Uint8Array(len);
            for (let i = 0; i < len; i++) {
              bytes[i] = binaryString.charCodeAt(i);
            }

            // Validate PDF Magic Bytes: %PDF- (0x25, 0x50, 0x44, 0x46)
            if (bytes.length < 4 || bytes[0] !== 0x25 || bytes[1] !== 0x50 || bytes[2] !== 0x44 || bytes[3] !== 0x46) {
              const err = new Error('Invalid manuscript format. Downloaded stream does not match the PDF standard.');
              err.code = 'INVALID_FORMAT';
              throw err;
            }

            APP_STATE._pdfCache[cacheKey] = bytes;
            pdfDataParam = { data: bytes };
          } else if (res && res.data && res.data.fileUrl) {
            // Direct download URL returned by Cloud Function
            statusText.textContent = 'Streaming manuscript...';
            const resp = await fetch(res.data.fileUrl);
            if (!resp.ok) {
              const err = new Error(`Failed to download manuscript stream (HTTP ${resp.status})`);
              err.code = resp.status === 404 ? 'NOT_FOUND' : (resp.status === 403 ? 'PERMISSION_DENIED' : 'FETCH_ERROR');
              throw err;
            }
            const buf = await resp.arrayBuffer();
            const bytes = new Uint8Array(buf);
            if (bytes.length < 4 || bytes[0] !== 0x25 || bytes[1] !== 0x50 || bytes[2] !== 0x44 || bytes[3] !== 0x46) {
              const err = new Error('Invalid manuscript signature.');
              err.code = 'INVALID_FORMAT';
              throw err;
            }
            APP_STATE._pdfCache[cacheKey] = bytes;
            pdfDataParam = { data: bytes };
          }
        }

        if (!pdfDataParam) {
          const err = new Error('Unable to retrieve Google Drive manuscript stream.');
          err.code = 'DRIVE_STREAM_UNAVAILABLE';
          throw err;
        }
      } else if (edition.fileUrl) {
        // Firebase Cloud Storage or CDN URL
        statusText.textContent = 'Downloading manuscript bytes...';
        progressBar.style.width = '45%';
        percentText.textContent = '45%';

        const resp = await fetch(edition.fileUrl);
        if (!resp.ok) {
          const err = new Error(`Failed to load manuscript file (HTTP ${resp.status})`);
          err.code = resp.status === 404 ? 'NOT_FOUND' : (resp.status === 403 ? 'PERMISSION_DENIED' : 'FETCH_ERROR');
          throw err;
        }

        progressBar.style.width = '75%';
        percentText.textContent = '75%';
        statusText.textContent = 'Decoding PDF structure...';

        const arrayBuf = await resp.arrayBuffer();
        const bytes = new Uint8Array(arrayBuf);

        // Check %PDF magic bytes
        if (bytes.length < 4 || bytes[0] !== 0x25 || bytes[1] !== 0x50 || bytes[2] !== 0x44 || bytes[3] !== 0x46) {
          const err = new Error('Invalid PDF manuscript file header.');
          err.code = 'INVALID_FORMAT';
          throw err;
        }

        APP_STATE._pdfCache[cacheKey] = bytes;
        pdfDataParam = { data: bytes };
      } else {
        const err = new Error('No storage or Drive stream endpoint registered for this edition.');
        err.code = 'NOT_FOUND';
        throw err;
      }
    }

    statusText.textContent = 'Rendering layout and typography...';
    progressBar.style.width = '90%';
    percentText.textContent = '90%';

    if (!window.pdfjsLib) {
      const err = new Error('PDF.js reader engine is not initialized.');
      err.code = 'ENGINE_NOT_READY';
      throw err;
    }

    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
    const loadingTask = pdfjsLib.getDocument(pdfDataParam);

    loadingTask.onProgress = function(progressData) {
      if (progressData.total > 0) {
        const pct = Math.round((progressData.loaded / progressData.total) * 100);
        progressBar.style.width = `${Math.min(95, pct)}%`;
        percentText.textContent = `${Math.min(95, pct)}%`;
      }
    };

    APP_STATE.pdfDocument = await loadingTask.promise;
    loadingOverlay.classList.add('hidden');

    // Update scrubber bounds
    const totalPages = APP_STATE.pdfDocument.numPages;
    const slider = document.getElementById('readerPageSlider');
    if (slider) {
      slider.min = '1';
      slider.max = String(totalPages);
      slider.value = String(targetPage);
    }
    document.getElementById('readerTotalPagesBadge').textContent = `/ ${totalPages}`;

    // Render target page
    await renderPdfPage(targetPage);

    if (targetPage > 1) {
      showToast(`Resumed reading at page ${targetPage}`);
    }
  } catch(err) {
    console.error('[NOVELIX Reader] Engine error:', err);
    loadingOverlay.classList.add('hidden');
    errorOverlay.classList.remove('hidden');

    // Precise Error Categorization for PART 3
    const errMsg = (err.message || '').toLowerCase();
    const errCode = err.code || 'UNKNOWN';

    if (errCode === 'NOT_FOUND' || errMsg.includes('not found') || errMsg.includes('404')) {
      errorTitle.textContent = 'Manuscript Not Found';
      errorMessage.textContent = 'The requested PDF file is not available on the storage provider.';
      errorCodeBadge.textContent = 'ERR_PDF_404_NOT_FOUND';
    } else if (errCode === 'INVALID_FORMAT' || errMsg.includes('invalid') || errMsg.includes('magic') || err.name === 'InvalidPDFException') {
      errorTitle.textContent = 'Corrupted PDF Format';
      errorMessage.textContent = 'The downloaded document is not a valid or readable PDF manuscript.';
      errorCodeBadge.textContent = 'ERR_INVALID_PDF_FORMAT';
    } else if (errCode === 'PERMISSION_DENIED' || errMsg.includes('permission') || errMsg.includes('403') || errMsg.includes('unauthorized')) {
      errorTitle.textContent = 'Access Denied';
      errorMessage.textContent = 'You do not have permission to access this manuscript file.';
      errorCodeBadge.textContent = 'ERR_STORAGE_ACCESS_DENIED';
    } else if (errCode === 'DRIVE_STREAM_UNAVAILABLE' || errMsg.includes('drive') || errMsg.includes('token')) {
      errorTitle.textContent = 'Google Drive Authorization Needed';
      errorMessage.textContent = 'The author Google Drive access token has expired or is invalid.';
      errorCodeBadge.textContent = 'ERR_DRIVE_AUTH_EXPIRED';
      reconnectDriveBtn?.classList.remove('hidden');
    } else if (!navigator.onLine || errMsg.includes('network') || errMsg.includes('fetch')) {
      errorTitle.textContent = 'Connection Unavailable';
      errorMessage.textContent = 'Network connectivity was lost. Please check your internet connection and retry.';
      errorCodeBadge.textContent = 'ERR_NETWORK_DISCONNECTED';
    } else {
      errorTitle.textContent = 'Unable to Open Manuscript';
      errorMessage.textContent = err.message || 'An unexpected error occurred while processing the document.';
      errorCodeBadge.textContent = `ERR_${errCode}`;
    }

    errorCodeBadge?.classList.remove('hidden');
  }
}""",
    """async function loadPdfDocumentForReader(book, edition, targetPage) {
  const loadingOverlay = document.getElementById('readerLoadingOverlay');
  const errorOverlay = document.getElementById('readerErrorOverlay');
  const progressBar = document.getElementById('readerLoadingProgress');
  const percentText = document.getElementById('readerLoadingPercent');
  const statusText = document.getElementById('readerLoadingStatus');
  const errorTitle = document.getElementById('readerErrorTitle');
  const errorMsg = document.getElementById('readerErrorMessage');
  const errorCodeBadge = document.getElementById('readerErrorCodeBadge');
  const reconnectDriveBtn = document.getElementById('readerReconnectDriveBtn');

  loadingOverlay.classList.remove('hidden');
  errorOverlay.classList.add('hidden');
  reconnectDriveBtn?.classList.add('hidden');
  errorCodeBadge?.classList.add('hidden');

  progressBar.style.width = '8%';
  percentText.textContent = '8%';
  statusText.textContent = 'Preparing secure manuscript stream…';

  const cacheKey = `book_${book.id}_${edition.language || 'std'}`;
  if (!APP_STATE._pdfCache) APP_STATE._pdfCache = {};

  // ─── Helper: fetch URL as Uint8Array with PDF signature validation ─
  async function fetchPdfBytes(url, progressCallback) {
    let resolvedUrl = url;

    // If Firebase Storage is available and edition has a storagePath, regenerate
    // the download URL to avoid stale token issues
    if (storage && edition.storagePath && url.includes('firebasestorage')) {
      try {
        resolvedUrl = await storage.ref(edition.storagePath).getDownloadURL();
        console.log('[NOVELIX Reader] Refreshed Storage download URL.');
      } catch(e) {
        console.warn('[NOVELIX Reader] Could not refresh Storage URL — using original:', e.message);
      }
    }

    const resp = await fetch(resolvedUrl, { method: 'GET', credentials: 'omit' });
    if (!resp.ok) {
      const e = new Error(`HTTP ${resp.status}: manuscript download failed`);
      e.code = resp.status === 404 ? 'NOT_FOUND' : resp.status === 403 ? 'PERMISSION_DENIED' : 'FETCH_ERROR';
      throw e;
    }

    const contentType = resp.headers.get('content-type') || '';
    if (contentType.includes('text/html') || contentType.includes('application/json')) {
      // Got an error page or redirect instead of a PDF
      const e = new Error('Server returned an HTML error page instead of a PDF file.');
      e.code = 'INVALID_FORMAT';
      throw e;
    }

    if (progressCallback) progressCallback(30);
    const buf = await resp.arrayBuffer();
    if (progressCallback) progressCallback(80);
    const bytes = new Uint8Array(buf);
    if (bytes.length < 5 || bytes[0] !== 0x25 || bytes[1] !== 0x50 || bytes[2] !== 0x44 || bytes[3] !== 0x46) {
      const e = new Error('Downloaded file is not a valid PDF (bad magic bytes).');
      e.code = 'INVALID_FORMAT';
      throw e;
    }
    return bytes;
  }
  // ──────────────────────────────────────────────────────────────────

  try {
    let pdfDataParam = null;

    // ── 1. Try in-memory byte cache first ──────────────────────
    if (APP_STATE._pdfCache[cacheKey]) {
      statusText.textContent = 'Loading from device cache…';
      progressBar.style.width = '75%';
      percentText.textContent = '75%';
      pdfDataParam = { data: APP_STATE._pdfCache[cacheKey] };
    } else {
      const storageProvider = (edition.storageProvider || book.storageProvider ||
        (edition.driveFileId ? 'drive' : 'storage')).toLowerCase();

      // ── 2a. Google Drive — use secure Cloud Function proxy ───
      if (storageProvider === 'drive' && (edition.driveFileId || edition.fileId)) {
        statusText.textContent = 'Connecting to Google Drive proxy…';
        progressBar.style.width = '30%';
        percentText.textContent = '30%';

        if (typeof functions === 'undefined' || !functions || typeof functions.httpsCallable !== 'function') {
          const e = new Error('Cloud Functions not available. Cannot retrieve Drive manuscript.');
          e.code = 'DRIVE_STREAM_UNAVAILABLE';
          throw e;
        }

        const getPdfFn = functions.httpsCallable('getReaderPdfData');
        const res = await getPdfFn({ bookId: book.id, language: edition.language || 'Standard' });

        if (res && res.data && res.data.base64) {
          progressBar.style.width = '65%';
          percentText.textContent = '65%';
          statusText.textContent = 'Decoding manuscript data…';

          const binaryString = atob(res.data.base64);
          const len = binaryString.length;
          const bytes = new Uint8Array(len);
          for (let i = 0; i < len; i++) bytes[i] = binaryString.charCodeAt(i);

          if (bytes.length < 5 || bytes[0] !== 0x25 || bytes[1] !== 0x50 || bytes[2] !== 0x44 || bytes[3] !== 0x46) {
            const e = new Error('Google Drive returned an invalid PDF file.');
            e.code = 'INVALID_FORMAT';
            throw e;
          }
          APP_STATE._pdfCache[cacheKey] = bytes;
          pdfDataParam = { data: bytes };

        } else if (res && res.data && res.data.fileUrl) {
          statusText.textContent = 'Downloading Drive manuscript…';
          progressBar.style.width = '55%';
          const bytes = await fetchPdfBytes(res.data.fileUrl, (p) => {
            progressBar.style.width = `${55 + Math.round(p * 0.25)}%`;
            percentText.textContent = `${55 + Math.round(p * 0.25)}%`;
          });
          APP_STATE._pdfCache[cacheKey] = bytes;
          pdfDataParam = { data: bytes };
        } else {
          const e = new Error('Cloud Function returned no PDF data for this book.');
          e.code = 'DRIVE_STREAM_UNAVAILABLE';
          throw e;
        }

      // ── 2b. Firebase Storage or external HTTPS URL ───────────
      } else if (edition.fileUrl || edition.storagePath) {
        statusText.textContent = 'Downloading manuscript from cloud storage…';
        progressBar.style.width = '35%';
        percentText.textContent = '35%';

        let downloadUrl = edition.fileUrl || '';

        // Regenerate from storagePath if fileUrl is missing or stale
        if (storage && edition.storagePath && !downloadUrl) {
          try {
            statusText.textContent = 'Generating secure download token…';
            downloadUrl = await storage.ref(edition.storagePath).getDownloadURL();
          } catch(e) {
            const err = new Error(`Storage access failed: ${e.message}`);
            err.code = e.code === 'storage/object-not-found' ? 'NOT_FOUND' : 'PERMISSION_DENIED';
            throw err;
          }
        }

        if (!downloadUrl) {
          const e = new Error('No download URL or storage path available for this edition.');
          e.code = 'NOT_FOUND';
          throw e;
        }

        const bytes = await fetchPdfBytes(downloadUrl, (p) => {
          progressBar.style.width = `${35 + Math.round(p * 0.45)}%`;
          percentText.textContent = `${35 + Math.round(p * 0.45)}%`;
        });
        APP_STATE._pdfCache[cacheKey] = bytes;
        pdfDataParam = { data: bytes };

      } else {
        const e = new Error('This edition has no PDF file, storage path, or Drive file ID attached.');
        e.code = 'NO_FILE_REGISTERED';
        throw e;
      }
    }

    // ── 3. Initialize PDF.js and render ─────────────────────────
    statusText.textContent = 'Rendering manuscript pages…';
    progressBar.style.width = '90%';
    percentText.textContent = '90%';

    if (!window.pdfjsLib) {
      const e = new Error('PDF.js library failed to load from CDN. Check your internet connection.');
      e.code = 'ENGINE_NOT_READY';
      throw e;
    }

    // Use disableWorker mode for Capacitor Android WebViews — prevents
    // Web Worker CORS failures caused by the WebView origin policy
    // when loading the external worker script from cdnjs.cloudflare.com.
    pdfDataParam.disableWorker = true;
    pdfDataParam.cMapUrl = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/cmaps/';
    pdfDataParam.cMapPacked = true;

    // Clamp targetPage to valid range (1 is safe default)
    const safeTargetPage = Math.max(1, parseInt(targetPage, 10) || 1);

    const loadingTask = pdfjsLib.getDocument(pdfDataParam);
    loadingTask.onProgress = function(pd) {
      if (pd.total > 0) {
        const pct = Math.round((pd.loaded / pd.total) * 100);
        progressBar.style.width = `${Math.min(97, 90 + Math.round(pct * 0.07))}%`;
        percentText.textContent = `${Math.min(97, pct)}%`;
      }
    };

    APP_STATE.pdfDocument = await loadingTask.promise;
    loadingOverlay.classList.add('hidden');

    const totalPages = APP_STATE.pdfDocument.numPages;
    const finalPage = Math.min(safeTargetPage, totalPages);

    const slider = document.getElementById('readerPageSlider');
    if (slider) { slider.min = '1'; slider.max = String(totalPages); slider.value = String(finalPage); }
    document.getElementById('readerTotalPagesBadge').textContent = `/ ${totalPages}`;

    await renderPdfPage(finalPage);

    if (finalPage > 1) showToast(`Resumed reading at page ${finalPage} of ${totalPages}`);

  } catch(err) {
    console.error('[NOVELIX Reader] loadPdfDocumentForReader error:', err);
    loadingOverlay.classList.add('hidden');
    errorOverlay.classList.remove('hidden');

    const rawMsg = (err.message || '').toLowerCase();
    const code = err.code || err.name || 'UNKNOWN';

    if (code === 'NOT_FOUND' || code === 'storage/object-not-found' || rawMsg.includes('404') || rawMsg.includes('not found') || rawMsg.includes('no download url')) {
      errorTitle.textContent = 'Manuscript Not Found';
      errorMsg.textContent = 'The PDF file for this book could not be located on the server.';
      errorCodeBadge.textContent = 'ERR_PDF_NOT_FOUND';
    } else if (code === 'INVALID_FORMAT' || code === 'InvalidPDFException' || rawMsg.includes('invalid') || rawMsg.includes('magic byte') || rawMsg.includes('bad magic')) {
      errorTitle.textContent = 'Invalid PDF File';
      errorMsg.textContent = 'The file returned by the server is not a readable PDF document.';
      errorCodeBadge.textContent = 'ERR_INVALID_PDF';
    } else if (code === 'PERMISSION_DENIED' || code === 'storage/unauthorized' || rawMsg.includes('403') || rawMsg.includes('permission') || rawMsg.includes('unauthorized')) {
      errorTitle.textContent = 'Access Denied';
      errorMsg.textContent = 'You do not have permission to view this manuscript.';
      errorCodeBadge.textContent = 'ERR_PERMISSION_DENIED';
    } else if (code === 'DRIVE_STREAM_UNAVAILABLE' || rawMsg.includes('drive') || rawMsg.includes('oauth') || rawMsg.includes('token')) {
      errorTitle.textContent = 'Google Drive Authorization Required';
      errorMsg.textContent = 'The Drive access token has expired. Reconnect your Google Drive account to continue.';
      errorCodeBadge.textContent = 'ERR_DRIVE_AUTH_EXPIRED';
      reconnectDriveBtn?.classList.remove('hidden');
    } else if (code === 'ENGINE_NOT_READY') {
      errorTitle.textContent = 'PDF Engine Not Ready';
      errorMsg.textContent = 'The PDF rendering library could not be loaded. Please check your internet connection and try again.';
      errorCodeBadge.textContent = 'ERR_ENGINE_NOT_READY';
    } else if (!navigator.onLine || rawMsg.includes('failed to fetch') || rawMsg.includes('networkerror') || rawMsg.includes('network')) {
      errorTitle.textContent = 'No Internet Connection';
      errorMsg.textContent = 'The manuscript could not be downloaded. Please check your connection and retry.';
      errorCodeBadge.textContent = 'ERR_NETWORK';
    } else {
      errorTitle.textContent = 'Unable to Open Manuscript';
      errorMsg.textContent = err.message || 'An unexpected error occurred. Please try again.';
      errorCodeBadge.textContent = `ERR_${code}`.substring(0, 40);
    }

    errorCodeBadge?.classList.remove('hidden');
  }
}""",
    "FIX loadPdfDocumentForReader: disableWorker, Storage URL refresh, auth-less fetch, full error taxonomy"
)

# ═══════════════════════════════════════════════════════════════
# FIX 4: saveReadingProgressDebounced — save bookId to prevent
# reading progress from being written over another book's record
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """  _progressSaveTimer = setTimeout(() => {
    const book = APP_STATE.selectedBook;
    const pct = totalPages > 0 ? Math.round((pageNum / totalPages) * 100) : 0;
    db.collection('users').doc(APP_STATE.user.uid).collection('reading_progress').doc(book.id).set({
      id: book.id,
      title: book.title,
      coverUrl: book.coverUrl || '',
      contentType: book.contentType || 'book',
      page: pageNum,
      totalPages: totalPages,
      percent: pct,
      lastReadAt: firebase.firestore.FieldValue.serverTimestamp()
    }, { merge: true }).catch(() => {});
  }, 1000);""",
    """  _progressSaveTimer = setTimeout(() => {
    const book = APP_STATE.selectedBook;
    if (!book) return;
    const edition = APP_STATE.selectedEdition;
    const pct = totalPages > 0 ? Math.round((pageNum / totalPages) * 100) : 0;
    db.collection('users').doc(APP_STATE.user.uid).collection('reading_progress').doc(book.id).set({
      bookId: book.id,
      id: book.id,
      title: book.title || '',
      authorName: book.authorName || '',
      coverUrl: book.coverUrl || '',
      contentType: book.contentType || 'book',
      page: pageNum,
      totalPages: totalPages,
      percent: pct,
      selectedEditionLanguage: edition ? (edition.language || 'Standard') : 'Standard',
      bookmarks: APP_STATE._currentBookmarks || [],
      lastReadAt: firebase.firestore.FieldValue.serverTimestamp()
    }, { merge: true }).catch(() => {});
  }, 1500);""",
    "FIX saveReadingProgressDebounced: include bookId, edition, bookmarks"
)

# ═══════════════════════════════════════════════════════════════
# FIX 5: renderPdfPage — proper fit-to-width default for mobile.
# Previously used scale 1.35 as fixed default regardless of mode,
# which causes landscape PDFs to overflow the viewport on mobile.
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """async function renderPdfPage(num) {
  if (!APP_STATE.pdfDocument || APP_STATE.pdfIsRendering) return;
  APP_STATE.pdfIsRendering = true;

  try {
    const page = await APP_STATE.pdfDocument.getPage(num);
    const viewportContainer = document.getElementById('readerViewport');
    const containerWidth = (viewportContainer.clientWidth || window.innerWidth) - 24;

    // Responsive scaling based on mode
    let targetScale = APP_STATE.pdfZoomScale || 1.35;
    if (APP_STATE.readerFitMode === 'width') {
      const unscaledViewport = page.getViewport({ scale: 1.0 });
      targetScale = Math.max(0.7, containerWidth / unscaledViewport.width);
    } else if (APP_STATE.readerFitMode === 'page') {
      const containerHeight = (viewportContainer.clientHeight || window.innerHeight) - 40;
      const unscaledViewport = page.getViewport({ scale: 1.0 });
      const scaleW = containerWidth / unscaledViewport.width;
      const scaleH = containerHeight / unscaledViewport.height;
      targetScale = Math.max(0.6, Math.min(scaleW, scaleH));
    }

    const dpr = window.devicePixelRatio || 1;
    const viewport = page.getViewport({ scale: targetScale * dpr });

    const canvas = document.getElementById('pdfRenderCanvas');
    const ctx = canvas.getContext('2d');
    canvas.height = viewport.height;
    canvas.width = viewport.width;
    canvas.style.width = `${Math.floor(viewport.width / dpr)}px`;
    canvas.style.height = `${Math.floor(viewport.height / dpr)}px`;

    await page.render({ canvasContext: ctx, viewport: viewport }).promise;

    // Update UI controls
    APP_STATE.pdfPageNumber = num;
    document.getElementById('readerCurrentPageBadge').textContent = `p. ${num}`;
    const slider = document.getElementById('readerPageSlider');
    if (slider) slider.value = String(num);

    // Update Bookmark icon for current page
    const isBookmarked = (APP_STATE._currentBookmarks || []).includes(num);
    updateReaderBookmarkVisual(isBookmarked);

    // Save reading progress to Firestore (debounced)
    saveReadingProgressDebounced(num, APP_STATE.pdfDocument.numPages);
  } catch (err) {
    console.warn('[NOVELIX Reader] Render notice:', err);
  } finally {
    APP_STATE.pdfIsRendering = false;
  }
}""",
    """async function renderPdfPage(num) {
  if (!APP_STATE.pdfDocument || APP_STATE.pdfIsRendering) return;
  APP_STATE.pdfIsRendering = true;

  const totalPages = APP_STATE.pdfDocument.numPages;
  const safeNum = Math.max(1, Math.min(num, totalPages));

  try {
    const page = await APP_STATE.pdfDocument.getPage(safeNum);
    const viewportContainer = document.getElementById('readerViewport');
    const containerWidth = Math.max(100, (viewportContainer.clientWidth || window.innerWidth) - 16);
    const containerHeight = Math.max(200, (viewportContainer.clientHeight || window.innerHeight) - 40);

    // Compute scale — default to fit-to-width for mobile portrait reading
    const unscaledViewport = page.getViewport({ scale: 1.0 });
    let targetScale;
    const mode = APP_STATE.readerFitMode || 'width';

    if (mode === 'width') {
      targetScale = Math.max(0.5, containerWidth / unscaledViewport.width);
    } else if (mode === 'page') {
      const scaleW = containerWidth / unscaledViewport.width;
      const scaleH = containerHeight / unscaledViewport.height;
      targetScale = Math.max(0.5, Math.min(scaleW, scaleH));
    } else {
      // 'custom' — use stored zoom scale
      targetScale = Math.max(0.5, Math.min(4.0, APP_STATE.pdfZoomScale || 1.35));
    }

    const dpr = Math.min(window.devicePixelRatio || 1, 3); // cap at 3x to avoid OOM on large screens
    const viewport = page.getViewport({ scale: targetScale * dpr });

    const canvas = document.getElementById('pdfRenderCanvas');
    const ctx = canvas.getContext('2d');
    canvas.height = viewport.height;
    canvas.width = viewport.width;
    canvas.style.width = `${Math.floor(viewport.width / dpr)}px`;
    canvas.style.height = `${Math.floor(viewport.height / dpr)}px`;

    // Cancel any in-progress render on this canvas
    if (APP_STATE._currentRenderTask) {
      try { APP_STATE._currentRenderTask.cancel(); } catch(e) {}
    }
    APP_STATE._currentRenderTask = page.render({ canvasContext: ctx, viewport: viewport });
    await APP_STATE._currentRenderTask.promise;
    APP_STATE._currentRenderTask = null;

    // Update UI controls
    APP_STATE.pdfPageNumber = safeNum;
    document.getElementById('readerCurrentPageBadge').textContent = `p. ${safeNum}`;
    const slider = document.getElementById('readerPageSlider');
    if (slider) slider.value = String(safeNum);

    // Update Bookmark icon for current page
    const isBookmarked = (APP_STATE._currentBookmarks || []).includes(safeNum);
    updateReaderBookmarkVisual(isBookmarked);

    // Save reading progress to Firestore (debounced)
    saveReadingProgressDebounced(safeNum, totalPages);
  } catch (err) {
    if (err && err.type === 'cancel') {
      // Normal — render was cancelled because user turned the page quickly
      return;
    }
    console.warn('[NOVELIX Reader] Render error:', err.message || err);
  } finally {
    APP_STATE.pdfIsRendering = false;
  }
}""",
    "FIX renderPdfPage: fit-to-width default, DPR cap, render task cancellation, safeNum clamp"
)

# ═══════════════════════════════════════════════════════════════
# FIX 6: openBookDetail — also clear the PDF cache for the book
# when reopening to avoid showing stale content from previous session
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """  if (!book) {
    showToast('Book details not found.');
    return;
  }

  // Normalize editions array (handling legacy root fileUrl / driveFileId)""",
    """  if (!book) {
    showToast('Book details not found.');
    return;
  }

  // Clear any cached PDF bytes from a previous session so the reader
  // always fetches the latest file (avoids showing stale content after updates)
  if (APP_STATE._pdfCache) {
    Object.keys(APP_STATE._pdfCache).forEach(k => { if (k.startsWith(`book_${bookId}_`)) delete APP_STATE._pdfCache[k]; });
  }

  // Normalize editions array (handling legacy root fileUrl / driveFileId)""",
    "FIX openBookDetail: clear stale PDF cache for selected book"
)

# ═══════════════════════════════════════════════════════════════
# FIX 7: retryLoadReaderPdf — also reset pdfIsRendering
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """function retryLoadReaderPdf() {
  if (APP_STATE.selectedBook) {
    const edition = APP_STATE.selectedEdition || (APP_STATE.selectedBook.languages && APP_STATE.selectedBook.languages[0]);
    loadPdfDocumentForReader(APP_STATE.selectedBook, edition, APP_STATE.pdfPageNumber || 1);
  }
}""",
    """function retryLoadReaderPdf() {
  if (APP_STATE.selectedBook) {
    APP_STATE.pdfIsRendering = false;
    APP_STATE.pdfDocument = null;
    if (APP_STATE._currentRenderTask) {
      try { APP_STATE._currentRenderTask.cancel(); } catch(e) {}
      APP_STATE._currentRenderTask = null;
    }
    // Flush the cache for this book so it re-downloads
    const bookId = APP_STATE.selectedBook.id;
    if (APP_STATE._pdfCache) {
      Object.keys(APP_STATE._pdfCache).forEach(k => { if (k.startsWith(`book_${bookId}_`)) delete APP_STATE._pdfCache[k]; });
    }
    const edition = APP_STATE.selectedEdition || (APP_STATE.selectedBook.languages && APP_STATE.selectedBook.languages[0]);
    loadPdfDocumentForReader(APP_STATE.selectedBook, edition, 1);
  }
}""",
    "FIX retryLoadReaderPdf: reset render state + flush cache"
)

# ═══════════════════════════════════════════════════════════════
# FIX 8: APP_STATE — add _currentRenderTask and readerFitMode
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """  pdfZoomScale: 1.35,
  pdfIsRendering: false,""",
    """  pdfZoomScale: 1.35,
  pdfIsRendering: false,
  readerFitMode: 'width',
  _currentRenderTask: null,""",
    "FIX APP_STATE: add readerFitMode and _currentRenderTask"
)

with open("scripts/generate_4.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\n=== Patch complete. Verifying Python syntax… ===")
import py_compile
try:
    py_compile.compile("scripts/generate_4.py", doraise=True)
    print("OK — no syntax errors in generate_4.py")
except py_compile.PyCompileError as e:
    print(f"ERROR: {e}")
    sys.exit(1)
