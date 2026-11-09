#!/usr/bin/env python3
"""
NOVELIX — Critical Reader Auto-Open Bug Fix & Full Startup Repair
Patches scripts/generate_4.py to:
1. Fix CSS specificity: enforce display: none !important on .modal-fullscreen
2. Remove 'flex' class from initial HTML of readerModal and adminDashboardModal, adding inline style="display: none !important; visibility: hidden !important;"
3. Ensure readerLoadingOverlay has 'hidden' by default and 0% progress initial state
4. Add early independent startup guard script at top of body
5. Update NavigationController.init() to forcefully close all modals, clear reading state, and guarantee Home screen
6. Add strict validation to launchActiveReader(): only open on explicit user action with valid book
7. Implement robust closeReaderModal(): abort in-flight downloads, destroy PDF tasks, reset styles & overlays
8. Harden loadPdfDocumentForReader(): real streaming progress, operation timeouts, concurrency locks, comprehensive error states
9. Handle Android Capacitor lifecycle: back button closing reader, appStateChange preserving active screen
"""

import os
import subprocess

TARGET = "scripts/generate_4.py"

with open(TARGET, "r", encoding="utf-8") as f:
    content = f.read()

# ─────────────────────────────────────────────────────────────
# 1. CSS SPECIFICITY FIX: .modal-fullscreen
# ─────────────────────────────────────────────────────────────
old_css = """    /* Fullscreen Modal */
    .modal-fullscreen {
      position: fixed;
      inset: 0;
      background: #0B0B10;
      z-index: 110;
      display: none;
      flex-direction: column;
      will-change: transform, opacity;
      transform: translateZ(0);
      -webkit-transform: translateZ(0);
    }
    .modal-fullscreen.open { display: flex; }"""

new_css = """    /* Fullscreen Modal (Strict Guard: Prevents Tailwind .flex override) */
    .modal-fullscreen {
      position: fixed;
      inset: 0;
      background: #0B0B10;
      z-index: 110;
      display: none !important;
      visibility: hidden !important;
      pointer-events: none !important;
      flex-direction: column;
      will-change: transform, opacity;
      transform: translateZ(0);
      -webkit-transform: translateZ(0);
    }
    .modal-fullscreen.open {
      display: flex !important;
      visibility: visible !important;
      pointer-events: auto !important;
    }"""

assert old_css in content, "Failed to find old .modal-fullscreen CSS"
content = content.replace(old_css, new_css)
print("1. Patched .modal-fullscreen CSS")

# ─────────────────────────────────────────────────────────────
# 2. HTML: adminDashboardModal & readerModal attribute updates
# ─────────────────────────────────────────────────────────────
old_admin_modal = '<div id="adminDashboardModal" class="modal-fullscreen flex flex-col bg-[#07070A] text-[#F5F3FA]">'
new_admin_modal = '<div id="adminDashboardModal" class="modal-fullscreen flex-col bg-[#07070A] text-[#F5F3FA]" style="display: none !important; visibility: hidden !important;">'
assert old_admin_modal in content, "Failed to find old adminDashboardModal HTML"
content = content.replace(old_admin_modal, new_admin_modal)
print("2a. Patched adminDashboardModal HTML")

old_reader_modal = '<div id="readerModal" class="modal-fullscreen flex flex-col bg-[#07070A] text-[#F5F3FA] select-none" data-theme="dark">'
new_reader_modal = '<div id="readerModal" class="modal-fullscreen flex-col bg-[#07070A] text-[#F5F3FA] select-none" data-theme="dark" style="display: none !important; visibility: hidden !important;">'
assert old_reader_modal in content, "Failed to find old readerModal HTML"
content = content.replace(old_reader_modal, new_reader_modal)
print("2b. Patched readerModal HTML")

# ─────────────────────────────────────────────────────────────
# 3. HTML: readerLoadingOverlay hidden by default, 0% progress
# ─────────────────────────────────────────────────────────────
old_loading_overlay = """    <!-- Reader Loading State Overlay -->
    <div id="readerLoadingOverlay" class="absolute inset-0 bg-[#07070A]/90 backdrop-blur-sm flex flex-col items-center justify-center z-30 transition-opacity">
      <div class="w-12 h-12 rounded-full border-2 border-app-primary border-t-transparent animate-spin mb-3"></div>
      <p id="readerLoadingStatus" class="font-display font-medium text-xs text-white">Loading secure manuscript...</p>
      <div class="w-48 h-1 bg-[#1A1A26] rounded-full mt-3 overflow-hidden">
        <div id="readerLoadingProgress" class="h-full bg-app-primary transition-all duration-300" style="width: 15%"></div>
      </div>
      <span id="readerLoadingPercent" class="text-[10px] text-app-muted mt-1 font-mono">15%</span>
    </div>"""

new_loading_overlay = """    <!-- Reader Loading State Overlay (Hidden by default, real progress) -->
    <div id="readerLoadingOverlay" class="hidden absolute inset-0 bg-[#07070A]/90 backdrop-blur-sm flex flex-col items-center justify-center z-30 transition-opacity">
      <div class="w-12 h-12 rounded-full border-2 border-app-primary border-t-transparent animate-spin mb-3"></div>
      <p id="readerLoadingStatus" class="font-display font-medium text-xs text-white">Loading secure manuscript...</p>
      <div class="w-48 h-1 bg-[#1A1A26] rounded-full mt-3 overflow-hidden">
        <div id="readerLoadingProgress" class="h-full bg-app-primary transition-all duration-300" style="width: 0%"></div>
      </div>
      <span id="readerLoadingPercent" class="text-[10px] text-app-muted mt-1 font-mono">0%</span>
    </div>"""

assert old_loading_overlay in content, "Failed to find old readerLoadingOverlay HTML"
content = content.replace(old_loading_overlay, new_loading_overlay)
print("3. Patched readerLoadingOverlay HTML")

# ─────────────────────────────────────────────────────────────
# 4. EARLY STARTUP GUARD: Immediate inline enforcement
# ─────────────────────────────────────────────────────────────
old_splash_guard = """<body>

<!-- ════════════════════════════════════════════════════════
     1. CUSTOM ANIMATED SPLASH SCREEN
═══════════════════════════════════════════════════════════ -->
<div id="splashScreen">"""

new_splash_guard = """<body>

<!-- Immediate Early Startup Guard: Prevents accidental modal flashing before scripts load -->
<script>
  (function() {
    try {
      var r = document.getElementById('readerModal');
      if (r) { r.style.setProperty('display', 'none', 'important'); r.style.setProperty('visibility', 'hidden', 'important'); r.classList.remove('open'); }
      var a = document.getElementById('adminDashboardModal');
      if (a) { a.style.setProperty('display', 'none', 'important'); a.style.setProperty('visibility', 'hidden', 'important'); a.classList.remove('open'); }
      document.body.style.overflow = '';
      document.body.style.position = '';
      document.body.style.width = '';
    } catch(e) {}
  })();
</script>

<!-- ════════════════════════════════════════════════════════
     1. CUSTOM ANIMATED SPLASH SCREEN
═══════════════════════════════════════════════════════════ -->
<div id="splashScreen">"""

assert old_splash_guard in content, "Failed to find splash screen insertion point"
content = content.replace(old_splash_guard, new_splash_guard)
print("4. Injected Early Startup Guard")

# ─────────────────────────────────────────────────────────────
# 5. NAVIGATION CONTROLLER: Enforce Clean Home Startup & Back Button
# ─────────────────────────────────────────────────────────────
old_nav_controller = """const NavigationController = {
  history: ['home'],
  
  init() {
    // 1. Force close any lingering modals on app launch
    document.querySelectorAll('.modal-fullscreen, .modal-sheet').forEach(m => m.classList.remove('open'));
    document.getElementById('devTerminal')?.classList.remove('open');
    document.body.style.overflow = '';
    document.body.style.position = '';
    document.body.style.width = '';

    // 2. Clear orphan reader state
    APP_STATE.pdfDocument = null;
    APP_STATE.pdfIsRendering = false;
    if (APP_STATE._currentRenderTask) {
      try { APP_STATE._currentRenderTask.cancel(); } catch(e) {}
      APP_STATE._currentRenderTask = null;
    }

    // 3. Guarantee landing on Home screen
    APP_STATE.activePage = 'home';
    switchPage('home');
    console.log('[NOVELIX] NavigationController: Clean Home startup guaranteed.');
  },

  navigate(pageId) {
    if (APP_STATE.activePage !== pageId) {
      this.history.push(pageId);
      if (this.history.length > 20) this.history.shift();
    }
    switchPage(pageId);
  },

  handleBackButton(e) {
    if (e) e.preventDefault();

    // Priority 1: Reader Modal open
    const readerModal = document.getElementById('readerModal');
    if (readerModal && readerModal.classList.contains('open')) {
      closeReaderModal();
      if (APP_STATE.selectedBook) openBookDetail(APP_STATE.selectedBook.id);
      return;
    }

    // Priority 2: Book Detail Modal open
    const bookDetail = document.getElementById('bookDetailModal');
    if (bookDetail && bookDetail.classList.contains('open')) {
      closeBookDetailModal();
      return;
    }

    // Priority 3: Any other open modal
    const otherModals = ['authModal', 'adminDashboardModal', 'notifModal', 'settingsModal', 'drivePickerModal'];
    for (const mId of otherModals) {
      const el = document.getElementById(mId);
      if (el && el.classList.contains('open')) {
        el.classList.remove('open');
        return;
      }
    }

    // Priority 4: Developer Terminal
    const term = document.getElementById('devTerminal');
    if (term && term.classList.contains('open')) {
      term.classList.remove('open');
      return;
    }

    // Priority 5: Secondary tabs -> Return to Home
    if (APP_STATE.activePage !== 'home') {
      switchPage('home');
      return;
    }

    // Priority 6: Already on Home — double back to exit
    const now = Date.now();
    if (!NavigationController._lastBackPress || now - NavigationController._lastBackPress > 2000) {
      NavigationController._lastBackPress = now;
      showToast('Press back again to exit NOVELIX');
    } else {
      if (window.Capacitor?.Plugins?.App?.exitApp) {
        window.Capacitor.Plugins.App.exitApp();
      }
    }
  }
};"""

new_nav_controller = """const NavigationController = {
  history: ['home'],
  
  init() {
    // 1. Force close and hide all fullscreen modals and backdrop sheets on app launch
    document.querySelectorAll('.modal-fullscreen').forEach(m => {
      m.classList.remove('open');
      m.style.setProperty('display', 'none', 'important');
      m.style.setProperty('visibility', 'hidden', 'important');
      m.style.setProperty('pointer-events', 'none', 'important');
    });
    document.querySelectorAll('.modal-backdrop, .modal-sheet').forEach(m => m.classList.remove('open'));
    document.getElementById('devTerminal')?.classList.remove('open');
    document.body.style.overflow = '';
    document.body.style.position = '';
    document.body.style.width = '';

    // 2. Clear orphan reader and selection state
    APP_STATE.selectedBook = null;
    APP_STATE.selectedEdition = null;
    APP_STATE.pdfDocument = null;
    APP_STATE._loadingPdf = false;
    APP_STATE.pdfIsRendering = false;
    if (APP_STATE._currentRenderTask) {
      try { APP_STATE._currentRenderTask.cancel(); } catch(e) {}
      APP_STATE._currentRenderTask = null;
    }
    if (APP_STATE._pdfAbortController) {
      try { APP_STATE._pdfAbortController.abort(); } catch(e) {}
      APP_STATE._pdfAbortController = null;
    }
    if (APP_STATE._pdfLoadingTask) {
      try { APP_STATE._pdfLoadingTask.destroy(); } catch(e) {}
      APP_STATE._pdfLoadingTask = null;
    }

    // 3. Guarantee landing on Home screen
    APP_STATE.activePage = 'home';
    switchPage('home');
    console.log('[NOVELIX] NavigationController: Clean Home startup guaranteed.');
  },

  navigate(pageId) {
    if (APP_STATE.activePage !== pageId) {
      this.history.push(pageId);
      if (this.history.length > 20) this.history.shift();
    }
    switchPage(pageId);
  },

  handleBackButton(e) {
    if (e) e.preventDefault();

    // Priority 1: Reader Modal open
    const readerModal = document.getElementById('readerModal');
    if (readerModal && (readerModal.classList.contains('open') || readerModal.style.display !== 'none')) {
      closeReaderModal();
      if (APP_STATE.selectedBook) openBookDetail(APP_STATE.selectedBook.id);
      return;
    }

    // Priority 2: Book Detail Modal open
    const bookDetail = document.getElementById('bookDetailModal');
    if (bookDetail && bookDetail.classList.contains('open')) {
      closeBookDetailModal();
      return;
    }

    // Priority 3: Any other open modal
    const otherModals = ['authModal', 'adminDashboardModal', 'notifModal', 'settingsModal', 'drivePickerModal', 'verificationModal', 'editProfileModal'];
    for (const mId of otherModals) {
      const el = document.getElementById(mId);
      if (el && (el.classList.contains('open') || el.style.display !== 'none')) {
        el.classList.remove('open');
        el.style.setProperty('display', 'none', 'important');
        return;
      }
    }

    // Priority 4: Developer Terminal
    const term = document.getElementById('devTerminal');
    if (term && term.classList.contains('open')) {
      term.classList.remove('open');
      return;
    }

    // Priority 5: Secondary tabs -> Return to Home
    if (APP_STATE.activePage !== 'home') {
      switchPage('home');
      return;
    }

    // Priority 6: Already on Home — double back to exit
    const now = Date.now();
    if (!NavigationController._lastBackPress || now - NavigationController._lastBackPress > 2000) {
      NavigationController._lastBackPress = now;
      showToast('Press back again to exit NOVELIX');
    } else {
      if (window.Capacitor?.Plugins?.App?.exitApp) {
        window.Capacitor.Plugins.App.exitApp();
      }
    }
  }
};"""

assert old_nav_controller in content, "Failed to find old NavigationController"
content = content.replace(old_nav_controller, new_nav_controller)
print("5. Patched NavigationController")

# ─────────────────────────────────────────────────────────────
# 6. ADMIN DASHBOARD OPEN / CLOSE HELPERS
# ─────────────────────────────────────────────────────────────
old_admin_open = "  document.getElementById('adminDashboardModal').classList.add('open');"
new_admin_open = """  const adm = document.getElementById('adminDashboardModal');
  if (adm) {
    adm.style.setProperty('display', 'flex', 'important');
    adm.style.setProperty('visibility', 'visible', 'important');
    adm.style.setProperty('pointer-events', 'auto', 'important');
    adm.classList.add('open');
  }"""
assert old_admin_open in content, "Failed to find adminDashboardModal.classList.add('open')"
content = content.replace(old_admin_open, new_admin_open)

old_admin_close = "function closeAdminDashboard() { document.getElementById('adminDashboardModal').classList.remove('open'); }"
new_admin_close = """function closeAdminDashboard() {
  const adm = document.getElementById('adminDashboardModal');
  if (adm) {
    adm.classList.remove('open');
    adm.style.setProperty('display', 'none', 'important');
    adm.style.setProperty('visibility', 'hidden', 'important');
    adm.style.setProperty('pointer-events', 'none', 'important');
  }
}"""
assert old_admin_close in content, "Failed to find old closeAdminDashboard"
content = content.replace(old_admin_close, new_admin_close)
print("6. Patched adminDashboard open and close helpers")

# ─────────────────────────────────────────────────────────────
# 7. READER CONTROLLER: launchActiveReader, closeReaderModal, loadPdfDocumentForReader
# ─────────────────────────────────────────────────────────────
old_reader_block_start = """// ────────────────────────────────────────────────────────
// NOVELIX 6.0 PROFESSIONAL MOBILE PDF READER CONTROLLER
// ────────────────────────────────────────────────────────
async function launchActiveReader() {"""

old_reader_block_end = """function reconnectDriveFromReader() {
  closeReaderModal();
  initiateGoogleDriveConnection();
}"""

# Find the block range
start_idx = content.find(old_reader_block_start)
end_idx = content.find(old_reader_block_end)
assert start_idx != -1 and end_idx != -1, "Failed to locate reader controller code block"

new_reader_block = """// ────────────────────────────────────────────────────────
// NOVELIX 8.0 ROBUST MOBILE PDF READER CONTROLLER & ENGINE
// ────────────────────────────────────────────────────────
async function launchActiveReader() {
  const book = APP_STATE.selectedBook;
  if (!book || !book.id) {
    console.warn('[NOVELIX Reader] Reader launch denied: No book selected.');
    closeReaderModal();
    switchPage('home');
    return;
  }

  // Guard against concurrent PDF launches
  if (APP_STATE._loadingPdf) {
    console.warn('[NOVELIX Reader] A manuscript load operation is already in flight.');
    return;
  }

  // ── Reset all reader state for fresh book session ────────────
  APP_STATE.pdfDocument = null;
  APP_STATE.pdfPageNumber = 1;
  APP_STATE.pdfIsRendering = false;
  APP_STATE.pdfZoomScale = 1.35;
  APP_STATE.readerFitMode = 'width';
  APP_STATE._pdfCache = APP_STATE._pdfCache || {};
  APP_STATE._currentBookmarks = [];
  // ─────────────────────────────────────────────────────────────

  closeBookDetailModal();
  document.body.style.overflow = 'hidden';
  document.body.style.position = 'fixed';
  document.body.style.width = '100%';

  const readerModal = document.getElementById('readerModal');
  if (readerModal) {
    readerModal.style.setProperty('display', 'flex', 'important');
    readerModal.style.setProperty('visibility', 'visible', 'important');
    readerModal.style.setProperty('pointer-events', 'auto', 'important');
    readerModal.classList.add('open');
  }

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
  if (!edition && (book.fileUrl || book.driveFileId || book.pdfUrl || book.storagePath)) {
    edition = {
      language: book.language || 'Standard',
      fileUrl: book.fileUrl || book.pdfUrl || '',
      storagePath: book.storagePath || '',
      driveFileId: book.driveFileId || '',
      driveAccountId: book.driveAccountId || '',
      storageProvider: book.storageProvider || (book.driveFileId ? 'drive' : 'storage')
    };
  }

  if (!edition || (!edition.fileUrl && !edition.storagePath && !edition.driveFileId)) {
    document.getElementById('readerLoadingOverlay')?.classList.add('hidden');
    const eo = document.getElementById('readerErrorOverlay');
    if (eo) eo.classList.remove('hidden');
    document.getElementById('readerErrorTitle').textContent = 'No Manuscript Attached';
    document.getElementById('readerErrorMessage').textContent =
      'This book does not have an attached PDF file. The author may not have uploaded a manuscript edition yet.';
    const badge = document.getElementById('readerErrorCodeBadge');
    if (badge) { badge.textContent = 'ERR_NO_MANUSCRIPT'; badge.classList.remove('hidden'); }
    document.getElementById('readerReconnectDriveBtn')?.classList.add('hidden');
    return;
  }

  APP_STATE.selectedEdition = edition;
  updateReaderBookmarkVisual(false);

  // Restore user reading progress from Firestore if available
  let startPage = APP_STATE.pdfPageNumber || 1;
  if (APP_STATE.user && startPage === 1) {
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
}

function closeReaderModal() {
  const readerModal = document.getElementById('readerModal');
  if (readerModal) {
    readerModal.classList.remove('open');
    readerModal.style.setProperty('display', 'none', 'important');
    readerModal.style.setProperty('visibility', 'hidden', 'important');
    readerModal.style.setProperty('pointer-events', 'none', 'important');
  }

  document.body.style.overflow = '';
  document.body.style.position = '';
  document.body.style.width = '';

  if (document.fullscreenElement) {
    document.exitFullscreen().catch(() => {});
  }

  // Cancel any in-progress render task
  if (APP_STATE._currentRenderTask) {
    try { APP_STATE._currentRenderTask.cancel(); } catch(e) {}
    APP_STATE._currentRenderTask = null;
  }

  // Abort any in-progress network download
  if (APP_STATE._pdfAbortController) {
    try { APP_STATE._pdfAbortController.abort(); } catch(e) {}
    APP_STATE._pdfAbortController = null;
  }

  // Destroy in-progress PDF.js loading task
  if (APP_STATE._pdfLoadingTask) {
    try { APP_STATE._pdfLoadingTask.destroy(); } catch(e) {}
    APP_STATE._pdfLoadingTask = null;
  }

  APP_STATE._loadingPdf = false;
  APP_STATE.pdfIsRendering = false;

  // Clean overlays
  document.getElementById('readerLoadingOverlay')?.classList.add('hidden');
  document.getElementById('readerErrorOverlay')?.classList.add('hidden');
}

// Timeout utility wrapper
function withTimeout(promise, ms, errorMsg, errorCode) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      const err = new Error(errorMsg || 'Operation timed out');
      err.code = errorCode || 'TIMEOUT';
      reject(err);
    }, ms);
    promise.then(
      res => { clearTimeout(timer); resolve(res); },
      err => { clearTimeout(timer); reject(err); }
    );
  });
}

async function loadPdfDocumentForReader(book, edition, targetPage) {
  const loadingOverlay = document.getElementById('readerLoadingOverlay');
  const errorOverlay = document.getElementById('readerErrorOverlay');
  const errorTitle = document.getElementById('readerErrorTitle');
  const errorMsg = document.getElementById('readerErrorMessage');
  const errorCodeBadge = document.getElementById('readerErrorCodeBadge');
  const progressBar = document.getElementById('readerLoadingProgress');
  const percentText = document.getElementById('readerLoadingPercent');
  const statusText = document.getElementById('readerLoadingStatus');
  const reconnectDriveBtn = document.getElementById('readerReconnectDriveBtn');

  // Helper to smoothly update real progress
  function updateProgress(pct, status) {
    const clamped = Math.max(5, Math.min(98, Math.round(pct)));
    if (progressBar) progressBar.style.width = `${clamped}%`;
    if (percentText) percentText.textContent = `${clamped}%`;
    if (status && statusText) statusText.textContent = status;
  }

  if (typeof pdfjsLib === 'undefined') {
    if (loadingOverlay) loadingOverlay.classList.add('hidden');
    if (errorOverlay) errorOverlay.classList.remove('hidden');
    if (errorTitle) errorTitle.textContent = 'PDF Reader Offline';
    if (errorMsg) errorMsg.textContent = 'The PDF rendering library is unavailable offline. Please check your network connection.';
    if (errorCodeBadge) {
      errorCodeBadge.textContent = 'ERR_PDF_LIB_OFFLINE';
      errorCodeBadge.classList.remove('hidden');
    }
    return;
  }

  // Cancel prior download if active
  if (APP_STATE._loadingPdf) {
    if (APP_STATE._pdfAbortController) {
      try { APP_STATE._pdfAbortController.abort(); } catch(e) {}
    }
    if (APP_STATE._pdfLoadingTask) {
      try { APP_STATE._pdfLoadingTask.destroy(); } catch(e) {}
    }
  }

  APP_STATE._loadingPdf = true;
  const abortController = new AbortController();
  APP_STATE._pdfAbortController = abortController;

  loadingOverlay?.classList.remove('hidden');
  errorOverlay?.classList.add('hidden');
  reconnectDriveBtn?.classList.add('hidden');
  errorCodeBadge?.classList.add('hidden');

  updateProgress(8, 'Preparing secure manuscript stream…');

  const cacheKey = `book_${book.id}_${edition.language || 'std'}`;
  if (!APP_STATE._pdfCache) APP_STATE._pdfCache = {};

  // ─── Helper: fetch URL as Uint8Array with streaming progress and validation ─
  async function fetchPdfBytes(url, progressCallback, signal) {
    let resolvedUrl = url;

    // Refresh download URL from Firebase Storage if path exists
    if (storage && edition.storagePath && url.includes('firebasestorage')) {
      try {
        resolvedUrl = await withTimeout(
          storage.ref(edition.storagePath).getDownloadURL(),
          12000,
          'Cloud storage download URL generation timed out (12s).',
          'STORAGE_TIMEOUT'
        );
        console.log('[NOVELIX Reader] Refreshed Storage download URL.');
      } catch(e) {
        console.warn('[NOVELIX Reader] Storage URL refresh note:', e.message);
      }
    }

    const fetchPromise = fetch(resolvedUrl, { method: 'GET', credentials: 'omit', signal });
    const resp = await withTimeout(
      fetchPromise,
      25000,
      'Manuscript download timed out (25s). Please check your internet connection.',
      'NETWORK_TIMEOUT'
    );

    if (!resp.ok) {
      const e = new Error(`HTTP ${resp.status}: manuscript download failed`);
      e.code = resp.status === 404 ? 'NOT_FOUND' : resp.status === 403 ? 'PERMISSION_DENIED' : 'FETCH_ERROR';
      throw e;
    }

    const contentType = resp.headers.get('content-type') || '';
    if (contentType.includes('text/html') || contentType.includes('application/json')) {
      const e = new Error('Server returned an error page instead of a PDF file.');
      e.code = 'INVALID_FORMAT';
      throw e;
    }

    const contentLength = parseInt(resp.headers.get('content-length') || '0', 10);
    const reader = resp.body.getReader();
    const chunks = [];
    let receivedBytes = 0;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
      receivedBytes += value.length;

      if (progressCallback) {
        if (contentLength > 0) {
          const pct = Math.round((receivedBytes / contentLength) * 100);
          progressCallback(pct);
        } else {
          progressCallback(Math.min(95, Math.round(receivedBytes / 40000)));
        }
      }
    }

    const allBytes = new Uint8Array(receivedBytes);
    let offset = 0;
    for (const chunk of chunks) {
      allBytes.set(chunk, offset);
      offset += chunk.length;
    }

    if (allBytes.length < 5 || allBytes[0] !== 0x25 || allBytes[1] !== 0x50 || allBytes[2] !== 0x44 || allBytes[3] !== 0x46) {
      const e = new Error('Downloaded file is not a valid PDF document (bad magic signature).');
      e.code = 'INVALID_FORMAT';
      throw e;
    }
    return allBytes;
  }
  // ──────────────────────────────────────────────────────────────────

  try {
    let pdfDataParam = null;

    // ── 1. Device memory cache ────────────────────────────────
    if (APP_STATE._pdfCache[cacheKey]) {
      updateProgress(75, 'Loading from device cache…');
      pdfDataParam = { data: APP_STATE._pdfCache[cacheKey] };
    } else {
      const storageProvider = (edition.storageProvider || book.storageProvider ||
        (edition.driveFileId ? 'drive' : 'storage')).toLowerCase();

      // ── 2a. Google Drive secure proxy ───────────────────────
      if (storageProvider === 'drive' && (edition.driveFileId || edition.fileId)) {
        updateProgress(25, 'Connecting to Google Drive proxy…');

        if (typeof functions === 'undefined' || !functions || typeof functions.httpsCallable !== 'function') {
          const e = new Error('Cloud Functions are unavailable to retrieve Drive manuscript.');
          e.code = 'DRIVE_STREAM_UNAVAILABLE';
          throw e;
        }

        const getPdfFn = functions.httpsCallable('getReaderPdfData');
        const res = await withTimeout(
          getPdfFn({ bookId: book.id, language: edition.language || 'Standard' }),
          25000,
          'Google Drive manuscript stream timed out (25s).',
          'DRIVE_TIMEOUT'
        );

        if (res && res.data && res.data.base64) {
          updateProgress(65, 'Decoding manuscript data…');

          const binaryString = atob(res.data.base64);
          const len = binaryString.length;
          const bytes = new Uint8Array(len);
          for (let i = 0; i < len; i++) bytes[i] = binaryString.charCodeAt(i);

          if (bytes.length < 5 || bytes[0] !== 0x25 || bytes[1] !== 0x50 || bytes[2] !== 0x44 || bytes[3] !== 0x46) {
            const e = new Error('Google Drive returned an invalid PDF manuscript.');
            e.code = 'INVALID_FORMAT';
            throw e;
          }
          APP_STATE._pdfCache[cacheKey] = bytes;
          pdfDataParam = { data: bytes };

        } else if (res && res.data && res.data.fileUrl) {
          updateProgress(45, 'Downloading Drive manuscript…');
          const bytes = await fetchPdfBytes(res.data.fileUrl, (p) => {
            updateProgress(45 + Math.round(p * 0.4), 'Downloading manuscript…');
          }, abortController.signal);
          APP_STATE._pdfCache[cacheKey] = bytes;
          pdfDataParam = { data: bytes };
        } else {
          const e = new Error('Cloud Function returned no PDF payload for this book.');
          e.code = 'DRIVE_STREAM_UNAVAILABLE';
          throw e;
        }

      // ── 2b. Firebase Storage or direct HTTPS URL ─────────────
      } else if (edition.fileUrl || edition.storagePath) {
        updateProgress(30, 'Downloading manuscript from storage…');

        let downloadUrl = edition.fileUrl || '';
        if (storage && edition.storagePath && !downloadUrl) {
          try {
            updateProgress(35, 'Generating download token…');
            downloadUrl = await withTimeout(
              storage.ref(edition.storagePath).getDownloadURL(),
              12000,
              'Storage token request timed out.',
              'STORAGE_TIMEOUT'
            );
          } catch(e) {
            const err = new Error(`Storage access failed: ${e.message}`);
            err.code = e.code === 'storage/object-not-found' ? 'NOT_FOUND' : 'PERMISSION_DENIED';
            throw err;
          }
        }

        if (!downloadUrl) {
          const e = new Error('No download URL or storage path found for this edition.');
          e.code = 'NOT_FOUND';
          throw e;
        }

        const bytes = await fetchPdfBytes(downloadUrl, (p) => {
          updateProgress(30 + Math.round(p * 0.55), 'Downloading manuscript…');
        }, abortController.signal);
        APP_STATE._pdfCache[cacheKey] = bytes;
        pdfDataParam = { data: bytes };

      } else {
        const e = new Error('This edition has no PDF file, storage path, or Drive ID attached.');
        e.code = 'NO_FILE_REGISTERED';
        throw e;
      }
    }

    // ── 3. Initialize PDF.js engine and parse document ────────
    updateProgress(88, 'Parsing manuscript structure…');

    if (!window.pdfjsLib) {
      const e = new Error('PDF.js library is not available.');
      e.code = 'ENGINE_NOT_READY';
      throw e;
    }

    pdfDataParam.disableWorker = true;
    pdfDataParam.cMapUrl = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/cmaps/';
    pdfDataParam.cMapPacked = true;

    const safeTargetPage = Math.max(1, parseInt(targetPage, 10) || 1);

    const loadingTask = pdfjsLib.getDocument(pdfDataParam);
    APP_STATE._pdfLoadingTask = loadingTask;

    loadingTask.onProgress = function(pd) {
      if (pd.total > 0) {
        const pct = Math.round((pd.loaded / pd.total) * 100);
        updateProgress(88 + Math.round(pct * 0.1), 'Parsing pages…');
      }
    };

    APP_STATE.pdfDocument = await withTimeout(
      loadingTask.promise,
      20000,
      'PDF document structure parsing timed out (20s).',
      'PDF_PARSE_TIMEOUT'
    );

    loadingOverlay?.classList.add('hidden');

    const totalPages = APP_STATE.pdfDocument.numPages;
    const finalPage = Math.min(safeTargetPage, totalPages);

    const slider = document.getElementById('readerPageSlider');
    if (slider) { slider.min = '1'; slider.max = String(totalPages); slider.value = String(finalPage); }
    document.getElementById('readerTotalPagesBadge').textContent = `/ ${totalPages}`;

    await renderPdfPage(finalPage);

    if (finalPage > 1) showToast(`Resumed reading at page ${finalPage} of ${totalPages}`);

  } catch(err) {
    if (err.name === 'AbortError' || abortController.signal.aborted) {
      console.log('[NOVELIX Reader] Manuscript loading was aborted by user.');
      return;
    }

    console.error('[NOVELIX Reader] loadPdfDocumentForReader error:', err);
    loadingOverlay?.classList.add('hidden');
    errorOverlay?.classList.remove('hidden');

    const rawMsg = (err.message || '').toLowerCase();
    const code = err.code || err.name || 'UNKNOWN';

    if (code === 'NOT_FOUND' || code === 'storage/object-not-found' || rawMsg.includes('404') || rawMsg.includes('not found') || rawMsg.includes('no download url')) {
      errorTitle.textContent = 'Manuscript Not Found';
      errorMsg.textContent = 'The PDF file for this book could not be located in cloud storage.';
      errorCodeBadge.textContent = 'ERR_PDF_NOT_FOUND';
    } else if (code === 'INVALID_FORMAT' || code === 'InvalidPDFException' || rawMsg.includes('invalid') || rawMsg.includes('magic') || rawMsg.includes('bad magic')) {
      errorTitle.textContent = 'Invalid PDF Manuscript';
      errorMsg.textContent = 'The file returned is corrupted or is not a valid PDF document.';
      errorCodeBadge.textContent = 'ERR_INVALID_PDF';
    } else if (code === 'PERMISSION_DENIED' || code === 'storage/unauthorized' || rawMsg.includes('403') || rawMsg.includes('permission') || rawMsg.includes('unauthorized')) {
      errorTitle.textContent = 'Access Restricted';
      errorMsg.textContent = 'You do not have permission to view this manuscript.';
      errorCodeBadge.textContent = 'ERR_PERMISSION_DENIED';
    } else if (code === 'DRIVE_STREAM_UNAVAILABLE' || code === 'DRIVE_TIMEOUT' || rawMsg.includes('drive') || rawMsg.includes('oauth') || rawMsg.includes('token')) {
      errorTitle.textContent = 'Google Drive Authorization Required';
      errorMsg.textContent = 'The Google Drive access token has expired. Please reconnect your Google Drive account.';
      errorCodeBadge.textContent = 'ERR_DRIVE_AUTH_EXPIRED';
      reconnectDriveBtn?.classList.remove('hidden');
    } else if (code === 'ENGINE_NOT_READY') {
      errorTitle.textContent = 'PDF Engine Not Ready';
      errorMsg.textContent = 'The PDF rendering engine is not ready. Please verify network access and retry.';
      errorCodeBadge.textContent = 'ERR_ENGINE_NOT_READY';
    } else if (code === 'NETWORK_TIMEOUT' || code === 'STORAGE_TIMEOUT' || code === 'PDF_PARSE_TIMEOUT' || rawMsg.includes('timed out')) {
      errorTitle.textContent = 'Request Timed Out';
      errorMsg.textContent = 'The manuscript download or parse operation took too long. Please check your connection and retry.';
      errorCodeBadge.textContent = 'ERR_TIMEOUT';
    } else if (!navigator.onLine || rawMsg.includes('failed to fetch') || rawMsg.includes('networkerror') || rawMsg.includes('network')) {
      errorTitle.textContent = 'No Internet Connection';
      errorMsg.textContent = 'The manuscript could not be downloaded. Please verify your internet connection.';
      errorCodeBadge.textContent = 'ERR_OFFLINE';
    } else {
      errorTitle.textContent = 'Unable to Open Manuscript';
      errorMsg.textContent = err.message || 'An unexpected error occurred while loading this document.';
      errorCodeBadge.textContent = `ERR_${code}`.substring(0, 40);
    }

    errorCodeBadge?.classList.remove('hidden');
  } finally {
    APP_STATE._loadingPdf = false;
  }
}

function reconnectDriveFromReader() {
  closeReaderModal();
  initiateGoogleDriveConnection();
}"""

content = content[:start_idx] + new_reader_block + content[end_idx + len(old_reader_block_end):]
print("7. Replaced Reader Controller & Engine")

# ─────────────────────────────────────────────────────────────
# 8. CAPACITOR LIFECYCLE: appStateChange listener
# ─────────────────────────────────────────────────────────────
old_cap_listener = """  if (window.Capacitor?.Plugins?.App?.addListener) {
    window.Capacitor.Plugins.App.addListener('backButton', () => NavigationController.handleBackButton(null));
  }"""

new_cap_listener = """  if (window.Capacitor?.Plugins?.App?.addListener) {
    window.Capacitor.Plugins.App.addListener('backButton', () => NavigationController.handleBackButton(null));
    window.Capacitor.Plugins.App.addListener('appStateChange', (state) => {
      console.log('[NOVELIX Lifecycle] App state change: isActive =', state.isActive);
      // Preserves current user screen when returning from background — does not force Home reset
    });
  }"""

assert old_cap_listener in content, "Failed to find old Capacitor backButton listener"
content = content.replace(old_cap_listener, new_cap_listener)
print("8. Added Capacitor appStateChange lifecycle listener")

# Save updated generate_4.py
with open(TARGET, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully patched {TARGET}")
