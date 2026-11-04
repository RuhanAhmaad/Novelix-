# NOVELIX — 404 "Page Not Found" Root Cause & Resolution Report

**Project:** NOVELIX (Android Capacitor & Firebase)  
**Firebase Project:** `novelxa-48f15`  
**Date:** November 4, 2026  
**Status:** Root Cause Identified & Resolved in Source Code; Deployment Procedures Documented  

---

## 1. Executive Summary

When attempting to connect Google Drive from within the NOVELIX Android application, users were presented with the following verbatim browser error:

```html
<h1>Error: Page not found</h1>
<h2>The requested URL was not found on this server.</h2>
```

A comprehensive investigation into the frontend routing, Firebase Hosting rules, Cloud Function HTTP endpoints, Capacitor deep-link schemes, and Google OAuth configurations was conducted. The exact broken endpoint was verified using direct HTTP probes.

---

## 2. Exact Broken URL & Server Response

### The Exact URL
```text
https://us-central1-novelxa-48f15.cloudfunctions.net/googleDriveCallback
```
*(and companion endpoint: `https://us-central1-novelxa-48f15.cloudfunctions.net/googleDriveAuth`)*

### Live Probe Verification (via curl)
```http
HTTP/2 404 
content-length: 272
content-type: text/html; charset=UTF-8
date: Wed, 04 Nov 2026 12:57:51 GMT
alt-svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000

<html><head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<title>404 Page not found</title>
</head>
<body text=#000000 bgcolor=#ffffff>
<h1>Error: Page not found</h1>
<h2>The requested URL was not found on this server.</h2>
<h2></h2>
</body></html>
```

The HTML returned by Google's Cloud Functions gateway matches the error message verbatim.

---

## 3. Investigation Checklist & Findings

| # | Investigation Area | Inspection Result | Status |
|---|-------------------|-------------------|--------|
| 1 | **Frontend Routes & Links** | Navigation previously lacked a fallback catch-all for undefined route IDs in `switchPage()`. If an unknown ID was requested, no view was activated. | **Fixed:** Added `#page-notfound` catch-all view with Return to Home & Explore buttons. |
| 2 | **Firebase Hosting (`firebase.json`)** | `public: "out"`, rewrite rules rewrite `**` to `/index.html`, and `/api/drive/*` rewrites to Cloud Functions. Hosting configuration is syntactically correct. | **Verified Correct** |
| 3 | **Cloud Functions Endpoints** | All 17 Cloud Functions are declared and exported in `functions/index.js` (`startGoogleDriveOAuth`, `googleDriveCallback`, etc.). However, they had not yet been deployed to the GCP project gateway. | **Pending CLI Deploy** |
| 4 | **OAuth Initiation & Callback** | Authorization code URL uses `CANONICAL_DRIVE_REDIRECT_URI` matching Google Cloud Console. Callback exchanges code for tokens, encrypts tokens via AES-256-GCM, and redirects to `novelix://drive-callback`. | **Fixed & Hardened** |
| 5 | **Redirect URLs & Deep Links** | `AndroidManifest.xml` has intent filter for `novelix://` scheme. Deep link handler in JS parses `novelix://drive-callback?status=success&email=...` and refreshes account list. | **Verified Correct** |
| 6 | **HTTP Methods & Parameters** | `googleDriveCallback` accepts `GET` requests with `code` and `state`. Error validation handles missing parameters with styled HTML responses. | **Verified Correct** |
| 7 | **Capacitor Android Config** | Capacitor loads bundled local assets from `file:///android_asset/public/index.html`. System browser `window.open(url, '_system')` launches native browser. | **Verified Correct** |
| 8 | **Backend Scoping Bug** | In `functions/index.js`, `sessionRef` was declared inside a `try` block but referenced again at the end of the callback, which would trigger a `ReferenceError` post-deployment. | **Fixed:** Hoisted `sessionRef` and guarded duplicate deletion. |

---

## 4. Root Causes

### Primary Root Cause: Cloud Functions Deployment Pending
The Cloud Functions code exists in `functions/index.js` with all 17 exports correctly written, but because the Firebase CLI was not authenticated on this Termux environment, the functions have not been deployed to Google Cloud (`us-central1-novelxa-48f15.cloudfunctions.net`). Hence, Google's Cloud gateway returns 404 for any incoming request to `googleDriveCallback` and `googleDriveAuth`.

### Secondary Root Cause: Frontend Unhandled Route State
In `switchPage(pageId)`, if any link or hash navigated to an unrecognized page identifier, the app cleared active classes without activating any target, causing a blank screen or broken UI.

### Tertiary Root Cause: Backend Scope Bug in Callback
In `functions/index.js`, line 643 called `await sessionRef.delete()` where `sessionRef` was scoped only to lines 531-540. Once deployed, this would have resulted in an uncaught `ReferenceError: sessionRef is not defined`, crashing the token exchange flow.

---

## 5. Changes Made & Code Fixes

1. **`functions/index.js`**:
   - Hoisted `sessionRef = null;` to outer scope.
   - Guarded duplicate cleanup: `if (sessionRef) { try { await sessionRef.delete(); } catch(e) {} }`.
   - Verified clean syntax: `node --check functions/index.js` passes with zero errors.

2. **`scripts/generate_4.py` & `out/index.html`**:
   - Added `#page-notfound` dedicated view in the HTML container.
   - Updated `switchPage(pageId)` to catch any unrecognized route and gracefully display the `#page-notfound` screen with working "Back to Home" and "Explore Catalog" actions.
   - Added comprehensive `ERROR_CATALOG` and `showGlobalError()` modal.
   - Replaced raw error strings with user-friendly descriptions.

3. **Android Assets**:
   - Synced regenerated `out/index.html` directly to `android/app/src/main/assets/public/index.html`.

4. **Project Configuration (`.firebaserc`)**:
   - Created `.firebaserc` pointing `default` project to `novelxa-48f15`.

---

## 6. Steps to Deploy Cloud Functions

Because Firebase CLI authentication requires interactive user login via Google OAuth, run the following in Termux:

```bash
# Step 1: Log in to Firebase CLI interactively
FIREBASE_BIN=$(find /data/user/0/com.termux/files/home/.cache/pnpm -name "firebase" -type f | head -1)
$FIREBASE_BIN login --no-localhost

# Step 2: Set Secret Manager credential for Google Drive
cd "/data/user/0/com.termux/files/home/Novelix project"
$FIREBASE_BIN functions:secrets:set GOOGLE_DRIVE_OAUTH_CLIENT_JSON --project novelxa-48f15

# Step 3: Deploy Functions and Hosting
$FIREBASE_BIN deploy --only functions,hosting --project novelxa-48f15
```

Once deployed, `curl -i "https://us-central1-novelxa-48f15.cloudfunctions.net/googleDriveCallback"` will return HTTP 400 (Missing authorization code parameter) instead of HTTP 404, proving the endpoint is live and responding.
