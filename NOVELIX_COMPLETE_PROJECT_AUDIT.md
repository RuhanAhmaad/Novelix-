# NOVELIX 7.0 — Complete Project Audit & APK Comparison

**Generated:** 2026-11-07  
**Firebase Project ID:** `novelxa-48f15`  
**Android Package ID:** `com.novelix.app`  
**Inspected APK:** `out/app-debug.apk` (and deployed `novelix.apk`, 9.30 MB)  
**Main Source:** `scripts/generate_4.py`, `out/index.html`, `android/app/src/main/assets/public/index.html`, `functions/index.js`, `capacitor.config.ts`

---

## Executive Summary

A comprehensive architectural inspection of the NOVELIX source code and the compiled Android APK was performed across all 17 functional domains. The application is built as a single-page hybrid application packaged via Capacitor 5.x for Android. 

The audit identified several critical areas:
1. **Startup Navigation & Modal Race Conditions:** Prior builds lacked an explicit initial reset sequence, allowing WebView state or DOM artifacts to trigger unexpected reader launches.
2. **Exposed Third-Party API Key:** An ImgBB API key (`a9985ccf572a0e05bce242e27cf8be33`) was hardcoded in client-side JavaScript.
3. **PDF.js Web Worker Cross-Origin Policy:** The PDF.js worker loaded from CDN causes cross-origin worker instantiation failures inside Android WebViews (`https://localhost`).
4. **Publishing Workflow Gaps:** Publication editing and unpublishing workflows were incomplete in the author profile.
5. **Fabricated Metrics & Fallbacks:** Fallback values (such as hardcoded `4.8` ratings) masked the absence of real Firestore reviews.

---

## 17-Domain Technical Audit

### 1. Application Startup and Lifecycle
- **Files/Functions:** `scripts/generate_4.py` (`DOMContentLoaded`, lines 2124–2163)
- **Root Cause:** App launch relied purely on static HTML class `active` on `#page-home` without programmatically resetting all fullscreen modals and body scroll locks. If the WebView process restored an existing session where `readerModal` had class `open`, the reader would appear on launch.
- **User-Visible Effect:** The application occasionally opened directly into the reader or a black modal instead of the Home screen.
- **Recommended Correction:** Implement a dedicated `NavigationStateController` that forces all modals closed, cleans up orphan render tasks, sets body overflow, and activates `switchPage('home')` on startup.
- **Requires Backend Deployment:** No.

### 2. HTML Entry Point & JavaScript Initialization
- **Files/Functions:** `scripts/generate_4.py`, `out/index.html`, `android/app/src/main/assets/public/index.html`
- **Root Cause:** Master application source is rendered as a standalone HTML file containing embedded styles and logic. Firebase SDK 10.14.1 compat scripts and Tailwind CDN are loaded in `<head>`.
- **User-Visible Effect:** Smooth initialization when network is available; potential CDN blocking if worker scripts load cross-origin.
- **Recommended Correction:** Standardize asset paths and ensure PDF.js uses single-thread mode (`disableWorker: true`) inside the WebView.
- **Requires Backend Deployment:** No.

### 3. All Navigation Routes
- **Files/Functions:** `switchPage(pageId)` (lines 5605–5631), `navigateTo(pageId)`
- **Root Cause:** Five primary tabs (`home`, `explore`, `library`, `publish`, `profile`) plus secondary pages (`drive`, `notfound`). Previous builds called `navigateTo('home')` from the library empty-state which was undefined until an alias was added.
- **User-Visible Effect:** Tapping certain buttons previously caused silent `TypeError: navigateTo is not a function`.
- **Recommended Correction:** Standardize navigation routing through a single `NavigationController` and register hardware back button support.
- **Requires Backend Deployment:** No.

### 4. Firebase Initialization
- **Files/Functions:** `scripts/generate_4.py` (lines 2060–2085)
- **Root Cause:** Standard compat initialization `firebase.initializeApp(FIREBASE_CONFIG)`. Services (`auth`, `db`, `storage`, `functions`, `messaging`) are instantiated within try-catch blocks. Region is correctly set to `us-central1`.
- **User-Visible Effect:** Stable cloud connectivity.
- **Recommended Correction:** Maintain explicit region definition and add fallback error states if Firebase fails to reach cloud endpoints.
- **Requires Backend Deployment:** No.

### 5. Authentication and Session Persistence
- **Files/Functions:** `executeGoogleAuth()`, `executeEmailLogin()`, `executeEmailRegister()`, `handleUserAuthenticated()`
- **Root Cause:** Google authentication uses `@codetrix-studio/capacitor-google-auth` on Android, returning an `idToken` passed to `firebase.auth.GoogleAuthProvider.credential()`. Email/password uses Firebase Auth with `LOCAL` persistence by default.
- **User-Visible Effect:** Persistent login across restarts.
- **Recommended Correction:** Maintain clean separation between Firebase Google Login (reader identity) and Google Drive OAuth (manuscript access).
- **Requires Backend Deployment:** No.

### 6. Firestore Collections and Document Structure
- **Files/Functions:** Collections: `books`, `users`, `users/{uid}/reading_progress`, `users/{uid}/bookmarks`, `users/{uid}/drive_accounts`, `admin_users`, `admin_logs`.
- **Root Cause:** Well-normalized document structures. Books support multi-language and multi-volume editions under the `languages` array.
- **User-Visible Effect:** Consistent metadata across views.
- **Recommended Correction:** Ensure queries handle missing fields gracefully without relying on hardcoded defaults.
- **Requires Backend Deployment:** No.

### 7. Firebase Storage
- **Files/Functions:** `uploadMediaFile()`, `storage.ref().put()`, `getDownloadURL()`
- **Root Cause:** Covers are uploaded to `covers/{bookId}/` and manuscripts to `books/{bookId}/pdfs/`.
- **User-Visible Effect:** Fast and reliable direct file upload to Google Cloud Storage infrastructure.
- **Recommended Correction:** Regenerate download URLs via `storage.ref(storagePath).getDownloadURL()` if token-based URLs expire.
- **Requires Backend Deployment:** Yes (Storage Security Rules update if permissions tighten).

### 8. Cloud Functions
- **Files/Functions:** `functions/index.js` (22 exported endpoints)
- **Root Cause:** Handles administrative claims (`verifyAdminStatus`, `setAdminRole`, `adminGetDashboardData`), Google Drive OAuth (`startGoogleDriveOAuth`, `googleDriveCallback`, `getReaderPdfData`), and triggers (`onDocumentWritten`).
- **User-Visible Effect:** Secure backend execution for sensitive token exchange.
- **Recommended Correction:** Keep all client secret handling in Secret Manager (`defineJsonSecret`).
- **Requires Backend Deployment:** Yes.

### 9. Google Drive OAuth
- **Files/Functions:** `initiateGoogleDriveConnection()`, `loadConnectedDriveAccounts()`, `browseDriveAccountFiles()`
- **Root Cause:** Authorization Code Flow redirecting to system browser, returning to app via `novelix://drive-callback` deep link. Cloud Function exchanges code for refresh token, stored encrypted with AES-256-GCM.
- **User-Visible Effect:** Allows authors to link one or more Google Drive accounts and publish manuscripts without exposing private tokens.
- **Recommended Correction:** Verify return deep-link handler ignores unrelated URLs and reloads connected accounts cleanly.
- **Requires Backend Deployment:** Yes.

### 10. PDF.js Reader
- **Files/Functions:** `loadPdfDocumentForReader()`, `renderPdfPage()`, `changeReaderPage()`, `zoomReader()`
- **Root Cause:** Web Worker instantiation failed inside Android WebView due to origin policy.
- **User-Visible Effect:** Black reader screen or worker timeout.
- **Recommended Correction:** Enforce `disableWorker: true`, cap device pixel ratio at 2.5 to prevent memory exhaustion, and cancel pending render tasks when changing pages.
- **Requires Backend Deployment:** No.

### 11. Book Publishing and Editing
- **Files/Functions:** `handlePublishSubmit()`, `addEditionRow()`, `openDrivePickerForPublish()`
- **Root Cause:** Initial version supported creation and deletion, but lacked an "Edit Publication" workflow to modify existing titles, descriptions, genres, and editions.
- **User-Visible Effect:** Authors had to delete and re-upload entire books to fix typos or add editions.
- **Recommended Correction:** Implement `openEditPublication(bookId)` and support drafting and unpublishing.
- **Requires Backend Deployment:** No.

### 12. Reading Progress and Bookmarks
- **Files/Functions:** `saveReadingProgressDebounced()`, `toggleReaderBookmark()`, `resumeReadingProgressBook()`
- **Root Cause:** Reading progress saved debounced, but previous versions risked saving against a stale `APP_STATE.selectedBook` if user navigated away quickly.
- **User-Visible Effect:** Progress could overwrite another book's record.
- **Recommended Correction:** Capture `bookId` and edition directly at invocation time.
- **Requires Backend Deployment:** No.

### 13. Notifications
- **Files/Functions:** `startNotificationsFeed()`, `openNotifModal()`
- **Root Cause:** Firestore listener on `users/{uid}/notifications`. Triggered by Cloud Functions on new reviews, chapters, and announcements.
- **User-Visible Effect:** Real-time bell badge and dropdown list.
- **Recommended Correction:** Add clear-all and mark-as-read operations.
- **Requires Backend Deployment:** No.

### 14. Profile and Social Features
- **Files/Functions:** `loadProfileContent()`, `switchProfileTab()`, `computeUserStats()`
- **Root Cause:** Profile tabs: Works, Library, Reviews, About. Computes real statistics from user's published books in Firestore.
- **User-Visible Effect:** Displays accurate works, chapter count, and cumulative read count.
- **Recommended Correction:** Remove hardcoded fallback avatar URLs and use authentic SVG initial fallbacks.
- **Requires Backend Deployment:** No.

### 15. Admin Panel and Security
- **Files/Functions:** `openAdminDashboard()`, `verifyAdminStatus`, `terminal` command `admin`
- **Root Cause:** Terminal `admin` command previously lacked server-side claim verification.
- **User-Visible Effect:** Anyone typing "admin" could attempt opening the panel.
- **Recommended Correction:** Enforce server-side custom claim verification via `getIdTokenResult(true)` (`claims.admin === true`).
- **Requires Backend Deployment:** Yes.

### 16. Capacitor Android Configuration
- **Files/Functions:** `capacitor.config.ts`, `android/app/src/main/AndroidManifest.xml`
- **Root Cause:** `androidScheme: "https"`, `server.cleartext: true`, package `com.novelix.app`. Deep links for `novelix://` and `https://novelix.app` are declared.
- **User-Visible Effect:** Correct scheme and deep-link routing.
- **Recommended Correction:** Maintain cleartext traffic and mixed content permissions for PDF previewing.
- **Requires Backend Deployment:** No.

### 17. External Dependencies and Performance
- **Files/Functions:** ImgBB API key in `generate_4.py`, CDN scripts for Tailwind and PDF.js.
- **Root Cause:** ImgBB API key (`a9985ccf572a0e05bce242e27cf8be33`) was hardcoded as a fallback image host.
- **User-Visible Effect:** Security vulnerability in APK binary decompilation.
- **Recommended Correction:** Completely eradicate hardcoded ImgBB key. Use Firebase Storage exclusively for all cover and avatar uploads.
- **Requires Backend Deployment:** No.

---

## Conclusion

The architecture is well-structured for hybrid mobile publishing, but required hardening against race conditions at startup, removal of exposed third-party keys, full implementation of author publication editing, and mobile touch gesture optimization in the PDF reader. All recommended corrections are addressed in subsequent phases.
