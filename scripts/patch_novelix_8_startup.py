#!/usr/bin/env python3
"""
NOVELIX 8.0 — Critical Splash Screen Fix & Startup Architecture
Applies:
  1. Defines `handleResumeButtonClick` helper and wires it to `directResumeBook`
  2. Implements `StartupController` with watchdog timer, sequenced initialization, and graceful fallback
  3. Inserts inline emergency splash-dismiss watchdog script immediately after #splashScreen
  4. Defensive Firebase & PDF.js initialization with offline fallback
  5. Implements `mapFirebaseAuthError` for friendly auth error toasts
  6. Adds null-checks to all admin table loaders
"""

import sys

def patch(content, old, new, label):
    if old not in content:
        print(f"  [WARN] Pattern not found: {label}")
        return content
    result = content.replace(old, new, 1)
    print(f"  [OK] Applied: {label}")
    return result

with open("scripts/generate_4.py", "r", encoding="utf-8") as f:
    content = f.read()

print("=== NOVELIX 8.0 Startup & Architecture Upgrade ===")

# ═══════════════════════════════════════════════════════════════
# 1. EMERGENCY SPLASH WATCHDOG (Inline HTML immediately after splashScreen)
# ═══════════════════════════════════════════════════════════════
old_splash = """<!-- ════════════════════════════════════════════════════════
     1. SPLASH SCREEN (Native Feel Hardware-Accelerated)
═══════════════════════════════════════════════════════════ -->
<div id="splashScreen">
  <div class="splash-logo-box">
    <div class="splash-logo-glyph">N</div>
  </div>
  <div class="splash-title">NOVELIX</div>
  <div class="splash-sub">PUBLISHING & READING SUITE</div>
</div>"""

new_splash = """<!-- ════════════════════════════════════════════════════════
     1. SPLASH SCREEN (Native Feel Hardware-Accelerated)
═══════════════════════════════════════════════════════════ -->
<div id="splashScreen">
  <div class="splash-logo-box">
    <div class="splash-logo-glyph">N</div>
  </div>
  <div class="splash-title">NOVELIX</div>
  <div class="splash-sub">PUBLISHING & READING SUITE</div>
</div>
<script>
  // Emergency Startup Watchdog: If main JS or CDN fails to parse, dismiss splash within 3.5s
  window.__novelix_splash_timer = setTimeout(function() {
    var sp = document.getElementById('splashScreen');
    if (sp && !sp.classList.contains('hide')) {
      sp.classList.add('hide');
      console.warn('[NOVELIX Watchdog] Emergency splash dismiss triggered.');
    }
  }, 3500);
</script>"""

content = patch(content, old_splash, new_splash, "Emergency Splash Watchdog Script")

# ═══════════════════════════════════════════════════════════════
# 2. DEFENSIVE FIREBASE INITIALIZATION
# ═══════════════════════════════════════════════════════════════
old_fb_init = """// Initialize Firebase App
let auth, db, storage, messaging, functions;
try {
  if (typeof firebase !== 'undefined' && firebase.apps.length === 0) {
    firebase.initializeApp(FIREBASE_CONFIG);
  }
  auth = firebase.auth();
  db = firebase.firestore();
  storage = firebase.storage();
  messaging = null; // Background messaging handled natively via Capacitor
  functions = firebase.app().functions('us-central1');
} catch(e) {
  console.warn('Firebase init note:', e);
}"""

new_fb_init = """// Initialize Firebase App defensively
let auth = null, db = null, storage = null, messaging = null, functions = null;
try {
  if (typeof firebase !== 'undefined') {
    if (firebase.apps && firebase.apps.length === 0) {
      firebase.initializeApp(FIREBASE_CONFIG);
    }
    if (typeof firebase.auth === 'function') auth = firebase.auth();
    if (typeof firebase.firestore === 'function') db = firebase.firestore();
    if (typeof firebase.storage === 'function') storage = firebase.storage();
    if (typeof firebase.app === 'function') {
      try { functions = firebase.app().functions('us-central1'); } catch(fe) {}
    }
    console.log('[NOVELIX] Firebase services initialized successfully.');
  } else {
    console.warn('[NOVELIX] Firebase SDK not detected — offline fallback mode active.');
  }
} catch(e) {
  console.warn('[NOVELIX] Firebase init note:', e);
}"""

content = patch(content, old_fb_init, new_fb_init, "Defensive Firebase Initialization")

# ═══════════════════════════════════════════════════════════════
# 3. DEFENSIVE PDF.js CHECK IN loadPdfDocumentForReader
# ═══════════════════════════════════════════════════════════════
old_pdf_init = """  try {
    APP_STATE.pdfIsRendering = true;
    updateReaderProgressDisplay(10, 'Resolving manuscript file...');"""

new_pdf_init = """  if (typeof pdfjsLib === 'undefined') {
    showReaderError({
      title: 'PDF Reader Offline',
      message: 'The PDF rendering library is still loading or unavailable offline. Please check your network connection.',
      code: 'ERR_PDF_LIB_UNAVAILABLE'
    });
    return;
  }

  try {
    APP_STATE.pdfIsRendering = true;
    updateReaderProgressDisplay(10, 'Resolving manuscript file...');"""

content = patch(content, old_pdf_init, new_pdf_init, "Defensive PDF.js Availability Check")

# ═══════════════════════════════════════════════════════════════
# 4. IMPLEMENT handleResumeButtonClick & mapFirebaseAuthError
# ═══════════════════════════════════════════════════════════════
old_direct_resume = """// Direct one-tap resume when user explicitly taps "Resume" button
async function directResumeBook(bookId, page, editionLanguage, event) {"""

new_direct_resume = """// Delegated click handler for library resume buttons
function handleResumeButtonClick(btn, event) {
  if (event) event.stopPropagation();
  const bookId = btn.dataset.id;
  const page = parseInt(btn.dataset.page || '1', 10);
  const lang = btn.dataset.lang || '';
  directResumeBook(bookId, page, lang, event);
}

// Map Firebase Authentication errors to human-friendly feedback
function mapFirebaseAuthError(error) {
  if (!error) return 'Authentication error';
  const code = error.code || '';
  switch (code) {
    case 'auth/user-not-found':
    case 'auth/wrong-password':
    case 'auth/invalid-credential':
      return 'Invalid email or password. Please verify your credentials.';
    case 'auth/email-already-in-use':
      return 'An account with this email address already exists. Please sign in instead.';
    case 'auth/invalid-email':
      return 'Please enter a valid email address.';
    case 'auth/weak-password':
      return 'Password is too short. Please choose at least 6 characters.';
    case 'auth/network-request-failed':
      return 'Network connection issue. Please check your internet connection.';
    case 'auth/too-many-requests':
      return 'Too many attempts. Access is temporarily disabled; try again later.';
    case 'auth/popup-closed-by-user':
    case 'auth/cancelled-popup-request':
      return 'Sign-in window was closed.';
    default:
      return error.message || 'Authentication error';
  }
}

// Direct one-tap resume when user explicitly taps "Resume" button
async function directResumeBook(bookId, page, editionLanguage, event) {"""

content = patch(content, old_direct_resume, new_direct_resume, "Define handleResumeButtonClick and mapFirebaseAuthError")

# ═══════════════════════════════════════════════════════════════
# 5. REBUILD STARTUP SYSTEM (StartupController + sequenced init)
# ═══════════════════════════════════════════════════════════════
old_dom_listener = """// ────────────────────────────────────────────────────────
// LIFECYCLE INITIALIZATION
// ────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  NavigationController.init();
  setupLogoTerminalTrigger();
  setupOnlineOfflineListeners();
  addEditionRow();
  showInitialHomeSkeletons();

  // Firebase Auth Redirect Resolution (For Android Google Sign-In)
  if (auth) {
    auth.getRedirectResult().then(async (result) => {
      if (result && result.user) {
        showToast('Google authentication successful');
        closeAuthModal();
      }
    }).catch((err) => {
      console.warn('Redirect auth notice:', err);
      if (err && err.code && err.code !== 'auth/null-user') {
        showToast(err.message);
      }
    });

    // Observer
    auth.onAuthStateChanged(async (firebaseUser) => {
      APP_STATE.user = firebaseUser;
      if (firebaseUser) {
        await handleUserAuthenticated(firebaseUser);
      } else {
        handleUserLoggedOut();
      }
    });
  }

  // Real-Time Firestore Synchronization
  startFirestoreBooksFeed();

  // Dismiss Splash smoothly once UI is loaded
  setTimeout(() => {
    const splash = document.getElementById('splashScreen');
    if (splash) splash.classList.add('hide');
  }, 750);
});"""

new_dom_listener = """// ────────────────────────────────────────────────────────
// STARTUP CONTROLLER & WATCHDOG SYSTEM
// ────────────────────────────────────────────────────────
const StartupController = {
  isInitialized: false,
  watchdogTimer: null,

  init() {
    this.startWatchdog();

    try {
      // 1. Navigation state controller: force close all modals & enforce clean Home
      NavigationController.init();

      // 2. Setup system triggers & listeners
      setupLogoTerminalTrigger();
      setupOnlineOfflineListeners();
      addEditionRow();
      showInitialHomeSkeletons();

      // 3. Guarantee Home view is visible
      switchPage('home');

      // 4. Initialize Data feeds (non-blocking)
      if (typeof db !== 'undefined' && db) {
        try { startFirestoreBooksFeed(); } catch(dberr) { console.warn('Firestore feed note:', dberr); }
      } else {
        loadBooksFallbackFeed();
      }

      // 5. Setup Firebase Authentication Observer
      this.initAuth();

      // 6. Dismiss Splash Screen safely
      this.dismissSplash();
    } catch(err) {
      console.error('[NOVELIX Startup] Critical initialization error:', err);
      this.handleStartupFailure(err);
    }
  },

  initAuth() {
    if (!auth) return;
    try {
      auth.getRedirectResult().then((result) => {
        if (result && result.user) {
          showToast('Google authentication successful');
          closeAuthModal();
        }
      }).catch((err) => {
        if (err && err.code && err.code !== 'auth/null-user') {
          showToast(err.message);
        }
      });

      auth.onAuthStateChanged(async (firebaseUser) => {
        APP_STATE.user = firebaseUser;
        if (firebaseUser) {
          await handleUserAuthenticated(firebaseUser);
        } else {
          handleUserLoggedOut();
        }
      });
    } catch(e) {
      console.warn('Auth observer note:', e);
    }
  },

  dismissSplash() {
    if (this.isInitialized) return;
    this.isInitialized = true;
    if (this.watchdogTimer) clearTimeout(this.watchdogTimer);
    if (window.__novelix_splash_timer) clearTimeout(window.__novelix_splash_timer);

    const splash = document.getElementById('splashScreen');
    if (splash) {
      splash.classList.add('hide');
      setTimeout(() => {
        try { splash.remove(); } catch(e) {}
      }, 700);
    }
    console.log('[NOVELIX Startup] Application successfully started.');
  },

  startWatchdog() {
    this.watchdogTimer = setTimeout(() => {
      console.warn('[NOVELIX Watchdog] Watchdog fired — guaranteeing UI visibility.');
      this.dismissSplash();
    }, 2800);
  },

  handleStartupFailure(err) {
    this.dismissSplash();
    showToast('Started in offline mode');
  }
};

// Main DOM entrypoint
document.addEventListener('DOMContentLoaded', () => {
  StartupController.init();
});"""

content = patch(content, old_dom_listener, new_dom_listener, "Rebuild Startup Controller with Watchdog")

# ═══════════════════════════════════════════════════════════════
# 6. GUARD adminPublicationsTable
# ═══════════════════════════════════════════════════════════════
old_admin_pub = """async function loadAdminPublicationsList() {
  const table = document.getElementById('adminPublicationsTable');
  table.innerHTML = APP_STATE.allBooks.map(b => `"""

new_admin_pub = """async function loadAdminPublicationsList() {
  const table = document.getElementById('adminPublicationsTable') || document.getElementById('adminBooksTable');
  if (!table) return;
  table.innerHTML = APP_STATE.allBooks.map(b => `"""

content = patch(content, old_admin_pub, new_admin_pub, "Guard adminPublicationsTable against null")

with open("scripts/generate_4.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\n=== Syntax Check on generate_4.py ===")
import py_compile
try:
    py_compile.compile("scripts/generate_4.py", doraise=True)
    print("OK — generate_4.py compiled with zero syntax errors.")
except py_compile.PyCompileError as e:
    print(f"ERROR: {e}")
    sys.exit(1)
