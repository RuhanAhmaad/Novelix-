# NOVELIX 4.0 — Google Drive Integration Setup Guide

Generated: 2026-11-04

---

## Overview

NOVELIX 4.0 supports connecting multiple Google accounts to import books (PDF/EPUB) directly from Google Drive. This uses the **Google Identity Services (GIS) Token Client** — a browser-side OAuth 2.0 flow that issues short-lived access tokens.

---

## Architecture

```
User clicks "Connect Drive Account"
        ↓
GIS Token Client popup (accounts.google.com)
        ↓
Access token granted (expires in ~1 hour)
        ↓
Token stored in Firestore: users/{uid}/drive_accounts/{accountId}
        ↓
Drive API v3 REST calls via fetch()
        ↓
File selected → downloaded to browser → uploaded to Firebase Storage
```

---

## Google Cloud Console Setup (Required)

### Step 1: Enable the Google Drive API

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select project `novelxa-48f15`
3. Navigate to **APIs & Services → Library**
4. Search for **Google Drive API** and click **Enable**

### Step 2: Configure OAuth Consent Screen

1. Navigate to **APIs & Services → OAuth consent screen**
2. Set **User Type** to **External** (for public apps)
3. Fill in:
   - App name: `NOVELIX`
   - User support email: your email
   - Developer contact: your email
4. Click **Save and Continue**
5. On **Scopes** page, click **Add or Remove Scopes**
6. Add these scopes:
   - `https://www.googleapis.com/auth/drive.readonly`
   - `https://www.googleapis.com/auth/userinfo.email`
   - `https://www.googleapis.com/auth/userinfo.profile`
7. Click **Save and Continue**
8. Add yourself as a **Test User** (required while app is in Testing mode)

### Step 3: Authorized JavaScript Origins

1. Navigate to **APIs & Services → Credentials**
2. Click on the **Web Client** OAuth 2.0 Client (Type 3)
   - Client ID: `239783323113-r33bjnuc153ghsgpshg8vp3mktqj6t36.apps.googleusercontent.com`
3. Under **Authorized JavaScript origins**, ensure these are present:
   - `https://novelxa-48f15.firebaseapp.com`
   - `http://localhost` (for local testing)
   - `capacitor://localhost` (for Android WebView)
4. Click **Save**

---

## How It Works in NOVELIX

### Connecting an Account

```javascript
// In the app — settings modal, Drive tab
// GIS Token Client is initialized with:
{
  client_id: "239783323113-r33bjnuc153ghsgpshg8vp3mktqj6t36.apps.googleusercontent.com",
  scope: "https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/userinfo.email",
  callback: (tokenResponse) => { /* store token */ }
}
```

### Stored in Firestore

```
users/{uid}/drive_accounts/{accountId}
  ├── email (string)
  ├── accessToken (string) — ⚠️ expires in ~1 hour
  ├── connectedAt (timestamp)
  └── displayName (string)
```

### Browsing Drive Files

The app queries Drive API v3 for PDF and EPUB files:
```
GET https://www.googleapis.com/drive/v3/files
  ?q=mimeType='application/pdf' or mimeType='application/epub+zip'
  &fields=files(id,name,size,modifiedTime,mimeType)
  &pageSize=50
  Authorization: Bearer {accessToken}
```

---

## Security Limitations & Recommendations

> **⚠️ Important**: The current implementation stores short-lived access tokens in Firestore. These expire after ~1 hour and cannot be refreshed without user interaction.

| Limitation | Current State | Recommended Improvement |
|------------|--------------|------------------------|
| Token storage | Access token in Firestore | Implement server-side token refresh via Cloud Functions |
| Token expiry | ~1 hour | Implement refresh token flow with Cloud Functions |
| Token exposure | Stored in Firestore (user's own doc) | Encrypt tokens at rest |
| Re-authentication | User must reconnect after 1 hour | Background refresh using GIS + Cloud Functions |

### Future: Server-Side Refresh Token (Phase 2)

To implement persistent Drive connections:
1. Use the **Authorization Code** flow instead of Token flow
2. Exchange code for refresh token server-side (Cloud Function)
3. Store refresh token encrypted in Firestore (or Secret Manager)
4. Cloud Function refreshes access token on demand

---

## Disconnecting Accounts

The app provides a disconnect button per Drive account in Settings → Drive tab. This deletes the `drive_accounts/{accountId}` document from Firestore. The user must re-authenticate with Google Drive if they want to reconnect.

---

## Testing

1. Open NOVELIX app
2. Navigate to Settings (gear icon in profile or nav)
3. Click **Drive & Cloud** tab
4. Click **Connect Google Drive Account**
5. Complete OAuth popup
6. The connected account email should appear in the list
7. Click **Browse Files** to open the Drive file picker
8. Select a PDF or EPUB file — it will be pre-filled in the publish form
