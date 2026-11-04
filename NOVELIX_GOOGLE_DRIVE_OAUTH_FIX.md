# NOVELIX — Google Drive OAuth Fix
## Error 400: origin_mismatch — Root Cause Analysis & Resolution

> **Status:** ✅ Fix implemented, committed, and pushed to GitHub (commit `148c7f2`)
> **Build:** GitHub Actions CI Run #18 triggered automatically

---

## 1. Root Cause: Error 400 `origin_mismatch`

### What went wrong

The frontend contained two strategies for starting Google Drive OAuth.

**Strategy 1** (backend callable + `window.open` as a named popup) silently failed on Android because Capacitor's WebView does not support `window.open()` returning a valid popup — it returns `null`.

**Strategy 2** (the fallback) then executed:

```html
<!-- Loaded on every page load -->
<script src="https://accounts.google.com/gsi/client" async defer></script>
```

```js
// Ran inside the Capacitor WebView
const tokenClient = google.accounts.oauth2.initTokenClient({
  client_id: '23165793827-un6a2kh299r2e7rroj9nivoku5josvlh.apps.googleusercontent.com',
  scope: 'drive.readonly ...',
  callback: ...
});
tokenClient.requestAccessToken({ prompt: 'select_account' });
```

The GIS library (`gsi/client`) performs an **implicit / token grant** request and sends the page's `Origin` header to Google. Inside a Capacitor WebView, the origin is `https://localhost`. Google rejects with:

> **Error 400: origin_mismatch**
> "The JavaScript origin in the request, `https://localhost`, does not match the ones registered for the OAuth client."

Google also explicitly blocks GIS token requests from embedded WebViews (`disallowed_useragent` policy). Registering `https://localhost` in GCP does **not** fix this — Google blocks it at the policy level for production clients.

---

## 2. Architecture Selected: Server-side Auth Code Flow + Android System Browser + Custom Deep Link

### Why this architecture

| Requirement | Solution |
|---|---|
| No website needed | Firebase Cloud Functions provide the HTTPS callback domain for free |
| No origin_mismatch | OAuth runs in the system browser (Chrome), not in WebView |
| No Client Secret in APK | Secret lives in Firebase Secret Manager / Cloud Function environment |
| Refresh tokens | Stored encrypted (AES-256-GCM) server-side in `users/{uid}/drive_secure_tokens/` |
| Return to app | `novelix://` custom scheme deep link, handled by existing `intent-filter` in AndroidManifest.xml |

### Flow

```
1. NOVELIX App calls getGoogleDriveAuthUrl callable
   → Cloud Function builds state-signed Google OAuth URL
   → Stores session in Firestore: drive_oauth_sessions/{stateId}

2. App calls window.open(authUrl, '_system')
   → Android opens Chrome (real browser, not WebView)

3. User authenticates at accounts.google.com
   (No WebView. No origin restriction. No origin_mismatch.)

4. Google redirects to Cloud Function:
   https://us-central1-novelxa-48f15.cloudfunctions.net/googleDriveCallback
   → Verifies state → looks up Firestore session → retrieves uid
   → Exchanges code for tokens
   → Encrypts refresh_token (AES-256-GCM)
   → Stores in users/{uid}/drive_secure_tokens/{accountId}
   → Stores metadata in users/{uid}/drive_accounts/{accountId}
   → Redirects: novelix://drive-callback?status=success&email=...&accountId=...

5. Android intent-filter catches novelix:// scheme
   → Capacitor App plugin fires appUrlOpen event
   → App reads status/email, refreshes drive accounts list
```

---

## 3. OAuth Client Configuration (Google Cloud Console)

**Client type:** Web Application (correct for server-side flow)

| Setting | Value |
|---|---|
| **Authorized JavaScript origins** | *(leave completely empty — not used)* |
| **Authorized redirect URIs** | `https://us-central1-novelxa-48f15.cloudfunctions.net/googleDriveCallback` |

> Do NOT add `https://localhost` or any WebView origin.

---

## 4. Files Changed (commit `148c7f2`)

### `scripts/generate_4.py` → rebuilds `out/index.html`

**Removed:**
- `<script src="https://accounts.google.com/gsi/client" async defer></script>`
- `google.accounts.oauth2.initTokenClient(...)` fallback strategy
- `window.open(authUrl, 'popup-name', 'width=540,...')` named popup

**Added:**
- `window.open(authUrl, '_system')` — routes to Android system browser
- `Capacitor.Plugins.App.addListener('appUrlOpen', ...)` — receives `novelix://drive-callback` return
- `visibilitychange` listener — fallback when user returns without deep link
- `APP_STATE._driveOAuthPending` flag — coordinates both return paths
- 401 handling in `browseDriveAccountFiles()` — detects stale token and shows reconnect UI

### `functions/index.js`

**Fixed:**
- Removed duplicate `status: 'active', hasRefreshToken, updatedAt` block (orphaned lines 638–641)
- `renderCallbackHtml()` auto-redirects to `novelix://drive-callback?status=success&email=...`
- `deepLinkUrl` now computed at JS function scope, not accidentally inside CSS block

---

## 5. Exact Redirect URI

```
https://us-central1-novelxa-48f15.cloudfunctions.net/googleDriveCallback
```

This must be the **only** entry in Google Cloud Console → Authorized redirect URIs.

---

## 6. Android Configuration

**Package name:** `io.ionic.novelix`

**Custom scheme already in `android/app/src/main/AndroidManifest.xml`:**
```xml
<intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="novelix" />
</intent-filter>
```

This handles the `novelix://drive-callback?...` redirect. **Already configured — no changes needed.**

**SHA-1 fingerprints:** Not required for this flow. Web Application clients are server-authenticated.

---

## 7. Cloud Functions

| Function | Type | Purpose |
|---|---|---|
| `getGoogleDriveAuthUrl` | Callable | Generates state-signed OAuth URL for authenticated NOVELIX user |
| `googleDriveCallback` | HTTP | Receives Google redirect, exchanges code, stores tokens, returns to `novelix://` |
| `getGoogleDriveAccessToken` | Callable | Returns fresh access token using stored refresh token |
| `disconnectGoogleDriveAccount` | Callable | Revokes & deletes account tokens |

---

## 8. Security Properties

| Property | Implementation |
|---|---|
| Client Secret | Firebase Secret Manager (`GOOGLE_DRIVE_OAUTH_CLIENT_JSON`) — backend only |
| Refresh tokens | AES-256-GCM encrypted, stored in `users/{uid}/drive_secure_tokens/` |
| State validation | UUID state in Firestore, 15-min TTL, deleted after use |
| User identity | `getGoogleDriveAuthUrl` requires Firebase Auth — NOVELIX user must be signed in |
| No secrets in APK | ✅ Zero credentials in `android/`, `out/`, or any frontend file |
| Firebase Google Sign-In | ✅ Completely separate — not affected |

---

## 9. Deployment

### Deploy Cloud Functions
```bash
firebase login
firebase use novelxa-48f15

# If secret not yet stored:
firebase functions:secrets:set GOOGLE_DRIVE_OAUTH_CLIENT_JSON

# Deploy Drive OAuth functions
firebase deploy --only functions:getGoogleDriveAuthUrl,functions:googleDriveCallback,functions:googleDriveAuth,functions:getGoogleDriveAccessToken,functions:disconnectGoogleDriveAccount
```

### Build APK
GitHub Actions CI triggered automatically on push. Monitor at:
https://github.com/RuhanAhmaad/Novelix-/actions

---

## 10. Testing Checklist (do not claim success without completing)

Install the APK from CI artifact, then:

- [ ] Open NOVELIX and sign in
- [ ] Go to Settings → Connected Services → Google Drive
- [ ] Tap **Connect Google Drive**
- [ ] **Chrome** (not a WebView popup) opens — Google account selection appears
- [ ] Select a Google account and authorize
- [ ] Chrome closes and NOVELIX reopens automatically via deep link
- [ ] Connected account email appears in the Drive section
- [ ] Tap **Browse Files** — PDF files from Drive appear
- [ ] Tap **Import** on a PDF — loads into Publishing Studio
- [ ] Tap **✕** to disconnect — account removed
- [ ] Tap **Connect Google Drive** again — works successfully

**Error 400: origin_mismatch must not appear at any point.**

---

## 11. Commit Reference

| Item | Value |
|---|---|
| Commit | `148c7f2` |
| Branch | `main` |
| Repo | https://github.com/RuhanAhmaad/Novelix-.git |
| CI Run | #18 |
| Files changed | `scripts/generate_4.py`, `out/index.html`, `android/app/src/main/assets/public/index.html`, `functions/index.js` |
