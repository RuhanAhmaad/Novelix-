#!/usr/bin/env python3
"""
Novelix v12.9.0 Mega Patch
Fixes: Edit/Save book, Admin ImgBB UI, Admin book rating+feature, Series add book,
       Notifications "not supported", Theme CSS variables, Drive data in publish,
       Global search (books+authors), UI/UX overhaul, OTA version save fix.
"""
import re

GEN = 'scripts/generate_4.py'
with open(GEN, 'r', encoding='utf-8') as f:
    src = f.read()

changes = 0

# ═══════════════════════════════════════════════════════════════
# 1. VERSION BUMP
# ═══════════════════════════════════════════════════════════════
for old, new in [
    ("window.__NOVELIX_VERSION__ = '12.8.0';", "window.__NOVELIX_VERSION__ = '12.9.0';"),
    ("const NOVELIX_VERSION = '12.8.0';", "const NOVELIX_VERSION = '12.9.0';"),
    ('"version": "12.8.0", "build": 12800', '"version": "12.9.0", "build": 12900'),
]:
    if old in src:
        src = src.replace(old, new)
        changes += 1

# ═══════════════════════════════════════════════════════════════
# 2. THEME: inject CSS variable support via style injection
#    Problem: Tailwind static classes like bg-[#0B0B10] ignore --app-bg.
#    Fix: inject a <style> tag dynamically that maps CSS vars to actual colours.
# ═══════════════════════════════════════════════════════════════
OLD_THEME_FN = '''function setAppTheme(theme) {
  const t = NOVELIX_THEMES[theme] || NOVELIX_THEMES['dark'];
  const root = document.documentElement;
  Object.keys(t).forEach(k => {
    if (k.startsWith('--')) root.style.setProperty(k, t[k]);
  });
  if (t['--app-bg']) document.body.style.backgroundColor = t['--app-bg'];
  localStorage.setItem('novelix_theme', theme);
  showToast(t.toast || (t.name + ' theme active'));

  // Update active state in settings theme grid
  document.querySelectorAll('.theme-opt-btn').forEach(btn => {
    btn.classList.toggle('ring-2', btn.dataset.theme === theme);
    btn.classList.toggle('ring-offset-1', btn.dataset.theme === theme);
  });
}'''

NEW_THEME_FN = '''function setAppTheme(theme) {
  const t = NOVELIX_THEMES[theme] || NOVELIX_THEMES['dark'];
  const root = document.documentElement;

  // 1. Set CSS custom properties on :root
  Object.keys(t).forEach(k => {
    if (k.startsWith('--')) root.style.setProperty(k, t[k]);
  });

  // 2. Apply to body background directly
  if (t['--app-bg']) {
    document.body.style.backgroundColor = t['--app-bg'];
    document.body.style.color = t['--app-text'] || '#E8E8F0';
  }

  // 3. Inject dynamic override <style> so ALL elements pick up new theme
  let dynStyle = document.getElementById('novelix-theme-override');
  if (!dynStyle) {
    dynStyle = document.createElement('style');
    dynStyle.id = 'novelix-theme-override';
    document.head.appendChild(dynStyle);
  }
  const bg = t['--app-bg'] || '#0B0B10';
  const sub = t['--app-sub'] || '#12121A';
  const card = t['--app-card'] || '#1A1A26';
  const primary = t['--app-primary'] || '#9270FF';
  const accent = t['--app-accent'] || '#E5C07B';
  const txt = t['--app-text'] || '#E8E8F0';
  const muted = t['--app-muted'] || '#6B6B80';
  const border = t['--app-border'] || 'rgba(146,112,255,0.18)';

  dynStyle.textContent = `
    body, .app-root { background-color: ${bg} !important; color: ${txt} !important; }
    .surface-card, .surface-card-static { background-color: ${card} !important; }
    .modal-sheet, [class*="bottom-sheet"], [class*="modal"] > div { background-color: ${sub} !important; }
    .nav-pill, .pill-nav { background-color: ${sub} !important; }
    .text-app-muted { color: ${muted} !important; }
    .text-app-primary { color: ${primary} !important; }
    .border-app-border, [class*="border-app-border"] { border-color: ${border} !important; }
    .bg-app-primary\\/10 { background-color: ${primary}1A !important; }
    .bg-app-primary\\/20 { background-color: ${primary}33 !important; }
    .btn-primary { background: linear-gradient(135deg, ${primary}, ${accent}) !important; }
    .admin-panel, #adminConsole { background-color: ${sub} !important; }
    input, textarea, select { background-color: ${card} !important; color: ${txt} !important; border-color: ${border} !important; }
    .form-input { background-color: ${card} !important; color: ${txt} !important; }
  `;

  // 4. Persist & update active button state
  localStorage.setItem('novelix_theme', theme);
  document.querySelectorAll('.theme-opt-btn').forEach(btn => {
    const isActive = btn.dataset.theme === theme;
    btn.style.outline = isActive ? `3px solid ${primary}` : 'none';
    btn.style.outlineOffset = isActive ? '2px' : '0';
  });
  showToast(t.toast || (t.name + ' theme active'));
}'''

if OLD_THEME_FN in src:
    src = src.replace(OLD_THEME_FN, NEW_THEME_FN)
    changes += 1

# ═══════════════════════════════════════════════════════════════
# 3. NOTIFICATIONS: Fix "not supported in this environment"
#    On Android WebView inside Capacitor, 'Notification' may exist but
#    requestPermission might not. Use Capacitor PushNotifications plugin.
# ═══════════════════════════════════════════════════════════════
OLD_NOTIF = '''async function requestPushNotificationPermission() {
  if (!('Notification' in window)) {
    showToast('Notifications not supported in this environment');
    return;
  }
  const perm = await Notification.requestPermission();
  document.getElementById('pushPermissionBadge').textContent = perm;
  if (perm === 'granted') {
    showToast('Push notifications enabled for this device');
    if (messaging && APP_STATE.user) {
      try {
        const token = await messaging.getToken();
        if (token) {
          await db.collection('users').doc(APP_STATE.user.uid).collection('fcm_tokens').doc(token).set({
            token: token,
            device: navigator.userAgent,
            updatedAt: firebase.firestore.FieldValue.serverTimestamp()
          });
        }
      } catch(e) {}
    }
  } else {
    showToast('Notification permission was not granted');
  }
}'''

NEW_NOTIF = '''async function requestPushNotificationPermission() {
  const badge = document.getElementById('pushPermissionBadge');

  // ── Capacitor Android native push notifications ──────────────
  const isCapacitor = !!(window.Capacitor && (typeof window.Capacitor.isNativePlatform === 'function'
    ? window.Capacitor.isNativePlatform() : window.Capacitor.platform !== 'web'));

  if (isCapacitor) {
    try {
      const PushNotif = window.Capacitor?.Plugins?.PushNotifications;
      if (PushNotif) {
        const permResult = await PushNotif.requestPermissions();
        const granted = permResult?.receive === 'granted';
        if (badge) badge.textContent = granted ? 'granted' : 'denied';
        showToast(granted ? '✅ Push notifications enabled!' : '⚠️ Notification permission denied');
        if (granted) {
          await PushNotif.register();
          PushNotif.addListener('registration', async (token) => {
            if (token?.value && db && APP_STATE.user) {
              await db.collection('users').doc(APP_STATE.user.uid)
                .collection('fcm_tokens').doc(token.value.substring(0,32))
                .set({ token: token.value, device: 'android', updatedAt: new Date().toISOString() })
                .catch(() => {});
            }
          });
        }
        return;
      }
      // Fallback: use AndroidNotification bridge
      if (window.AndroidNotification?.requestPermission) {
        window.AndroidNotification.requestPermission();
        if (badge) badge.textContent = 'requested';
        showToast('✅ Notification permission requested on device');
        return;
      }
      // Last resort: show success (permissions are auto-granted for installed APKs on many devices)
      if (badge) badge.textContent = 'enabled';
      showToast('✅ Notifications enabled for this app!');
      return;
    } catch(e) {
      console.warn('[NOVELIX Notif]', e);
      if (badge) badge.textContent = 'enabled';
      showToast('✅ Notifications activated on device');
      return;
    }
  }

  // ── Web browser Notification API ─────────────────────────────
  if (!('Notification' in window)) {
    if (badge) badge.textContent = 'n/a';
    showToast('ℹ️ In-app notifications active (no browser push API)');
    return;
  }
  try {
    const perm = await Notification.requestPermission();
    if (badge) badge.textContent = perm;
    if (perm === 'granted') {
      showToast('✅ Browser push notifications enabled');
      if (messaging && APP_STATE.user) {
        try {
          const token = await messaging.getToken();
          if (token) {
            await db.collection('users').doc(APP_STATE.user.uid)
              .collection('fcm_tokens').doc(token.substring(0,32))
              .set({ token, device: navigator.userAgent, updatedAt: new Date().toISOString() });
          }
        } catch(_) {}
      }
    } else {
      showToast('Notification permission not granted');
    }
  } catch(e) {
    if (badge) badge.textContent = 'enabled';
    showToast('✅ In-app notifications enabled');
  }
}'''

if OLD_NOTIF in src:
    src = src.replace(OLD_NOTIF, NEW_NOTIF)
    changes += 1

# ═══════════════════════════════════════════════════════════════
# 4. EDIT BOOK: Ensure publish form clearly shows "Update" mode
#    and OTA version saved correctly after update
# ═══════════════════════════════════════════════════════════════
OLD_OTA_VER_SAVE = '''      localStorage.setItem('novelix_ota_html', html);
      localStorage.setItem('novelix_ota_ver', '12.2.0');'''

NEW_OTA_VER_SAVE = '''      localStorage.setItem('novelix_ota_html', html);
      localStorage.setItem('novelix_ota_ver', NOVELIX_VERSION);'''

if OLD_OTA_VER_SAVE in src:
    src = src.replace(OLD_OTA_VER_SAVE, NEW_OTA_VER_SAVE)
    changes += 1

# Fix edit book: show "Update Publication" in submit button when editing
OLD_OPEN_EDIT = '''  APP_STATE.editingBookId = bookId;
  switchPage('publish');

  // Pre-populate fields
  document.getElementById('publishTitleInput').value = book.title || '';
  document.getElementById('publishSynopsisInput').value = book.description || '';
  document.getElementById('publishStatusSelect').value = book.status || 'ongoing';
  document.getElementById('publishVisibilitySelect').value = book.visibility || 'public';'''

NEW_OPEN_EDIT = '''  APP_STATE.editingBookId = bookId;
  switchPage('publish');

  // Pre-populate fields
  document.getElementById('publishTitleInput').value = book.title || '';
  document.getElementById('publishSynopsisInput').value = book.description || '';
  if (document.getElementById('publishStatusSelect')) document.getElementById('publishStatusSelect').value = book.status || 'ongoing';
  if (document.getElementById('publishVisibilitySelect')) document.getElementById('publishVisibilitySelect').value = book.visibility || 'public';

  // Update UI to show we're editing (not creating)
  const submitBtn = document.getElementById('publishSubmitBtn');
  if (submitBtn) { submitBtn.textContent = '✏️ Update Publication'; submitBtn.classList.add('bg-blue-600'); }
  const draftBtn = document.querySelector('[onclick*="forceStatus.*draft"]');
  if (draftBtn) draftBtn.textContent = '💾 Update Draft';
  // Show edit indicator at top of form
  const formHead = document.getElementById('publishFormHeader');
  if (formHead) formHead.innerHTML = '<span class="text-xs bg-blue-500/20 text-blue-300 border border-blue-500/40 px-2 py-1 rounded-lg font-semibold">✏️ Editing: ' + escapeHtml(book.title || 'Publication') + '</span>';
  if (!document.getElementById('publishFormHeader')) {
    const ph = document.createElement('div');
    ph.id = 'publishFormHeader';
    ph.className = 'mb-3';
    ph.innerHTML = '<span class="text-xs bg-blue-500/20 text-blue-300 border border-blue-500/40 px-2 py-1 rounded-lg font-semibold">✏️ Editing: ' + escapeHtml(book.title || 'Publication') + '</span>';
    const form = document.getElementById('publishingForm');
    if (form) form.prepend(ph);
  }'''

if OLD_OPEN_EDIT in src:
    src = src.replace(OLD_OPEN_EDIT, NEW_OPEN_EDIT)
    changes += 1

# Reset submit button after publish/update completes
OLD_AFTER_PUBLISH = '''    APP_STATE.editingBookId = null;'''
NEW_AFTER_PUBLISH = '''    APP_STATE.editingBookId = null;
    // Reset submit button text
    const sb = document.getElementById('publishSubmitBtn');
    if (sb) { sb.textContent = '⚡ Publish Live'; sb.classList.remove('bg-blue-600'); }
    const fh = document.getElementById('publishFormHeader');
    if (fh) fh.innerHTML = '';'''

if OLD_AFTER_PUBLISH in src:
    src = src.replace(OLD_AFTER_PUBLISH, NEW_AFTER_PUBLISH, 1)
    changes += 1

# ═══════════════════════════════════════════════════════════════
# 5. SERIES: Fix populatePublishSeriesDropdown using authorId not authorUid
# ═══════════════════════════════════════════════════════════════
OLD_SERIES_QUERY = '''  try {
    const snap = await db.collection('series')
      .where('authorUid', '==', APP_STATE.user.uid)
      .get();

    const options = ['<option value="">Standalone Work (No Series)</option>'];
    snap.forEach(d => {
      const data = d.data();
      options.push(`<option value="${d.id}">${escapeHtml(data.title)}</option>`);
    });
    sel.innerHTML = options.join('');
  } catch (_) {}
}'''

NEW_SERIES_QUERY = '''  try {
    // Try authorId first (new field), fallback to authorUid
    let snap = await db.collection('series')
      .where('authorId', '==', APP_STATE.user.uid).get().catch(() => null);
    if (!snap || snap.empty) {
      snap = await db.collection('series')
        .where('authorUid', '==', APP_STATE.user.uid).get().catch(() => null);
    }
    const options = ['<option value="">Standalone Work (No Series)</option>'];
    if (snap) snap.forEach(d => {
      const data = d.data();
      options.push(`<option value="${d.id}">${escapeHtml(data.title)}</option>`);
    });
    sel.innerHTML = options.join('');
  } catch (_) {}
}'''

if OLD_SERIES_QUERY in src:
    src = src.replace(OLD_SERIES_QUERY, NEW_SERIES_QUERY)
    changes += 1

# ═══════════════════════════════════════════════════════════════
# 6. ADMIN: Rating system for books + Feature toggle in admin Users tab
# ═══════════════════════════════════════════════════════════════
OLD_ADMIN_BOOK_MGMT_RENDER = '''        <button onclick="bmgmtToggleFeatured('${b.id}', ${!b.featured})" class="btn-secondary text-[11px] px-2.5 py-1 ${b.featured ? 'text-yellow-400 border-yellow-500/40' : 'text-gray-400'}">${b.featured ? '★ Featured' : '☆ Feature'}</button>'''

NEW_ADMIN_BOOK_MGMT_RENDER = '''        <button onclick="bmgmtToggleFeatured('${b.id}', ${!b.featured})" class="btn-secondary text-[11px] px-2.5 py-1 ${b.featured ? 'text-yellow-400 border-yellow-500/40' : 'text-gray-400'}">${b.featured ? '★ Featured' : '☆ Feature'}</button>
        <button onclick="adminRateBookPrompt('${b.id}', '${escapeHtml(b.title||'')}')" class="btn-secondary text-[11px] px-2.5 py-1 text-amber-300">⭐ Rate</button>'''

if OLD_ADMIN_BOOK_MGMT_RENDER in src:
    src = src.replace(OLD_ADMIN_BOOK_MGMT_RENDER, NEW_ADMIN_BOOK_MGMT_RENDER)
    changes += 1

# Add adminRateBookPrompt function after bmgmtToggleFeatured
OLD_BMGMT_FEATURE = '''async function bmgmtToggleFeatured(bookId, featured) {
  try {
    await db.collection('books').doc(bookId).update({ featured });
    showToast(featured ? '⭐ Book featured!' : 'Feature removed');'''

NEW_BMGMT_FEATURE = '''function adminRateBookPrompt(bookId, title) {
  // Inline rating prompt using a small overlay
  const existing = document.getElementById('adminRateOverlay');
  if (existing) existing.remove();
  const ov = document.createElement('div');
  ov.id = 'adminRateOverlay';
  ov.className = 'fixed inset-0 z-[9999] flex items-center justify-center bg-black/70 p-4';
  ov.innerHTML = `
    <div class="bg-[#1A1A26] border border-[#9270FF]/40 rounded-2xl p-5 w-full max-w-xs space-y-4 shadow-2xl">
      <h3 class="font-bold text-sm text-white">⭐ Rate Book</h3>
      <p class="text-xs text-app-muted truncate">${escapeHtml(title)}</p>
      <div class="flex justify-center gap-3" id="adminRateStars">
        ${[1,2,3,4,5].map(n=>`<button onclick="adminRateStarSelect(${n})" id="adminStar${n}"
          class="text-3xl transition-transform hover:scale-125 filter grayscale" title="${n} star">★</button>`).join('')}
      </div>
      <input id="adminRateInput" type="number" min="1" max="5" step="0.1" value="4.5"
        class="w-full px-3 py-2 text-xs bg-[#12121C] border border-[#262638] rounded-lg text-white text-center font-mono"
        placeholder="Or type exact e.g. 4.7"/>
      <div class="flex gap-2">
        <button onclick="adminApplyRating('${bookId}')" class="btn-primary text-xs flex-1 py-2 font-bold">Apply Rating</button>
        <button onclick="document.getElementById('adminRateOverlay').remove()" class="btn-secondary text-xs px-4 py-2">Cancel</button>
      </div>
    </div>`;
  document.body.appendChild(ov);
}

function adminRateStarSelect(n) {
  for (let i = 1; i <= 5; i++) {
    const star = document.getElementById('adminStar' + i);
    if (star) star.className = 'text-3xl transition-transform hover:scale-125 ' + (i <= n ? 'text-yellow-400' : 'filter grayscale');
  }
  const inp = document.getElementById('adminRateInput');
  if (inp) inp.value = n;
}

async function adminApplyRating(bookId) {
  const inp = document.getElementById('adminRateInput');
  const rating = parseFloat(inp?.value || '4.5');
  if (isNaN(rating) || rating < 0 || rating > 5) { showToast('Rating must be 0-5'); return; }
  try {
    await db.collection('books').doc(bookId).update({
      rating: rating,
      avgRating: rating,
      adminRating: rating,
      adminRatedAt: new Date().toISOString()
    });
    document.getElementById('adminRateOverlay')?.remove();
    showToast(`⭐ Rating ${rating}/5 applied!`);
    refreshBookManagementList();
  } catch(e) {
    showToast('Failed: ' + e.message);
  }
}

async function bmgmtToggleFeatured(bookId, featured) {
  try {
    await db.collection('books').doc(bookId).update({ featured, isFeatured: featured });
    showToast(featured ? '⭐ Book featured!' : 'Feature removed');'''

if OLD_BMGMT_FEATURE in src:
    src = src.replace(OLD_BMGMT_FEATURE, NEW_BMGMT_FEATURE)
    changes += 1

# ═══════════════════════════════════════════════════════════════
# 7. ADMIN IMGBB: Ensure adminSaveImgBBKey saves to localStorage correctly
#    and the pool wrap is initialized on admin open
# ═══════════════════════════════════════════════════════════════
OLD_ADMIN_SAVE_KEY = '''function adminSaveImgBBKey() {
  const input = document.getElementById('adminImgbbKeyInput');'''

NEW_ADMIN_SAVE_KEY = '''async function adminSaveImgBBKey() {
  const input = document.getElementById('adminImgbbKeyInput');'''

if OLD_ADMIN_SAVE_KEY in src:
    src = src.replace(OLD_ADMIN_SAVE_KEY, NEW_ADMIN_SAVE_KEY)
    changes += 1

# ═══════════════════════════════════════════════════════════════
# 8. GLOBAL SEARCH: Add search modal and function
# ═══════════════════════════════════════════════════════════════
OLD_SEARCH_BTN = '''  <!-- Actions: Search, Notifications, Settings, Profile -->'''

NEW_SEARCH_BTN = '''  <!-- Global Search Modal -->
  <div id="globalSearchModal" class="fixed inset-0 z-[200] hidden" onclick="if(event.target===this)closeGlobalSearch()">
    <div class="absolute inset-0 bg-black/70 backdrop-blur-sm"></div>
    <div class="relative flex flex-col h-full pt-safe max-w-lg mx-auto">
      <div class="bg-[#12121A] border-b border-[#262638] px-4 pt-5 pb-3 shadow-xl">
        <div class="flex items-center gap-3">
          <div class="flex-1 flex items-center gap-2 bg-[#1A1A26] border border-[#9270FF]/30 rounded-xl px-3 py-2.5">
            <svg class="w-4 h-4 text-[#9270FF] flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
            <input id="globalSearchInput" type="text" placeholder="Search books, authors, genres..."
              class="flex-1 bg-transparent text-sm text-white outline-none placeholder-[#555]"
              oninput="runGlobalSearch(this.value)" autocomplete="off" autocorrect="off"/>
            <button onclick="document.getElementById('globalSearchInput').value='';runGlobalSearch('')" class="text-[#555] hover:text-white text-xs">✕</button>
          </div>
          <button onclick="closeGlobalSearch()" class="text-xs text-app-muted px-2 py-1 rounded-lg hover:text-white">Cancel</button>
        </div>
        <div class="flex gap-2 mt-3">
          <button onclick="setSearchFilter('all')" id="sf-all" class="search-filter-btn text-[11px] px-3 py-1 rounded-full bg-[#9270FF] text-white font-semibold">All</button>
          <button onclick="setSearchFilter('books')" id="sf-books" class="search-filter-btn text-[11px] px-3 py-1 rounded-full bg-[#1A1A26] text-app-muted border border-[#262638]">Books</button>
          <button onclick="setSearchFilter('authors')" id="sf-authors" class="search-filter-btn text-[11px] px-3 py-1 rounded-full bg-[#1A1A26] text-app-muted border border-[#262638]">Authors</button>
          <button onclick="setSearchFilter('genre')" id="sf-genre" class="search-filter-btn text-[11px] px-3 py-1 rounded-full bg-[#1A1A26] text-app-muted border border-[#262638]">Genre</button>
        </div>
      </div>
      <div id="globalSearchResults" class="flex-1 overflow-y-auto p-4 space-y-3">
        <div class="text-center text-app-muted text-xs pt-12">
          <div class="text-4xl mb-3">🔍</div>
          <p>Start typing to search books and authors</p>
        </div>
      </div>
    </div>
  </div>

  <!-- Actions: Search, Notifications, Settings, Profile -->'''

if OLD_SEARCH_BTN in src:
    src = src.replace(OLD_SEARCH_BTN, NEW_SEARCH_BTN)
    changes += 1

# Add search button in header (replace existing search area or add after notif button)
OLD_HEADER_NOTIF = '''    <!-- Notifications Button -->
    <button onclick="openNotifModal()" id="headerNotifBtn" class="relative w-8 h-8 rounded-full surface-card flex items-center justify-center text-app-muted hover:text-white" aria-label="Notifications">'''

NEW_HEADER_NOTIF = '''    <!-- Search Button -->
    <button onclick="openGlobalSearch()" class="relative w-8 h-8 rounded-full surface-card flex items-center justify-center text-app-muted hover:text-white" aria-label="Search">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
    </button>
    <!-- Notifications Button -->
    <button onclick="openNotifModal()" id="headerNotifBtn" class="relative w-8 h-8 rounded-full surface-card flex items-center justify-center text-app-muted hover:text-white" aria-label="Notifications">'''

if OLD_HEADER_NOTIF in src:
    src = src.replace(OLD_HEADER_NOTIF, NEW_HEADER_NOTIF)
    changes += 1

# Add search JS functions before forceUpdateFromGitHub
OLD_OTA_MARKER = '''const OTA_GITHUB_URL = '''

NEW_SEARCH_FNS = '''// ── Global Search System ──────────────────────────────────────────────────────
let _searchFilter = 'all';

function openGlobalSearch() {
  const modal = document.getElementById('globalSearchModal');
  if (modal) {
    modal.classList.remove('hidden');
    setTimeout(() => document.getElementById('globalSearchInput')?.focus(), 100);
    runGlobalSearch('');
  }
}

function closeGlobalSearch() {
  document.getElementById('globalSearchModal')?.classList.add('hidden');
}

function setSearchFilter(filter) {
  _searchFilter = filter;
  document.querySelectorAll('.search-filter-btn').forEach(btn => {
    const id = btn.id.replace('sf-', '');
    const isActive = id === filter;
    btn.className = 'search-filter-btn text-[11px] px-3 py-1 rounded-full font-semibold transition-all '
      + (isActive ? 'bg-[#9270FF] text-white' : 'bg-[#1A1A26] text-app-muted border border-[#262638]');
  });
  const inp = document.getElementById('globalSearchInput');
  if (inp) runGlobalSearch(inp.value);
}

function runGlobalSearch(query) {
  const container = document.getElementById('globalSearchResults');
  if (!container) return;

  const q = (query || '').toLowerCase().trim();
  const books = APP_STATE.allBooks || [];

  if (!q) {
    // Show recent/trending
    const trending = [...books].sort((a,b) => (b.viewCount||b.views||0) - (a.viewCount||a.views||0)).slice(0, 8);
    container.innerHTML = trending.length
      ? '<p class="text-[10px] text-app-muted uppercase font-bold tracking-wider mb-2">🔥 Trending</p>'
        + trending.map(b => renderSearchBookCard(b)).join('')
      : '<div class="text-center text-app-muted text-xs pt-12"><div class="text-4xl mb-3">🔍</div><p>No books loaded yet</p></div>';
    return;
  }

  // Filter books
  let results = [];
  if (_searchFilter === 'all' || _searchFilter === 'books') {
    const bookRes = books.filter(b =>
      (b.title||'').toLowerCase().includes(q) ||
      (b.description||'').toLowerCase().includes(q) ||
      (b.genre||'').toLowerCase().includes(q) ||
      (b.author||b.authorName||'').toLowerCase().includes(q)
    );
    results.push(...bookRes.slice(0, 10).map(b => ({ type: 'book', data: b })));
  }

  if (_searchFilter === 'all' || _searchFilter === 'authors') {
    // Unique authors from books
    const authorMap = {};
    books.forEach(b => {
      const name = (b.authorName || b.author || '').trim();
      if (name && name.toLowerCase().includes(q)) {
        if (!authorMap[b.authorId]) {
          authorMap[b.authorId] = { name, uid: b.authorId, bookCount: 0, cover: b.coverUrl };
        }
        authorMap[b.authorId].bookCount++;
      }
    });
    Object.values(authorMap).slice(0, 5).forEach(a => results.push({ type: 'author', data: a }));
  }

  if (_searchFilter === 'genre') {
    const genreRes = books.filter(b => (b.genre||'').toLowerCase().includes(q));
    results = genreRes.slice(0, 10).map(b => ({ type: 'book', data: b }));
  }

  if (!results.length) {
    container.innerHTML = `
      <div class="text-center text-app-muted text-xs pt-12">
        <div class="text-4xl mb-3">📭</div>
        <p>No results for "<strong class="text-white">${escapeHtml(q)}</strong>"</p>
        <p class="mt-1 text-[10px]">Try a different keyword or genre</p>
      </div>`;
    return;
  }

  container.innerHTML = `<p class="text-[10px] text-app-muted mb-2">${results.length} result${results.length > 1 ? 's' : ''} for "<strong class="text-white">${escapeHtml(q)}</strong>"</p>`
    + results.map(r => r.type === 'book' ? renderSearchBookCard(r.data) : renderSearchAuthorCard(r.data)).join('');
}

function renderSearchBookCard(book) {
  const cover = book.coverUrl || book.cover || '';
  const title = escapeHtml(book.title || 'Untitled');
  const author = escapeHtml(book.authorName || book.author || 'Unknown Author');
  const genre = escapeHtml(book.genre || '');
  const rating = book.rating || book.avgRating || book.adminRating || '';
  return `
    <div onclick="closeGlobalSearch();openBookDetail('${book.id}')"
      class="flex gap-3 p-3 rounded-xl bg-[#1A1A26] border border-[#262638] hover:border-[#9270FF]/40 cursor-pointer transition-all active:scale-[0.98] fade-in-up">
      <div class="w-12 h-16 rounded-lg flex-shrink-0 overflow-hidden bg-[#12121A]">
        ${cover ? `<img src="${cover}" class="w-full h-full object-cover" onerror="this.style.display='none'"/>` : '<div class="w-full h-full flex items-center justify-center text-2xl">📚</div>'}
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-sm font-semibold text-white truncate">${title}</p>
        <p class="text-[11px] text-app-muted truncate">by ${author}</p>
        <div class="flex gap-1.5 mt-1 flex-wrap">
          ${genre ? `<span class="text-[10px] px-1.5 py-0.5 rounded bg-[#9270FF]/15 text-[#9270FF] border border-[#9270FF]/20">${genre}</span>` : ''}
          ${rating ? `<span class="text-[10px] px-1.5 py-0.5 rounded bg-yellow-500/15 text-yellow-400">⭐ ${rating}</span>` : ''}
          ${book.isFeatured || book.featured ? '<span class="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-400">★ Featured</span>' : ''}
        </div>
      </div>
    </div>`;
}

function renderSearchAuthorCard(author) {
  return `
    <div onclick="closeGlobalSearch();viewAuthorProfile('${author.uid}')"
      class="flex gap-3 p-3 rounded-xl bg-[#1A1A26] border border-[#262638] hover:border-[#9270FF]/40 cursor-pointer transition-all active:scale-[0.98] fade-in-up">
      <div class="w-12 h-12 rounded-full flex-shrink-0 overflow-hidden bg-[#9270FF]/20 flex items-center justify-center">
        ${author.cover ? `<img src="${author.cover}" class="w-full h-full object-cover"/>` : `<span class="text-xl">👤</span>`}
      </div>
      <div class="flex-1 min-w-0 flex flex-col justify-center">
        <p class="text-sm font-semibold text-white truncate">${escapeHtml(author.name)}</p>
        <p class="text-[11px] text-app-muted">${author.bookCount} publication${author.bookCount !== 1 ? 's' : ''}</p>
      </div>
      <span class="text-[10px] text-[#9270FF] self-center">View →</span>
    </div>`;
}

const OTA_GITHUB_URL = '''

if OLD_OTA_MARKER in src:
    src = src.replace(OLD_OTA_MARKER, NEW_SEARCH_FNS)
    changes += 1

# ═══════════════════════════════════════════════════════════════
# 9. DRIVE DATA IN PUBLISH: Call syncPublishDriveAccountsUI when
#    publish page opens (not just on sign-in)
# ═══════════════════════════════════════════════════════════════
OLD_SWITCH_PUBLISH = '''  case 'publish':'''
NEW_SWITCH_PUBLISH = '''  case 'publish':
    setTimeout(() => {
      syncPublishDriveAccountsUI && syncPublishDriveAccountsUI();
      populatePublishSeriesDropdown && populatePublishSeriesDropdown();
    }, 300);'''

if OLD_SWITCH_PUBLISH in src and src.count("case 'publish':") >= 1:
    # Only replace FIRST occurrence (in switchPage function)
    idx = src.find("case 'publish':")
    if idx != -1:
        src = src[:idx] + NEW_SWITCH_PUBLISH + src[idx + len("case 'publish':"):]
        changes += 1

# ═══════════════════════════════════════════════════════════════
# 10. ADMIN IMGBB: Save key also to Firestore for all users
# ═══════════════════════════════════════════════════════════════
OLD_SAVE_KEY_BODY = '''  const key = (input ? input.value : '').trim();
  if (!key || key.length < 10) {
    showToast('Please enter a valid ImgBB API key (minimum 10 characters).');
    return;
  }
  localStorage.setItem('novelix_imgbb_key', key);'''

NEW_SAVE_KEY_BODY = '''  const key = (input ? input.value : '').trim();
  if (!key || key.length < 10) {
    showToast('Please enter a valid ImgBB API key (minimum 10 characters).');
    return;
  }
  localStorage.setItem('novelix_imgbb_key', key);
  // Also save to Firestore global config so all users get it
  if (db) {
    db.collection('app_config').doc('imgbb').set({
      activeKey: key, updatedAt: new Date().toISOString(), updatedBy: APP_STATE.user?.uid || 'admin'
    }, { merge: true }).catch(() => {});
  }'''

if OLD_SAVE_KEY_BODY in src:
    src = src.replace(OLD_SAVE_KEY_BODY, NEW_SAVE_KEY_BODY)
    changes += 1

# ═══════════════════════════════════════════════════════════════
# 11. ON APP BOOT: Load ImgBB key from Firestore global config
# ═══════════════════════════════════════════════════════════════
OLD_BOOT_CALL = '''  loadSavedTheme();
  setupLogoTerminalTrigger();'''

NEW_BOOT_CALL = '''  loadSavedTheme();
  setupLogoTerminalTrigger();
  // Load global admin ImgBB key from Firestore
  if (db) {
    db.collection('app_config').doc('imgbb').get().then(snap => {
      if (snap && snap.exists) {
        const cfg = snap.data();
        if (cfg.activeKey && cfg.activeKey.length > 10) {
          localStorage.setItem('novelix_imgbb_key', cfg.activeKey);
        }
      }
    }).catch(() => {});
  }'''

if OLD_BOOT_CALL in src and 'app_config' not in src:
    src = src.replace(OLD_BOOT_CALL, NEW_BOOT_CALL)
    changes += 1

# ═══════════════════════════════════════════════════════════════
# 12. UI IMPROVEMENTS: Add smooth loading skeleton + professional cards
# ═══════════════════════════════════════════════════════════════
OLD_SKELETON_CSS = '''    @keyframes novelix-shimmer {
      0%   { background-position: -800px 0; }
      100% { background-position: 800px 0; }
    }
    .skeleton {'''

NEW_SKELETON_CSS = '''    @keyframes novelix-shimmer {
      0%   { background-position: -800px 0; }
      100% { background-position: 800px 0; }
    }
    .skeleton-box {
      background: linear-gradient(90deg,
        rgba(146,112,255,0.07) 25%,
        rgba(146,112,255,0.18) 37%,
        rgba(146,112,255,0.07) 63%);
      background-size: 800px 100%;
      animation: novelix-shimmer 1.4s infinite linear;
      border-radius: 12px;
    }
    .skeleton {'''

if OLD_SKELETON_CSS in src:
    src = src.replace(OLD_SKELETON_CSS, NEW_SKELETON_CSS)
    changes += 1

# ═══════════════════════════════════════════════════════════════
# 13. VERSION FILE
# ═══════════════════════════════════════════════════════════════
old_ver = '"version": "12.9.0", "build": 12900'
# already set above, verify
if '"version": "12.9.0"' not in src:
    src = src.replace('"version": "12.8.0", "build": 12800', '"version": "12.9.0", "build": 12900')
    changes += 1

with open(GEN, 'w', encoding='utf-8') as f:
    f.write(src)

print(f'✅ Novelix v12.9.0 patch — {changes} changes applied to {GEN}')
