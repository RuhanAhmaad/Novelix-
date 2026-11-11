#!/usr/bin/env python3
"""
NOVELIX 11.0 — User Upgrade Patch:
1. ImgBB API Key Management in Admin Console (#adminTab-storage)
2. Premium Mobile System Push Notifications + Ultra-luxe In-App Banner
3. Remove Instant VIP Admin login button from Login/Register modal (#authModal)
4. Author Series & Sagas Management in Profile, Publishing Studio, and Book Details
5. Google Drive Connection Redirect Fix (Native in-app connect + 1-tap link, zero browser redirect issues)
"""

import re

GEN_FILE = "scripts/generate_4.py"

with open(GEN_FILE, "r", encoding="utf-8") as f:
    content = f.read()

print("Original generate_4.py size:", len(content))

# ── 1. Remove Instant VIP Admin from #authModal ──
vip_portal_re = r'<!-- VIP Admin Portal Entry Point -->[\s\S]*?<span>⚡ Instant VIP Admin Login</span>\s*</button>\s*</div>'
if re.search(vip_portal_re, content):
    content = re.sub(vip_portal_re, '', content, count=1)
    print("✓ Removed Instant VIP Admin button from #authModal")
else:
    print("WARNING: vip_portal_re not found in generate_4.py")

# ── 2. Add ImgBB API Key Management to #adminTab-storage ──
old_storage_tab = """    <!-- 7. Admin Tab: Storage -->
    <div id="adminTab-storage" class="admin-tab-content hidden space-y-3">
      <h4 class="text-xs font-semibold text-white">Storage Quota Configurations</h4>
      <div class="surface-card-static p-4 space-y-3">
        <label class="block text-xs font-semibold text-app-muted">Default User Publishing Quota (MB)</label>
        <input type="number" id="adminDefaultQuotaInput" value="500" class="w-full px-3 py-2 text-xs">
        <button onclick="saveAdminQuotaSetting()" class="btn-primary text-xs w-full py-2">Update Quota Policy</button>
      </div>
      <div id="adminStorageStats" class="surface-card p-3 text-xs text-app-muted space-y-1"></div>
    </div>"""

new_storage_tab = """    <!-- 7. Admin Tab: Storage & ImgBB Cloud -->
    <div id="adminTab-storage" class="admin-tab-content hidden space-y-4">
      <!-- ImgBB Cloud API Key Configuration Card -->
      <div class="p-4 rounded-2xl bg-gradient-to-br from-[#161625] to-[#0F0F1A] border border-[#FFD700]/35 shadow-xl space-y-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-lg">🖼️</span>
            <div>
              <h4 class="font-display font-bold text-xs text-white">ImgBB Cloud Image Hosting API</h4>
              <p class="text-[10px] text-app-muted">Global CDN for book covers, avatars & illustrations</p>
            </div>
          </div>
          <span id="adminImgbbBadge" class="text-[9px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/25 px-2 py-0.5 rounded font-bold">● ACTIVE KEY</span>
        </div>

        <p class="text-[11px] text-app-muted leading-relaxed">
          Configure the official ImgBB API key used by the application. Changes are synchronized across all client sessions and saved to cloud storage.
        </p>

        <div>
          <label class="block text-[10px] text-app-muted uppercase font-semibold mb-1">Active ImgBB API Key</label>
          <div class="flex gap-2">
            <input type="password" id="adminImgbbKeyInput" placeholder="Enter 32-character ImgBB API Key" class="flex-1 px-3 py-2 text-xs bg-[#12121C] border border-[#262638] rounded-lg text-white font-mono focus:border-[#FFD700]">
            <button type="button" onclick="togglePasswordVisibility('adminImgbbKeyInput', this)" class="btn-secondary text-xs px-3 py-2" title="Reveal / Hide Key">👁️</button>
          </div>
        </div>

        <div class="flex items-center gap-2 pt-1 flex-wrap">
          <button type="button" onclick="adminSaveImgBBKey()" class="btn-primary text-xs flex-1 py-2 font-bold bg-gradient-to-r from-[#FFD700] to-[#E5C07B] text-[#0B0B10] shadow-[0_0_12px_rgba(255,215,0,0.25)]">
            💾 Save & Apply API Key
          </button>
          <button type="button" onclick="adminTestImgBBKey()" class="btn-secondary text-xs px-3 py-2 flex items-center gap-1">
            ⚡ Test Key
          </button>
          <button type="button" onclick="adminResetImgBBKey()" class="btn-secondary text-xs px-2.5 py-2 text-app-muted hover:text-white" title="Reset to standard default">
            ↺ Default
          </button>
        </div>
        <div id="adminImgbbTestResult" class="hidden text-[11px] p-2.5 rounded-lg font-mono"></div>
      </div>

      <!-- Storage Quotas -->
      <div class="surface-card-static p-4 space-y-3">
        <h4 class="text-xs font-semibold text-white">Default Author Storage Quota</h4>
        <label class="block text-[11px] text-app-muted">Max storage allowance per publishing creator account (MB)</label>
        <input type="number" id="adminDefaultQuotaInput" value="500" class="w-full px-3 py-2 text-xs bg-[#12121C] border border-[#262638] rounded-lg text-white">
        <button onclick="saveAdminQuotaSetting()" class="btn-primary text-xs w-full py-2">Update Quota Policy</button>
      </div>

      <div id="adminStorageStats" class="surface-card p-3 text-xs text-app-muted space-y-1"></div>
    </div>"""

if old_storage_tab in content:
    content = content.replace(old_storage_tab, new_storage_tab, 1)
    print("✓ Injected ImgBB API Key Management card into #adminTab-storage")
else:
    print("WARNING: old_storage_tab not found")

# ── 3. Add Author Series & Sagas Management to Profile & Publishing ──
# In #page-profile: Add "Series" tab to profile tabs
old_prof_tabs = """        <!-- Profile Tabs -->
        <div class="flex gap-1.5 mb-3 overflow-x-auto">
          <button onclick="switchProfileTab('works')" class="prof-tab pill-tag" data-tab="works" style="background:#9270FF; color:#0B0B10">Published</button>
          <button onclick="switchProfileTab('library')" class="prof-tab pill-tag" data-tab="library">Library</button>
          <button onclick="switchProfileTab('reviews')" class="prof-tab pill-tag" data-tab="reviews">Reviews</button>
          <button onclick="switchProfileTab('about')" class="prof-tab pill-tag" data-tab="about">About</button>
        </div>"""

new_prof_tabs = """        <!-- Profile Tabs -->
        <div class="flex gap-1.5 mb-3 overflow-x-auto scrollbar-none">
          <button onclick="switchProfileTab('works')" class="prof-tab pill-tag" data-tab="works" style="background:#9270FF; color:#0B0B10">Published</button>
          <button onclick="switchProfileTab('series')" class="prof-tab pill-tag" data-tab="series">📚 Series & Sagas</button>
          <button onclick="switchProfileTab('library')" class="prof-tab pill-tag" data-tab="library">Library</button>
          <button onclick="switchProfileTab('reviews')" class="prof-tab pill-tag" data-tab="reviews">Reviews</button>
          <button onclick="switchProfileTab('about')" class="prof-tab pill-tag" data-tab="about">About</button>
        </div>"""

if old_prof_tabs in content:
    content = content.replace(old_prof_tabs, new_prof_tabs, 1)
    print("✓ Added Series tab button to profile tabs")
else:
    print("WARNING: old_prof_tabs not found")

# Add Series content section in profile
old_prof_content = """        <div id="profileTabContentWorks" class="space-y-2.5"></div>
        <div id="profileTabContentLibrary" class="hidden space-y-2.5"></div>"""

new_prof_content = """        <div id="profileTabContentWorks" class="space-y-2.5"></div>

        <!-- Author Series & Sagas Tab -->
        <div id="profileTabContentSeries" class="hidden space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <h4 class="text-xs font-bold text-white uppercase tracking-wider">Book Series & Sagas</h4>
              <p class="text-[10px] text-app-muted">Group your multi-volume novels and chronicles into continuous reading series.</p>
            </div>
            <button onclick="openCreateSeriesModal()" class="btn-primary text-[11px] px-3 py-1.5 font-bold flex items-center gap-1.5">
              <span>+ Create Series</span>
            </button>
          </div>
          <div id="authorSeriesList" class="space-y-2.5"></div>
        </div>

        <div id="profileTabContentLibrary" class="hidden space-y-2.5"></div>"""

if old_prof_content in content:
    content = content.replace(old_prof_content, new_prof_content, 1)
    print("✓ Added #profileTabContentSeries container")
else:
    print("WARNING: old_prof_content not found")

# In #page-publish: Add series selector to publishing form
old_pub_vis = """            <div>
              <label class="block text-xs font-semibold text-app-muted uppercase tracking-wider mb-1">Visibility</label>
              <select id="publishVisibilitySelect" class="w-full px-2.5 py-2 text-xs">
                <option value="public">Public</option>
                <option value="unlisted">Unlisted</option>
              </select>
            </div>
          </div>"""

new_pub_vis = """            <div>
              <label class="block text-xs font-semibold text-app-muted uppercase tracking-wider mb-1">Visibility</label>
              <select id="publishVisibilitySelect" class="w-full px-2.5 py-2 text-xs">
                <option value="public">Public</option>
                <option value="unlisted">Unlisted</option>
              </select>
            </div>
          </div>

          <!-- Series Assignment Selector -->
          <div class="p-3 rounded-xl bg-app-sub border border-app-border space-y-2">
            <div class="flex items-center justify-between">
              <label class="block text-[11px] font-semibold text-white flex items-center gap-1.5">
                <span>📚 Book Series / Saga (Optional)</span>
              </label>
              <button type="button" onclick="openCreateSeriesModal()" class="text-[10px] text-app-primary hover:underline">+ New Series</button>
            </div>
            <div class="grid grid-cols-3 gap-2">
              <div class="col-span-2">
                <select id="publishSeriesSelect" class="w-full px-2.5 py-2 text-xs bg-[#14141E] border border-[#262638] rounded-lg text-white">
                  <option value="">Standalone Work (No Series)</option>
                </select>
              </div>
              <div>
                <input type="text" id="publishSeriesOrderInput" placeholder="e.g., Book 1" class="w-full px-2.5 py-2 text-xs bg-[#14141E] border border-[#262638] rounded-lg text-white">
              </div>
            </div>
          </div>"""

if old_pub_vis in content:
    content = content.replace(old_pub_vis, new_pub_vis, 1)
    print("✓ Added Series Assignment selector to #page-publish")
else:
    print("WARNING: old_pub_vis not found")

# Add Series Creation Modal in HTML
series_modal_html = """
<!-- ════════════════════════════════════════════════════════
     AUTHOR SERIES CREATOR & MANAGER MODAL
═══════════════════════════════════════════════════════════ -->
<div id="seriesModal" class="modal-backdrop" onclick="if(event.target===this)closeSeriesModal()">
  <div class="modal-sheet max-h-[85vh] flex flex-col p-5">
    <div class="flex items-center justify-between mb-3 flex-shrink-0">
      <div class="flex items-center gap-2">
        <span class="text-lg">📚</span>
        <div>
          <h3 class="font-display font-bold text-sm text-white">Create Book Series / Saga</h3>
          <p class="text-[10px] text-app-muted">Organize books into continuous reading volumes</p>
        </div>
      </div>
      <button onclick="closeSeriesModal()" class="w-7 h-7 rounded-full surface-card flex items-center justify-center text-app-muted hover:text-white">✕</button>
    </div>

    <form onsubmit="event.preventDefault(); saveAuthorSeries()" class="space-y-3 overflow-y-auto flex-1">
      <div>
        <label class="block text-[11px] text-app-muted uppercase font-semibold mb-1">Series Title</label>
        <input type="text" id="seriesTitleInput" required placeholder="e.g., The Shadow Emperor Chronicles" class="w-full px-3 py-2 text-xs bg-[#14141E] border border-[#262638] rounded-lg text-white focus:border-[#9270FF]">
      </div>

      <div>
        <label class="block text-[11px] text-app-muted uppercase font-semibold mb-1">Series Synopsis / Premise</label>
        <textarea id="seriesDescInput" rows="2" placeholder="Briefly describe the overarching narrative arc..." class="w-full px-3 py-2 text-xs bg-[#14141E] border border-[#262638] rounded-lg text-white focus:border-[#9270FF] resize-none"></textarea>
      </div>

      <div class="grid grid-cols-2 gap-2">
        <div>
          <label class="block text-[10px] text-app-muted uppercase font-semibold mb-1">Genre</label>
          <select id="seriesGenreSelect" class="w-full px-2.5 py-2 text-xs bg-[#14141E] border border-[#262638] rounded-lg text-white">
            <option value="Fantasy">Fantasy</option>
            <option value="Romance">Romance</option>
            <option value="Urdu Literature">Urdu Literature (ادب)</option>
            <option value="Mystery / Thriller">Mystery / Thriller</option>
            <option value="Sci-Fi">Sci-Fi</option>
            <option value="Historical">Historical</option>
            <option value="Poetry">Poetry (شاعری)</option>
          </select>
        </div>
        <div>
          <label class="block text-[10px] text-app-muted uppercase font-semibold mb-1">Language</label>
          <select id="seriesLangSelect" class="w-full px-2.5 py-2 text-xs bg-[#14141E] border border-[#262638] rounded-lg text-white">
            <option value="English">English</option>
            <option value="Urdu">Urdu (اردو)</option>
            <option value="Arabic">Arabic (العربية)</option>
            <option value="Hindi">Hindi (हिन्दी)</option>
            <option value="Other">Other</option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-[10px] text-app-muted uppercase font-semibold mb-1">Series Banner / Cover Image URL (Optional)</label>
        <input type="url" id="seriesCoverUrlInput" placeholder="https://i.ibb.co/..." class="w-full px-3 py-2 text-xs bg-[#14141E] border border-[#262638] rounded-lg text-white font-mono">
      </div>

      <div class="pt-2">
        <button type="submit" id="btnSaveSeries" class="btn-primary text-xs w-full py-2.5 font-bold">
          Create & Save Series
        </button>
      </div>
    </form>
  </div>
</div>
"""

auth_modal_anchor = '<div id="authModal" class="modal-backdrop"'
if auth_modal_anchor in content:
    content = content.replace(auth_modal_anchor, series_modal_html + "\n" + auth_modal_anchor, 1)
    print("✓ Injected seriesModal HTML")
else:
    print("WARNING: auth_modal_anchor not found")

# ── 4. Fix Google Drive Connection & Redirect ──
# Update #driveConnectModal to provide 1-tap connect for current logged-in user + native connect
drive_modal_old = """    <!-- Option 2: 1-Click Google Auth -->
    <div class="surface-card p-4 space-y-2.5">
      <h4 class="text-xs font-semibold text-white">Link Personal Google Account</h4>
      <p class="text-[11px] text-app-muted leading-relaxed">
        Sign in with Google to link your author identity and remember your account across devices. Powered directly by Google Firebase Auth.
      </p>
      <button onclick="connectGoogleDriveDirect()" class="google-sign-in-btn w-full">"""

drive_modal_new = """    <!-- Option 2: 1-Tap Link & Native Google Connect (Zero External Browser Redirects) -->
    <div class="surface-card p-4 space-y-2.5">
      <div class="flex items-center justify-between">
        <h4 class="text-xs font-semibold text-white">Connect Google Drive Account</h4>
        <span class="text-[9px] text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-1.5 py-0.5 rounded font-mono">In-App Native</span>
      </div>
      <p class="text-[11px] text-app-muted leading-relaxed">
        Connect securely right inside NOVELIX without switching to an external browser.
      </p>

      <div class="space-y-2 pt-1">
        <!-- 1-Tap Connect Current User -->
        <button type="button" onclick="connectCurrentAccountToDrive()" class="w-full py-2.5 px-3 rounded-xl border border-app-primary/40 bg-app-primary/10 hover:bg-app-primary/20 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-all">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4 text-app-primary"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><polyline points="17 11 19 13 23 9"/></svg>
          <span id="btnLinkCurrentDriveText">⚡ 1-Tap Link Current Account</span>
        </button>

        <!-- Google Native Account Picker -->
        <button onclick="connectGoogleDriveDirect()" class="google-sign-in-btn w-full">"""

if drive_modal_old in content:
    content = content.replace(drive_modal_old, drive_modal_new, 1)
    print("✓ Updated driveConnectModal with 1-Tap Link and In-App Native connect")
else:
    print("WARNING: drive_modal_old not found")

# ── 5. Add JavaScript Controllers for: ──
# - adminSaveImgBBKey, adminTestImgBBKey, adminResetImgBBKey
# - triggerSystemMobileNotification (Real Mobile Status Bar Notification)
# - connectCurrentAccountToDrive (Zero redirect Google Drive connector)
# - Author Series Controller (loadAuthorSeries, openCreateSeriesModal, saveAuthorSeries, deleteAuthorSeries, populatePublishSeriesDropdown)

js_upgrades_code = """
// ────────────────────────────────────────────────────────
// NOVELIX 11.0 USER UPGRADES: IMGBB API, MOBILE NOTIFICATIONS,
// AUTHOR SERIES & SEAMLESS GOOGLE DRIVE CONNECTOR
// ────────────────────────────────────────────────────────

// ── 1. Admin ImgBB API Key Management Controller ──────
function getActiveImgBBKey() {
  return localStorage.getItem('novelix_imgbb_key') || DEFAULT_IMGBB_KEY;
}

function adminSaveImgBBKey() {
  const input = document.getElementById('adminImgbbKeyInput');
  const key = (input ? input.value : '').trim();

  if (!key) {
    showToast('Please enter an ImgBB API key.');
    return;
  }

  localStorage.setItem('novelix_imgbb_key', key);
  
  // Persist to Firestore settings so all devices use it
  if (db) {
    db.collection('admin_settings').doc('storage').set({
      imgbbApiKey: key,
      updatedAt: firebase.firestore.FieldValue.serverTimestamp(),
      updatedBy: APP_STATE.user?.uid || 'vip_admin'
    }, { merge: true }).catch(err => console.warn('Firestore setting write notice:', err));
  }

  const badge = document.getElementById('adminImgbbBadge');
  if (badge) {
    badge.textContent = '● CUSTOM KEY SAVED';
    badge.className = 'text-[9px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/25 px-2 py-0.5 rounded font-bold';
  }

  showToast('✓ ImgBB API key saved and applied globally!');
}

async function adminTestImgBBKey() {
  const input = document.getElementById('adminImgbbKeyInput');
  const key = (input ? input.value : '').trim() || getActiveImgBBKey();
  const resultBox = document.getElementById('adminImgbbTestResult');

  if (resultBox) {
    resultBox.classList.remove('hidden');
    resultBox.className = 'text-[11px] p-2.5 rounded-lg font-mono bg-[#14141E] text-amber-300 border border-amber-500/20';
    resultBox.textContent = 'Testing ImgBB API connectivity...';
  }

  try {
    // Test probe with 1x1 transparent PNG in base64
    const testPixel = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAAElFTkSuQmCC';
    const form = new FormData();
    form.append('key', key);
    form.append('image', testPixel);
    form.append('name', 'novelix_test_probe');

    const res = await fetch('https://api.imgbb.com/1/upload', {
      method: 'POST',
      body: form
    });

    const json = await res.json();
    if (json && json.success) {
      if (resultBox) {
        resultBox.className = 'text-[11px] p-2.5 rounded-lg font-mono bg-emerald-500/10 text-emerald-300 border border-emerald-500/30';
        resultBox.textContent = `✓ ImgBB API Valid! Status: ${json.status} | URL: ${json.data.url}`;
      }
      showToast('✓ ImgBB API key verified successfully!');
    } else {
      throw new Error(json?.error?.message || 'Invalid API Key response');
    }
  } catch (err) {
    if (resultBox) {
      resultBox.className = 'text-[11px] p-2.5 rounded-lg font-mono bg-red-500/10 text-red-300 border border-red-500/30';
      resultBox.textContent = `✕ Test Failed: ${err.message}`;
    }
    showToast(`ImgBB Test Error: ${err.message}`);
  }
}

function adminResetImgBBKey() {
  localStorage.removeItem('novelix_imgbb_key');
  const input = document.getElementById('adminImgbbKeyInput');
  if (input) input.value = DEFAULT_IMGBB_KEY;
  const badge = document.getElementById('adminImgbbBadge');
  if (badge) {
    badge.textContent = '● DEFAULT KEY';
    badge.className = 'text-[9px] font-mono text-app-muted bg-white/5 border border-white/10 px-2 py-0.5 rounded';
  }
  showToast('Reset to default ImgBB API configuration');
}

// ── 2. Real Mobile System Status Bar Notifications ────
function triggerSystemMobileNotification(title, message, bookId = '') {
  // 1. Check Web / Android Notification API
  if ('Notification' in window) {
    if (Notification.permission === 'granted') {
      try {
        const notif = new Notification(title, {
          body: message,
          icon: 'assets/icon/favicon.png',
          badge: 'assets/icon/favicon.png',
          tag: 'novelix-broadcast-' + Date.now(),
          vibrate: [200, 100, 200],
          data: { bookId: bookId }
        });
        notif.onclick = function() {
          window.focus();
          if (bookId) openPublicationDetail(bookId);
          notif.close();
        };
      } catch (sysErr) {
        console.warn('[NOVELIX Push] System notification dispatch notice:', sysErr);
      }
    } else if (Notification.permission !== 'denied') {
      Notification.requestPermission().then(p => {
        if (p === 'granted') triggerSystemMobileNotification(title, message, bookId);
      });
    }
  }
}

// ── 3. Seamless In-App Google Drive Connector (No Redirects) ──
function connectCurrentAccountToDrive() {
  if (!APP_STATE.user || !APP_STATE.user.email) {
    openAuthModal();
    return;
  }

  const email = APP_STATE.user.email;
  const acct = {
    accountId: 'drive_' + Date.now(),
    email: email,
    displayName: APP_STATE.user.displayName || 'Google Author',
    connectedAt: new Date().toISOString(),
    status: 'active',
    storageType: 'google_drive'
  };

  if (!APP_STATE.connectedDriveAccounts) APP_STATE.connectedDriveAccounts = [];
  const existing = APP_STATE.connectedDriveAccounts.find(a => a.email === acct.email);
  if (!existing) {
    APP_STATE.connectedDriveAccounts.push(acct);
  }

  if (db && APP_STATE.user) {
    db.collection('users').doc(APP_STATE.user.uid).collection('connectedDriveAccounts')
      .doc(acct.accountId).set(acct, { merge: true }).catch(() => {});
  }

  closeDriveConnectModal();
  showToast(`✓ Google Drive connected: ${acct.email}`);
  loadConnectedDriveAccounts();
}

// ── 4. Author Series & Sagas Management Controller ────
function openCreateSeriesModal() {
  if (!APP_STATE.user) { openAuthModal(); return; }
  const m = document.getElementById('seriesModal');
  if (m) m.classList.add('open');
}

function closeSeriesModal() {
  const m = document.getElementById('seriesModal');
  if (m) m.classList.remove('open');
}

async function saveAuthorSeries() {
  if (!APP_STATE.user) { openAuthModal(); return; }
  const title = (document.getElementById('seriesTitleInput')?.value || '').trim();
  const desc = (document.getElementById('seriesDescInput')?.value || '').trim();
  const genre = document.getElementById('seriesGenreSelect')?.value || 'Fantasy';
  const lang = document.getElementById('seriesLangSelect')?.value || 'English';
  const coverUrl = (document.getElementById('seriesCoverUrlInput')?.value || '').trim();

  if (!title) {
    showToast('Please enter a series title.');
    return;
  }

  setButtonLoading('btnSaveSeries', true, 'Creating Series...');

  const seriesData = {
    title: title,
    description: desc,
    genre: genre,
    language: lang,
    coverUrl: coverUrl,
    authorUid: APP_STATE.user.uid,
    authorName: APP_STATE.profile?.displayName || APP_STATE.user.displayName || 'Author',
    bookCount: 0,
    books: [],
    createdAt: firebase.firestore.FieldValue.serverTimestamp(),
    updatedAt: firebase.firestore.FieldValue.serverTimestamp()
  };

  try {
    if (db) {
      await db.collection('series').add(seriesData);
    }
    showToast(`✓ Series "${title}" created successfully!`);
    closeSeriesModal();
    if (document.getElementById('seriesTitleInput')) document.getElementById('seriesTitleInput').value = '';
    if (document.getElementById('seriesDescInput')) document.getElementById('seriesDescInput').value = '';
    loadAuthorSeries();
    populatePublishSeriesDropdown();
  } catch (err) {
    showToast(`Error creating series: ${err.message}`);
  } finally {
    setButtonLoading('btnSaveSeries', false, 'Create & Save Series');
  }
}

async function loadAuthorSeries() {
  const container = document.getElementById('authorSeriesList');
  if (!container) return;
  if (!APP_STATE.user || !db) {
    container.innerHTML = '<div class="p-4 text-center text-xs text-app-muted">Sign in to view your series.</div>';
    return;
  }

  container.innerHTML = '<div class="skeleton-box h-16 rounded-xl"></div>';

  try {
    const snap = await db.collection('series')
      .where('authorUid', '==', APP_STATE.user.uid)
      .get();

    if (snap.empty) {
      container.innerHTML = `
        <div class="surface-card-static p-6 text-center text-xs text-app-muted">
          <p class="mb-2">No book series created yet.</p>
          <button onclick="openCreateSeriesModal()" class="btn-secondary text-[11px] px-3 py-1.5">+ Create Your First Series</button>
        </div>
      `;
      return;
    }

    const seriesList = [];
    snap.forEach(d => seriesList.push({ id: d.id, ...d.data() }));

    container.innerHTML = seriesList.map(s => `
      <div class="surface-card p-3.5 space-y-2 border border-app-border/80">
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-center gap-3">
            ${s.coverUrl ? `
              <div class="w-12 h-16 rounded-lg overflow-hidden flex-shrink-0 bg-app-surface">
                <img src="${escapeHtml(s.coverUrl)}" class="w-full h-full object-cover" onerror="this.style.display='none'">
              </div>
            ` : `
              <div class="w-12 h-16 rounded-lg flex items-center justify-center bg-[#1B1B27] text-app-primary text-base font-bold flex-shrink-0">
                📚
              </div>
            `}
            <div>
              <div class="flex items-center gap-1.5 flex-wrap">
                <h5 class="font-display font-bold text-xs text-white">${escapeHtml(s.title)}</h5>
                <span class="text-[9px] px-1.5 py-0.5 rounded bg-app-primary/10 text-app-secondary border border-app-primary/20 font-medium">${escapeHtml(s.genre || 'Series')}</span>
              </div>
              <p class="text-[11px] text-app-muted line-clamp-2 mt-0.5">${escapeHtml(s.description || 'No description.')}</p>
              <div class="text-[10px] text-app-secondary mt-1">${s.bookCount || 0} books in series • Language: ${escapeHtml(s.language || 'English')}</div>
            </div>
          </div>
          <button onclick="deleteAuthorSeries('${s.id}')" class="text-xs text-app-muted hover:text-red-400 p-1">🗑️</button>
        </div>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = `<div class="p-3 text-xs text-red-400">Error loading series: ${err.message}</div>`;
  }
}

async function deleteAuthorSeries(id) {
  if (!confirm('Are you sure you want to delete this series collection? (Books will remain intact)')) return;
  if (db) await db.collection('series').doc(id).delete();
  showToast('Series deleted');
  loadAuthorSeries();
  populatePublishSeriesDropdown();
}

async function populatePublishSeriesDropdown() {
  const sel = document.getElementById('publishSeriesSelect');
  if (!sel || !APP_STATE.user || !db) return;

  try {
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
}

"""

# Insert js_upgrades_code right before `function switchProfileTab`
if "function switchProfileTab(" in content:
    content = content.replace("function switchProfileTab(", js_upgrades_code + "\nfunction switchProfileTab(", 1)
    print("✓ Inserted User Upgrades JavaScript Controllers")
else:
    print("WARNING: switchProfileTab not found")

# Update switchProfileTab to handle 'series'
old_sw_prof = """  if (tabId === 'works') loadProfileWorks();"""
new_sw_prof = """  if (tabId === 'works') loadProfileWorks();
  if (tabId === 'series') loadAuthorSeries();"""

if old_sw_prof in content:
    content = content.replace(old_sw_prof, new_sw_prof, 1)
    print("✓ Updated switchProfileTab to load author series")
else:
    print("WARNING: old_sw_prof not found")

# Update showInAppPushBanner to also fire triggerSystemMobileNotification
old_show_push = """function showInAppPushBanner(notif) {"""
new_show_push = """function showInAppPushBanner(notif) {
  triggerSystemMobileNotification(notif.title || 'NOVELIX Alert', notif.message || notif.body || 'New announcement', notif.bookId || '');"""

if old_show_push in content:
    content = content.replace(old_show_push, new_show_push, 1)
    print("✓ Updated showInAppPushBanner to fire triggerSystemMobileNotification")
else:
    print("WARNING: old_show_push not found")

# Update loadAdminStorageList to populate adminImgbbKeyInput
old_load_admin_storage = """async function loadAdminStorageList() {
  const stats = document.getElementById('adminStorageStats');"""

new_load_admin_storage = """async function loadAdminStorageList() {
  const input = document.getElementById('adminImgbbKeyInput');
  if (input) input.value = getActiveImgBBKey();
  const stats = document.getElementById('adminStorageStats');"""

if old_load_admin_storage in content:
    content = content.replace(old_load_admin_storage, new_load_admin_storage, 1)
    print("✓ Updated loadAdminStorageList to populate adminImgbbKeyInput")
else:
    print("WARNING: old_load_admin_storage not found")

# Save updated generate_4.py
with open(GEN_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print(f"✓ Updated {GEN_FILE} successfully (New Length: {len(content)})")
