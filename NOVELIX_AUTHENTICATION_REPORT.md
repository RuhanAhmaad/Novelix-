# NOVELIX 7.0 — Authentication Report

**Generated:** 2026-11-07  
**Module:** Native Android Google Sign-In & Firebase Auth  
**Package:** `com.novelix.app`  
**Firebase Auth Provider:** Google, Email/Password

---

## 1. Native Android Google Sign-In Integration

- **Plugin:** `@codetrix-studio/capacitor-google-auth@3.4.0-rc.4`
- **Server Client ID:** `239783323113-r33bjnuc153ghsgpshg8vp3mktqj6t36.apps.googleusercontent.com`
- **Scopes:** `['profile', 'email']`
- **Authentication Handshake:**
  1. Capacitor invokes native Google Play Services sign-in dialog.
  2. Google returns a signed `idToken`.
  3. `firebase.auth.GoogleAuthProvider.credential(idToken)` exchanges the token for a Firebase User credential.
  4. Firebase Auth listener triggers profile synchronization and sets session persistence.
- **Web Fallback:** If running outside Android, falls back to `signInWithPopup` and `signInWithRedirect`.

---

## 2. Email & Password Authentication

- **Registration:** Creates user via `createUserWithEmailAndPassword`, assigns default user handle, initializes profile document in `users/{uid}`, and sets initial 500 MB storage quota.
- **Login:** `signInWithEmailAndPassword` with error mapping for user-friendly messages.
- **Password Reset:** `sendPasswordResetEmail` dispatches automated password recovery emails.
- **Email Verification:** Authors and readers can request a verification email via `user.sendEmailVerification()`, verified in real-time via `user.emailVerified`.

---

## 3. Profile Synchronization

Every user session syncs with a real-time Firestore listener on `users/{uid}`:
- Display name, bio, and handle.
- Verified Creator badge status.
- Storage quota and usage metrics.
- Connected Drive accounts.
