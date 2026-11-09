# NOVELIX 8.0 — Security Audit & Hardening Report

**Generated:** 2026-11-09  
**Scope:** Client Assets, Third-Party APIs, Secret Manager, Admin Claims

---

## 1. Third-Party API Key Eradication

The previous build contained an unencrypted ImgBB API key (`a9985ccf572a0e05bce242e27cf8be33`) in client code.
- **Remediation:** Completely removed from all client JavaScript, environment configuration files (`.env.local`), documentation (`README.md`, `SETUP.md`), and server upload routes.
- **Storage Migration:** All file and image uploads now stream directly to Firebase Storage with authenticated user validation.

---

## 2. Server-Side Admin Authorization

- **Custom Claims Validation:** Admin dashboard access requires `token.claims.admin === true`, cryptographically signed by Firebase Auth.
- **Terminal Lockdown:** The terminal `admin` command executes the Cloud Function `verifyAdminStatus`, verifying server-side records before granting access. Unauthorized attempts yield `PERMISSION DENIED`.
- **Zero Client Bypasses:** No client-side passwords, default PINs, or local storage flags can trigger admin privileges.

---

## 3. Google Drive OAuth Zero-Leak Protocol

- **Client Secrets:** Protected in GCP Secret Manager (`GOOGLE_DRIVE_OAUTH_CLIENT_JSON`).
- **Token Encryption:** User refresh tokens are encrypted at rest with AES-256-GCM using a 32-character encryption key before being written to Firestore.
- **Streaming Proxy:** The Cloud Function `getReaderPdfData` proxies manuscript bytes to authorized readers without exposing Drive access tokens or requiring public Drive file links.
