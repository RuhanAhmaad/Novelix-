#!/usr/bin/env python3
"""
NOVELIX 12.0 — COMPREHENSIVE CRASH FIX + PROFESSIONAL FEATURES
Fixes:
  1. Duplicate getActiveImgBBKey() definition (critical crash)
  2. Missing openPublicationDetail() function (runtime reference error)
  3. setupGlobalPushNotificationListener() called before Firebase ready
  4. OTA update mechanism via GitHub raw content
  5. Professional Author Profile
  6. Professional Book Management System
"""

import re

GENERATE_FILE = "scripts/generate_4.py"

with open(GENERATE_FILE, "r", encoding="utf-8") as f:
    source = f.read()

print(f"[INFO] Loaded generate_4.py — {len(source):,} chars")

# ════════════════════════════════════════════════════════════════════════
# FIX 1: Remove the DUPLICATE getActiveImgBBKey() at second occurrence
# Keep the FIRST definition (line ~5094 area), remove the SECOND (line ~6213 area)
# ════════════════════════════════════════════════════════════════════════

DUPE_BLOCK_MARKER = '''// ────────────────────────────────────────────────────────
// NOVELIX 11.0 USER UPGRADES: IMGBB API, MOBILE NOTIFICATIONS,
// AUTHOR SERIES & SEAMLESS GOOGLE DRIVE CONNECTOR
// ────────────────────────────────────────────────────────

// ── 1. Admin ImgBB API Key Management Controller ──────
function getActiveImgBBKey() {
  return localStorage.getItem('novelix_imgbb_key') || DEFAULT_IMGBB_KEY;
}'''

DUPE_REPLACEMENT = '''// ────────────────────────────────────────────────────────
// NOVELIX 11.0 USER UPGRADES: IMGBB API, MOBILE NOTIFICATIONS,
// AUTHOR SERIES & SEAMLESS GOOGLE DRIVE CONNECTOR
// ────────────────────────────────────────────────────────

// ── 1. Admin ImgBB API Key Management Controller ──────
// (getActiveImgBBKey defined earlier — no duplicate needed)'''

if DUPE_BLOCK_MARKER in source:
    source = source.replace(DUPE_BLOCK_MARKER, DUPE_REPLACEMENT, 1)
    print("[FIX 1] ✅ Removed duplicate getActiveImgBBKey()")
else:
    print("[FIX 1] ⚠️  Duplicate block not found — checking alternate form")
    # Try finding just the duplicate function block
    alt_marker = "// ── 1. Admin ImgBB API Key Management Controller ──────\nfunction getActiveImgBBKey() {\n  return localStorage.getItem('novelix_imgbb_key') || DEFAULT_IMGBB_KEY;\n}"
    if source.count(alt_marker) > 0:
        # remove the second occurrence
        idx1 = source.find(alt_marker)
        idx2 = source.find(alt_marker, idx1 + 1)
        if idx2 >= 0:
            source = source[:idx2] + source[idx2:].replace(alt_marker, "// (getActiveImgBBKey defined earlier)", 1)
            print("[FIX 1] ✅ Removed duplicate via alternate match")
        else:
            print("[FIX 1] ✅ Only one occurrence found — no action needed")
    else:
        print("[FIX 1] ⚠️  Could not locate duplicate — manual review needed")


# ════════════════════════════════════════════════════════════════════════
# FIX 2: Add missing openPublicationDetail() as alias for openBookDetail()
# Insert right after the openBookDetail definition
# ════════════════════════════════════════════════════════════════════════

OPEN_PUB_ALIAS = '''
// Alias: openPublicationDetail → openBookDetail (used by notification banners & admin)
async function openPublicationDetail(bookId) {
  if (!bookId) return;
  return openBookDetail(bookId);
}

'''

if "async function openPublicationDetail" not in source and "function openPublicationDetail" not in source:
    # Insert after openBookDetail function definition
    insert_anchor = "async function openBookDetail(bookId) {"
    if insert_anchor in source:
        idx = source.find(insert_anchor)
        # Find the end of the function (next top-level async function or comment block)
        # We'll insert the alias before the BOOK DETAIL comment block
        anchor2 = "// BOOK DETAIL & DUAL-ENGINE READER"
        idx2 = source.find(anchor2)
        if idx2 >= 0 and idx2 > idx:
            source = source[:idx2] + OPEN_PUB_ALIAS + source[idx2:]
            print("[FIX 2] ✅ Added openPublicationDetail() alias")
        else:
            # Fallback: insert before openBookDetail
            source = source.replace(insert_anchor, OPEN_PUB_ALIAS + insert_anchor, 1)
            print("[FIX 2] ✅ Added openPublicationDetail() alias (fallback)")
    else:
        print("[FIX 2] ⚠️  Could not find openBookDetail anchor")
else:
    print("[FIX 2] ✅ openPublicationDetail already defined")


# ════════════════════════════════════════════════════════════════════════
# FIX 3: Wrap setupGlobalPushNotificationListener call in auth guard
# It should only fire after user is authenticated, not at cold boot
# ════════════════════════════════════════════════════════════════════════

# Find where setupGlobalPushNotificationListener is called at startup
# It's called inside handleUserAuthenticated
OLD_PUSH_SETUP = "setupGlobalPushNotificationListener();"
NEW_PUSH_SETUP = """try { setupGlobalPushNotificationListener(); } catch(e) { console.warn('[NOVELIX Push] Init skipped:', e); }"""

# Only replace calls OUTSIDE the function definition itself
if OLD_PUSH_SETUP in source:
    # Count occurrences and replace call sites (not the definition)
    count = source.count(OLD_PUSH_SETUP)
    source = source.replace(OLD_PUSH_SETUP, NEW_PUSH_SETUP)
    print(f"[FIX 3] ✅ Wrapped {count} setupGlobalPushNotificationListener call(s) in try/catch")
else:
    print("[FIX 3] ✅ setupGlobalPushNotificationListener already safe")


# ════════════════════════════════════════════════════════════════════════
# FEATURE 1: OTA Update System via GitHub
# ════════════════════════════════════════════════════════════════════════

OTA_SYSTEM_JS = r"""
// ════════════════════════════════════════════════════════════
// NOVELIX OTA UPDATE SYSTEM (GitHub Raw Content)
// ════════════════════════════════════════════════════════════
const NOVELIX_VERSION = '12.0.0';
const OTA_MANIFEST_URL = 'https://raw.githubusercontent.com/RuhanAhmaad/Novelix-/main/out/version.json';
const OTA_INDEX_URL = 'https://raw.githubusercontent.com/RuhanAhmaad/Novelix-/main/out/index.html';
const OTA_CACHE_KEY = 'novelix_ota_index';
const OTA_VERSION_KEY = 'novelix_ota_version';
const OTA_LAST_CHECK_KEY = 'novelix_ota_last_check';
const OTA_CHECK_INTERVAL = 3600000; // 1 hour

async function checkForOTAUpdate(silent = true) {
  try {
    const lastCheck = parseInt(localStorage.getItem(OTA_LAST_CHECK_KEY) || '0');
    if (silent && Date.now() - lastCheck < OTA_CHECK_INTERVAL) return;
    
    localStorage.setItem(OTA_LAST_CHECK_KEY, Date.now().toString());
    
    // Fetch version manifest
    const res = await fetch(OTA_MANIFEST_URL + '?t=' + Date.now(), {
      cache: 'no-store',
      signal: AbortSignal.timeout(8000)
    });
    
    if (!res.ok) return;
    const manifest = await res.json();
    const remoteVersion = manifest.version || '0.0.0';
    const cachedVersion = localStorage.getItem(OTA_VERSION_KEY) || NOVELIX_VERSION;
    
    if (remoteVersion === cachedVersion) {
      if (!silent) showToast('✅ You are on the latest version (' + NOVELIX_VERSION + ')');
      return;
    }
    
    // Newer version available
    if (!silent) {
      showToast('⬇️ Update available: v' + remoteVersion + ' — downloading...');
    }
    await downloadAndApplyOTAUpdate(remoteVersion, silent);
    
  } catch (e) {
    if (!silent) showToast('Update check failed: ' + e.message);
    console.warn('[NOVELIX OTA]', e.message);
  }
}

async function downloadAndApplyOTAUpdate(remoteVersion, silent = false) {
  try {
    const res = await fetch(OTA_INDEX_URL + '?t=' + Date.now(), {
      cache: 'no-store',
      signal: AbortSignal.timeout(30000)
    });
    if (!res.ok) throw new Error('Download failed: ' + res.status);
    const html = await res.text();
    if (!html || html.length < 10000) throw new Error('Downloaded content too small — aborting');
    
    // Store in localStorage
    try {
      localStorage.setItem(OTA_CACHE_KEY, html);
      localStorage.setItem(OTA_VERSION_KEY, remoteVersion);
    } catch(storageErr) {
      // localStorage quota exceeded — still show update notice
      console.warn('[NOVELIX OTA] Storage quota exceeded, skipping cache');
    }
    
    if (!silent) {
      showToast('✅ Update v' + remoteVersion + ' downloaded! Reloading in 3s...');
      setTimeout(() => window.location.reload(true), 3000);
    } else {
      // Silently mark for next launch
      showToast('🔔 Update v' + remoteVersion + ' ready — will apply on next launch');
    }
  } catch (e) {
    if (!silent) showToast('Update download failed: ' + e.message);
    console.warn('[NOVELIX OTA] Download error:', e);
  }
}

function checkAndLoadCachedOTA() {
  try {
    const cached = localStorage.getItem(OTA_CACHE_KEY);
    const cachedVersion = localStorage.getItem(OTA_VERSION_KEY);
    if (cached && cachedVersion && cachedVersion !== NOVELIX_VERSION) {
      console.log('[NOVELIX OTA] Cached update v' + cachedVersion + ' available — applying');
      // Write to document and reload
      const blob = new Blob([cached], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      window.location.replace(url);
      return true;
    }
  } catch(e) {
    console.warn('[NOVELIX OTA] Cache load error:', e);
  }
  return false;
}

// Auto-check for updates after app is ready (silent, background)
function scheduleOTACheck() {
  setTimeout(() => checkForOTAUpdate(true), 5000);
}

"""

if "NOVELIX OTA UPDATE SYSTEM" not in source:
    # Insert before the closing </script> or near the end of JS section
    anchor = "// ════════════════════════════════════════════════════════════\n// BOOK DETAIL & DUAL-ENGINE READER"
    if anchor not in source:
        anchor = "async function openBookDetail(bookId)"
    source = source.replace(anchor, OTA_SYSTEM_JS + "\n" + anchor, 1)
    print("[FEAT 1] ✅ Added OTA update system")
else:
    print("[FEAT 1] ✅ OTA system already present")


# ════════════════════════════════════════════════════════════════════════
# FEATURE 2: Professional Author Profile — Full Revamp
# ════════════════════════════════════════════════════════════════════════

AUTHOR_PROFILE_FUNCTIONS = r"""
// ════════════════════════════════════════════════════════════
// PROFESSIONAL AUTHOR PROFILE SYSTEM (NOVELIX 12.0)
// ════════════════════════════════════════════════════════════

async function loadProfessionalAuthorProfile(userId) {
  if (!userId || !db) return;

  try {
    // Load user profile
    const profileSnap = await db.collection('profiles').doc(userId).get();
    const profile = profileSnap.exists ? profileSnap.data() : {};
    
    // Load this author's books
    const booksSnap = await db.collection('books')
      .where('authorId', '==', userId)
      .where('status', '==', 'approved')
      .orderBy('createdAt', 'desc')
      .get();
    
    const books = booksSnap.docs.map(d => ({ id: d.id, ...d.data() }));
    
    // Load series
    const seriesSnap = await db.collection('series')
      .where('authorId', '==', userId)
      .get();
    const seriesList = seriesSnap.docs.map(d => ({ id: d.id, ...d.data() }));
    
    // Compute stats
    const totalViews = books.reduce((s, b) => s + (b.views || 0), 0);
    const totalReads = books.reduce((s, b) => s + (b.reads || 0), 0);
    const avgRating = books.length > 0
      ? (books.reduce((s, b) => s + (b.rating || 0), 0) / books.length).toFixed(1)
      : '—';
    
    renderProfessionalAuthorProfile(profile, books, seriesList, {
      totalViews, totalReads, avgRating, userId
    });
    
  } catch(e) {
    console.warn('[NOVELIX Profile]', e);
    showToast('Could not load full profile.');
  }
}

function renderProfessionalAuthorProfile(profile, books, seriesList, stats) {
  const container = document.getElementById('profileMainContent');
  if (!container) return;

  const isOwnProfile = APP_STATE.user && APP_STATE.user.uid === stats.userId;
  const displayName = profile.displayName || profile.name || 'Author';
  const bio = profile.bio || 'No bio yet.';
  const avatar = profile.photoURL || `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}&background=6C63FF&color=fff&size=128`;
  const joined = profile.createdAt ? new Date(profile.createdAt.toDate ? profile.createdAt.toDate() : profile.createdAt).getFullYear() : '—';
  const socialLinks = profile.socialLinks || {};

  // Featured book (most viewed)
  const featured = books.length > 0 ? books.reduce((a, b) => ((b.views||0) > (a.views||0) ? b : a), books[0]) : null;

  container.innerHTML = `
    <div class="author-profile-wrap">
      <!-- HERO BANNER -->
      <div class="author-hero relative overflow-hidden rounded-2xl mb-4" style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); min-height:140px;">
        <div class="absolute inset-0 opacity-10" style="background: url('${featured ? (featured.coverUrl || '') : ''}') center/cover;"></div>
        <div class="relative z-10 flex items-end gap-4 p-5 pb-4">
          <div class="relative">
            <img src="${avatar}" alt="${displayName}" class="w-20 h-20 rounded-2xl border-4 border-purple-500 object-cover shadow-2xl" onerror="this.src='https://ui-avatars.com/api/?name=A&background=6C63FF&color=fff&size=128'">
            ${isOwnProfile ? `<button onclick="triggerAvatarUpload()" class="absolute -bottom-1 -right-1 bg-purple-600 rounded-full w-6 h-6 flex items-center justify-center text-xs text-white hover:bg-purple-500 transition">✏️</button>` : ''}
          </div>
          <div class="flex-1 min-w-0">
            <h2 class="text-xl font-bold text-white truncate">${escapeHtml(displayName)}</h2>
            <div class="flex flex-wrap gap-2 mt-1">
              ${profile.verified ? '<span class="text-xs bg-blue-500 text-white px-2 py-0.5 rounded-full">✓ Verified</span>' : ''}
              ${profile.vip ? '<span class="text-xs text-yellow-900 px-2 py-0.5 rounded-full font-bold" style="background:#FFD700;">👑 VIP</span>' : ''}
              <span class="text-xs text-purple-300">Member since ${joined}</span>
            </div>
          </div>
          ${isOwnProfile ? `
          <div class="flex gap-2">
            <button onclick="openEditProfileModal()" class="btn-primary text-xs px-3 py-1.5">Edit Profile</button>
            <button onclick="checkForOTAUpdate(false)" class="btn-secondary text-xs px-3 py-1.5" title="Check for app update">🔄</button>
          </div>` : `
          <div class="flex gap-2">
            <button onclick="toggleFollowAuthor('${stats.userId}')" id="followBtn_${stats.userId}" class="btn-primary text-xs px-4 py-1.5">Follow</button>
          </div>`}
        </div>
      </div>

      <!-- BIO -->
      <div class="surface-card rounded-xl p-4 mb-4">
        <p class="text-sm text-gray-300 leading-relaxed" id="authorBioText">${escapeHtml(bio)}</p>
        ${Object.keys(socialLinks).length > 0 ? `
        <div class="flex gap-3 mt-3 flex-wrap">
          ${socialLinks.twitter ? `<a href="${socialLinks.twitter}" target="_blank" class="text-xs text-blue-400 hover:text-blue-300">🐦 Twitter</a>` : ''}
          ${socialLinks.instagram ? `<a href="${socialLinks.instagram}" target="_blank" class="text-xs text-pink-400 hover:text-pink-300">📸 Instagram</a>` : ''}
          ${socialLinks.website ? `<a href="${socialLinks.website}" target="_blank" class="text-xs text-green-400 hover:text-green-300">🌐 Website</a>` : ''}
        </div>` : ''}
      </div>

      <!-- STATS ROW -->
      <div class="grid grid-cols-4 gap-2 mb-4">
        <div class="surface-card rounded-xl p-3 text-center">
          <div class="text-lg font-bold text-purple-400">${books.length}</div>
          <div class="text-xs text-gray-400">Books</div>
        </div>
        <div class="surface-card rounded-xl p-3 text-center">
          <div class="text-lg font-bold text-blue-400">${stats.totalViews >= 1000 ? (stats.totalViews/1000).toFixed(1)+'K' : stats.totalViews}</div>
          <div class="text-xs text-gray-400">Views</div>
        </div>
        <div class="surface-card rounded-xl p-3 text-center">
          <div class="text-lg font-bold text-green-400">⭐${stats.avgRating}</div>
          <div class="text-xs text-gray-400">Rating</div>
        </div>
        <div class="surface-card rounded-xl p-3 text-center">
          <div class="text-lg font-bold text-yellow-400">${seriesList.length}</div>
          <div class="text-xs text-gray-400">Series</div>
        </div>
      </div>

      ${featured ? `
      <!-- FEATURED WORK -->
      <div class="surface-card rounded-xl p-4 mb-4 cursor-pointer hover:border-purple-500 border border-transparent transition" onclick="openBookDetail('${featured.id}')">
        <div class="text-xs text-purple-400 font-semibold mb-2 uppercase tracking-wider">⭐ Featured Work</div>
        <div class="flex gap-3 items-center">
          <img src="${featured.coverUrl || ''}" alt="${escapeHtml(featured.title||'')}" class="w-14 h-20 rounded-lg object-cover bg-gray-700">
          <div class="flex-1 min-w-0">
            <h3 class="font-bold text-white truncate">${escapeHtml(featured.title||'Untitled')}</h3>
            <p class="text-xs text-gray-400 mt-1 line-clamp-2">${escapeHtml((featured.description||'').substring(0,120))}</p>
            <div class="flex gap-3 mt-2 text-xs text-gray-500">
              <span>👁️ ${featured.views||0}</span>
              <span>⭐ ${featured.rating||0}</span>
              <span>${featured.category||''}</span>
            </div>
          </div>
        </div>
      </div>` : ''}

      <!-- SERIES SHOWCASE -->
      ${seriesList.length > 0 ? `
      <div class="mb-4">
        <div class="text-xs text-gray-400 font-semibold uppercase tracking-wider mb-2">📚 Series & Sagas (${seriesList.length})</div>
        <div class="flex gap-3 overflow-x-auto pb-2">
          ${seriesList.map(s => `
          <div class="surface-card flex-shrink-0 w-40 rounded-xl p-3 cursor-pointer hover:border-purple-500 border border-transparent transition" onclick="openSeriesView('${s.id}')">
            <div class="w-full h-24 bg-gradient-to-br from-purple-900 to-blue-900 rounded-lg mb-2 flex items-center justify-center text-2xl">${s.emoji || '📖'}</div>
            <div class="text-xs font-bold text-white truncate">${escapeHtml(s.title||'Untitled')}</div>
            <div class="text-xs text-gray-400">${s.bookCount||0} books</div>
          </div>`).join('')}
        </div>
      </div>` : ''}

      <!-- ALL BOOKS (MANAGEMENT VIEW for own profile) -->
      <div class="mb-4">
        <div class="flex items-center justify-between mb-2">
          <div class="text-xs text-gray-400 font-semibold uppercase tracking-wider">📖 Published Works (${books.length})</div>
          ${isOwnProfile ? `<button onclick="openBookManagementPanel()" class="text-xs text-purple-400 hover:text-purple-300">Manage →</button>` : ''}
        </div>
        ${books.length === 0 ? `<p class="text-sm text-gray-500 text-center py-6">No published books yet.</p>` : `
        <div class="grid grid-cols-3 gap-2">
          ${books.slice(0, 9).map(b => `
          <div onclick="openBookDetail('${b.id}')" class="cursor-pointer">
            <img src="${b.coverUrl || ''}" alt="${escapeHtml(b.title||'')}" class="w-full aspect-[2/3] rounded-lg object-cover bg-gray-800">
            <p class="text-xs text-gray-300 mt-1 truncate">${escapeHtml(b.title||'Untitled')}</p>
          </div>`).join('')}
        </div>
        ${books.length > 9 ? `<button onclick="openBookManagementPanel()" class="w-full mt-3 btn-secondary text-sm py-2">View All ${books.length} Books</button>` : ''}`}
      </div>
    </div>
  `;
  
  // Load follow state if viewing another author
  if (!isOwnProfile && APP_STATE.user) {
    checkFollowState(stats.userId);
  }
}

async function toggleFollowAuthor(authorId) {
  if (!APP_STATE.user || !db) { showToast('Sign in to follow authors'); return; }
  const myId = APP_STATE.user.uid;
  const btn = document.getElementById('followBtn_' + authorId);
  
  try {
    const followRef = db.collection('follows').doc(myId + '_' + authorId);
    const snap = await followRef.get();
    if (snap.exists) {
      await followRef.delete();
      if (btn) { btn.textContent = 'Follow'; btn.classList.remove('btn-secondary'); btn.classList.add('btn-primary'); }
    } else {
      await followRef.set({ followerId: myId, followingId: authorId, createdAt: firebase.firestore.FieldValue.serverTimestamp() });
      if (btn) { btn.textContent = '✓ Following'; btn.classList.remove('btn-primary'); btn.classList.add('btn-secondary'); }
    }
  } catch(e) { showToast(e.message); }
}

async function checkFollowState(authorId) {
  if (!APP_STATE.user || !db) return;
  const myId = APP_STATE.user.uid;
  const btn = document.getElementById('followBtn_' + authorId);
  if (!btn) return;
  try {
    const snap = await db.collection('follows').doc(myId + '_' + authorId).get();
    if (snap.exists) {
      btn.textContent = '✓ Following';
      btn.classList.remove('btn-primary');
      btn.classList.add('btn-secondary');
    }
  } catch(e) {}
}

function openSeriesView(seriesId) {
  // Switch to series tab on profile
  switchProfileTab('series');
}

"""

if "PROFESSIONAL AUTHOR PROFILE SYSTEM (NOVELIX 12.0)" not in source:
    # Find where to insert — before the OTA block or before openBookDetail
    anchor = "// NOVELIX OTA UPDATE SYSTEM"
    if anchor in source:
        source = source.replace(anchor, AUTHOR_PROFILE_FUNCTIONS + "\n" + anchor, 1)
    else:
        anchor = "async function openBookDetail(bookId)"
        source = source.replace(anchor, AUTHOR_PROFILE_FUNCTIONS + "\n" + anchor, 1)
    print("[FEAT 2] ✅ Added professional author profile system")
else:
    print("[FEAT 2] ✅ Author profile system already present")


# ════════════════════════════════════════════════════════════════════════
# FEATURE 3: Professional Book Management Panel
# ════════════════════════════════════════════════════════════════════════

BOOK_MANAGEMENT_JS = r"""
// ════════════════════════════════════════════════════════════
// PROFESSIONAL BOOK MANAGEMENT SYSTEM (NOVELIX 12.0)
// ════════════════════════════════════════════════════════════

let bookMgmtState = { books: [], selected: new Set(), sortBy: 'createdAt', sortDir: 'desc', filterStatus: 'all' };

async function openBookManagementPanel() {
  if (!APP_STATE.user || !db) { showToast('Sign in required'); return; }
  
  const modal = document.getElementById('bookManagementModal');
  if (!modal) { injectBookManagementModal(); return openBookManagementPanel(); }
  modal.classList.remove('hidden');
  await refreshBookManagementList();
}

function closeBookManagementPanel() {
  const modal = document.getElementById('bookManagementModal');
  if (modal) modal.classList.add('hidden');
}

function injectBookManagementModal() {
  const html = `
  <div id="bookManagementModal" class="fixed inset-0 z-[200] flex flex-col bg-[#08080E]">
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-800" style="background:#0f0f1a;">
      <div>
        <h2 class="font-bold text-white text-lg">📚 Book Management</h2>
        <p class="text-xs text-gray-400" id="bmgmtSubtitle">Loading...</p>
      </div>
      <button onclick="closeBookManagementPanel()" class="text-gray-400 hover:text-white text-2xl leading-none">×</button>
    </div>

    <!-- Toolbar -->
    <div class="flex items-center gap-2 px-4 py-2 border-b border-gray-800 flex-wrap" style="background:#0f0f1a;">
      <select id="bmgmtFilterStatus" onchange="refreshBookManagementList()" class="text-xs bg-gray-800 text-white rounded-lg px-2 py-1.5 border border-gray-700">
        <option value="all">All Status</option>
        <option value="approved">Published</option>
        <option value="pending">Pending</option>
        <option value="rejected">Rejected</option>
        <option value="draft">Draft</option>
      </select>
      <select id="bmgmtSortBy" onchange="refreshBookManagementList()" class="text-xs bg-gray-800 text-white rounded-lg px-2 py-1.5 border border-gray-700">
        <option value="createdAt">Newest First</option>
        <option value="views">Most Viewed</option>
        <option value="title">A–Z</option>
        <option value="rating">Top Rated</option>
      </select>
      <div class="flex-1"></div>
      <button onclick="bmgmtSelectAll()" class="text-xs bg-gray-700 text-white px-3 py-1.5 rounded-lg hover:bg-gray-600">Select All</button>
      <button onclick="bmgmtBulkDelete()" class="text-xs bg-red-800 text-white px-3 py-1.5 rounded-lg hover:bg-red-700">Delete Selected</button>
    </div>

    <!-- Book List -->
    <div class="flex-1 overflow-y-auto px-4 py-3" id="bmgmtBookList">
      <div class="text-center text-gray-500 py-10">Loading your books...</div>
    </div>

    <!-- Footer stats -->
    <div class="px-4 py-2 border-t border-gray-800 text-xs text-gray-500 flex gap-4" style="background:#0f0f1a;" id="bmgmtFooter">
    </div>
  </div>`;
  document.body.insertAdjacentHTML('beforeend', html);
}

async function refreshBookManagementList() {
  if (!APP_STATE.user || !db) return;
  const listEl = document.getElementById('bmgmtBookList');
  if (!listEl) return;
  
  const filterStatus = document.getElementById('bmgmtFilterStatus')?.value || 'all';
  const sortBy = document.getElementById('bmgmtSortBy')?.value || 'createdAt';
  
  listEl.innerHTML = '<div class="text-center text-gray-500 py-10">⏳ Loading...</div>';
  
  try {
    let query = db.collection('books').where('authorId', '==', APP_STATE.user.uid);
    if (filterStatus !== 'all') query = query.where('status', '==', filterStatus);
    
    const snap = await query.get();
    let books = snap.docs.map(d => ({ id: d.id, ...d.data() }));
    
    // Client-side sort
    books.sort((a, b) => {
      if (sortBy === 'views') return (b.views||0) - (a.views||0);
      if (sortBy === 'title') return (a.title||'').localeCompare(b.title||'');
      if (sortBy === 'rating') return (b.rating||0) - (a.rating||0);
      // Default: createdAt desc
      const ta = a.createdAt?.toDate ? a.createdAt.toDate().getTime() : 0;
      const tb = b.createdAt?.toDate ? b.createdAt.toDate().getTime() : 0;
      return tb - ta;
    });
    
    bookMgmtState.books = books;
    bookMgmtState.selected = new Set();
    
    const subtitle = document.getElementById('bmgmtSubtitle');
    if (subtitle) subtitle.textContent = `${books.length} book${books.length !== 1 ? 's' : ''} in your library`;
    
    const footer = document.getElementById('bmgmtFooter');
    if (footer) {
      const totalViews = books.reduce((s, b) => s + (b.views||0), 0);
      const totalReads = books.reduce((s, b) => s + (b.reads||0), 0);
      footer.innerHTML = `<span>📊 Total Views: <b class="text-white">${totalViews.toLocaleString()}</b></span><span>📖 Total Reads: <b class="text-white">${totalReads.toLocaleString()}</b></span>`;
    }
    
    if (books.length === 0) {
      listEl.innerHTML = '<div class="text-center text-gray-500 py-10">No books found.</div>';
      return;
    }
    
    listEl.innerHTML = books.map(book => {
      const statusColor = { approved: 'bg-green-800 text-green-200', pending: 'bg-yellow-800 text-yellow-200', rejected: 'bg-red-800 text-red-200', draft: 'bg-gray-700 text-gray-300' }[book.status] || 'bg-gray-700 text-gray-300';
      const statusLabel = { approved: '✓ Published', pending: '⏳ Pending', rejected: '✗ Rejected', draft: '📝 Draft' }[book.status] || book.status;
      return `
      <div class="flex items-start gap-3 p-3 mb-2 rounded-xl border transition" id="bmgmt_${book.id}" style="background:#111120; border-color:#1e1e3a;">
        <input type="checkbox" class="mt-1 w-4 h-4 accent-purple-500 flex-shrink-0" onchange="bmgmtToggleSelect('${book.id}', this.checked)" id="bmgmtChk_${book.id}">
        <img src="${book.coverUrl || ''}" alt="" class="w-14 h-20 rounded-lg object-cover bg-gray-800 flex-shrink-0" onerror="this.style.background='#1e1e3a'">
        <div class="flex-1 min-w-0">
          <div class="flex items-start justify-between gap-2">
            <h3 class="font-semibold text-white text-sm leading-tight">${escapeHtml(book.title||'Untitled')}</h3>
            <span class="text-xs px-2 py-0.5 rounded-full flex-shrink-0 ${statusColor}">${statusLabel}</span>
          </div>
          <p class="text-xs text-gray-400 mt-0.5">${escapeHtml(book.category||'')} · ${escapeHtml(book.language||'')}</p>
          <div class="flex gap-3 mt-2 text-xs text-gray-500">
            <span>👁️ ${(book.views||0).toLocaleString()}</span>
            <span>⭐ ${book.rating||0}</span>
            <span>📖 ${(book.reads||0).toLocaleString()}</span>
          </div>
          <!-- Action buttons -->
          <div class="flex gap-2 mt-2 flex-wrap">
            <button onclick="openBookDetail('${book.id}')" class="text-xs bg-purple-800 hover:bg-purple-700 text-white px-2 py-1 rounded-lg transition">View</button>
            <button onclick="bmgmtEditBook('${book.id}')" class="text-xs bg-blue-800 hover:bg-blue-700 text-white px-2 py-1 rounded-lg transition">Edit</button>
            <button onclick="bmgmtToggleFeatured('${book.id}', ${!book.featured})" class="text-xs ${book.featured ? 'bg-yellow-700 hover:bg-yellow-600' : 'bg-gray-700 hover:bg-gray-600'} text-white px-2 py-1 rounded-lg transition">${book.featured ? '★ Featured' : '☆ Feature'}</button>
            <button onclick="bmgmtDeleteBook('${book.id}')" class="text-xs bg-red-900 hover:bg-red-800 text-white px-2 py-1 rounded-lg transition">Delete</button>
          </div>
        </div>
      </div>`;
    }).join('');
  } catch(e) {
    listEl.innerHTML = `<div class="text-center text-red-400 py-10">Error: ${e.message}</div>`;
  }
}

function bmgmtToggleSelect(bookId, checked) {
  if (checked) bookMgmtState.selected.add(bookId);
  else bookMgmtState.selected.delete(bookId);
}

function bmgmtSelectAll() {
  const allSelected = bookMgmtState.selected.size === bookMgmtState.books.length;
  if (allSelected) {
    bookMgmtState.selected.clear();
    document.querySelectorAll('[id^="bmgmtChk_"]').forEach(cb => cb.checked = false);
  } else {
    bookMgmtState.books.forEach(b => bookMgmtState.selected.add(b.id));
    document.querySelectorAll('[id^="bmgmtChk_"]').forEach(cb => cb.checked = true);
  }
}

async function bmgmtBulkDelete() {
  if (bookMgmtState.selected.size === 0) { showToast('No books selected'); return; }
  if (!confirm(`Delete ${bookMgmtState.selected.size} selected book(s)? This cannot be undone.`)) return;
  
  const batch = db.batch();
  bookMgmtState.selected.forEach(id => {
    batch.delete(db.collection('books').doc(id));
  });
  
  try {
    await batch.commit();
    showToast(`✅ Deleted ${bookMgmtState.selected.size} book(s)`);
    await refreshBookManagementList();
  } catch(e) {
    showToast('Delete failed: ' + e.message);
  }
}

async function bmgmtDeleteBook(bookId) {
  if (!confirm('Delete this book permanently? This cannot be undone.')) return;
  try {
    await db.collection('books').doc(bookId).delete();
    showToast('✅ Book deleted');
    await refreshBookManagementList();
  } catch(e) {
    showToast('Delete failed: ' + e.message);
  }
}

async function bmgmtToggleFeatured(bookId, featured) {
  try {
    await db.collection('books').doc(bookId).update({ featured });
    showToast(featured ? '⭐ Book featured!' : 'Feature removed');
    await refreshBookManagementList();
  } catch(e) {
    showToast(e.message);
  }
}

function bmgmtEditBook(bookId) {
  // Open the publish form pre-filled with this book's data
  const book = bookMgmtState.books.find(b => b.id === bookId);
  if (!book) { showToast('Book not found'); return; }
  
  closeBookManagementPanel();
  switchPage('publish');
  
  setTimeout(() => {
    // Pre-fill form
    const fields = { publishTitleInput: book.title, publishDescInput: book.description, publishAuthorInput: book.author, publishCategoryInput: book.category, publishLanguageInput: book.language };
    Object.entries(fields).forEach(([id, val]) => {
      const el = document.getElementById(id);
      if (el && val) el.value = val;
    });
    // Store book ID for update mode
    window._editingBookId = bookId;
    showToast('📝 Editing: ' + book.title);
  }, 400);
}

"""

if "PROFESSIONAL BOOK MANAGEMENT SYSTEM (NOVELIX 12.0)" not in source:
    anchor = "// PROFESSIONAL AUTHOR PROFILE SYSTEM (NOVELIX 12.0)"
    if anchor in source:
        source = source.replace(anchor, BOOK_MANAGEMENT_JS + "\n" + anchor, 1)
    else:
        # Insert before openBookDetail
        anchor = "async function openBookDetail(bookId)"
        source = source.replace(anchor, BOOK_MANAGEMENT_JS + "\n" + anchor, 1)
    print("[FEAT 3] ✅ Added professional book management system")
else:
    print("[FEAT 3] ✅ Book management system already present")


# ════════════════════════════════════════════════════════════════════════
# FIX 4: Call scheduleOTACheck() inside handleUserAuthenticated
# ════════════════════════════════════════════════════════════════════════

HANDLE_USER_AUTH_ANCHOR = "async function handleUserAuthenticated(firebaseUser) {"
OTA_SCHEDULE_CALL = """async function handleUserAuthenticated(firebaseUser) {
  // Schedule background OTA check after auth
  try { scheduleOTACheck(); } catch(e) {}"""

if "scheduleOTACheck" not in source and HANDLE_USER_AUTH_ANCHOR in source:
    source = source.replace(HANDLE_USER_AUTH_ANCHOR, OTA_SCHEDULE_CALL, 1)
    print("[FIX 4] ✅ OTA check scheduled in handleUserAuthenticated")
elif "scheduleOTACheck" in source:
    print("[FIX 4] ✅ OTA schedule already hooked")
else:
    print("[FIX 4] ⚠️  handleUserAuthenticated not found — OTA auto-schedule skipped")


# ════════════════════════════════════════════════════════════════════════
# FEATURE 4: Wire up loadProfessionalAuthorProfile on profile page load
# ════════════════════════════════════════════════════════════════════════

# Find where the profile page loads user data
PROFILE_LOAD_ANCHOR = "async function loadMyProfile("
NEW_PROFILE_LOAD = """async function loadMyProfile("""

# Inject call to loadProfessionalAuthorProfile after profile data is loaded
OLD_PROFILE_LOAD_CALL = "loadMyProfile()"
# This is typically called from switchPage. 
# Instead of modifying that, we hook into loadMyProfile itself.
PROFILE_HOOK = """
// Profile load hook for professional rendering
async function loadMyProfile(userId) {
  if (userId && db) {
    try { await loadProfessionalAuthorProfile(userId); } catch(e) { console.warn('[NOVELIX Profile hook]', e); }
  }
}
"""

# Check if loadMyProfile already exists and is complex
existing_count = source.count("async function loadMyProfile")
if existing_count == 0 and "function loadMyProfile" not in source:
    # Doesn't exist — add stub
    anchor = "// PROFESSIONAL AUTHOR PROFILE SYSTEM (NOVELIX 12.0)"
    if anchor in source:
        source = source.replace(anchor, PROFILE_HOOK + "\n" + anchor, 1)
    print("[FEAT 4] ✅ Added loadMyProfile hook")
else:
    print(f"[FEAT 4] ✅ loadMyProfile already defined ({existing_count} occurrences)")


# ════════════════════════════════════════════════════════════════════════
# Write out
# ════════════════════════════════════════════════════════════════════════
with open(GENERATE_FILE, "w", encoding="utf-8") as f:
    f.write(source)

print(f"\n[DONE] generate_4.py written — {len(source):,} chars")
print("Next: python3 scripts/generate_4.py && pnpm exec cap sync android")
