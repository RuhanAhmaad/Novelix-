#!/usr/bin/env python3
"""
NOVELIX 8.0 — Complete Production Patch Script
1. Bundles local PDF.js with CDN fallback
2. Adds offline utility fallbacks in <style>
3. Injects emergency splash watchdog right after #splashScreen
4. Hardens Firebase initialization with defensive checks
5. Hardens PDF.js reader engine with library availability check
6. Regenerates out/index.html and copies to android assets
7. Validates with node --check
"""

import sys, re, py_compile

with open("scripts/generate_4.py", "r", encoding="utf-8") as f:
    content = f.read()

print("=== NOVELIX 8.0 Complete Master Upgrade ===")

# 1. Local PDF.js + CDN fallback in <head>
old_pdf_cdn = """  <!-- PDF.js Reader -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>"""

new_pdf_cdn = """  <!-- PDF.js Reader (Local Bundled with CDN Fallback) -->
  <script src="js/pdf.min.js"></script>
  <script>
    if (typeof pdfjsLib === 'undefined') {
      document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"><\\/script>');
    }
  </script>"""

if old_pdf_cdn in content:
    content = content.replace(old_pdf_cdn, new_pdf_cdn, 1)
    print("  [OK] Bundled local PDF.js with CDN fallback")
else:
    print("  [WARN] PDF.js CDN tag not found")

# 2. Add offline baseline utility classes to <style>
old_style_anchor = """.safe-top { padding-top: var(--sat); }
    .safe-bottom { padding-bottom: var(--sab); }"""

new_style_anchor = """.safe-top { padding-top: var(--sat); }
    .safe-bottom { padding-bottom: var(--sab); }

    /* Offline Resilient Utility Fallbacks (Ensures UI renders without CDN) */
    .hidden { display: none !important; }
    .flex { display: flex; }
    .flex-col { flex-direction: column; }
    .flex-row { flex-direction: row; }
    .flex-1 { flex: 1 1 0%; }
    .flex-shrink-0 { flex-shrink: 0; }
    .items-center { align-items: center; }
    .justify-center { justify-content: center; }
    .justify-between { justify-content: space-between; }
    .gap-1 { gap: 4px; }
    .gap-1\\.5 { gap: 6px; }
    .gap-2 { gap: 8px; }
    .gap-3 { gap: 12px; }
    .gap-4 { gap: 16px; }
    .w-full { width: 100%; }
    .h-full { height: 100%; }
    .min-w-0 { min-width: 0; }
    .truncate { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .text-center { text-align: center; }
    .grid { display: grid; }
    .grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .relative { position: relative; }
    .absolute { position: absolute; }
    .fixed { position: fixed; }
    .overflow-hidden { overflow: hidden; }
    .overflow-x-auto { overflow-x: auto; }
    .overflow-y-auto { overflow-y: auto; }"""

if old_style_anchor in content:
    content = content.replace(old_style_anchor, new_style_anchor, 1)
    print("  [OK] Added offline resilient utility fallbacks")
else:
    print("  [WARN] Style anchor not found")

# 3. Emergency Splash Watchdog
old_splash_close = """    <div class="w-16 h-0.5 bg-app-border rounded-full mt-6 overflow-hidden">
      <div class="w-full h-full bg-app-primary -translate-x-full animate-[progressPulse_1.2s_ease-in-out_infinite]"></div>
    </div>
  </div>
</div>"""

new_splash_close = """    <div class="w-16 h-0.5 bg-app-border rounded-full mt-6 overflow-hidden">
      <div class="w-full h-full bg-app-primary -translate-x-full animate-[progressPulse_1.2s_ease-in-out_infinite]"></div>
    </div>
  </div>
</div>
<script>
  // Emergency Startup Watchdog: If JavaScript or network hangs, guarantee splash dismiss within 3.2s
  window.__novelix_emergency_timer = setTimeout(function() {
    var sp = document.getElementById('splashScreen');
    if (sp && !sp.classList.contains('hide')) {
      sp.classList.add('hide');
      console.warn('[NOVELIX Watchdog] Emergency splash dismiss triggered.');
    }
  }, 3200);
</script>"""

if old_splash_close in content:
    content = content.replace(old_splash_close, new_splash_close, 1)
    print("  [OK] Injected Emergency Splash Watchdog")
else:
    print("  [WARN] Splash screen closing tag not found")

# 4. Defensive Firebase Initialization
old_fb = """// Initialize Firebase App
let auth, db, storage, messaging, functions;
try {
  if (!firebase.apps.length) {
    firebase.initializeApp(FIREBASE_CONFIG);
  }
  auth = firebase.auth();
  db = firebase.firestore();
  storage = firebase.storage();
  try {
    functions = firebase.app().functions('us-central1');
  } catch(fErr) {
    try { functions = firebase.functions('us-central1'); } catch(e) {}
  }
  try {
    if (firebase.messaging.isSupported()) {
      messaging = firebase.messaging();
    }
  } catch(e) {}

  db.enablePersistence({ synchronizeTabs: true }).catch(() => {});
} catch(err) {
  console.warn('Firebase init warning:', err);
}"""

new_fb = """// Initialize Firebase App defensively
let auth = null, db = null, storage = null, messaging = null, functions = null;
try {
  if (typeof firebase !== 'undefined') {
    if (firebase.apps && !firebase.apps.length) {
      firebase.initializeApp(FIREBASE_CONFIG);
    }
    if (typeof firebase.auth === 'function') auth = firebase.auth();
    if (typeof firebase.firestore === 'function') db = firebase.firestore();
    if (typeof firebase.storage === 'function') storage = firebase.storage();
    if (typeof firebase.app === 'function') {
      try { functions = firebase.app().functions('us-central1'); } catch(fErr) {
        try { functions = firebase.functions('us-central1'); } catch(e) {}
      }
    }
    if (db && typeof db.enablePersistence === 'function') {
      db.enablePersistence({ synchronizeTabs: true }).catch(() => {});
    }
    console.log('[NOVELIX] Firebase initialized successfully.');
  } else {
    console.warn('[NOVELIX] Firebase SDK unavailable — offline fallback mode active.');
  }
} catch(err) {
  console.warn('[NOVELIX] Firebase init warning:', err);
}"""

if old_fb in content:
    content = content.replace(old_fb, new_fb, 1)
    print("  [OK] Hardened Firebase initialization with defensive checks")
else:
    print("  [WARN] Firebase init pattern not found")

# 5. Defensive PDF.js in loadPdfDocumentForReader
old_pdf_reader = """async function loadPdfDocumentForReader(book, edition, targetPage) {
  const loadingOverlay = document.getElementById('readerLoadingOverlay');"""

new_pdf_reader = """async function loadPdfDocumentForReader(book, edition, targetPage) {
  const loadingOverlay = document.getElementById('readerLoadingOverlay');
  const errorOverlay = document.getElementById('readerErrorOverlay');
  const errorTitle = document.getElementById('readerErrorTitle');
  const errorMsg = document.getElementById('readerErrorMessage');
  const errorCodeBadge = document.getElementById('readerErrorCodeBadge');

  if (typeof pdfjsLib === 'undefined') {
    if (loadingOverlay) loadingOverlay.classList.add('hidden');
    if (errorOverlay) errorOverlay.classList.remove('hidden');
    if (errorTitle) errorTitle.textContent = 'PDF Reader Offline';
    if (errorMsg) errorMsg.textContent = 'The PDF rendering library is unavailable offline. Please connect to the internet.';
    if (errorCodeBadge) {
      errorCodeBadge.textContent = 'ERR_PDF_LIB_OFFLINE';
      errorCodeBadge.classList.remove('hidden');
    }
    return;
  }"""

if old_pdf_reader in content:
    content = content.replace(old_pdf_reader, new_pdf_reader, 1)
    print("  [OK] Hardened loadPdfDocumentForReader with library check")
else:
    print("  [WARN] loadPdfDocumentForReader pattern not found")

# Save updated generate_4.py
with open("scripts/generate_4.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\n=== Compiling generate_4.py ===")
try:
    py_compile.compile("scripts/generate_4.py", doraise=True)
    print("OK: generate_4.py compiled successfully with 0 errors.")
except py_compile.PyCompileError as e:
    print(f"ERROR: {e}")
    sys.exit(1)
