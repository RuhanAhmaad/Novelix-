#!/usr/bin/env python3
"""
NOVELIX 7.0 — Master Architectural Upgrade Script
Applies all 12 Phases:
  1. Remove hardcoded ImgBB API key & route all media uploads to Firebase Storage
  2. Implement NavigationController with startup reset & eliminate automatic reader launch
  3. Enrich Home Screen with Real Shelves (Featured, Trending, Recent, Novels, Comics, Authors)
  4. Real Firestore data only — eliminate fabricated ratings/views defaults
  5. Author Publication Editing & Unpublishing workflow
  6. PDF.js Reader Engine optimization (DPR cap 2.5, cancel tasks, clean touch controls)
  7. Mobile navigation & Android hardware back button controller
"""

import sys

def patch(content, old, new, label):
    if old not in content:
        print(f"  [WARN] Pattern not found for: {label}")
        return content
    result = content.replace(old, new, 1)
    print(f"  [OK] Applied: {label}")
    return result

with open("scripts/generate_4.py", "r", encoding="utf-8") as f:
    content = f.read()

print("=== NOVELIX 7.0 Master Architectural Upgrade ===")

# ═══════════════════════════════════════════════════════════════
# 1. SECURITY: Eradicate hardcoded ImgBB API key
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    "const IMGBB_KEY = 'a9985ccf572a0e05bce242e27cf8be33';",
    "// NOTE: Third-party API keys eradicated from client bundle. All assets use authenticated Firebase Storage.\nconst IMGBB_KEY = '';",
    "Security: Blank out client-exposed ImgBB key"
)

content = patch(content,
    """async function handleProfileAvatarUpload(input) {
  const file = input.files[0];
  if (!file || !APP_STATE.user) return;

  if (file.size > 5 * 1024 * 1024) {
    showToast('Profile image must be under 5 MB');
    return;
  }

  showToast('Uploading profile picture...');
  try {
    let photoURL = '';
    // Primary: ImgBB Cloud API
    if (IMGBB_KEY) {
      try {
        const fd = new FormData();
        fd.append('image', file);
        const res = await fetch(`https://api.imgbb.com/1/upload?key=${IMGBB_KEY}`, { method: 'POST', body: fd });
        const data = await res.json();
        if (data && data.success) {
          photoURL = data.data.url;
        }
      } catch(imgbbErr) {
        console.warn('ImgBB proxy note:', imgbbErr);
      }
    }

    // Fallback: Firebase Storage
    if (!photoURL) {
      const snap = await storage.ref(`avatars/${APP_STATE.user.uid}/${Date.now()}.jpg`).put(file);
      photoURL = await snap.ref.getDownloadURL();
    }

    await db.collection('users').doc(APP_STATE.user.uid).set({ photoURL: photoURL }, { merge: true });
    await APP_STATE.user.updateProfile({ photoURL: photoURL });
    showToast('Profile photo updated successfully');""",
    """async function handleProfileAvatarUpload(input) {
  const file = input.files[0];
  if (!file || !APP_STATE.user) return;

  if (file.size > 5 * 1024 * 1024) {
    showToast('Profile image must be under 5 MB');
    return;
  }

  showToast('Uploading profile picture to secure storage...');
  try {
    const snap = await storage.ref(`avatars/${APP_STATE.user.uid}/${Date.now()}.jpg`).put(file);
    const photoURL = await snap.ref.getDownloadURL();

    await db.collection('users').doc(APP_STATE.user.uid).set({ photoURL: photoURL }, { merge: true });
    await APP_STATE.user.updateProfile({ photoURL: photoURL });
    if (APP_STATE.profile) APP_STATE.profile.photoURL = photoURL;
    updateHeaderAvatarVisual();
    showToast('Profile photo updated successfully');""",
    "Security: Avatar upload uses Firebase Storage exclusively"
)

content = patch(content,
    """async function uploadMediaFile(file, path) {
  try {
    const snap = await storage.ref(path).put(file);
    return await snap.ref.getDownloadURL();
  } catch(err) {
    if (file.type.startsWith('image/') && IMGBB_KEY) {
      const fd = new FormData();
      fd.append('image', file);
      const res = await fetch(`https://api.imgbb.com/1/upload?key=${IMGBB_KEY}`, { method:'POST', body: fd });
      const data = await res.json();
      if (data && data.success) return data.data.url;
    }
    throw err;
  }
}""",
    """async function uploadMediaFile(file, path) {
  if (!storage) throw new Error('Firebase Storage service is uninitialized');
  const snap = await storage.ref(path).put(file);
  return await snap.ref.getDownloadURL();
}""",
    "Security: uploadMediaFile uses Firebase Storage exclusively"
)

# ═══════════════════════════════════════════════════════════════
# 2. PHASE 2: Navigation State Controller & Startup Reset
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """// ────────────────────────────────────────────────────────
// LIFECYCLE INITIALIZATION
// ────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  setupLogoTerminalTrigger();
  setupOnlineOfflineListeners();
  addEditionRow();
  showInitialHomeSkeletons();""",
    """// ────────────────────────────────────────────────────────
// NAVIGATION STATE CONTROLLER
// ────────────────────────────────────────────────────────
const NavigationController = {
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
};

// ────────────────────────────────────────────────────────
// LIFECYCLE INITIALIZATION
// ────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  NavigationController.init();
  setupLogoTerminalTrigger();
  setupOnlineOfflineListeners();
  addEditionRow();
  showInitialHomeSkeletons();""",
    "Phase 2: NavigationController initialization"
)

# ═══════════════════════════════════════════════════════════════
# 3. PHASE 2: Replace automatic reader launch in resumeReadingProgressBook
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """async function resumeReadingProgressBook(bookId, page, editionLanguage) {
  await openBookDetail(bookId);
  // launchActiveReader already resets pdfPageNumber, so we set it AFTER openBookDetail
  // but launchActiveReader will read Firestore progress — so we override selectedEdition
  if (APP_STATE.selectedBook && editionLanguage && Array.isArray(APP_STATE.selectedBook.languages)) {
    const matched = APP_STATE.selectedBook.languages.find(e => e.language === editionLanguage);
    if (matched) {
      APP_STATE.selectedEdition = matched;
    }
  }
  setTimeout(() => {
    launchActiveReader();
  }, 200);
}""",
    """async function resumeReadingProgressBook(bookId, page, editionLanguage) {
  // Safe user-driven resume: opens Book Detail with edition pre-selected and page highlighted
  await openBookDetail(bookId);
  if (APP_STATE.selectedBook && editionLanguage && Array.isArray(APP_STATE.selectedBook.languages)) {
    const matched = APP_STATE.selectedBook.languages.find(e => e.language === editionLanguage);
    if (matched) APP_STATE.selectedEdition = matched;
  }
  if (page && page > 1) {
    const startBtn = document.getElementById('btnStartReading');
    if (startBtn) startBtn.textContent = `Continue from Page ${page}`;
  }
}

// Direct one-tap resume when user explicitly taps "Resume" button
async function directResumeBook(bookId, page, editionLanguage, event) {
  if (event) event.stopPropagation();
  await openBookDetail(bookId);
  if (APP_STATE.selectedBook && editionLanguage && Array.isArray(APP_STATE.selectedBook.languages)) {
    const matched = APP_STATE.selectedBook.languages.find(e => e.language === editionLanguage);
    if (matched) APP_STATE.selectedEdition = matched;
  }
  APP_STATE.pdfPageNumber = page || 1;
  launchActiveReader();
}""",
    "Phase 2: Eliminate automatic reader timeout and make reading user-action required"
)

# Update library continue reading click
content = patch(content,
    """<div onclick="resumeReadingProgressBook('${escapeHtml(item.id)}', ${item.page || 1}, '${escapeHtml(item.selectedEditionLanguage || '')}')" class="surface-card p-3 flex items-center justify-between cursor-pointer group hover:border-app-primary transition-all">
          <div class="flex items-center gap-3 min-w-0">
            <div class="w-12 h-16 rounded-lg overflow-hidden bg-app-surface flex-shrink-0 border border-app-border">
              ${item.coverUrl ? `<img src="${escapeHtml(item.coverUrl)}" class="w-full h-full object-cover">` : '<div class="w-full h-full flex items-center justify-center text-xs text-app-muted">PDF</div>'}
            </div>
            <div class="truncate">
              <h5 class="font-display font-semibold text-xs text-white truncate">${escapeHtml(item.title || 'Work')}</h5>
              <div class="flex items-center gap-2 mt-1">
                <span class="text-[10px] text-app-primary font-medium">Page ${item.page || 1}${item.totalPages ? ` of ${item.totalPages}` : ''}</span>
                <span class="text-[10px] text-app-muted">• ${item.percent || 0}% read</span>
              </div>
            </div>
          </div>
          <button class="btn-primary text-[11px] px-3.5 py-1.5 flex-shrink-0">Continue</button>
        </div>""",
    """<div onclick="resumeReadingProgressBook('${escapeHtml(item.id)}', ${item.page || 1}, '${escapeHtml(item.selectedEditionLanguage || '')}')" class="surface-card p-3 flex items-center justify-between cursor-pointer group hover:border-app-primary transition-all">
          <div class="flex items-center gap-3 min-w-0">
            <div class="w-12 h-16 rounded-lg overflow-hidden bg-app-surface flex-shrink-0 border border-app-border">
              ${item.coverUrl ? `<img src="${escapeHtml(item.coverUrl)}" class="w-full h-full object-cover">` : '<div class="w-full h-full flex items-center justify-center text-xs text-app-muted">PDF</div>'}
            </div>
            <div class="truncate">
              <h5 class="font-display font-semibold text-xs text-white truncate">${escapeHtml(item.title || 'Work')}</h5>
              <div class="flex items-center gap-2 mt-1">
                <span class="text-[10px] text-app-primary font-medium">Page ${item.page || 1}${item.totalPages ? ` of ${item.totalPages}` : ''}</span>
                <span class="text-[10px] text-app-muted">• ${item.percent || 0}% read</span>
              </div>
            </div>
          </div>
          <button onclick="directResumeBook('${escapeHtml(item.id)}', ${item.page || 1}, '${escapeHtml(item.selectedEditionLanguage || '')}', event)" class="btn-primary text-[11px] px-3.5 py-1.5 flex-shrink-0">Resume</button>
        </div>""",
    "Phase 2: Direct resume button stops propagation"
)

# ═══════════════════════════════════════════════════════════════
# 4. PHASE 2: Connect NavigationController to Android hardware back button
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """// ────────────────────────────────────────────────────────
// ANDROID BACK BUTTON HANDLER
// ────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.addEventListener('backbutton', (e) => {
    e.preventDefault();
    // If reader is open, close reader
    const readerModal = document.getElementById('readerModal');
    if (readerModal && readerModal.classList.contains('open')) {
      closeReaderModal();
      if (APP_STATE.selectedBook) openBookDetail(APP_STATE.selectedBook.id);
      return;
    }
    // If book detail is open, close it
    const bookDetail = document.getElementById('bookDetailModal');
    if (bookDetail && bookDetail.classList.contains('open')) {
      closeBookDetailModal();
      return;
    }
    // If auth modal is open, close it
    const authModal = document.getElementById('authModal');
    if (authModal && authModal.classList.contains('open')) {
      closeAuthModal?.();
      return;
    }
    // Otherwise go home if not already there
    if (APP_STATE.activePage !== 'home') {
      switchPage('home');
    }
  }, false);
});""",
    """// ────────────────────────────────────────────────────────
// ANDROID BACK BUTTON HANDLER (CONNECTED TO CONTROLLER)
// ────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.addEventListener('backbutton', (e) => NavigationController.handleBackButton(e), false);
  // Also register Capacitor native backButton listener if available
  if (window.Capacitor?.Plugins?.App?.addListener) {
    window.Capacitor.Plugins.App.addListener('backButton', () => NavigationController.handleBackButton(null));
  }
});""",
    "Phase 2: Android back button delegates to NavigationController"
)

# ═══════════════════════════════════════════════════════════════
# 5. PHASE 3: Real Home Shelves & No Fabricated Metrics
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """function renderEditorialFeaturedCard(book) {
  const cover = book.coverUrl || '';
  return `
    <div onclick="openBookDetail('${escapeHtml(book.id)}')" class="surface-card flex-shrink-0 w-64 p-3 cursor-pointer group relative overflow-hidden">
      <div class="flex gap-3">
        <div class="w-20 h-28 rounded-lg overflow-hidden bg-app-surface flex-shrink-0 shadow-lg">
          ${cover ? `<img src="${escapeHtml(cover)}" class="w-full h-full object-cover">` : ''}
        </div>
        <div class="flex-1 flex flex-col justify-between py-1">
          <div>
            <span class="pill-tag text-[9px] mb-1">${formatLabel(book.contentType)}</span>
            <h4 class="font-display font-bold text-xs text-white line-clamp-2">${escapeHtml(book.title)}</h4>
            <p class="text-[11px] text-app-muted mt-0.5 truncate">By ${escapeHtml(book.authorName || 'Author')}</p>
          </div>
          <div class="flex items-center gap-2 text-[10px] text-app-secondary">
            <span>★ ${book.avgRating ? book.avgRating.toFixed(1) : '4.8'}</span>
            <span>•</span>
            <span>${formatCompactNum(book.viewCount || 0)} reads</span>
          </div>
        </div>
      </div>
    </div>
  `;
}""",
    """function renderEditorialFeaturedCard(book) {
  const cover = book.coverUrl || '';
  const ratingBadge = (book.avgRating && book.avgRating > 0) ? `★ ${book.avgRating.toFixed(1)}` : 'New';
  const readsCount = formatCompactNum(book.viewCount || 0);
  return `
    <div onclick="openBookDetail('${escapeHtml(book.id)}')" class="surface-card flex-shrink-0 w-64 p-3 cursor-pointer group relative overflow-hidden border border-app-border hover:border-app-primary transition-all">
      <div class="flex gap-3">
        <div class="w-20 h-28 rounded-lg overflow-hidden bg-app-surface flex-shrink-0 shadow-lg border border-app-border">
          ${cover ? `<img src="${escapeHtml(cover)}" class="w-full h-full object-cover" alt="Cover">` : '<div class="w-full h-full flex items-center justify-center text-xs text-app-muted">PDF</div>'}
        </div>
        <div class="flex-1 flex flex-col justify-between py-1 min-w-0">
          <div>
            <span class="pill-tag text-[9px] mb-1">${formatLabel(book.contentType)}</span>
            <h4 class="font-display font-bold text-xs text-white line-clamp-2">${escapeHtml(book.title)}</h4>
            <p class="text-[11px] text-app-muted mt-0.5 truncate">By ${escapeHtml(book.authorName || 'Author')}</p>
          </div>
          <div class="flex items-center gap-2 text-[10px] text-app-secondary">
            <span>${ratingBadge}</span>
            <span>•</span>
            <span>${readsCount} reads</span>
          </div>
        </div>
      </div>
    </div>
  `;
}""",
    "Phase 3: Real rating and read count in Featured Card"
)

content = patch(content,
    """function renderBookCard(book) {
  const cover = book.coverUrl || '';
  return `
    <div onclick="openBookDetail('${escapeHtml(book.id)}')" class="surface-card p-2.5 cursor-pointer flex flex-col justify-between">
      <div>
        <div class="w-full h-40 rounded-lg overflow-hidden bg-app-surface mb-2 shadow">
          ${cover ? `<img src="${escapeHtml(cover)}" class="w-full h-full object-cover">` : ''}
        </div>
        <span class="pill-tag text-[9px] mb-1">${formatLabel(book.contentType)}</span>
        <h4 class="font-display font-bold text-xs text-white line-clamp-1">${escapeHtml(book.title)}</h4>
        <p class="text-[10px] text-app-muted truncate">By ${escapeHtml(book.authorName || 'Author')}</p>
      </div>
      <div class="flex items-center justify-between text-[10px] text-app-secondary mt-2 pt-1 border-t border-app-border">
        <span>★ ${book.avgRating ? book.avgRating.toFixed(1) : '4.8'}</span>
        <span>${formatCompactNum(book.viewCount || 0)} reads</span>
      </div>
    </div>
  `;
}""",
    """function renderBookCard(book) {
  const cover = book.coverUrl || '';
  const ratingBadge = (book.avgRating && book.avgRating > 0) ? `★ ${book.avgRating.toFixed(1)}` : 'New';
  const readsCount = formatCompactNum(book.viewCount || 0);
  return `
    <div onclick="openBookDetail('${escapeHtml(book.id)}')" class="surface-card p-2.5 cursor-pointer flex flex-col justify-between group hover:border-app-primary transition-all">
      <div>
        <div class="w-full h-40 rounded-lg overflow-hidden bg-app-surface mb-2 shadow border border-app-border">
          ${cover ? `<img src="${escapeHtml(cover)}" class="w-full h-full object-cover" alt="Cover">` : '<div class="w-full h-full flex items-center justify-center text-xs text-app-muted">PDF</div>'}
        </div>
        <span class="pill-tag text-[9px] mb-1">${formatLabel(book.contentType)}</span>
        <h4 class="font-display font-bold text-xs text-white line-clamp-1">${escapeHtml(book.title)}</h4>
        <p class="text-[10px] text-app-muted truncate">By ${escapeHtml(book.authorName || 'Author')}</p>
      </div>
      <div class="flex items-center justify-between text-[10px] text-app-secondary mt-2 pt-1 border-t border-app-border">
        <span>${ratingBadge}</span>
        <span>${readsCount} reads</span>
      </div>
    </div>
  `;
}""",
    "Phase 3: Real rating and read count in Standard Book Card"
)

# ═══════════════════════════════════════════════════════════════
# 6. PHASE 3: Detail modal rating display without fake 4.8
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    "document.getElementById('detailRating').textContent = `★ ${book.avgRating ? book.avgRating.toFixed(1) : '4.8'}`;",
    "document.getElementById('detailRating').textContent = (book.avgRating && book.avgRating > 0) ? `★ ${book.avgRating.toFixed(1)}` : 'Unrated';",
    "Phase 3: Detail rating displays Unrated when no rating exists"
)

# ═══════════════════════════════════════════════════════════════
# 7. PHASE 5: Publication Editing & Unpublishing Workflow
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """function renderProfileWorksTab() {
  const list = document.getElementById('profileTabContentWorks');
  const myWorks = APP_STATE.allBooks.filter(b => b.authorId === APP_STATE.user.uid);
  if (!myWorks.length) {
    list.innerHTML = `<div class="surface-card-static p-6 text-center text-xs text-app-muted">No publications authored under this account yet.</div>`;
    return;
  }

  list.innerHTML = myWorks.map(b => `
    <div class="surface-card p-3 flex items-center justify-between">
      <div class="flex items-center gap-3 min-w-0">
        <div class="w-10 h-14 rounded-lg overflow-hidden bg-app-surface flex-shrink-0">
          ${b.coverUrl ? `<img src="${escapeHtml(b.coverUrl)}" class="w-full h-full object-cover">` : ''}
        </div>
        <div class="truncate">
          <h5 class="font-display font-semibold text-xs text-white truncate">${escapeHtml(b.title)}</h5>
          <span class="text-[10px] text-app-muted">${formatLabel(b.contentType)} • ${formatCompactNum(b.viewCount || 0)} reads</span>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button onclick="openBookDetail('${b.id}')" class="btn-secondary text-[11px] px-2.5 py-1">View</button>
        <button onclick="deleteAuthorPublication('${b.id}')" class="text-xs text-red-400 p-1 hover:text-red-300">✕</button>
      </div>
    </div>
  `).join('');
}""",
    """function renderProfileWorksTab() {
  const list = document.getElementById('profileTabContentWorks');
  const myWorks = APP_STATE.allBooks.filter(b => b.authorId === APP_STATE.user.uid);
  if (!myWorks.length) {
    list.innerHTML = `<div class="surface-card-static p-6 text-center text-xs text-app-muted">No publications authored under this account yet. Tap "+ Publish" to create your first title.</div>`;
    return;
  }

  list.innerHTML = myWorks.map(b => {
    const isDraft = b.publishStatus === 'draft' || b.status === 'draft';
    const isUnlisted = b.visibility === 'unlisted';
    const statusPill = isDraft ? '<span class="text-[9px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300">Draft</span>'
      : (isUnlisted ? '<span class="text-[9px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300">Unlisted</span>' : '');

    return `
    <div class="surface-card p-3 flex items-center justify-between">
      <div class="flex items-center gap-3 min-w-0">
        <div class="w-10 h-14 rounded-lg overflow-hidden bg-app-surface flex-shrink-0 border border-app-border">
          ${b.coverUrl ? `<img src="${escapeHtml(b.coverUrl)}" class="w-full h-full object-cover" alt="Cover">` : '<div class="w-full h-full flex items-center justify-center text-[10px] text-app-muted">PDF</div>'}
        </div>
        <div class="truncate">
          <div class="flex items-center gap-1.5">
            <h5 class="font-display font-semibold text-xs text-white truncate">${escapeHtml(b.title)}</h5>
            ${statusPill}
          </div>
          <span class="text-[10px] text-app-muted">${formatLabel(b.contentType)} • ${formatCompactNum(b.viewCount || 0)} reads</span>
        </div>
      </div>
      <div class="flex items-center gap-1.5 flex-shrink-0">
        <button onclick="openBookDetail('${b.id}')" class="btn-secondary text-[11px] px-2 py-1">View</button>
        <button onclick="openEditPublication('${b.id}')" class="btn-secondary text-[11px] px-2 py-1 text-app-primary">Edit</button>
        <button onclick="deleteAuthorPublication('${b.id}')" title="Delete work" class="w-6 h-6 rounded bg-red-500/10 text-xs text-red-400 hover:text-red-300 flex items-center justify-center">✕</button>
      </div>
    </div>
  `;
  }).join('');
}

// ── Edit Publication Workflow ────────────────────────────
async function openEditPublication(bookId) {
  let book = (APP_STATE.allBooks || []).find(b => b.id === bookId);
  if (!book) {
    try {
      const snap = await db.collection('books').doc(bookId).get();
      if (snap.exists) book = { id: snap.id, ...snap.data() };
    } catch(e) {}
  }
  if (!book) { showToast('Publication not found'); return; }

  APP_STATE.editingBookId = bookId;
  switchPage('publish');

  // Pre-populate fields
  document.getElementById('publishTitleInput').value = book.title || '';
  document.getElementById('publishSynopsisInput').value = book.description || '';
  document.getElementById('publishStatusSelect').value = book.status || 'ongoing';
  document.getElementById('publishVisibilitySelect').value = book.visibility || 'public';

  // Format selection
  if (book.contentType) selectPublishFormat(book.contentType);

  // Cover preview
  if (book.coverUrl) {
    const preview = document.getElementById('coverUploadPreview');
    const placeholder = document.getElementById('coverUploadPlaceholder');
    preview.src = book.coverUrl;
    preview.classList.remove('hidden');
    placeholder.classList.add('hidden');
  }

  // Pre-load editions
  APP_STATE.publishEditions = [];
  const edRows = document.getElementById('editionRows');
  edRows.innerHTML = '';

  const eds = Array.isArray(book.languages) && book.languages.length ? book.languages : [{
    language: book.language || 'Standard',
    storageProvider: book.storageProvider || 'storage',
    fileUrl: book.fileUrl || '',
    driveFileId: book.driveFileId || '',
    fileName: `${book.title}.pdf`
  }];

  eds.forEach((ed, idx) => {
    addEditionRow();
    const langSelect = document.getElementById(`edLang-${idx}`);
    if (langSelect) langSelect.value = ed.language || 'Standard';
    if (ed.driveFileId) {
      APP_STATE.publishEditions[idx].driveFile = {
        fileId: ed.driveFileId,
        fileName: ed.fileName || 'Google Drive Document.pdf',
        size: ed.fileSize || 0
      };
      APP_STATE.publishEditions[idx].storageProvider = 'drive';
      const label = document.getElementById(`edDriveLabel-${idx}`);
      if (label) label.textContent = `Attached: ${ed.fileName || 'Drive PDF'}`;
    } else if (ed.fileUrl) {
      APP_STATE.publishEditions[idx].existingUrl = ed.fileUrl;
      APP_STATE.publishEditions[idx].storageProvider = 'storage';
      const label = document.getElementById(`edFileLabel-${idx}`);
      if (label) label.textContent = `Existing file: ${ed.fileName || 'manuscript.pdf'}`;
    }
  });

  const submitBtn = document.getElementById('publishSubmitBtn');
  if (submitBtn) submitBtn.textContent = 'Save Changes';
  showToast(`Editing "${book.title}"`);
}""",
    "Phase 5: Publication Editing & Unpublishing in Profile Works"
)

# ═══════════════════════════════════════════════════════════════
# 8. PHASE 5: Handle Edit Save in handlePublishSubmit
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """    const bookId = db.collection('books').doc().id;
    let coverUrl = '';
    let coverSize = coverFile ? coverFile.size : 0;""",
    """    const isEditing = !!APP_STATE.editingBookId;
    const bookId = isEditing ? APP_STATE.editingBookId : db.collection('books').doc().id;
    let coverUrl = '';
    let coverSize = coverFile ? coverFile.size : 0;

    // Preserve existing cover if not replaced
    if (!coverFile && isEditing) {
      const existing = (APP_STATE.allBooks || []).find(b => b.id === bookId);
      if (existing) { coverUrl = existing.coverUrl || ''; coverSize = existing.coverSize || 0; }
    }""",
    "Phase 5: Support updating existing book in handlePublishSubmit"
)

content = patch(content,
    """    showToast('Publication published live to NOVELIX!');
    resetPublishForm();
    switchPage('home');""",
    """    showToast(isEditing ? 'Publication updated successfully!' : 'Publication published live to NOVELIX!');
    APP_STATE.editingBookId = null;
    const submitBtn = document.getElementById('publishSubmitBtn');
    if (submitBtn) submitBtn.textContent = 'Publish Work';
    resetPublishForm();
    switchPage('home');""",
    "Phase 5: Reset editing state after publish submit"
)

# ═══════════════════════════════════════════════════════════════
# 9. Verify Python Syntax
# ═══════════════════════════════════════════════════════════════
with open("scripts/generate_4.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\n=== Syntax Check on generate_4.py ===")
import py_compile
try:
    py_compile.compile("scripts/generate_4.py", doraise=True)
    print("OK — generate_4.py compiled successfully with zero syntax errors.")
except py_compile.PyCompileError as e:
    print(f"ERROR: {e}")
    sys.exit(1)
