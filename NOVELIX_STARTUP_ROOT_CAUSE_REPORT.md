# NOVELIX 8.0 — Startup & Splash Screen Root Cause Report

**Generated:** 2026-11-09  
**Platform:** Capacitor Android (`com.novelix.app`)  
**Firebase App:** `novelxa-48f15`  
**Primary Affected Component:** Application Lifecycle, Splash Screen & Embedded JavaScript

---

## 1. Executive Summary

In NOVELIX 7.0, an issue occurred on app launch where the custom HTML splash screen remained permanently displayed on screen, rendering the entire interface unreachable. 

Decompilation and syntax analysis with `node --check` revealed that a JavaScript `SyntaxError` existed inside the main script block. Because JavaScript engines halt script execution upon encountering a parse-time syntax error, the `DOMContentLoaded` event listener inside the script was never registered. Consequently, the splash dismissal function never executed, trapping the user on the splash screen indefinitely.

---

## 2. Exact Original Syntax Error

### Location
`scripts/generate_4.py`, line 4641 (and compiled `out/index.html` line 4639).

### Problematic Token
```javascript
<button onclick="directResumeBook('${escapeHtml(item.id)}', ${item.page || 1}, '${escapeHtml(item.selectedEditionLanguage || \'\')}', event)" class="btn-primary ...">Resume</button>
```

### Analysis of the Failure
Inside the JavaScript template literal:
```javascript
${escapeHtml(item.selectedEditionLanguage || \'\')}
```
The escape sequences `\'\'` inside the template substitution `${...}` were invalid in the JavaScript lexical grammar. When Node.js and the Android Chrome WebView parsed this line:
```
SyntaxError: Invalid or unexpected token
    at wrapSafe (node:internal/modules/cjs/loader:1876:18)
    at checkSyntax (node:internal/main/check_syntax:76:3)
```

Because this error occurred during script parsing, the entire 163 KB application script was rejected by the engine before any code executed.

---

## 3. Duplicate Variable Declaration Syntax Error

During syntax auditing with `node --check`, a second parse-time error was identified in `loadPdfDocumentForReader()`:
```
SyntaxError: Identifier 'errorOverlay' has already been declared
SyntaxError: Identifier 'reconnectDriveBtn' has already been declared
```
Declarations using `const` were duplicated inside the function scope, which throws an unrecoverable `SyntaxError` in ES6+.

---

## 4. Rebuilt Startup Architecture

To guarantee the application can never be trapped on an endless splash screen, NOVELIX 8.0 replaces the timer-based startup with a multi-layered watchdog architecture:

```
                  ┌──────────────────────────────┐
                  │ Android App / WebView Launch │
                  └──────────────┬───────────────┘
                                 │
                     ┌───────────▼───────────┐
                     │ HTML Entry Point Load │
                     └───────────┬───────────┘
                                 │
         ┌───────────────────────┴───────────────────────┐
         │                                               │
┌────────▼─────────────────────────┐          ┌──────────▼───────────────┐
│ Inline Emergency Watchdog Timer  │          │ Main StartupController   │
│ (Executes in <head> & <body>)    │          │ - NavigationController   │
│ - Sets 3.2s fail-safe timeout    │          │ - switchPage('home')     │
│ - Force-dismisses splash screen  │          │ - startFirestoreBooksFeed│
│   if JS or network hangs         │          │ - Safe splash dismiss    │
└──────────────────────────────────┘          └──────────────────────────┘
```

### Layer 1: Inline Emergency Watchdog
Immediately following the `#splashScreen` markup in the HTML DOM:
```html
<script>
  window.__novelix_emergency_timer = setTimeout(function() {
    var sp = document.getElementById('splashScreen');
    if (sp && !sp.classList.contains('hide')) {
      sp.classList.add('hide');
      console.warn('[NOVELIX Watchdog] Emergency splash dismiss triggered.');
    }
  }, 3200);
</script>
```
If the network drops, remote CDNs fail, or any unexpected script error occurs, this independent inline watchdog forces the splash screen to dismiss within 3.2 seconds.

### Layer 2: Sequenced Startup Controller
The application lifecycle is orchestrated by `StartupController.init()`:
1. Starts the watchdog timer.
2. Invokes `NavigationController.init()` to force-close all modals and reset body scroll locks.
3. Activates `switchPage('home')` to ensure Home is the guaranteed active screen.
4. Starts non-blocking real-time data feeds (`startFirestoreBooksFeed`).
5. Initializes Firebase Auth observers without blocking UI rendering.
6. Dismisses the splash screen smoothly with hardware-accelerated transitions.

---

## 5. Verification

1. **Syntax Validation:** All 4 inline script blocks extracted from `out/index.html` were audited with `node --check` and passed with zero errors:
   - `check_script_0.js`: 168 bytes — ✅ PASSED
   - `check_script_1.js`: 686 bytes — ✅ PASSED
   - `check_script_2.js`: 394 bytes — ✅ PASSED
   - `check_script_3.js`: 167,706 bytes — ✅ PASSED
2. **Offline Simulation:** Verified that if network is disconnected or Firebase is unreachable, `StartupController` catches the error, dismisses the splash, and displays Home with offline fallback cards.
