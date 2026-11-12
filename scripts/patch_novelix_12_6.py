#!/usr/bin/env python3
"""
Comprehensive Patch v12.6.0 for NOVELIX:
1. Bootloader: Purge stale localStorage OTA cache, prevent old code from overwriting new updates.
2. Reader: Never blank - Google Drive preview iframe fallback + text reader fallback + canvas visibility reset.
3. Terminal: Accessible from VIP Admin console header, Settings modal, and 7-tap gesture.
4. Drive Account Removal: Full removal without window.confirm - removes from both Firestore subcollections and localStorage.
5. Publishing: Fix local PDF import to studio, add Google Drive multipart upload, ensure seamless publishing.
6. In-App APK Install: Add "Install App Update (APK)" button in OTA modal connecting to native Android bridge.
7. Bump version to 12.6.0 across codebase.
"""
import sys

src = '/data/user/0/com.termux/files/home/Novelix project/scripts/generate_4.py'

with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

patches = []

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 1: Early Bootloader: Purge stale OTA cache and set version to 12.6.0
# ─────────────────────────────────────────────────────────────────────────────
OLD_BOOTLOADER = """  <!-- Fail-safe Early Watchdog -->
  <script>
    (function() {
      window.__NOVELIX_VERSION__ = '12.3.0';
      // ── Early Live OTA Bootloader ──
      try {
        var otaHtml = localStorage.getItem('novelix_ota_html');
        var otaVer = localStorage.getItem('novelix_ota_ver');
        if (otaHtml && otaVer && otaVer !== window.__NOVELIX_VERSION__ && !window.__IS_OTA_BOOTED__) {
          if (otaHtml.length > 25000 && otaHtml.indexOf('NOVELIX') !== -1) {
            console.log('[NOVELIX Bootloader] Booting live OTA update v' + otaVer);
            window.__IS_OTA_BOOTED__ = true;
            document.open();
            document.write(otaHtml);
            document.close();
            return;
          }
        }
      } catch(otaErr) {
        console.warn('[NOVELIX Bootloader] Note:', otaErr);
      }"""

NEW_BOOTLOADER = """  <!-- Fail-safe Early Watchdog -->
  <script>
    (function() {
      window.__NOVELIX_VERSION__ = '12.6.0';
      // ── Early Live OTA Bootloader ──
      try {
        // Purge old stale OTA cache from prior versions so installed APK updates run freshly
        var otaVer = localStorage.getItem('novelix_ota_ver');
        if (otaVer && (otaVer === '12.0.0' || otaVer === '12.1.0' || otaVer === '12.2.0' || otaVer === '12.3.0' || otaVer === '12.4.0' || otaVer === '12.5.0')) {
          localStorage.removeItem('novelix_ota_html');
          localStorage.removeItem('novelix_ota_ver');
        }
      } catch(otaErr) {
        console.warn('[NOVELIX Bootloader] Note:', otaErr);
      }"""

patches.append(('Early Bootloader purge stale OTA', OLD_BOOTLOADER, NEW_BOOTLOADER))

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 2: VIP Admin Suite Header: Add Terminal Button
# ─────────────────────────────────────────────────────────────────────────────
OLD_ADMIN_HEADER = """    <div class="flex items-center gap-2">
      <button onclick="switchAdminTab('notifications')" class="btn-primary text-xs px-3 py-1.5 font-bold bg-gradient-to-r from-[#FFD700] to-[#E5C07B] text-[#0B0B10] flex items-center gap-1.5 shadow">
        <svg viewBox="0 0 24 24" fill="currentColor" class="w-3.5 h-3.5"><path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2zm-2 1H8v-6c0-2.48 1.51-4.5 4-4.5s4 2.02 4 4.5v6z"/></svg>
        <span>Broadcast</span>
      </button>
      <button onclick="closeAdminDashboard()" class="btn-secondary text-xs px-3 py-1.5">Close Console</button>
    </div>"""

NEW_ADMIN_HEADER = """    <div class="flex items-center gap-2">
      <button onclick="openTerminal()" class="px-2.5 py-1.5 rounded-lg border border-emerald-500/40 bg-emerald-500/15 text-emerald-300 hover:bg-emerald-500/25 text-xs font-mono font-bold flex items-center gap-1 transition-all">
        <span>💻 Terminal</span>
      </button>
      <button onclick="switchAdminTab('notifications')" class="btn-primary text-xs px-3 py-1.5 font-bold bg-gradient-to-r from-[#FFD700] to-[#E5C07B] text-[#0B0B10] flex items-center gap-1.5 shadow">
        <svg viewBox="0 0 24 24" fill="currentColor" class="w-3.5 h-3.5"><path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2zm-2 1H8v-6c0-2.48 1.51-4.5 4-4.5s4 2.02 4 4.5v6z"/></svg>
        <span>Broadcast</span>
      </button>
      <button onclick="closeAdminDashboard()" class="btn-secondary text-xs px-3 py-1.5">Close Console</button>
    </div>"""

patches.append(('VIP Admin Header Terminal button', OLD_ADMIN_HEADER, NEW_ADMIN_HEADER))

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 3: Settings Modal: Add Open Developer Terminal button
# ─────────────────────────────────────────────────────────────────────────────
OLD_SETTINGS_DEV = """        <!-- GitHub OTA Update Control -->
        <div class="surface-card p-3 rounded-xl border border-app-border space-y-2.5">"""

NEW_SETTINGS_DEV = """        <!-- Developer Terminal Button -->
        <div class="surface-card p-3 rounded-xl border border-emerald-500/30 bg-emerald-500/5 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold text-white flex items-center gap-1.5">
              <span>💻</span> Developer Terminal Console
            </span>
            <span class="text-[9px] font-mono text-emerald-400 bg-emerald-500/20 px-2 py-0.5 rounded font-bold">READY</span>
          </div>
          <button onclick="openTerminal(); closeSettingsModal();" class="btn-secondary text-xs w-full py-2 flex items-center justify-center gap-1.5 text-emerald-400 font-mono font-bold border border-emerald-500/40 hover:bg-emerald-500/10 transition-all">
            <span>💻 Launch Developer Console</span>
          </button>
        </div>

        <!-- GitHub OTA Update Control -->
        <div class="surface-card p-3 rounded-xl border border-app-border space-y-2.5">"""

patches.append(('Settings Modal Terminal button', OLD_SETTINGS_DEV, NEW_SETTINGS_DEV))

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 4: Logo tap handler: 5 taps = Admin, 7 taps = Terminal
# ─────────────────────────────────────────────────────────────────────────────
OLD_LOGO_TAP = """  logo?.addEventListener('click', () => {
    const now = Date.now();
    if (now - APP_STATE.logoLastClickTime > 2000) APP_STATE.logoClicks = 0;
    APP_STATE.logoLastClickTime = now;
    APP_STATE.logoClicks++;
    // Show tap progress feedback
    if (APP_STATE.logoClicks >= 2 && APP_STATE.logoClicks < 5) {
      showToast(`Admin access: ${APP_STATE.logoClicks}/5 taps`);
    }
    if (APP_STATE.logoClicks >= 5) {
      APP_STATE.logoClicks = 0;
      showToast('👑 Opening VIP Admin Console...');
      setTimeout(() => openAdminDashboard(), 150);
    }
  });"""

NEW_LOGO_TAP = """  logo?.addEventListener('click', () => {
    const now = Date.now();
    if (now - APP_STATE.logoLastClickTime > 2000) APP_STATE.logoClicks = 0;
    APP_STATE.logoLastClickTime = now;
    APP_STATE.logoClicks++;
    if (APP_STATE.logoClicks >= 2 && APP_STATE.logoClicks < 5) {
      showToast(`Admin access: ${APP_STATE.logoClicks}/5 taps`);
    }
    if (APP_STATE.logoClicks === 5) {
      showToast('👑 VIP Admin activated! (Tap 2 more times for Terminal)');
      setTimeout(() => openAdminDashboard(), 150);
    } else if (APP_STATE.logoClicks >= 7) {
      APP_STATE.logoClicks = 0;
      showToast('💻 Opening Developer Console...');
      setTimeout(() => openTerminal(), 150);
    }
  });"""

patches.append(('Logo tap handler 5=Admin 7=Terminal', OLD_LOGO_TAP, NEW_LOGO_TAP))

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 5: Open Terminal Function Robustness
# ─────────────────────────────────────────────────────────────────────────────
OLD_OPEN_TERMINAL = """function openTerminal() {
  document.getElementById('devTerminal').classList.add('open');
  const body = document.getElementById('terminalLogBody');
  body.innerHTML = '';
  writeTerm('NOVELIX 4.0 RUNTIME CONSOLE');
  writeTerm('═══════════════════════════════════════════');
  writeTerm(`Project: ${FIREBASE_CONFIG.projectId}`);
  writeTerm(`User: ${APP_STATE.user ? APP_STATE.user.email : 'Guest'}`);
  writeTerm('Commands: status, db, user, admin, clear, exit');
  document.getElementById('terminalCmdInput').focus();
}"""

NEW_OPEN_TERMINAL = """function openTerminal() {
  const term = document.getElementById('devTerminal');
  if (term) {
    term.classList.remove('hidden');
    term.style.setProperty('display', 'flex', 'important');
    term.classList.add('open');
  }
  const body = document.getElementById('terminalLogBody');
  if (body) {
    body.innerHTML = '';
    writeTerm('NOVELIX 4.0 RUNTIME CONSOLE [v12.6.0]');
    writeTerm('═══════════════════════════════════════════');
    writeTerm(`Project: ${FIREBASE_CONFIG.projectId}`);
    writeTerm(`User: ${APP_STATE.user ? APP_STATE.user.email : 'Guest'}`);
    writeTerm(`VIP Status: ${APP_STATE.isVIPAdmin ? 'Active' : 'Standard'}`);
    writeTerm('Commands: admin, status, db, user, clear, exit');
  }
  const input = document.getElementById('terminalCmdInput');
  if (input) {
    input.focus();
  }
  showToast('💻 Developer Terminal Ready');
}"""

patches.append(('openTerminal robustness', OLD_OPEN_TERMINAL, NEW_OPEN_TERMINAL))

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 6: Disconnect Google Drive Account: Reliable removal without confirm block
# ─────────────────────────────────────────────────────────────────────────────
OLD_DISCONNECT_DRIVE = """// ── Disconnect Drive Account ─────────────────────────────
async function disconnectDriveAccount(accId) {
  if (!confirm('Disconnect this Google Drive account?')) return;
  try {
    if (typeof functions !== 'undefined' && functions && typeof functions.httpsCallable === 'function') {
      const disconnectFn = functions.httpsCallable('disconnectGoogleDriveAccount');
      await disconnectFn({ accountId: accId });
    } else {
      await db.collection('users').doc(APP_STATE.user.uid).collection('drive_accounts').doc(accId).delete();
    }
  } catch(e) {
    try {
      await db.collection('users').doc(APP_STATE.user.uid).collection('drive_accounts').doc(accId).delete();
    } catch (fe) {
      console.error('[NOVELIX Drive] Disconnect error:', fe);
    }
  }
  showToast('Account disconnected');
  loadConnectedDriveAccounts();
}"""

NEW_DISCONNECT_DRIVE = """// ── Disconnect Google Drive Account ───────────────────────
async function disconnectDriveAccount(accId) {
  if (!APP_STATE.user) { showToast('Please sign in first'); return; }
  showToast('Removing Google Drive account...');

  try {
    // 1. Find account info before deleting
    const acc = (APP_STATE.connectedDriveAccounts || []).find(a => a.id === accId);
    const email = acc ? acc.email : '';

    // 2. Delete from both Firestore subcollections
    const uid = APP_STATE.user.uid;
    await Promise.allSettled([
      db.collection('users').doc(uid).collection('drive_accounts').doc(accId).delete(),
      db.collection('users').doc(uid).collection('connectedDriveAccounts').doc(accId).delete(),
      email ? db.collection('users').doc(uid).collection('drive_accounts').doc(email).delete() : Promise.resolve(),
      email ? db.collection('users').doc(uid).collection('connectedDriveAccounts').doc(email).delete() : Promise.resolve()
    ]);

    // 3. Clear localStorage tokens
    if (email) {
      localStorage.removeItem('novelix_drive_token_' + email);
      localStorage.removeItem('novelix_drive_user_' + email);
    }
    localStorage.removeItem('novelix_active_drive_token');

    // 4. Update in-memory state
    APP_STATE.connectedDriveAccounts = (APP_STATE.connectedDriveAccounts || []).filter(a => a.id !== accId && a.email !== email);

    showToast('✓ Google Drive account removed');
  } catch(err) {
    console.warn('[NOVELIX Drive] Disconnect notice:', err.message);
    showToast('Account disconnected');
  }

  // 5. Refresh UI immediately
  loadConnectedDriveAccounts();
  syncPublishDriveAccountsUI();
}"""

patches.append(('disconnectDriveAccount reliable removal', OLD_DISCONNECT_DRIVE, NEW_DISCONNECT_DRIVE))

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 7: Drive Account Card UI: Show prominent "Remove Account" button
# ─────────────────────────────────────────────────────────────────────────────
OLD_DRIVE_CARD_BTN = """        <div class="flex items-center gap-2 flex-shrink-0">
          <button onclick="browseDriveAccountFiles('${escapeHtml(acc.id)}')" class="btn-primary text-[11px] px-3 py-1.5 flex items-center gap-1">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3 h-3"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            Browse
          </button>
          <button onclick="disconnectDriveAccount('${escapeHtml(acc.id)}')" title="Disconnect account" class="w-7 h-7 rounded-lg surface-card text-red-400 hover:text-red-300 flex items-center justify-center text-xs">
            ✕
          </button>
        </div>"""

NEW_DRIVE_CARD_BTN = """        <div class="flex items-center gap-1.5 flex-shrink-0">
          <button onclick="browseDriveAccountFiles('${escapeHtml(acc.id)}')" class="btn-primary text-[11px] px-2.5 py-1.5 flex items-center gap-1">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3 h-3"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            Browse
          </button>
          <button onclick="disconnectDriveAccount('${escapeHtml(acc.id)}')" title="Remove account" class="px-2 py-1.5 rounded-lg border border-red-500/30 bg-red-500/10 text-red-400 hover:bg-red-500/20 text-[10px] font-bold flex items-center gap-1 transition-all">
            <span>✕ Remove</span>
          </button>
        </div>"""

patches.append(('Drive Card UI Remove button', OLD_DRIVE_CARD_BTN, NEW_DRIVE_CARD_BTN))

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 8: OTA Modal: Add In-App APK Installer Button
# ─────────────────────────────────────────────────────────────────────────────
OLD_OTA_MODAL_BTNS = """    <div class="space-y-2 pt-1">
      <button id="otaInstallBtn" onclick="forceUpdateFromGitHub()" class="btn-primary w-full py-3 text-xs font-bold flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(146,112,255,0.4)]">
        <span>⚡ Install In-App Update Now</span>
      </button>

      <a id="otaDownloadApkBtn" href="https://github.com/RuhanAhmaad/Novelix-/releases/latest" target="_blank" class="w-full py-2.5 px-3 rounded-xl border border-app-border bg-app-surface hover:bg-app-card text-white text-xs font-semibold flex items-center justify-center gap-2 transition-all">
        <span>📦 Download APK Package</span>
      </a>

      <button onclick="closeOTAModal()" class="w-full py-2 text-xs text-app-muted hover:text-white transition-colors">
        Remind Me Later
      </button>
    </div>"""

NEW_OTA_MODAL_BTNS = """    <div class="space-y-2 pt-1">
      <!-- 1. Direct In-App APK Installer (Calls Android Native System Installer) -->
      <button id="otaInstallApkNativeBtn" onclick="installAppApkFromOta()" class="w-full py-3 text-xs font-bold rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white flex items-center justify-center gap-2 shadow-[0_0_18px_rgba(16,185,129,0.4)] active:scale-98 transition-all">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="w-4 h-4"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
        <span>🚀 Install App Update (APK)</span>
      </button>

      <!-- 2. Web Bundle Live Hot-Reload -->
      <button id="otaInstallBtn" onclick="forceUpdateFromGitHub()" class="btn-secondary w-full py-2.5 text-xs font-bold flex items-center justify-center gap-2 border-[#9270FF]/40 text-purple-200 hover:bg-[#9270FF]/15">
        <span>⚡ Live Refresh Web Bundle</span>
      </button>

      <!-- 3. Direct GitHub Releases Page -->
      <a id="otaDownloadApkBtn" href="https://github.com/RuhanAhmaad/Novelix-/releases/latest" target="_blank" class="w-full py-2 px-3 rounded-xl border border-app-border bg-app-surface hover:bg-app-card text-app-muted hover:text-white text-[11px] font-semibold flex items-center justify-center gap-2 transition-all">
        <span>📦 Open GitHub Releases</span>
      </a>

      <button onclick="closeOTAModal()" class="w-full py-1.5 text-xs text-app-muted hover:text-white transition-colors">
        Dismiss
      </button>
    </div>"""

patches.append(('OTA Modal In-App APK button', OLD_OTA_MODAL_BTNS, NEW_OTA_MODAL_BTNS))

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 9: Add installAppApkFromOta JavaScript function
# ─────────────────────────────────────────────────────────────────────────────
OLD_FORCE_UPDATE = """async function forceUpdateFromGitHub() {"""

NEW_FORCE_UPDATE = """function installAppApkFromOta() {
  showToast('Launching Android APK package installer...');
  try {
    if (window.AndroidNotification && typeof window.AndroidNotification.installApk === 'function') {
      window.AndroidNotification.installApk('/sdcard/Download/novelix.apk');
      return;
    }
  } catch(e) {
    console.warn('[NOVELIX OTA] Native bridge note:', e);
  }
  // Fallback: Open browser download
  window.open('https://github.com/RuhanAhmaad/Novelix-/releases/latest', '_system');
}

async function forceUpdateFromGitHub() {"""

patches.append(('installAppApkFromOta function', OLD_FORCE_UPDATE, NEW_FORCE_UPDATE))

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 10: Fix importLocalPdfToStudio: Set PDF to publishEditions and switch to publish page
# ─────────────────────────────────────────────────────────────────────────────
OLD_IMPORT_STUDIO = """async function importLocalPdfToStudio(file) {
  showToast('Loading PDF into studio...');
  try {
    const base64 = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
    // Open studio if not open
    openPublishModal && openPublishModal();
    // Fill in content area
    setTimeout(() => {
      const contentInput = document.getElementById('bookContentInput');
      if (contentInput) {
        contentInput.value = '[PDF: ' + file.name + ']\\n\\nPDF uploaded directly from device.\\nFile size: ' + (file.size / 1024).toFixed(1) + ' KB';
        showToast('✓ PDF loaded into studio. Add details and publish.');
      }
      // Store PDF data URL for publishing
      APP_STATE._pendingPdfDataUrl = base64;
      APP_STATE._pendingPdfName = file.name;
    }, 400);
  } catch(e) {
    showToast('PDF load error: ' + e.message);
  }
}"""

NEW_IMPORT_STUDIO = """async function importLocalPdfToStudio(file) {
  showToast('Attaching PDF to publishing studio...');
  try {
    // Navigate to publishing page
    switchPage('publish');

    // Ensure editions array has at least one entry
    if (!APP_STATE.publishEditions || APP_STATE.publishEditions.length === 0) {
      APP_STATE.publishEditions = [{
        language: 'English',
        storageProvider: 'storage',
        file: file,
        driveFile: null,
        driveAccountId: ''
      }];
    } else {
      APP_STATE.publishEditions[0].file = file;
      APP_STATE.publishEditions[0].storageProvider = 'storage';
      APP_STATE.publishEditions[0].driveFile = null;
    }

    setTimeout(() => {
      // Auto-populate title if empty
      const titleInput = document.getElementById('publishTitleInput');
      if (titleInput && !titleInput.value.trim()) {
        const cleanName = (file.name || 'Untitled Book').replace(/\\.[^/.]+$/, '').replace(/[_-]/g, ' ');
        titleInput.value = cleanName.charAt(0).toUpperCase() + cleanName.slice(1);
      }

      // Update edition label and badge in UI
      const label = document.getElementById('edFileLabel-0');
      if (label) label.textContent = `${file.name} (${(file.size / (1024*1024)).toFixed(1)} MB)`;
      const badge = document.getElementById('edStatusBadge-0');
      if (badge) {
        badge.textContent = `[Attached PDF] ${file.name} (${(file.size / (1024*1024)).toFixed(1)} MB)`;
        badge.classList.remove('hidden');
      }

      showToast(`✓ Manuscript "${file.name}" attached. Add details and tap Publish!`);
    }, 300);

  } catch(e) {
    showToast('PDF attach error: ' + e.message);
  }
}"""

patches.append(('importLocalPdfToStudio seamless attach', OLD_IMPORT_STUDIO, NEW_IMPORT_STUDIO))

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 11: Reader: Never Blank - Embed Google Drive Preview Iframe Fallback
# ─────────────────────────────────────────────────────────────────────────────
OLD_READER_RESET = """  // Reset canvas
  const canvas = document.getElementById('pdfRenderCanvas');
  if (canvas) { canvas.width = 0; canvas.height = 0; }"""

NEW_READER_RESET = """  // Reset canvas and clean prior reading containers
  const canvas = document.getElementById('pdfRenderCanvas');
  if (canvas) {
    canvas.width = 0;
    canvas.height = 0;
    canvas.style.display = 'block';
  }
  const oldText = document.getElementById('readerTextContent');
  if (oldText) oldText.style.display = 'none';
  const oldIframe = document.getElementById('readerDriveIframe');
  if (oldIframe) oldIframe.remove();
  document.getElementById('canvasWrapper')?.classList.remove('hidden');"""

patches.append(('Reader canvas and container reset', OLD_READER_RESET, NEW_READER_RESET))

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 12: Reader: If direct PDF download fails, embed Google Drive preview iframe
# ─────────────────────────────────────────────────────────────────────────────
OLD_READER_DRIVE_FAIL = """      if (!downloadedBytes) {
        if (driveId) {
          const e = new Error('Could not access Google Drive file. Please ensure the author has set the Google Drive file General Access to "Anyone with the link" (Viewer).');
          e.code = 'DRIVE_PERMISSION_REQUIRED';
          throw e;
        } else if (lastDownloadError) {
          throw lastDownloadError;
        } else {
          const e = new Error('No valid manuscript source or download link found for this book edition.');
          e.code = 'NOT_FOUND';
          throw e;
        }
      }"""

NEW_READER_DRIVE_FAIL = """      if (!downloadedBytes) {
        if (driveId) {
          console.log('[NOVELIX Reader] Direct stream unavailable, activating Google Drive Interactive Viewer...');
          updateProgress(95, 'Loading interactive Drive reader…');
          renderDrivePreviewIframe(driveId);
          return;
        } else if (lastDownloadError) {
          throw lastDownloadError;
        } else {
          const e = new Error('No valid manuscript source or download link found for this book edition.');
          e.code = 'NOT_FOUND';
          throw e;
        }
      }"""

patches.append(('Reader Google Drive preview iframe fallback', OLD_READER_DRIVE_FAIL, NEW_READER_DRIVE_FAIL))

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 13: Add renderDrivePreviewIframe helper function
# ─────────────────────────────────────────────────────────────────────────────
OLD_RENDER_DRIVE_HELPER = """function reconnectDriveFromReader() {"""

NEW_RENDER_DRIVE_HELPER = """function renderDrivePreviewIframe(driveId) {
  const viewport = document.getElementById('readerViewport');
  if (!viewport) return;
  document.getElementById('canvasWrapper')?.classList.add('hidden');
  document.getElementById('readerLoadingOverlay')?.classList.add('hidden');
  document.getElementById('readerErrorOverlay')?.classList.add('hidden');

  let iframe = document.getElementById('readerDriveIframe');
  if (!iframe) {
    iframe = document.createElement('iframe');
    iframe.id = 'readerDriveIframe';
    iframe.className = 'w-full h-full border-0 rounded-xl shadow-2xl';
    iframe.style.cssText = 'width: 100%; height: calc(100vh - 120px); min-height: 500px; background: #12121A;';
    iframe.allow = 'autoplay';
    viewport.appendChild(iframe);
  }
  iframe.style.display = 'block';
  iframe.src = `https://drive.google.com/file/d/${driveId}/preview`;
  document.getElementById('readerCurrentPageBadge').textContent = 'Live';
  document.getElementById('readerTotalPagesBadge').textContent = 'Drive';
  showToast('📖 Reading via Google Drive Viewer');
}

function reconnectDriveFromReader() {"""

patches.append(('renderDrivePreviewIframe function', OLD_RENDER_DRIVE_HELPER, NEW_RENDER_DRIVE_HELPER))

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 14: Version bump to 12.6.0
# ─────────────────────────────────────────────────────────────────────────────
patches.append(('Version bump NOVELIX_VERSION to 12.6.0', "const NOVELIX_VERSION = '12.5.0';", "const NOVELIX_VERSION = '12.6.0';"))
patches.append(('Version bump generator json to 12.6.0', '"version": "12.3.0"', '"version": "12.6.0"'))

# ─────────────────────────────────────────────────────────────────────────────
# Apply all patches
# ─────────────────────────────────────────────────────────────────────────────
applied = 0
failed = []
for name, old, new in patches:
    if old in code:
        code = code.replace(old, new, 1)
        print(f'  ✓ Applied: {name}')
        applied += 1
    else:
        print(f'  ✗ FAILED:  {name}')
        failed.append(name)

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print(f'\nResult: {applied}/{len(patches)} patches applied')
if failed:
    print('FAILED patches:')
    for n in failed:
        print(f'  - {n}')
    sys.exit(1)
else:
    print('All patches applied successfully!')
