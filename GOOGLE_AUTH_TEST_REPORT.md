# NOVELIX 3.0 — Firebase & Google Authentication Audit & Verification Report

**Date**: November 3, 2026  
**Platform**: NOVELIX Digital Publishing & Reading Platform  
**Target Environment**: Android (Capacitor Native Shell) + Web Fallback  
**Application ID / Package**: `com.novelix.app`  
**Firebase Project ID**: `novelxa-48f15`  

---

## 1. Credentials & Identity Verification

Every configuration value in NOVELIX 3.0 has been verified against the official `android/app/google-services.json` and the dedicated debug keystore.

### 1.1 Keystore Fingerprints
- **Keystore Path**: `android/app/debug.keystore`
- **Keystore Alias**: `androiddebugkey`
- **Keystore Password**: `android`
- **Verified SHA-1**:
  ```text
  8A:FA:EA:99:07:A6:1B:C4:04:F0:3A:B0:43:7F:9D:86:B4:74:7F:B3
  ```
- **Verified SHA-256**:
  ```text
  7C:7C:92:17:8F:85:6E:CC:E8:6A:8E:F4:B0:BE:2D:8F:84:B2:82:FB:F9:1F:C1:25:D4:8A:14:47:9A:B7:91:78
  ```

### 1.2 Registered OAuth 2.0 Clients (from `google-services.json`)
- **Android Native Client ID (`client_type: 1`)**:
  ```text
  239783323113-mrginf621qi61nbrek9b23qde2u53g5j.apps.googleusercontent.com
  ```
  *(Bound directly to package `com.novelix.app` and SHA-1 `8A:FA:EA:99:...`)*
- **Web / Server Client ID (`client_type: 3`)**:
  ```text
  239783323113-r33bjnuc153ghsgpshg8vp3mktqj6t36.apps.googleusercontent.com
  ```
- **Web API Key**:
  ```text
  AIzaSyDzlkwY8Xcyyp-fh_JS_z2ob4xgc4YnLps
  ```
- **Auth Domain**:
  ```text
  novelxa-48f15.firebaseapp.com
  ```

---

## 2. Authentication Flow Architecture in Capacitor Android

### 2.1 The Android WebView Challenge
Google OAuth strictly disallows authorization requests from embedded WebViews (`disallowed_useragent` error 403). Using `signInWithPopup` inside an Android WebView fails with a security policy rejection.

### 2.2 NOVELIX 3.0 Hybrid Dual-Path Solution
NOVELIX 3.0 implements an intelligent environment-aware authentication flow:

1. **Environment Detection**:
   ```javascript
   const isCapacitor = window.Capacitor && window.Capacitor.isNativePlatform();
   ```
2. **Native Android Execution (`signInWithRedirect`)**:
   - When running on Android, the Google login action invokes:
     ```javascript
     const provider = new GoogleAuthProvider();
     provider.addScope('profile');
     provider.addScope('email');
     await signInWithRedirect(auth, provider);
     ```
   - This launches Google's secure browser flow through the system Chrome Custom Tab.
3. **Redirect Result Capture**:
   - On application startup (or return from redirect), NOVELIX immediately listens for pending credentials:
     ```javascript
     getRedirectResult(auth).then(async (result) => {
       if (result && result.user) {
         await handleUserAuthentication(result.user);
       }
     }).catch((err) => {
       console.error("Redirect auth resolution failed:", err);
     });
     ```
4. **Desktop / Web Fallback (`signInWithPopup`)**:
   - If running in a desktop browser or development server, the app automatically uses `signInWithPopup(auth, provider)` for an instantaneous popup modal.

---

## 3. Native Deep Link & Manifest Integration

In `android/app/src/main/AndroidManifest.xml`, the primary activity is registered to capture the Firebase OAuth callback URLs:

```xml
<intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="https"
          android:host="novelxa-48f15.firebaseapp.com"
          android:pathPrefix="/__/auth/handler" />
</intent-filter>
```

---

## 4. User Profile Provisioning in Cloud Firestore

Upon successful Google or Email/Password authentication:
1. NOVELIX checks the `users/{uid}` document in Cloud Firestore.
2. If the user is logging in for the first time, a comprehensive profile document is provisioned automatically:
   - `uid`: Unique Firebase UID
   - `email`: Authenticated Google or custom email
   - `displayName`: Google full name or assigned pen name
   - `photoURL`: High-resolution Google avatar or generated SVG avatar
   - `role`: Default `"reader"` (with ability to toggle `"author"` in studio)
   - `createdAt`: Server timestamp
   - `readingProgress`: Empty map initialized for real-time synchronization
   - `savedBooks`: Array initialized for offline bookmarks
3. If an existing profile document is found, it is merged with the latest profile metadata while preserving all bookmarks, chapters read, and history.

---

## 5. Firebase Console Prerequisite Checklist

For complete functionality on Android:

| Check | Item | Status | Action Required |
| :---: | :--- | :---: | :--- |
| ✅ | **`google-services.json`** | Present & Verified | None (embedded in `android/app`) |
| ✅ | **Debug Keystore Binding** | Verified | Embedded in `android/app/build.gradle` |
| ✅ | **SHA-1 Fingerprint Registered** | Verified | Added to Firebase Project Settings |
| ⚠️ | **Google Provider in Firebase Console** | Requires Check | Go to **Firebase Console → Authentication → Sign-in method → Google** and verify **Status is Enabled**. Ensure support email is selected. |
| ⚠️ | **Email/Password Provider** | Requires Check | In **Sign-in method**, verify **Email/Password** is **Enabled**. |
| ⚠️ | **Cloud Firestore Rules** | Configured | Verify rules permit read/write for authenticated users (`request.auth != null`). |

---

## 6. Verification Summary

- **Zero Fake Mocking**: All authentication hooks communicate directly with live Firebase SDK (`9.23.0`).
- **Signature Security**: The APK is signed with the exact debug keystore matching the SHA-1 registered in Firebase.
- **Session Continuity**: `onAuthStateChanged` maintains active sessions across cold starts and app restarts.
