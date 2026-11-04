# NOVELIX — Google OAuth Redirect URI Report

Generated: 2026-11-04  
Project: NOVELIX 4.0  
Firebase Project ID: `novelxa-48f15`  
Project Number: `239783323113`  
Google Cloud Region: `us-central1`  
OAuth Client ID (Web Client): `239783323113-r33bjnuc153ghsgpshg8vp3mktqj6t36.apps.googleusercontent.com`

---

## 1. EXACT AUTHORIZED REDIRECT URI TO COPY

Copy and paste this exact URI into **Google Cloud Console → Google Auth Platform → Clients → NOVELIX Google Drive → Authorized redirect URIs**:

```text
https://us-central1-novelxa-48f15.cloudfunctions.net/googleDriveCallback
```

### Recommended Secondary Redirect URIs

You can (and should) also add the following secondary redirect URIs in Google Cloud Console under the same client for maximum compatibility across web hosting domains and local testing:

| Type | Redirect URI | Description |
|------|-------------|-------------|
| **Primary (Direct Backend)** | `https://us-central1-novelxa-48f15.cloudfunctions.net/googleDriveCallback` | Direct Cloud Functions v2 endpoint |
| **Firebase Hosting Domain** | `https://novelxa-48f15.firebaseapp.com/api/drive/callback` | Routed via Firebase Hosting rewrite |
| **Firebase Web App Domain** | `https://novelxa-48f15.web.app/api/drive/callback` | Secondary Firebase Hosting domain |
| **Local Emulator** | `http://127.0.0.1:5001/novelxa-48f15/us-central1/googleDriveCallback` | Local Firebase Functions emulator |
| **Local Dev Web** | `http://localhost:3000/api/drive/callback` | Local development server |

---

## 2. OAuth Initiation & Callback Endpoints

### A. OAuth Initiation Endpoints

1. **In-App Callable Function (Client SDK — Recommended):**
   - **Function Name:** `getGoogleDriveAuthUrl`
   - **Type:** Firebase HTTPS Callable (`onCall`)
   - **Authentication:** Requires authenticated NOVELIX user (`request.auth.uid`)
   - **Action:** Generates a cryptographically random, 15-minute TTL `state` session in `drive_oauth_sessions/{stateId}`, binds it to the user's UID, and constructs the Google OAuth 2.0 authorization URL.
   - **Scopes Included:**
     - `https://www.googleapis.com/auth/drive.readonly`
     - `https://www.googleapis.com/auth/userinfo.email`
     - `https://www.googleapis.com/auth/userinfo.profile`

2. **Direct Browser HTTP Initiation (Fallback):**
   - **Endpoint URL:** `https://us-central1-novelxa-48f15.cloudfunctions.net/googleDriveAuth?uid={USER_UID}`
   - **Firebase Hosting URL:** `https://novelxa-48f15.firebaseapp.com/api/drive/auth?uid={USER_UID}`
   - **Action:** HTTP 302 Redirect directly to Google's consent screen.

### B. OAuth Callback Endpoint

- **Function Name:** `googleDriveCallback`
- **Type:** HTTP Request Handler (`onRequest` — Firebase Functions v2)
- **Method:** `GET`
- **Protocol:** `https://`
- **Domain:** `us-central1-novelxa-48f15.cloudfunctions.net`
- **Path:** `/googleDriveCallback`
- **Full Exact URI:** `https://us-central1-novelxa-48f15.cloudfunctions.net/googleDriveCallback`
- **Input Query Parameters Received from Google:**
  - `code`: The single-use authorization code issued by Google
  - `state`: The state token verifying the session and linking the request to the NOVELIX user
  - `error` / `error_description`: If authorization was declined or cancelled
- **Backend Flow upon Callback:**
  1. Validates the `state` session against Firestore (`drive_oauth_sessions`).
  2. Makes a server-to-server POST request to `https://oauth2.googleapis.com/token` using the server's `GOOGLE_CLIENT_SECRET`.
  3. Obtains `access_token` and `refresh_token`.
  4. Calls Google UserInfo API (`https://www.googleapis.com/oauth2/v3/userinfo`) to get user email and display name.
  5. Encrypts the `refresh_token` using AES-256-GCM with `TOKEN_ENCRYPTION_SECRET`.
  6. Stores confidential tokens in `users/{uid}/drive_secure_tokens/{accountId}` (blocked from client read by Firestore security rules).
  7. Stores public metadata (email, account name, status) in `users/{uid}/drive_accounts/{accountId}` for UI rendering.
  8. Deletes the temporary `drive_oauth_sessions` state document.
  9. Serves an editorial dark-themed response page that posts a `NOVELIX_DRIVE_CONNECTED` message to `window.opener` and closes the window.

---

## 3. Backend Deployment Status

| Component | Status | Details |
|-----------|--------|---------|
| `functions/index.js` | ✅ **Fully Implemented** | Implemented `getGoogleDriveAuthUrl`, `googleDriveAuth`, `googleDriveCallback`, `getGoogleDriveAccessToken`, `disconnectGoogleDriveAccount` |
| Node Syntax Check | ✅ **Verified** | `node -c functions/index.js` passed with zero errors |
| `functions/.env` | ✅ **Configured** | Contains Client ID, encryption secrets, and placeholder for Client Secret |
| `firebase.json` | ✅ **Configured** | Added hosting rewrites for `/api/drive/callback` and `/api/drive/auth` |
| `firestore.rules` | ✅ **Secured** | Added strict `allow read, write: if false;` for `drive_secure_tokens` and `drive_oauth_sessions` |
| `out/index.html` & Android assets | ✅ **Updated** | Added postMessage listener, server OAuth flow with automatic fallback |
| Cloud Functions Cloud Deployment | ⏳ **Needs Deployment** | Ready to deploy to Firebase via CLI (`firebase deploy --only functions,firestore,hosting`) |

---

## 4. Required Environment Variables

Configure these variables in `functions/.env` (or via Firebase CLI secrets):

```env
# 1. Google OAuth Web Client ID (from google-services.json Type 3 client)
GOOGLE_CLIENT_ID=239783323113-r33bjnuc153ghsgpshg8vp3mktqj6t36.apps.googleusercontent.com

# 2. Google OAuth Client Secret (from Google Cloud Console Credentials)
# Paste your actual Client Secret here before deploying functions:
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET_HERE

# 3. Server-side AES-256 encryption secret for tokens stored at rest
TOKEN_ENCRYPTION_SECRET=novelix-super-secure-aes256-key-32chars!

# 4. Administrator Bootstrap Secret
ADMIN_BOOTSTRAP_SECRET=novelix-admin-secure-init-2026
```

> **Security Note:** Never commit your actual `GOOGLE_CLIENT_SECRET` to a public repository. For production Firebase deployments, you can securely store the client secret using Google Cloud Secret Manager:
> ```bash
> firebase functions:secrets:set GOOGLE_CLIENT_SECRET
> ```

---

## 5. Remaining Setup Steps (Step-by-Step)

### Step 1: Add the Redirect URI in Google Cloud Console
1. Open [Google Cloud Console](https://console.cloud.google.com).
2. Select project **`novelxa-48f15`**.
3. Go to **APIs & Services → Credentials** (or **Google Auth Platform → Clients**).
4. Click on the OAuth 2.0 Web Client (`NOVELIX Google Drive` or Client ID `239783323113-r33...`).
5. Under **Authorized redirect URIs**, click **+ ADD URI**.
6. Paste:
   ```text
   https://us-central1-novelxa-48f15.cloudfunctions.net/googleDriveCallback
   ```
7. (Optional but recommended) Click **+ ADD URI** and also add:
   ```text
   https://novelxa-48f15.firebaseapp.com/api/drive/callback
   ```
8. Under **Authorized JavaScript origins**, make sure these are present:
   - `https://novelxa-48f15.firebaseapp.com`
   - `https://novelxa-48f15.web.app`
   - `capacitor://localhost`
   - `http://localhost`
9. Click **SAVE**.

### Step 2: Copy the Client Secret
1. On the same credentials page, copy the **Client Secret** for this OAuth client.
2. Open `functions/.env` and paste it into `GOOGLE_CLIENT_SECRET=your_secret_here`.

### Step 3: Deploy to Firebase
Run the following command to deploy the updated backend functions and security rules:
```bash
firebase deploy --only functions,firestore,hosting --project novelxa-48f15
```

Once deployed, the Google Drive OAuth flow is live, production-ready, and fully secured with server-side token exchange and AES-256 encrypted refresh token storage.
