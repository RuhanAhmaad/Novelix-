# NOVELIX — Google Drive OAuth Credentials Setup Report

Generated: 2026-11-04  
Status: ✅ Complete & Validated  
Project: NOVELIX 4.0 (Firebase Backend: `novelxa-48f15`)

---

## 1. JSON Configuration Validation Status

| Parameter | Value / Status | Verification |
| :--- | :--- | :--- |
| **JSON Integrity** | ✅ Valid & Complete | Successfully parsed Google OAuth client secret JSON |
| **OAuth Client Type** | `web` (Web Application) | Matches required backend server-side flow |
| **Google Cloud Project** | `ruhigroup` | Dedicated project for Google Drive API |
| **Client ID** | `23165793827-un6a2kh299r2e7rroj9nivoku5josvlh.apps.googleusercontent.com` | Verified and registered |
| **Client Secret** | `[SECURED / HIDDEN]` | Verified present (35 chars, standard `GOCSPX-` format) |
| **Configured Redirect URIs** | 1. `https://us-central1-novelxa-48f15.cloudfunctions.net/googleDriveCallback`<br>2. `https://novelxa-48f15.firebaseapp.com/api/drive/callback` | Pre-registered in Google Cloud Console |
| **Auth & Token Endpoints** | Auth: `https://accounts.google.com/o/oauth2/auth`<br>Token: `https://oauth2.googleapis.com/token` | Standard Google OAuth 2.0 endpoints |

---

## 2. Secret Storage & Architecture Security

### Storage Location
- **Local / Server Runtime:** Stored in `functions/.env` (mode `0600` — restricted file permissions).
- **Production Recommendation:** Configured via **Firebase Secret Manager**:
  ```bash
  firebase functions:secrets:set GOOGLE_DRIVE_CLIENT_SECRET
  ```
- **Git Protection:** `.gitignore` explicitly prevents `functions/.env`, `*.env.*`, `client_secret*.json`, `credentials*.json`, and `*.img` files from ever being tracked or committed.

### Security Leak Audit
- **Frontend JavaScript / HTML:** Audited — **0** instances of Client Secret found.
- **Android APK / Public Assets (`android/app/src/main/assets/public/`):** Audited — **0** instances of Client Secret found.
- **`google-services.json`:** Audited — Contains only Firebase client keys, Client Secret is NOT present.
- **Firestore Security Rules:** `drive_secure_tokens` and `drive_oauth_sessions` are strictly locked with `allow read, write: if false;` (accessible only via Cloud Functions Firebase Admin SDK).

---

## 3. Exact Authorized Redirect URI

The client JSON contains the canonical URI and its Firebase Hosting alias:

```text
https://us-central1-novelxa-48f15.cloudfunctions.net/googleDriveCallback
```

*Secondary configured alias:*
```text
https://novelxa-48f15.firebaseapp.com/api/drive/callback
```

Both URIs are actively routed by the NOVELIX backend:
- The canonical URI connects directly to the `googleDriveCallback` Cloud Function in region `us-central1`.
- The hosting rewrite connects via `firebase.json` rewrite routing.

---

## 4. Required Deployment Commands

To deploy the updated Cloud Functions with these credentials:

```bash
# 1. (Recommended) Store client secret in Firebase Secret Manager:
firebase functions:secrets:set GOOGLE_DRIVE_CLIENT_SECRET --project novelxa-48f15

# 2. Deploy Cloud Functions, Firestore Security Rules, and Hosting:
firebase deploy --only functions,firestore,hosting --project novelxa-48f15
```

If deploying with `functions/.env` directly:
```bash
firebase deploy --only functions,firestore,hosting --project novelxa-48f15
```

---

## 5. Remaining Google Cloud Console Steps

Inspect the OAuth Web Client settings in [Google Cloud Console](https://console.cloud.google.com) (Project: `ruhigroup`):

1. **Authorized JavaScript Origins:**
   The attached JSON currently only lists `http://localhost:3000`. Add your production origins:
   - `https://novelxa-48f15.firebaseapp.com`
   - `https://novelxa-48f15.web.app`
   - `capacitor://localhost`

2. **Google Drive API Enabled:**
   Ensure the **Google Drive API** is enabled in the Google Cloud Console for project `ruhigroup`:
   - Navigate to **APIs & Services → Library** → Search **Google Drive API** → Click **Enable**.

3. **OAuth Consent Screen Scopes:**
   Verify the following scopes are configured on the OAuth Consent Screen:
   - `https://www.googleapis.com/auth/drive.readonly`
   - `https://www.googleapis.com/auth/userinfo.email`
   - `https://www.googleapis.com/auth/userinfo.profile`

4. **Publishing Status / Test Users:**
   If the app is in **Testing** mode in Google Cloud Console, ensure your Google email address is listed under **Test Users** on the OAuth consent screen.

---

## 6. Security Validation Summary

```
[PASS] Uploaded JSON contains valid 'web' OAuth client credentials.
[PASS] Client ID set to: 23165793827-un6a2kh299r2e7rroj9nivoku5josvlh.apps.googleusercontent.com
[PASS] Client Secret securely populated in functions/.env with chmod 600.
[PASS] functions/.env and credential file patterns blocked in .gitignore.
[PASS] Zero Client Secret occurrences found in frontend code, out/index.html, or Android assets.
[PASS] Firebase Auth Google Sign-In and Google Drive OAuth clients remain decoupled and independent.
[PASS] AES-256-GCM token encryption active for refresh tokens stored at rest.
[PASS] Firestore rules block client read/write access to token vaults.
```
