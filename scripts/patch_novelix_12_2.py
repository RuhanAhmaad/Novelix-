#!/usr/bin/env python3
import re
import sys

def patch():
    with open('scripts/generate_4.py', 'r', encoding='utf-8') as f:
        content = f.read()

    orig_len = len(content)
    print(f"Original content length: {orig_len}")

    # 1. Update Version and Early OTA Bootloader
    target_early = """  <script>
    (function() {
      window.__NOVELIX_VERSION__ = '12.0.0';
      window.addEventListener('error', function(e) {
        console.warn('[NOVELIX Early Error Guard]', e.message);
        var s = document.getElementById('splashScreen');
        if (s) { s.classList.add('hide'); s.style.display = 'none'; }
      });
      setTimeout(function() {
        var s = document.getElementById('splashScreen');
        if (s && !s.classList.contains('hide')) {
          s.classList.add('hide');
          setTimeout(function() { try { s.style.display = 'none'; s.remove(); } catch(err){} }, 300);
        }
      }, 2000);
    })();
  </script>"""

    replacement_early = """  <script>
    (function() {
      window.__NOVELIX_VERSION__ = '12.2.0';
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
      }

      window.addEventListener('error', function(e) {
        console.warn('[NOVELIX Early Error Guard]', e.message);
        var s = document.getElementById('splashScreen');
        if (s) { s.classList.add('hide'); s.style.display = 'none'; }
      });
      setTimeout(function() {
        var s = document.getElementById('splashScreen');
        if (s && !s.classList.contains('hide')) {
          s.classList.add('hide');
          setTimeout(function() { try { s.style.display = 'none'; s.remove(); } catch(err){} }, 300);
        }
      }, 2000);
    })();
  </script>"""

    if target_early in content:
        content = content.replace(target_early, replacement_early, 1)
        print("✓ Patched Early OTA Bootloader")
    else:
        print("✗ Could not find target_early")

    # 2. Add OTA Update Modal right before driveConnectModal
    target_modal = """<!-- ════════════════════════════════════════════════════════
     GOOGLE DRIVE SMART CONNECT & FAST PUBLISHING MODAL
═══════════════════════════════════════════════════════════ -->
<div id="driveConnectModal\""""

    replacement_modal = """<!-- ════════════════════════════════════════════════════════
     IN-APP OTA UPDATE INSTALLER MODAL
═══════════════════════════════════════════════════════════ -->
<div id="otaUpdateModal" class="modal-backdrop" onclick="if(event.target===this)closeOTAModal()">
  <div class="modal-sheet max-h-[85vh] flex flex-col p-6 space-y-4">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2.5">
        <div class="w-10 h-10 rounded-xl flex items-center justify-center bg-gradient-to-br from-[#9270FF] to-[#6C63FF] text-white font-bold text-base shadow-lg shadow-[#9270FF]/30">
          ⚡
        </div>
        <div>
          <h3 class="font-display font-bold text-sm text-white flex items-center gap-2">
            NOVELIX Update
            <span id="otaModalVerBadge" class="text-[10px] px-2 py-0.5 rounded-full bg-app-primary/20 text-app-primary border border-app-primary/40 font-mono font-bold">v12.2.0</span>
          </h3>
          <p class="text-[11px] text-app-muted">New release ready to install</p>
        </div>
      </div>
      <button onclick="closeOTAModal()" class="w-8 h-8 rounded-full surface-card flex items-center justify-center text-app-muted hover:text-white">✕</button>
    </div>

    <div class="p-4 rounded-xl border border-app-border bg-[#13121F] space-y-2.5">
      <div class="flex items-center justify-between text-xs">
        <span class="text-app-muted">Installed Build:</span>
        <span class="text-white font-mono font-bold">v12.1.0</span>
      </div>
      <div class="flex items-center justify-between text-xs">
        <span class="text-app-muted">Available Release:</span>
        <span id="otaModalLatestVer" class="text-emerald-400 font-mono font-bold">v12.2.0</span>
      </div>
      <div class="pt-1.5 border-t border-app-border/40 text-[11px] text-slate-300 space-y-1">
        <p class="font-semibold text-white">What's New:</p>
        <p class="text-emerald-300">• Direct Google Drive OAuth with verified access tokens</p>
        <p class="text-emerald-300">• Live mobile status bar notifications</p>
        <p class="text-emerald-300">• Seamless manuscript reading without internal errors</p>
        <p class="text-emerald-300">• One-tap in-app OTA installer engine</p>
      </div>
    </div>

    <!-- Progress bar during download -->
    <div id="otaProgressWrapper" class="hidden space-y-1.5">
      <div class="flex justify-between text-[11px]">
        <span id="otaProgressLabel" class="text-app-muted">Downloading update...</span>
        <span id="otaProgressPct" class="text-app-primary font-bold">0%</span>
      </div>
      <div class="w-full h-2 rounded-full bg-app-surface overflow-hidden">
        <div id="otaProgressBar" class="h-full bg-gradient-to-r from-[#9270FF] to-[#6C63FF] transition-all duration-200" style="width: 0%"></div>
      </div>
    </div>

    <div class="space-y-2 pt-1">
      <button id="otaInstallBtn" onclick="forceUpdateFromGitHub()" class="btn-primary w-full py-3 text-xs font-bold flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(146,112,255,0.4)]">
        <span>⚡ Install In-App Update Now</span>
      </button>

      <a id="otaDownloadApkBtn" href="https://github.com/RuhanAhmaad/Novelix-/releases/latest" target="_blank" class="w-full py-2.5 px-3 rounded-xl border border-app-border bg-app-surface hover:bg-app-card text-white text-xs font-semibold flex items-center justify-center gap-2 transition-all">
        <span>📦 Download APK Package</span>
      </a>

      <button onclick="closeOTAModal()" class="w-full py-2 text-xs text-app-muted hover:text-white transition-colors">
        Remind Me Later
      </button>
    </div>
  </div>
</div>

<!-- ════════════════════════════════════════════════════════
     GOOGLE DRIVE SMART CONNECT & FAST PUBLISHING MODAL
═══════════════════════════════════════════════════════════ -->
<div id="driveConnectModal\""""

    if target_modal in content:
        content = content.replace(target_modal, replacement_modal, 1)
        print("✓ Inserted OTA Update Modal")
    else:
        print("✗ Could not find target_modal")

    # 3. Patch Notification Trigger and Native Bridge
    target_notif = """// ── 2. Real Mobile System Status Bar Notifications ────
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
}"""

    replacement_notif = """// ── 2. Real Mobile System Status Bar Notifications ────
function triggerSystemMobileNotification(title, message, bookId = '') {
  console.log('[NOVELIX Notification] Dispatching alert:', title, message);

  // 1. Android Native System Tray Notification (via MainActivity Java Bridge)
  if (window.AndroidNotification && typeof window.AndroidNotification.showNotification === 'function') {
    try {
      window.AndroidNotification.showNotification(title, message, bookId || '');
      console.log('[NOVELIX Notification] Dispatched to Android status bar via Java bridge');
      return;
    } catch(bridgeErr) {
      console.warn('[NOVELIX Notification] Java bridge notice:', bridgeErr);
    }
  }

  // 2. Request Android 13+ permission via native bridge if available
  if (window.AndroidNotification && typeof window.AndroidNotification.requestPermission === 'function') {
    try { window.AndroidNotification.requestPermission(); } catch(_) {}
  }

  // 3. Web Notification API fallback
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
          if (bookId) openBookDetail(bookId);
          notif.close();
        };
      } catch (sysErr) {
        console.warn('[NOVELIX Push] Web notification notice:', sysErr);
      }
    } else if (Notification.permission !== 'denied') {
      Notification.requestPermission().then(p => {
        if (p === 'granted') triggerSystemMobileNotification(title, message, bookId);
      });
    }
  }
}

// User-facing notification test helper
function testMobileNotification() {
  if (window.AndroidNotification && typeof window.AndroidNotification.requestPermission === 'function') {
    try { window.AndroidNotification.requestPermission(); } catch(_) {}
  }
  triggerSystemMobileNotification('NOVELIX Alert', '🔔 Notifications are working on your device!', '');
  showToast('✓ Mobile notification sent to status bar');
}"""

    if target_notif in content:
        content = content.replace(target_notif, replacement_notif, 1)
        print("✓ Patched triggerSystemMobileNotification with Android Native Bridge")
    else:
        print("✗ Could not find target_notif")

    # 4. Patch connectGoogleDriveDirect and connectCurrentAccountToDrive
    target_drive_connect = """async function connectGoogleDriveDirect() {
  showToast('Connecting Google Drive via In-App Native Auth...');
  try {
    const isCapacitor = !!(window.Capacitor && (typeof window.Capacitor.isNativePlatform === 'function' ? window.Capacitor.isNativePlatform() : window.Capacitor.platform !== 'web'));
    const googleAuthPlugin = window.Capacitor?.Plugins?.GoogleAuth;

    // 1. Android Native Google Sign-In (Zero browser redirects!)
    if (isCapacitor && googleAuthPlugin) {
      console.log('[NOVELIX Drive] Initiating native Android Google Sign-In bottom-sheet...');
      try {
        await googleAuthPlugin.initialize({
          clientId: '239783323113-r33bjnuc153ghsgpshg8vp3mktqj6t36.apps.googleusercontent.com',
          scopes: ['profile', 'email'],
          grantOfflineAccess: true,
        });
      } catch (initErr) {
        console.warn('[NOVELIX Drive] GoogleAuth initialize note:', initErr);
      }

      const googleUser = await googleAuthPlugin.signIn();
      if (googleUser && googleUser.email) {
        const email = googleUser.email;
        const displayName = googleUser.name || googleUser.displayName || 'Google Author';
        const acct = {
          accountId: 'drive_' + Date.now(),
          email: email,
          displayName: displayName,
          connectedAt: new Date().toISOString(),
          status: 'active',
          storageType: 'google_drive'
        };

        if (!APP_STATE.connectedDriveAccounts) APP_STATE.connectedDriveAccounts = [];
        const existing = APP_STATE.connectedDriveAccounts.find(a => a.email === acct.email);
        if (!existing) APP_STATE.connectedDriveAccounts.push(acct);

        if (db && APP_STATE.user) {
          await db.collection('users').doc(APP_STATE.user.uid).collection('connectedDriveAccounts')
            .doc(acct.accountId).set(acct, { merge: true }).catch(() => {});
        }

        closeDriveConnectModal();
        showToast(`✓ Google Drive connected: ${acct.email}`);
        loadConnectedDriveAccounts();
        return;
      }
    }

    // 2. If already logged in, 1-tap connect immediately!
    if (APP_STATE.user && APP_STATE.user.email) {
      connectCurrentAccountToDrive();
      return;
    }

    // 3. Web fallback with popup
    if (typeof firebase !== 'undefined' && firebase.auth) {
      const provider = new firebase.auth.GoogleAuthProvider();
      provider.addScope('email');
      provider.addScope('profile');
      const res = await firebase.auth().signInWithPopup(provider);
      if (res && res.user && res.user.email) {
        connectCurrentAccountToDrive();
        return;
      }
    }

    showToast('Drive Connected! Fast direct link publishing is active.');
    closeDriveConnectModal();

  } catch (err) {
    console.warn('[NOVELIX Drive] Connect error:', err);
    if (err.code === 'auth/popup-closed-by-user' || err.code === '12501') {
      showToast('Google sign-in was closed.');
    } else {
      showToast('Fast Direct Publishing active! You can paste any Drive link directly.');
      closeDriveConnectModal();
    }
  }
}"""

    replacement_drive_connect = """async function connectGoogleDriveDirect() {
  showToast('Connecting Google Drive via In-App Native Auth...');
  try {
    const isCapacitor = !!(window.Capacitor && (typeof window.Capacitor.isNativePlatform === 'function' ? window.Capacitor.isNativePlatform() : window.Capacitor.platform !== 'web'));
    const googleAuthPlugin = window.Capacitor?.Plugins?.GoogleAuth;

    const driveScopes = [
      'profile',
      'email',
      'https://www.googleapis.com/auth/drive.readonly',
      'https://www.googleapis.com/auth/drive.file'
    ];

    // 1. Android Native Google Sign-In with real Google Drive scopes
    if (isCapacitor && googleAuthPlugin) {
      console.log('[NOVELIX Drive] Initiating native Google Drive Sign-In...');
      try {
        await googleAuthPlugin.initialize({
          clientId: '239783323113-r33bjnuc153ghsgpshg8vp3mktqj6t36.apps.googleusercontent.com',
          scopes: driveScopes,
          grantOfflineAccess: true,
        });
      } catch (initErr) {
        console.warn('[NOVELIX Drive] GoogleAuth initialize note:', initErr);
      }

      const googleUser = await googleAuthPlugin.signIn();
      if (googleUser && googleUser.email) {
        const email = googleUser.email;
        const displayName = googleUser.name || googleUser.displayName || 'Google Author';
        const accessToken = googleUser.authentication?.accessToken || googleUser.accessToken || '';
        const idToken = googleUser.authentication?.idToken || googleUser.idToken || '';
        const accId = 'drive_' + Date.now();

        const acct = {
          id: accId,
          accountId: accId,
          email: email,
          displayName: displayName,
          picture: googleUser.imageUrl || '',
          accessToken: accessToken,
          idToken: idToken,
          hasDriveScope: true,
          connectedAt: new Date().toISOString(),
          status: 'active',
          storageType: 'google_drive'
        };

        if (accessToken) {
          try {
            localStorage.setItem('novelix_drive_token_' + email, accessToken);
            localStorage.setItem('novelix_active_drive_token', accessToken);
          } catch(_) {}
        }

        if (!APP_STATE.connectedDriveAccounts) APP_STATE.connectedDriveAccounts = [];
        const existingIdx = APP_STATE.connectedDriveAccounts.findIndex(a => a.email === acct.email);
        if (existingIdx > -1) {
          APP_STATE.connectedDriveAccounts[existingIdx] = acct;
        } else {
          APP_STATE.connectedDriveAccounts.push(acct);
        }

        if (db && APP_STATE.user) {
          await Promise.all([
            db.collection('users').doc(APP_STATE.user.uid).collection('drive_accounts').doc(accId).set(acct, { merge: true }).catch(() => {}),
            db.collection('users').doc(APP_STATE.user.uid).collection('connectedDriveAccounts').doc(accId).set(acct, { merge: true }).catch(() => {})
          ]);
        }

        closeDriveConnectModal();
        showToast(`✓ Google Drive connected with real access: ${acct.email}`);
        loadConnectedDriveAccounts();
        return;
      }
    }

    // 2. Web popup fallback with Drive scopes
    if (typeof firebase !== 'undefined' && firebase.auth) {
      const provider = new firebase.auth.GoogleAuthProvider();
      provider.addScope('https://www.googleapis.com/auth/drive.readonly');
      provider.addScope('https://www.googleapis.com/auth/drive.file');
      const res = await firebase.auth().signInWithPopup(provider);
      if (res && res.user && res.user.email) {
        const token = res.credential?.accessToken || '';
        const accId = 'drive_' + Date.now();
        const acct = {
          id: accId,
          accountId: accId,
          email: res.user.email,
          displayName: res.user.displayName || 'Google Author',
          picture: res.user.photoURL || '',
          accessToken: token,
          hasDriveScope: true,
          connectedAt: new Date().toISOString(),
          status: 'active',
          storageType: 'google_drive'
        };

        if (token) {
          try {
            localStorage.setItem('novelix_drive_token_' + res.user.email, token);
            localStorage.setItem('novelix_active_drive_token', token);
          } catch(_) {}
        }

        if (!APP_STATE.connectedDriveAccounts) APP_STATE.connectedDriveAccounts = [];
        APP_STATE.connectedDriveAccounts.push(acct);

        if (db && APP_STATE.user) {
          await db.collection('users').doc(APP_STATE.user.uid).collection('drive_accounts').doc(accId).set(acct, { merge: true }).catch(() => {});
        }

        closeDriveConnectModal();
        showToast(`✓ Google Drive connected: ${acct.email}`);
        loadConnectedDriveAccounts();
        return;
      }
    }

    showToast('Drive Connected! Direct link publishing is ready.');
    closeDriveConnectModal();

  } catch (err) {
    console.warn('[NOVELIX Drive] Connect error:', err);
    if (err.code === 'auth/popup-closed-by-user' || err.code === '12501') {
      showToast('Google sign-in was closed.');
    } else {
      showToast('Fast Direct Publishing active! You can paste any Drive link directly.');
      closeDriveConnectModal();
    }
  }
}"""

    if target_drive_connect in content:
        content = content.replace(target_drive_connect, replacement_drive_connect, 1)
        print("✓ Patched connectGoogleDriveDirect with real Drive scopes and token persistence")
    else:
        print("✗ Could not find target_drive_connect")

    # 5. Patch connectCurrentAccountToDrive
    target_current_drive = """function connectCurrentAccountToDrive() {
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
}"""

    replacement_current_drive = """async function connectCurrentAccountToDrive() {
  if (!APP_STATE.user || !APP_STATE.user.email) {
    openAuthModal();
    return;
  }

  // Trigger real OAuth with Drive scope so we obtain an access token
  connectGoogleDriveDirect();
}"""

    if target_current_drive in content:
        content = content.replace(target_current_drive, replacement_current_drive, 1)
        print("✓ Patched connectCurrentAccountToDrive")
    else:
        print("✗ Could not find target_current_drive")

    # 6. Patch loadConnectedDriveAccounts to load tokens and check both collections
    target_load_drive = """    // Firestore fallback
    if (!accounts.length) {
      const snap = await db.collection('users').doc(APP_STATE.user.uid).collection('drive_accounts').get();
      snap.forEach(d => accounts.push(d.data()));
    }"""

    replacement_load_drive = """    // Firestore lookup across both drive_accounts and connectedDriveAccounts collections
    if (!accounts.length) {
      const [snap1, snap2] = await Promise.all([
        db.collection('users').doc(APP_STATE.user.uid).collection('drive_accounts').get().catch(() => ({ docs: [] })),
        db.collection('users').doc(APP_STATE.user.uid).collection('connectedDriveAccounts').get().catch(() => ({ docs: [] }))
      ]);

      const seen = new Set();
      const addAcc = (data) => {
        const id = data.id || data.accountId || data.email;
        if (!seen.has(id)) {
          seen.add(id);
          // Restore access token from local storage if available
          if (!data.accessToken && data.email) {
            data.accessToken = localStorage.getItem('novelix_drive_token_' + data.email) || localStorage.getItem('novelix_active_drive_token') || '';
          }
          data.id = data.id || data.accountId || ('drive_' + Date.now());
          accounts.push(data);
        }
      };

      (snap1.docs || []).forEach(d => addAcc(d.data()));
      (snap2.docs || []).forEach(d => addAcc(d.data()));
    }"""

    if target_load_drive in content:
        content = content.replace(target_load_drive, replacement_load_drive, 1)
        print("✓ Patched loadConnectedDriveAccounts")
    else:
        print("✗ Could not find target_load_drive")

    # 7. Patch browseDriveAccountFiles
    target_browse_drive = """  // Strategy 2: Client fetch with token
  let token = acc.accessToken;"""

    replacement_browse_drive = """  // Strategy 2: Client fetch with token
  let token = acc.accessToken || localStorage.getItem('novelix_drive_token_' + acc.email) || localStorage.getItem('novelix_active_drive_token');"""

    if target_browse_drive in content:
        content = content.replace(target_browse_drive, replacement_browse_drive, 1)
        print("✓ Patched browseDriveAccountFiles token fallback")
    else:
        print("✗ Could not find target_browse_drive")

    # 8. Patch live notification listener in Startup and Notifications feed
    target_startup_notif = """      auth.onAuthStateChanged(async (firebaseUser) => {
        APP_STATE.user = firebaseUser;
        if (firebaseUser) {
          await handleUserAuthenticated(firebaseUser);
        } else {
          handleUserLoggedOut();
        }
      });"""

    replacement_startup_notif = """      auth.onAuthStateChanged(async (firebaseUser) => {
        APP_STATE.user = firebaseUser;
        // Start push listeners immediately
        try { setupGlobalPushNotificationListener(); } catch(_) {}
        if (firebaseUser) {
          await handleUserAuthenticated(firebaseUser);
        } else {
          handleUserLoggedOut();
        }
      });"""

    if target_startup_notif in content:
        content = content.replace(target_startup_notif, replacement_startup_notif, 1)
        print("✓ Patched auth.onAuthStateChanged to trigger setupGlobalPushNotificationListener")
    else:
        print("✗ Could not find target_startup_notif")

    # 9. Patch setupGlobalPushNotificationListener to handle timestamp objects safely
    target_push_listener = """function setupGlobalPushNotificationListener() {
  if (!db) return;
  const launchTime = Date.now();

  try {
    db.collection('notifications')
      .orderBy('createdAt', 'desc')
      .limit(10)
      .onSnapshot(snapshot => {
        snapshot.docChanges().forEach(change => {
          if (change.type === 'added') {
            const data = change.doc.data();
            // If created after app launched or within the last 15 seconds, show heads-up banner
            if (data && data.createdAt && data.createdAt > (launchTime - 15000)) {
              showInAppPushBanner({ id: change.doc.id, ...data });
            }
          }
        });
      }, err => {
        console.warn('[NOVELIX Push] Global feed notice:', err.message);
      });
  } catch (e) {
    console.warn('[NOVELIX Push] Listener init notice:', e);
  }
}"""

    replacement_push_listener = """function setupGlobalPushNotificationListener() {
  if (!db || window._globalPushListenerActive) return;
  window._globalPushListenerActive = true;
  const launchTime = Date.now();
  console.log('[NOVELIX Push] Global notification listener initiated');

  try {
    db.collection('notifications')
      .orderBy('createdAt', 'desc')
      .limit(10)
      .onSnapshot(snapshot => {
        snapshot.docChanges().forEach(change => {
          if (change.type === 'added') {
            const data = change.doc.data();
            let cTime = 0;
            if (data && data.createdAt) {
              if (typeof data.createdAt === 'number') cTime = data.createdAt;
              else if (data.createdAt.toMillis) cTime = data.createdAt.toMillis();
              else if (data.createdAt.seconds) cTime = data.createdAt.seconds * 1000;
              else cTime = new Date(data.createdAt).getTime() || 0;
            }
            if (cTime > (launchTime - 15000)) {
              const title = data.title || 'NOVELIX Broadcast';
              const body = data.message || data.body || 'New announcement';
              const bookId = data.bookId || '';
              triggerSystemMobileNotification(title, body, bookId);
              showInAppPushBanner({ id: change.doc.id, ...data });
            }
          }
        });
      }, err => {
        console.warn('[NOVELIX Push] Global feed notice:', err.message);
      });
  } catch (e) {
    console.warn('[NOVELIX Push] Listener init notice:', e);
  }
}"""

    if target_push_listener in content:
        content = content.replace(target_push_listener, replacement_push_listener, 1)
        print("✓ Patched setupGlobalPushNotificationListener")
    else:
        print("✗ Could not find target_push_listener")

    # 10. Patch startNotificationsFeed to trigger mobile notification on user's feed additions
    target_user_notifs = """  APP_STATE.notifUnsub = db.collection('users').doc(uid).collection('notifications')
    .orderBy('createdAt', 'desc')
    .limit(30)
    .onSnapshot(snap => {
      let unread = 0;
      const list = [];
      snap.forEach(d => {
        const data = d.data();
        if (!data.isRead) unread++;
        list.push({ id: d.id, ...data });
      });"""

    replacement_user_notifs = """  let _feedLoadedOnce = false;
  APP_STATE.notifUnsub = db.collection('users').doc(uid).collection('notifications')
    .orderBy('createdAt', 'desc')
    .limit(30)
    .onSnapshot(snap => {
      let unread = 0;
      const list = [];
      snap.docChanges().forEach(change => {
        if (change.type === 'added') {
          const d = change.doc.data();
          if (_feedLoadedOnce && !d.isRead) {
            const title = d.title || d.bookTitle || 'NOVELIX Notification';
            const body = d.message || d.body || 'You have a new update';
            const bookId = d.publicationId || d.bookId || '';
            triggerSystemMobileNotification(title, body, bookId);
            showInAppPushBanner({ id: change.doc.id, title, message: body, bookId });
          }
        }
      });
      _feedLoadedOnce = true;
      snap.forEach(d => {
        const data = d.data();
        if (!data.isRead) unread++;
        list.push({ id: d.id, ...data });
      });"""

    if target_user_notifs in content:
        content = content.replace(target_user_notifs, replacement_user_notifs, 1)
        print("✓ Patched startNotificationsFeed for live status bar alerts")
    else:
        print("✗ Could not find target_user_notifs")

    # 11. Patch OTA updater engine with XHR fallback, custom modal, and clean install
    target_ota_engine = """const NOVELIX_VERSION = '12.1.0';
const OTA_GITHUB_URL = 'https://raw.githubusercontent.com/RuhanAhmaad/Novelix-/main/out/index.html';
const OTA_VERSION_URL = 'https://raw.githubusercontent.com/RuhanAhmaad/Novelix-/main/out/version.json';

// ── Live OTA Update Engine ────────────────────────────────
async function checkForOTAUpdate(silent = true) {
  const statusEl = document.getElementById('otaStatusText');
  if (statusEl) statusEl.textContent = 'Checking GitHub...';

  try {
    const res = await fetch(OTA_VERSION_URL + '?t=' + Date.now(), {
      cache: 'no-store',
      signal: AbortSignal.timeout(6000)
    });

    if (!res.ok) {
      if (statusEl) statusEl.textContent = '● Up to date (v' + NOVELIX_VERSION + ')';
      if (!silent) showToast('✅ You are running the latest version (' + NOVELIX_VERSION + ')');
      return;
    }

    const data = await res.json();
    const remoteVer = data.version || '12.0.0';

    if (remoteVer === NOVELIX_VERSION) {
      if (statusEl) statusEl.textContent = '● Up to date (v' + NOVELIX_VERSION + ')';
      if (!silent) showToast('✅ Running latest NOVELIX build (v' + NOVELIX_VERSION + ')');
    } else {
      if (statusEl) statusEl.innerHTML = '<span class="text-amber-400">⚡ Update available: v' + remoteVer + '</span>';
      if (!silent) {
        if (confirm('🚀 New version v' + remoteVer + ' is available on GitHub!\\n\\nPull and install update now?')) {
          await forceUpdateFromGitHub();
        }
      } else {
        showToast('🔔 New NOVELIX update v' + remoteVer + ' available on GitHub');
      }
    }
  } catch (e) {
    if (statusEl) statusEl.textContent = '● Offline / Current (v' + NOVELIX_VERSION + ')';
    if (!silent) showToast('Update check note: Running current build (v' + NOVELIX_VERSION + ')');
  }
}

async function forceUpdateFromGitHub() {
  const statusEl = document.getElementById('otaStatusText');
  if (statusEl) statusEl.textContent = '⏳ Downloading latest source from GitHub...';
  showToast('⬇️ Pulling latest NOVELIX release from GitHub...');

  try {
    const res = await fetch(OTA_GITHUB_URL + '?t=' + Date.now(), {
      cache: 'no-store',
      signal: AbortSignal.timeout(35000)
    });

    if (!res.ok) throw new Error('HTTP ' + res.status + ' while downloading from GitHub');
    const html = await res.text();

    if (!html || html.length < 15000 || !html.includes('NOVELIX')) {
      throw new Error('Downloaded bundle verification failed — invalid code structure.');
    }

    // Cache to localStorage
    try {
      localStorage.setItem('novelix_ota_html', html);
      localStorage.setItem('novelix_ota_ver', '12.0.0-ota-' + Date.now());
    } catch(err) {
      console.warn('[NOVELIX OTA] LocalStorage quota notice:', err);
    }

    if (statusEl) statusEl.innerHTML = '<span class="text-emerald-400">✓ Updated! Applying...</span>';
    showToast('✅ Downloaded latest NOVELIX! Applying update in 2 seconds...');

    setTimeout(() => {
      // Hot-replace document
      document.open();
      document.write(html);
      document.close();
    }, 1800);

  } catch (err) {
    if (statusEl) statusEl.innerHTML = '<span class="text-red-400">✗ ' + err.message + '</span>';
    showToast('Update failed: ' + err.message);
  }
}"""

    replacement_ota_engine = """const NOVELIX_VERSION = '12.2.0';
const OTA_GITHUB_URL = 'https://raw.githubusercontent.com/RuhanAhmaad/Novelix-/main/out/index.html';
const OTA_VERSION_URL = 'https://raw.githubusercontent.com/RuhanAhmaad/Novelix-/main/out/version.json';

// Direct robust fetch with XHR fallback for CapacitorHttp
async function fetchWithXHRFallback(url, timeoutMs = 25000) {
  try {
    const res = await fetch(url, { cache: 'no-store', signal: AbortSignal.timeout(timeoutMs) });
    if (res.ok) {
      const text = await res.text();
      return { ok: true, status: res.status, text: () => Promise.resolve(text), json: () => Promise.resolve(JSON.parse(text)) };
    }
  } catch(e) {
    console.warn('[NOVELIX Fetch] Native fetch notice, trying XHR fallback:', e.message);
  }

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.timeout = timeoutMs;
    xhr.onload = function() {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve({
          ok: true,
          status: xhr.status,
          text: () => Promise.resolve(xhr.responseText),
          json: () => Promise.resolve(JSON.parse(xhr.responseText))
        });
      } else {
        reject(new Error('HTTP ' + xhr.status));
      }
    };
    xhr.onerror = () => reject(new Error('Network request failed'));
    xhr.ontimeout = () => reject(new Error('Request timed out'));
    xhr.send();
  });
}

function openOTAModal(remoteVer, data) {
  const m = document.getElementById('otaUpdateModal');
  if (!m) return;
  const badge = document.getElementById('otaModalVerBadge');
  const latestVer = document.getElementById('otaModalLatestVer');
  if (badge) badge.textContent = 'v' + remoteVer;
  if (latestVer) latestVer.textContent = 'v' + remoteVer;
  m.classList.add('open');
}

function closeOTAModal() {
  const m = document.getElementById('otaUpdateModal');
  if (m) m.classList.remove('open');
}

// ── Live OTA Update Engine ────────────────────────────────
async function checkForOTAUpdate(silent = true) {
  const statusEl = document.getElementById('otaStatusText');
  if (statusEl) statusEl.textContent = 'Checking GitHub...';

  try {
    const res = await fetchWithXHRFallback(OTA_VERSION_URL + '?t=' + Date.now(), 8000);
    const data = await res.json();
    const remoteVer = data.version || '12.2.0';

    if (remoteVer === NOVELIX_VERSION) {
      if (statusEl) statusEl.textContent = '● Up to date (v' + NOVELIX_VERSION + ')';
      if (!silent) showToast('✅ You are running the latest version (' + NOVELIX_VERSION + ')');
    } else {
      if (statusEl) statusEl.innerHTML = '<span class="text-amber-400">⚡ Update available: v' + remoteVer + '</span>';
      openOTAModal(remoteVer, data);
      if (!silent) {
        showToast('🚀 New NOVELIX version v' + remoteVer + ' is ready to install!');
      }
    }
  } catch (e) {
    if (statusEl) statusEl.textContent = '● Current (v' + NOVELIX_VERSION + ')';
    if (!silent) showToast('Running build v' + NOVELIX_VERSION);
  }
}

async function forceUpdateFromGitHub() {
  const statusEl = document.getElementById('otaStatusText');
  const progWrapper = document.getElementById('otaProgressWrapper');
  const progBar = document.getElementById('otaProgressBar');
  const progPct = document.getElementById('otaProgressPct');
  const installBtn = document.getElementById('otaInstallBtn');

  if (statusEl) statusEl.textContent = '⏳ Downloading latest source...';
  if (progWrapper) progWrapper.classList.remove('hidden');
  if (progBar) progBar.style.width = '25%';
  if (progPct) progPct.textContent = '25%';
  if (installBtn) { installBtn.disabled = true; installBtn.textContent = 'Downloading update...'; }
  showToast('⬇️ Pulling latest release from GitHub...');

  try {
    if (progBar) progBar.style.width = '60%';
    if (progPct) progPct.textContent = '60%';

    const res = await fetchWithXHRFallback(OTA_GITHUB_URL + '?t=' + Date.now(), 45000);
    const html = await res.text();

    if (!html || html.length < 20000 || !html.includes('NOVELIX')) {
      throw new Error('Downloaded bundle verification failed.');
    }

    if (progBar) progBar.style.width = '95%';
    if (progPct) progPct.textContent = '95%';

    // Cache to localStorage
    try {
      localStorage.setItem('novelix_ota_html', html);
      localStorage.setItem('novelix_ota_ver', '12.2.0');
    } catch(err) {
      console.warn('[NOVELIX OTA] LocalStorage note:', err);
    }

    if (progBar) progBar.style.width = '100%';
    if (progPct) progPct.textContent = '100%';
    if (statusEl) statusEl.innerHTML = '<span class="text-emerald-400">✓ Updated! Applying...</span>';
    showToast('✅ Update installed! Applying live updates...');

    setTimeout(() => {
      closeOTAModal();
      // Reload document to run newly cached OTA bundle
      window.location.reload(true);
    }, 1500);

  } catch (err) {
    if (progWrapper) progWrapper.classList.add('hidden');
    if (installBtn) { installBtn.disabled = false; installBtn.textContent = '⚡ Retry In-App Update'; }
    if (statusEl) statusEl.innerHTML = '<span class="text-red-400">✗ ' + err.message + '</span>';
    showToast('Update failed: ' + err.message);
  }
}"""

    if target_ota_engine in content:
        content = content.replace(target_ota_engine, replacement_ota_engine, 1)
        print("✓ Patched OTA Updater Engine with modal and robust installation")
    else:
        print("✗ Could not find target_ota_engine")

    # 12. Patch fetchPdfBytes to handle Google Drive virus scan warning pages
    target_fetch_pdf = """    const contentType = resp.headers.get('content-type') || '';
    if (contentType.includes('text/html') || contentType.includes('application/json')) {
      const e = new Error('Server returned an error page or confirmation instead of a PDF file.');
      e.code = 'INVALID_FORMAT';
      throw e;
    }"""

    replacement_fetch_pdf = """    const contentType = resp.headers.get('content-type') || '';
    if (contentType.includes('text/html')) {
      // Check if this is a Google Drive virus scan warning confirmation page
      try {
        const pageText = await resp.text();
        const confirmMatch = pageText.match(/confirm=([0-9a-zA-Z_-]+)/i) ||
                             pageText.match(/\/uc\\?export=download&(?:amp;)?confirm=([0-9a-zA-Z_-]+)/i);
        const fileIdMatch = pageText.match(/id=([0-9a-zA-Z_-]{25,})/i) || resolvedUrl.match(/id=([0-9a-zA-Z_-]{25,})/i);

        if (confirmMatch && confirmMatch[1] && fileIdMatch && fileIdMatch[1]) {
          console.log('[NOVELIX Reader] Detected Google Drive confirmation token, bypassing warning page...');
          const bypassedUrl = `https://drive.usercontent.google.com/download?id=${fileIdMatch[1]}&export=download&confirm=${confirmMatch[1]}`;
          const retryResp = await fetch(bypassedUrl, { method: 'GET', credentials: 'omit', signal });
          if (retryResp.ok) {
            const buf = await retryResp.arrayBuffer();
            const bArr = new Uint8Array(buf);
            if (bArr.length >= 5 && bArr[0] === 0x25 && bArr[1] === 0x50) return bArr;
          }
        }
      } catch(confirmErr) {
        console.warn('[NOVELIX Reader] Confirmation scrape note:', confirmErr);
      }

      const e = new Error('Google Drive requires confirmation or permission. Please ensure file is shared as Anyone with the link (Viewer).');
      e.code = 'DRIVE_PERMISSION_REQUIRED';
      throw e;
    }"""

    if target_fetch_pdf in content:
        content = content.replace(target_fetch_pdf, replacement_fetch_pdf, 1)
        print("✓ Patched fetchPdfBytes with Google Drive confirmation bypass")
    else:
        print("✗ Could not find target_fetch_pdf")

    # 13. Patch loadPdfDocumentForReader to eliminate Cloud Functions internal error
    target_reader_cf = """      // Strategy 2: If direct downloads didn't succeed, and Cloud Functions are available, try Callable getReaderPdfData safely
      if (!downloadedBytes && typeof functions !== 'undefined' && functions && typeof functions.httpsCallable === 'function') {
        try {
          updateProgress(65, 'Checking cloud manuscript proxy…');
          const getPdfFn = functions.httpsCallable('getReaderPdfData');
          const res = await withTimeout(
            getPdfFn({ bookId: book.id, language: edition.language || 'Standard' }),
            10000,
            'Drive proxy timed out',
            'DRIVE_TIMEOUT'
          );

          if (res && res.data && res.data.base64) {
            updateProgress(75, 'Decoding manuscript data…');
            const binaryString = atob(res.data.base64);
            const len = binaryString.length;
            const bytes = new Uint8Array(len);
            for (let i = 0; i < len; i++) bytes[i] = binaryString.charCodeAt(i);
            if (bytes.length >= 5 && bytes[0] === 0x25 && bytes[1] === 0x50 && bytes[2] === 0x44 && bytes[3] === 0x46) {
              downloadedBytes = bytes;
            }
          } else if (res && res.data && res.data.fileUrl) {
            const bytes = await fetchPdfBytes(res.data.fileUrl, null, abortController.signal);
            if (bytes && bytes.length > 20) downloadedBytes = bytes;
          }
        } catch(cfErr) {
          console.warn('[NOVELIX Reader] Cloud Function proxy note:', cfErr.message || cfErr.code);
        }
      }"""

    replacement_reader_cf = """      // Strategy 2: Try authorized Google Drive API fetch if user has connected Drive account
      if (!downloadedBytes && driveId) {
        const driveToken = localStorage.getItem('novelix_active_drive_token') ||
          (APP_STATE.connectedDriveAccounts && APP_STATE.connectedDriveAccounts[0]?.accessToken);

        if (driveToken) {
          try {
            updateProgress(65, 'Streaming via authorized Google Drive API…');
            const apiResp = await fetch(`https://www.googleapis.com/drive/v3/files/${driveId}?alt=media`, {
              headers: { Authorization: `Bearer ${driveToken}` },
              signal: abortController.signal
            });
            if (apiResp.ok) {
              const buf = await apiResp.arrayBuffer();
              const bArr = new Uint8Array(buf);
              if (bArr.length >= 5 && bArr[0] === 0x25 && bArr[1] === 0x50) {
                downloadedBytes = bArr;
                console.log('[NOVELIX Reader] Successfully downloaded via authorized Google Drive API');
              }
            }
          } catch(apiErr) {
            console.warn('[NOVELIX Reader] Drive API fetch note:', apiErr);
          }
        }
      }"""

    if target_reader_cf in content:
        content = content.replace(target_reader_cf, replacement_reader_cf, 1)
        print("✓ Replaced Cloud Function getReaderPdfData with direct Google Drive API authorized stream")
    else:
        print("✗ Could not find target_reader_cf")

    # 14. Patch version.json dump at the end
    target_vjson = 'json.dump({"version": "12.1.0", "build": 12100, "releaseDate": "2026-11-11", "name": "NOVELIX 12.1 Ultra Suite"}, vf, indent=2)'
    replacement_vjson = 'json.dump({"version": "12.2.0", "build": 12200, "releaseDate": "2026-11-11", "name": "NOVELIX 12.2 Enterprise"}, vf, indent=2)'

    if target_vjson in content:
        content = content.replace(target_vjson, replacement_vjson, 1)
        print("✓ Patched version.json generator to v12.2.0")
    else:
        print("✗ Could not find target_vjson")

    with open('scripts/generate_4.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Patched successfully. New length: {len(content)}")

if __name__ == '__main__':
    patch()
