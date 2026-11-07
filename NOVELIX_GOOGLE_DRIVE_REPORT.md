# NOVELIX 7.0 — Google Drive Integration Report

**Generated:** 2026-11-07  
**Module:** Multi-Account Google Drive OAuth & Secure Cloud Proxy  
**Cloud Functions:** `functions/index.js` (Region: `us-central1`)

---

## 1. Zero-Leak Security Architecture

- **No Secrets in Client Bundle:** Neither the Google Drive OAuth Client Secret nor user refresh tokens are ever bundled into the client JavaScript or APK assets.
- **Server-Side Token Exchange:** The OAuth 2.0 authorization code is exchanged for tokens inside the Cloud Function `googleDriveCallback`.
- **Encryption at Rest:** Refresh tokens are encrypted using AES-256-GCM with a 32-character key before storage in `users/{uid}/drive_accounts/{accountId}`.
- **Dedicated OAuth Scope:** `https://www.googleapis.com/auth/drive.readonly` and `https://www.googleapis.com/auth/drive.file` — strictly separated from Firebase Google Sign-In.

---

## 2. Multi-Account Capabilities

Authors can connect multiple Google accounts (e.g. personal and publishing archive):
- **Account Switcher:** Authors can switch between connected accounts in the Drive Picker modal.
- **File Browser:** Callable function `listGoogleDriveFiles` retrieves authorized PDF files without making files publicly accessible.
- **Streaming Proxy:** The callable function `getReaderPdfData` uses the author's refreshed token server-side to fetch the file binary and return Base64 to authorized readers.
- **Disconnect:** Authors can disconnect accounts at any time, which deletes the encrypted tokens from Firestore.

---

## 3. Deep-Link Return Protocol

- **Initiation:** App opens the Google authorization URL in the system browser.
- **Return URI:** The Cloud Function redirects to `novelix://drive-callback?status=success&email=...&accountId=...`.
- **Handling:** Capacitor App plugin listens for `appUrlOpen` and `visibilitychange`, refreshing connected accounts without requiring manual app reloads.
