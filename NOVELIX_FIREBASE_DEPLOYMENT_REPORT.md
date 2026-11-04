# NOVELIX — Firebase Deployment & Google Drive OAuth Report

Generated: 2026-11-04  
Target Firebase Project: `novelxa-48f15`  
Google Cloud Project for Drive OAuth: `ruhigroup`  
Deployment Status: ⏳ **Code-Ready & Validated — Awaiting Interactive CLI Login & Blaze Approval**

---

## 1. Executive Summary

The NOVELIX backend has been upgraded with **Firebase Secret Manager** integration using `defineJsonSecret()`. The entire Google OAuth Web client configuration is bound specifically to the Google Drive OAuth functions, preventing any credential leakage to other functions or client-side assets.

Because this environment is a headless Linux shell on Android Termux without a graphical web browser, running `firebase deploy` requires an interactive OAuth login (`--no-localhost`) or a CI token. All technical details, code bindings, and exact deployment steps are documented below.

---

## 2. Cloud Functions Architecture & Secret Binding

### Secret Definition
- **Secret Name:** `GOOGLE_DRIVE_OAUTH_CLIENT_JSON`
- **Method:** `defineJsonSecret('GOOGLE_DRIVE_OAUTH_CLIENT_JSON')` via `firebase-functions/params`
- **Runtime Environment:** Node.js 20 on Cloud Functions for Firebase (2nd Gen)

### Secret Access Policy (Least Privilege)
The secret `GOOGLE_DRIVE_OAUTH_CLIENT_JSON` is bound **exclusively** to the 4 functions requiring Google Drive OAuth credentials:

| Function Name | Type | Secret Bound? | Purpose |
| :--- | :--- | :---: | :--- |
| `getGoogleDriveAuthUrl` | Callable (`onCall`) | ✅ **YES** | Generates Google OAuth consent URL with state |
| `googleDriveAuth` | HTTP (`onRequest`) | ✅ **YES** | Direct browser redirect initiation |
| `googleDriveCallback` | HTTP (`onRequest`) | ✅ **YES** | Exchanges authorization code for tokens |
| `getGoogleDriveAccessToken` | Callable (`onCall`) | ✅ **YES** | Refreshes access tokens via refresh token |
| `disconnectGoogleDriveAccount` | Callable (`onCall`) | ❌ NO | Deletes account records & secure token docs |
| `setAdminRole` | Callable (`onCall`) | ❌ NO | Admin role bootstrap |
| `onReviewWritten` | Firestore Trigger | ❌ NO | Review aggregation |
| `onChapterPublished` | Firestore Trigger | ❌ NO | FCM chapter notifications |
| `onFollowCreated` | Firestore Trigger | ❌ NO | Follower notifications |
| `onBookStorageUpdated` | Firestore Trigger | ❌ NO | Storage quota calculation |
| `reviewCreatorVerification` | Callable (`onCall`) | ❌ NO | Admin verification decisions |
| `broadcastAnnouncement` | Callable (`onCall`) | ❌ NO | FCM topic broadcasts |

---

## 3. Verified Endpoints & Redirect URI Configuration

| Endpoint | Protocol / URL | Notes |
| :--- | :--- | :--- |
| **Canonical Callback URI** | `https://us-central1-novelxa-48f15.cloudfunctions.net/googleDriveCallback` | Primary redirect URI in Google Cloud Console |
| **Hosting Alias Callback** | `https://novelxa-48f15.firebaseapp.com/api/drive/callback` | Proxied via `firebase.json` rewrite |
| **In-App Initiation** | Callable `getGoogleDriveAuthUrl` | Returns signed state token & Google consent URL |
| **Direct Browser Initiation** | `https://us-central1-novelxa-48f15.cloudfunctions.net/googleDriveAuth?uid={UID}` | Direct browser redirect |
| **Token Refresh Callable** | Callable `getGoogleDriveAccessToken` | Transparently refreshes expired access tokens |

### Google Drive Scopes Supported:
1. `https://www.googleapis.com/auth/drive.readonly`
2. `https://www.googleapis.com/auth/userinfo.email`
3. `https://www.googleapis.com/auth/userinfo.profile`

---

## 4. Pre-Flight Verification & System Requirements

### A. Firebase CLI Authentication Check
When checking the Firebase CLI on this machine:
```text
$ pnpm dlx firebase-tools projects:list
Error: Failed to authenticate, have you run firebase login?
```
The Firebase CLI session is currently unauthenticated. Because Termux has no GUI browser, an interactive browser login is required (see Section 5 below).

### B. Firebase Project Billing Requirement (Blaze Plan)
- Cloud Functions (2nd Gen) and Google Cloud Secret Manager require the **Blaze (pay-as-you-go) billing plan** on the Firebase project `novelxa-48f15`.
- If your project is on the free Spark plan, Cloud Functions deployment will pause with an error requiring a billing account.
- **Action:** Ensure Blaze billing is enabled at [Firebase Console → novelxa-48f15 → Usage and Billing](https://console.firebase.google.com/project/novelxa-48f15/usage).

### C. Required Google Cloud APIs (Project `novelxa-48f15`)
The following APIs must be enabled (the CLI enables them automatically upon deployment if authenticated with Owner/Editor permissions):
- Cloud Functions API (`cloudfunctions.googleapis.com`)
- Cloud Build API (`cloudbuild.googleapis.com`)
- Secret Manager API (`secretmanager.googleapis.com`)
- Cloud Run Admin API (`run.googleapis.com`)
- Artifact Registry API (`artifactregistry.googleapis.com`)

---

## 5. Step-by-Step Deployment Instructions (For You to Run)

Please execute the following 3 steps in your Termux terminal to complete the cloud deployment:

### Step 1: Log In to Firebase CLI
Run:
```bash
pnpm dlx firebase-tools login --no-localhost
```
1. The CLI will display a Google authorization URL: `https://accounts.google.com/o/oauth2/auth?...`
2. Open that URL in your mobile browser, sign in with your Google account that owns project `novelxa-48f15`, and authorize the CLI.
3. Google will present an authorization code. Copy and paste it back into your Termux terminal.

### Step 2: Store the OAuth Client Secret JSON in Secret Manager
Run the following command to store the client JSON securely without exposing it in files:
```bash
cat "/data/user/0/com.termux/files/home/.gemini/antigravity-cli/brain/4cdc78a0-3966-41b6-abec-f02ff2179705/.user_uploaded/media_1793760406873_4aaf746e.img" | pnpm dlx firebase-tools functions:secrets:set GOOGLE_DRIVE_OAUTH_CLIENT_JSON --project novelxa-48f15
```
*(If prompted to destroy old versions or grant permissions to the Cloud Functions service account, press `Y`)*.

### Step 3: Deploy Functions, Rules, and Hosting
```bash
pnpm dlx firebase-tools deploy --only functions,firestore,hosting --project novelxa-48f15
```

---

## 6. Android APK Build Status

All NOVELIX 4.0 features, including the Google Drive OAuth integration, settings modal, storage meter, and creator verification, have been committed and synced to `android/app/src/main/assets/public/index.html`.

Pushing to GitHub triggers the GitHub Actions CI pipeline to compile the permanent `app-debug.apk`. The resulting APK is downloaded directly to:
- `novelix.apk`
- `/sdcard/Download/novelix.apk`
