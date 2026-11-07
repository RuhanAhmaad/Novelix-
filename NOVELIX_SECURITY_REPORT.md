# NOVELIX 7.0 — Security Hardening Report

**Generated:** 2026-11-07  
**Scope:** Client Assets, Cloud Functions, Admin Access, Third-Party Credentials

---

## 1. Remediation of Compromised ImgBB Key

### Threat Description
The earlier APK build contained an unencrypted ImgBB API key (`a9985ccf572a0e05bce242e27cf8be33`) in client-side JavaScript. This exposed the third-party account to quota abuse and unauthorized uploads.

### Actions Taken
1. **Key Eradication:** The key was removed from all client source files (`scripts/generate_4.py`, `out/index.html`, `android/app/src/main/assets/public/index.html`).
2. **Environment File Cleansing:** Stripped from `.env.local`, `README.md`, and `SETUP.md`.
3. **Migration to Firebase Storage:** All image uploads (book covers, user profile avatars) now upload directly to Google Cloud-backed Firebase Storage (`covers/` and `avatars/` paths) with user authentication checks.

---

## 2. Server-Side Admin Authorization

- **Custom Claims:** Admin status is validated via Firebase Authentication Custom Claims (`claims.admin === true`).
- **Callable Verification:** The Cloud Function `verifyAdminStatus` checks the caller's server-side token rather than trusting any client-side boolean flag.
- **Terminal Command Hardening:** The developer terminal command `admin` requires server verification before granting access. Typing "admin" without authorized claims outputs `PERMISSION DENIED`.
- **Tamper-Evident Audit Logging:** All administrative actions (user bans, moderation, quota adjustments) write an append-only entry to `admin_logs`.

---

## 3. Google Drive OAuth Security

- **Client Secrets:** Protected in Secret Manager (`GOOGLE_DRIVE_OAUTH_CLIENT_JSON`).
- **Encrypted Token Storage:** Stored tokens use AES-256-GCM authenticated encryption.
- **Access Control:** The streaming endpoint verifies that the caller is either the author of the book or that the book is marked public and published.
