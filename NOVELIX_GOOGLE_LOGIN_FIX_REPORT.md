# NOVELIX 5.0 — Google Login Fix & Architecture Report

## 1. Executive Summary

In NOVELIX 4.x and earlier, attempting to sign in using Google on Android triggered a silent authentication failure or an unresolved redirect loop. The underlying root cause has been comprehensively diagnosed, architecturally isolated, and remediated by installing and registering native Play Services Authentication via `@codetrix-studio/capacitor-google-auth`, extracting the cryptographically verified Google ID Token, and exchanging it for a first-class Firebase Auth credential via `firebase.auth.GoogleAuthProvider.credential(idToken)`.

---

## 2. Root Cause Analysis

### A. The In-WebView Redirect Flaw
Previously, `scripts/generate_4.py` invoked `auth.signInWithRedirect(provider)` when running in a Capacitor mobile environment:
```javascript
// PREVIOUS BROKEN IMPLEMENTATION
if (isCapacitor) {
  await auth.signInWithRedirect(provider);
}
```
In a native Capacitor Android application:
1. The webview navigation initiates an external redirect to `https://accounts.google.com`.
2. Upon authentication, Google redirects back to `https://novelxa-48f15.firebaseapp.com/__/auth/handler`.
3. Because the Capacitor webview operates under an internal HTTPS custom scheme (`https://localhost` or `https`), the redirect leaves the WebView context or causes a session desynchronization.
4. When `auth.getRedirectResult()` was called during `DOMContentLoaded`, it consistently resolved to `null` user, leaving the user unauthenticated and stuck on the login modal.

### B. Separation of Google Sign-In vs. Google Drive OAuth
A secondary issue identified in previous iterations was conflation between Google Account Sign-In (Firebase Authentication) and Google Drive OAuth authorizations (access to files/folders).
- **Firebase Google Sign-In** requires only `email` and `profile` scopes to authenticate the user identity in Firebase.
- **Google Drive Access** requires an independent OAuth 2.0 Authorization Code flow with Secret Manager encrypted tokens and specific Drive scopes (`drive.readonly`, `drive.file`).

---

## 3. Implemented Fixes & Architecture

### A. Native Android Play Services Authentication
1. **Added Google Play Services Auth Dependency:**
   In `android/app/build.gradle`:
   ```groovy
   implementation 'com.google.android.gms:play-services-auth:21.3.0'
   ```
2. **Installed Capacitor Google Auth Plugin:**
   Added `@codetrix-studio/capacitor-google-auth: 3.4.0-rc.4` to `package.json` and linked in `android/capacitor.settings.gradle` and `android/app/capacitor.build.gradle`.
3. **Explicit Bridge Registration:**
   In `android/app/src/main/java/com/novelix/app/MainActivity.java`:
   ```java
   package com.novelix.app;
   import android.os.Bundle;
   import com.getcapacitor.BridgeActivity;
   import com.codetrixstudio.capacitor.GoogleAuth.GoogleAuth;

   public class MainActivity extends BridgeActivity {
       @Override
       public void onCreate(Bundle savedInstanceState) {
           registerPlugin(GoogleAuth.class);
           super.onCreate(savedInstanceState);
       }
   }
   ```
4. **OAuth Client Registration in Native Resources:**
   In `android/app/src/main/res/values/strings.xml`:
   ```xml
   <string name="server_client_id">239783323113-r33bjnuc153ghsgpshg8vp3mktqj6t36.apps.googleusercontent.com</string>
   ```
   In `capacitor.config.ts`:
   ```typescript
   plugins: {
     GoogleAuth: {
       scopes: ['profile', 'email'],
       serverClientId: '239783323113-r33bjnuc153ghsgpshg8vp3mktqj6t36.apps.googleusercontent.com',
       forceCodeForRefreshToken: false,
     }
   }
   ```
   Matching the registered Web OAuth Client ID (`client_type: 3`) in `google-services.json` and the SHA-1 debug fingerprint (`8A:FA:EA:99:07:A6:1B:C4:04:F0:3A:B0:43:7F:9D:86:B4:74:7F:B3`).

### B. Seamless ID Token Credential Exchange
In `scripts/generate_4.py`, `executeGoogleAuth()` now leverages the native Google Sign-In sheet:
```javascript
const googleUser = await googleAuthPlugin.signIn();
const idToken = googleUser?.authentication?.idToken || googleUser?.idToken;
const credential = firebase.auth.GoogleAuthProvider.credential(idToken);
const userCred = await auth.signInWithCredential(credential);
```
- **Error Handling & Cancellation:** If the user dismisses the native account selector sheet (error code `12501` or `cancelled`), the app catches it gracefully without showing scary alerts.
- **Web Fallback:** On web browsers or desktop environments, the flow falls back cleanly to `auth.signInWithPopup(provider)`.
- **Session Persistence:** Firebase Authentication retains state across app restarts via `firebase.auth().onAuthStateChanged`.

---

## 4. Verification Checklist

| Test Item | Expected Result | Status |
|-----------|-----------------|--------|
| Play Services Auth Dependency | Compiles with version 21.3.0 | PASS |
| Plugin Registration | Native bridge exposes `GoogleAuth` | PASS |
| OAuth Server Client ID | Matches Web Client ID in `google-services.json` | PASS |
| Cancellation Handling | Dismissing Google dialog does not throw unhandled exception | PASS |
| Credential Exchange | Valid Firebase User returned with UID, email, displayName | PASS |
| State Persistence | App launch restores session via `onAuthStateChanged` | PASS |
