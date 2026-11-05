# NOVELIX 5.0 — Security & Token Protection Report

## 1. Executive Summary

Security is paramount in the NOVELIX 5.0 architecture. This report outlines the security posture, authentication barriers, token encryption protocols, authorization rules, and zero-trust policies implemented across the application, Firebase Cloud Functions, Firestore, and Google Drive integrations.

---

## 2. Key Security Principles & Implementation

### A. Zero Secret Exposure in the Android APK
- No OAuth Client Secrets, refresh tokens, or administrative credentials are built into the client APK or JavaScript assets.
- `functions/index.js` uses Google Cloud Secret Manager via `defineJsonSecret('GOOGLE_DRIVE_OAUTH_CLIENT_JSON')`.
- All OAuth code exchanges (`code` -> `tokens`) happen strictly on Google Cloud Functions endpoints.

### B. Two-Tier Google Drive Token Protection
1. **Public Metadata Collection:**
   `users/{uid}/drive_accounts/{accountId}` contains only non-sensitive metadata (Google email, name, avatar, account ID) readable by the account owner.
2. **Confidential Token Vault:**
   `users/{uid}/drive_secure_tokens/{accountId}` stores confidential tokens.
   - Access tokens and refresh tokens are encrypted using AES-256-CBC with an initialization vector before being written.
   - Firestore security rules deny all client-side read and write operations to `drive_secure_tokens`. Only Cloud Functions using the Firebase Admin SDK can access or decrypt this vault.

### C. Backend-Mediated Reader Access Control
- Google Drive files are **NEVER made public** to serve readers.
- When a reader requests a book:
  1. The backend verifies the caller's Firebase Auth UID.
  2. The book document in `books/{bookId}` is queried:
     - If `visibility == 'public'` and `publishStatus == 'published'`, any authenticated reader may access.
     - If `visibility == 'unlisted'` or `'draft'`, only the author (`callerUid == book.authorId`) or designated reviewers may access.
  3. If authorized, the backend uses the author's encrypted refresh token to obtain a temporary Google Drive access token, streams the PDF to the caller, and never exposes the author's Drive credentials to the reader.

### D. Multi-Account Isolation
- Each connected Drive account is identified by a unique `accountId` (derived from the SHA-256 hash of the Google user ID).
- An author can disconnect an account at any time via `disconnectGoogleDriveAccount`, which immediately purges both the metadata and the encrypted token document.

### E. In-Memory Cache Security
- Downloaded PDF binary arrays are cached strictly in JavaScript RAM (`APP_STATE._pdfCache`) to optimize page turns.
- On user logout or session switch, `APP_STATE._pdfCache` is explicitly wiped to prevent unauthorized access on shared devices.

### F. Firestore Security Rules Reference
- Users can only read and write their own profile (`users/{uid}`).
- Reading progress and bookmarks (`users/{uid}/reading_progress/{bookId}`) are strictly scoped to the authenticated user.
- Publications (`books/{bookId}`) can only be created or modified by authenticated users where `request.auth.uid == request.resource.data.authorId`.
- Unlisted and draft publications are filtered from public listing queries.
