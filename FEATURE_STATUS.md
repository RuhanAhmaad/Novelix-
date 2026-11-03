# NOVELIX 2.2 — Feature Status

> Release: NOVELIX 2.2 (Firebase Cloud Engine)  
> Project ID: `novelxa-48f15`  
> Android Package: `com.novelix.app`  
> Updated: 2026-11-03

---

## Status Legend

| Status | Definition |
|---|---|
| ✅ VERIFIED | Feature implemented, connected to Firebase, tested, and verified |
| 🟢 IMPLEMENTED | Code is written and connected to Firebase services |
| 🟡 IN PROGRESS | Partial implementation or integration underway |
| ⚙️ CONFIGURATION REQUIRED | Requires one-time setup in Google Cloud / Firebase Console |
| 🔴 NOT STARTED | Planned for future release |

---

## 1. Firebase Authentication

| Feature | Status | Implementation Details |
|---|---|---|
| Email/Password Registration | 🟢 IMPLEMENTED | `auth.createUserWithEmailAndPassword()` + initial Firestore profile document |
| Email/Password Login | 🟢 IMPLEMENTED | `auth.signInWithEmailAndPassword()` + real error reporting |
| Google Sign-In | 🟢 IMPLEMENTED | `auth.signInWithPopup(GoogleAuthProvider)` with redirect fallback |
| Password Reset | 🟢 IMPLEMENTED | `auth.sendPasswordResetEmail()` sends email from Firebase Auth |
| Email Verification | 🟢 IMPLEMENTED | `user.sendEmailVerification()` |
| Session Persistence | ✅ VERIFIED | LocalStorage + IndexedDB native Firebase session management |
| Real-time Auth Observer | ✅ VERIFIED | `auth.onAuthStateChanged()` dynamically toggles UI state |
| Account Sign-Out | ✅ VERIFIED | `auth.signOut()` safely cleans active session |

---

## 2. Cloud Firestore Real-Time Database

| Feature | Status | Implementation Details |
|---|---|---|
| Real-Time Books Listener | ✅ VERIFIED | `db.collection('books').onSnapshot()` synchronizes across all devices without refresh |
| Real-Time Notification Stream | 🟢 IMPLEMENTED | `users/{uid}/notifications` real-time listener |
| Real-Time Reviews Stream | 🟢 IMPLEMENTED | `books/{id}/reviews` real-time listener inside detail modal |
| Offline Persistence | ✅ VERIFIED | `db.enablePersistence({ synchronizeTabs: true })` |
| View Count Tracking | 🟢 IMPLEMENTED | Atomic increment `FieldValue.increment(1)` on open |
| Like System | 🟢 IMPLEMENTED | Document existence in `users/{uid}/likes` + book counter update |
| Bookmark System | 🟢 IMPLEMENTED | `users/{uid}/bookmarks` cloud synchronization |
| Reading Progress | 🟢 IMPLEMENTED | `users/{uid}/reading_progress` saves page number and timestamp |

---

## 3. Firebase Storage

| Feature | Status | Implementation Details |
|---|---|---|
| Cover Upload | 🟢 IMPLEMENTED | `storage.ref('covers/{bookId}/...')` + ImgBB fallback |
| PDF Document Upload | 🟢 IMPLEMENTED | `storage.ref('books/{bookId}/pdfs/...')` |
| Avatar & Banner Upload | 🟢 IMPLEMENTED | `storage.ref('avatars/{uid}/...')` and `storage.ref('banners/{uid}/...')` |
| MIME Type & Size Validation | ✅ VERIFIED | Enforced in `storage.rules` (PDF <= 50MB, Images <= 10MB) |

---

## 4. Reading Systems

| Feature | Status | Implementation Details |
|---|---|---|
| PDF.js Cloud Reader | ✅ VERIFIED | Loads directly from Firebase Storage download URL, zoom controls, page range input |
| Manhwa Vertical Reader | 🟢 IMPLEMENTED | Fullscreen image viewer with chapter navigation & PDF fallback |
| Reading Progress Restore | 🟢 IMPLEMENTED | Resumes last read page stored in Firestore |
| Language Edition Selector | 🟢 IMPLEMENTED | Switch between multi-language PDFs without duplicating publication records |

---

## 5. Administration & Developer Tools

| Feature | Status | Implementation Details |
|---|---|---|
| 5-Click Retro Terminal | ✅ VERIFIED | Activated by tapping NOVELIX logo 5 times within 2 seconds |
| Terminal Diagnostics | ✅ VERIFIED | `status`, `db`, `storage`, `user`, `books`, `version` |
| Role-Gated Admin Panel | 🟢 IMPLEMENTED | Verified against custom claim `request.auth.token.admin` and `admin_users` collection |
| Publication Moderation | 🟢 IMPLEMENTED | Admin can delete/approve publications directly from Firestore |

---

## 6. Google Drive Integration

| Feature | Status | Implementation Details |
|---|---|---|
| Drive Accounts Schema | 🟢 IMPLEMENTED | `users/{uid}/drive_accounts` collection |
| Google Drive OAuth Flow | ⚙️ CONFIGURATION REQUIRED | Requires Google Cloud Console OAuth 2.0 Web Client credentials with Drive scopes |
| Disconnect Drive Account | 🟢 IMPLEMENTED | Cloud document deletion |

---

## 7. Android Application & Build

| Feature | Status | Implementation Details |
|---|---|---|
| `google-services.json` Placement | ✅ VERIFIED | Placed in `android/app/google-services.json` |
| Google Services Gradle Plugin | ✅ VERIFIED | Applied in `android/app/build.gradle` and root `build.gradle` |
| Firebase Android BoM | ✅ VERIFIED | BoM `33.9.0` with Analytics, Auth, Firestore, Storage, Messaging |
| Android Permissions | ✅ VERIFIED | Internet, Storage, Camera, Notifications in `AndroidManifest.xml` |
| GitHub Actions CI Pipeline | ✅ VERIFIED | Automated compilation with Java 21 & Node 22 |
