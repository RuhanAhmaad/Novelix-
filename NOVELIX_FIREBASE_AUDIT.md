# NOVELIX 8.0 — Firebase & Data Integrity Audit Report

**Generated:** 2026-11-09  
**Firebase Project:** `novelxa-48f15`  
**Database:** Cloud Firestore (`us-central1`)  
**Storage Bucket:** `novelxa-48f15.firebasestorage.app`

---

## 1. Firebase Service Availability & Defensive Initialization

To prevent initialization crashes when offline or when CDN scripts are delayed, all Firebase services are instantiated with runtime function checks:

```javascript
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
  }
} catch(err) {
  console.warn('[NOVELIX] Firebase init warning:', err);
}
```

---

## 2. Firestore Collections & Schema Integrity

All existing production records are strictly preserved without alteration or destructive overwrites:

| Collection | Path | Record Purpose | Security Rules Enforcement |
|---|---|---|---|
| `books` | `/books/{bookId}` | Published manuscripts, editions, view counts | Public read if published; author write only |
| `users` | `/users/{uid}` | User profiles, handles, verification status | Public read; owner write only |
| `reading_progress` | `/users/{uid}/reading_progress/{bookId}` | Current page, total pages, last read | Owner read and write only |
| `bookmarks` | `/users/{uid}/bookmarks/{bookId}` | Saved books | Owner read and write only |
| `drive_accounts` | `/users/{uid}/drive_accounts/{accountId}` | Encrypted Google Drive tokens | Server-side Cloud Function only |
| `admin_users` | `/admin_users/{uid}` | Configured administrators | Server-side Cloud Function only |
| `admin_logs` | `/admin_logs/{logId}` | Tamper-evident admin audit trail | Append-only server-side write |

---

## 3. Storage Architecture

All media assets are stored exclusively in authenticated Google Cloud Storage via Firebase Storage:
- **Book Covers:** `covers/{bookId}/{timestamp}.jpg`
- **User Avatars:** `avatars/{uid}/{timestamp}.jpg`
- **Manuscripts (PDF):** `books/{bookId}/pdfs/{language}_{timestamp}.pdf`

Expired download URLs are automatically refreshed on the client using `storage.ref(edition.storagePath).getDownloadURL()`.
