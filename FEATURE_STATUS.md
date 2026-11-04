# NOVELIX 4.0 — Feature Status

Generated: 2026-11-04

---

## Feature Completion Overview

| Feature | Status | Notes |
|---------|--------|-------|
| Settings button (profile + nav) | ✅ Done | Gear icon in header + profile page |
| Settings modal — Account tab | ✅ Done | Edit profile, change password, delete account, logout |
| Settings modal — Drive tab | ✅ Done | Connect/disconnect Drive accounts, browse files |
| Settings modal — Storage tab | ✅ Done | Real-time quota meter, used/remaining display |
| Settings modal — Notifications tab | ✅ Done | Per-type notification toggles saved to Firestore |
| Settings modal — Appearance tab | ✅ Done | Font size, reading mode preferences |
| Settings modal — About tab | ✅ Done | App version, links, legal |
| Real-time storage quota meter | ✅ Done | Computed by Cloud Function, displayed in settings + publish form |
| Quota enforcement on publish | ✅ Done | Publish button disabled when over quota |
| Google Drive OAuth (multi-account) | ✅ Done | GIS Token Client, up to N accounts |
| Drive file picker modal | ✅ Done | Browse, search, select PDF/EPUB |
| Creator verification request | ✅ Done | Modal with reason + social links |
| Creator verification admin review | ✅ Done | Admin dashboard verifications tab |
| Verification badge (creator) | ✅ Done | Purple checkmark on verified creator profiles |
| Verification badge (email) | ✅ Done | Blue checkmark when Firebase emailVerified |
| FCM push notifications | ✅ Done | New chapter + follow + announcement |
| Notification preferences | ✅ Done | Per-type toggles in settings |
| FCM token registration | ✅ Done | Saved to `users/{uid}/fcm_tokens/` |
| Notification center | ✅ Done | Real-time, mark-read, delete |
| Profile redesign — 5 stats | ✅ Done | Books, Followers, Following, Reviews, Reads |
| Profile redesign — 4 tabs | ✅ Done | Published, Reading List, Bookmarks, Reviews |
| Profile edit modal | ✅ Done | Avatar, name, bio, social links |
| Verification banner on profile | ✅ Done | Shows when creator verified |
| ImgBB avatar upload | ✅ Done | Primary: ImgBB API; Fallback: Firebase Storage |
| Admin dashboard | ✅ Done | 5-click logo + `admin` terminal command |
| Admin: Users tab | ✅ Done | Search, stats, grant/revoke admin |
| Admin: Verifications tab | ✅ Done | Pending queue, approve/reject with note |
| Admin: Publications tab | ✅ Done | All books, force-remove |
| Admin: Storage tab | ✅ Done | Top consumers, adjust quotas |
| Admin: Announcements tab | ✅ Done | Compose + broadcast FCM |
| Admin: Audit Logs tab | ✅ Done | Paginated audit trail |
| Auth UI redesign | ✅ Done | Show/hide password, confirm password, terms checkbox |
| Animated splash screen | ✅ Done (3.0) | Logo + tagline fade-in |
| Premium dark editorial theme | ✅ Done (3.0) | #0B0B10 background, violet accents |
| PDF.js reader | ✅ Preserved | Full PDF viewer with page navigation |
| Manhwa/image reader | ✅ Preserved | Chapter-based image reader |
| Publishing studio | ✅ Preserved | Multi-language upload form |
| Library + bookmarks | ✅ Preserved | Real-time Firestore backed |
| Explore / browse page | ✅ Preserved | Genre filter, search |
| Retro terminal | ✅ Preserved | 5-click trigger, `help`, `clear`, `about`, `stats`, `admin` |
| Email/password auth | ✅ Done | Firebase Auth |
| Google Sign-In (Android) | ✅ Done | signInWithRedirect + getRedirectResult |
| Password reset | ✅ Done | sendPasswordResetEmail |
| Email verification | ✅ Done | sendEmailVerification |

---

## Known Issues & Limitations

| Issue | Severity | Plan |
|-------|---------|------|
| Drive access tokens expire in ~1 hour | Medium | Phase 2: server-side refresh tokens |
| ImgBB key exposed in frontend | Medium | Phase 2: Cloud Function proxy |
| FCM background notifications require native plugin | Low | Install @capacitor/push-notifications |
| Storage quota uses 2 MB estimate for untracked files | Low | Enforce fileSize on all uploads |
| No FCM rate limiting on broadcast | Low | Add App Check + rate limiting |

---

## Version History

| Version | Date | Key Changes |
|---------|------|------------|
| 1.0 | Initial | Basic reading app |
| 2.0 | — | Supabase backend, publishing, PDF reader |
| 2.2 | — | Firebase migration (Auth, Firestore, Storage) |
| 3.0 | 2026-11-03 | Premium UI redesign, editorial theme, Google Auth on Android |
| 4.0 | 2026-11-04 | Settings, Drive, storage meter, verification, admin dashboard, notifications |

---

## APK Build Status

| Build | Status | Location |
|-------|--------|----------|
| NOVELIX 3.0 | ✅ Success (CI run 41694760855) | novelix.apk + /sdcard/Download/ |
| NOVELIX 4.0 | 🔄 Pending push → CI build | Will be at novelix.apk after CI completes |

---

## Files Changed in 4.0

| File | Change |
|------|--------|
| `out/index.html` | Complete NOVELIX 4.0 SPA (3326 lines, 163 KB) |
| `android/app/src/main/assets/public/index.html` | Synced from out/ |
| `functions/index.js` | 7 Cloud Functions (complete rewrite) |
| `firestore.rules` | Added verification, announcements, fcm_tokens rules |
| `storage.rules` | Added verifications path, raised file size limits |
| `firestore.indexes.json` | Added 2 composite indexes |
| `FIREBASE_FEATURES_REPORT.md` | New documentation |
| `GOOGLE_DRIVE_SETUP.md` | New documentation |
| `NOTIFICATION_SETUP.md` | New documentation |
| `ADMIN_SECURITY_REPORT.md` | New documentation |
| `FEATURE_STATUS.md` | This file |
