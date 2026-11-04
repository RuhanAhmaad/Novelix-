# NOVELIX 4.0 — Admin Security Report

Generated: 2026-11-04

---

## Admin Authentication Model

NOVELIX uses **Firebase Custom Claims** for admin access control — the industry-standard approach for Firebase applications.

```
Firebase Auth Token → { admin: true } claim
         ↓
Verified server-side in Cloud Functions
         ↓
Verified client-side via getIdTokenResult()
         ↓
Admin Dashboard unlocked in NOVELIX UI
```

---

## Admin Access Points

### 1. Admin Dashboard (UI)
- **Trigger**: Click NOVELIX logo 5 times → type `admin` in retro terminal
- **Gate**: `user.getIdTokenResult()` must return `claims.admin === true`
- **What it shows**: User management, verification requests, publications, storage, announcements, audit logs
- **If non-admin tries**: Terminal returns `Access denied. No admin privileges.`

### 2. `setAdminRole` Cloud Function
- **Purpose**: Bootstrap the first admin user
- **Protection**: Requires `ADMIN_BOOTSTRAP_SECRET` environment variable match
- **One-time use**: After bootstrap, change the secret or disable the function

### 3. `reviewCreatorVerification` Cloud Function
- **Protection**: `request.auth.token.admin == true` checked server-side
- **Non-admin call**: Returns `unauthenticated` or `permission-denied` error

### 4. `broadcastAnnouncement` Cloud Function
- **Protection**: Same admin claim check
- **Rate limiting**: Not currently implemented — recommended for production

---

## Bootstrap Procedure

### Step 1: Get Your Firebase UID

```javascript
// In browser console on the NOVELIX app (while logged in)
firebase.auth().currentUser.uid
// Copy the returned UID
```

### Step 2: Call the Bootstrap Function

```bash
# Using Firebase CLI
firebase functions:call setAdminRole \
  --data '{"uid":"YOUR_UID","secret":"novelix-admin-secure-init-2026"}' \
  --project novelxa-48f15
```

Or from within the NOVELIX app terminal:
1. Click logo 5 times
2. Type: `setadmin YOUR_UID novelix-admin-secure-init-2026`

### Step 3: Refresh Your Token

Log out and log back in to Firebase Auth so the new custom claim is included in your ID token.

### Step 4: Change the Bootstrap Secret

> **⚠️ CRITICAL**: Change `ADMIN_BOOTSTRAP_SECRET` after bootstrapping your first admin.

```bash
# Using Firebase Functions Gen 2 env
# Edit functions/.env:
ADMIN_BOOTSTRAP_SECRET=your-new-secret-here-change-this

# Redeploy functions
firebase deploy --only functions --project novelxa-48f15
```

---

## Firestore Security Rules — Admin Protections

The following fields are **write-protected** even for authenticated users:

| Field | Collection | Who Can Write |
|-------|-----------|---------------|
| `creatorVerified` | `users/{uid}` | Cloud Functions only (via Admin SDK) |
| `creatorVerificationStatus` | `users/{uid}` | Cloud Functions only |
| `storageQuotaBytes` | `users/{uid}` | Cloud Functions only |
| All fields | `admin_logs/{id}` | Cloud Functions only (append-only) |
| All fields | `announcements/{id}` | Admin user only |

### Key Rule Snippet

```javascript
// From firestore.rules
function isAdmin() {
  return request.auth.token.admin == true ||
         exists(/databases/$(database)/documents/admin_users/$(request.auth.uid));
}

// Users cannot self-elevate creatorVerified
allow update: if request.auth.uid == userId
              && !request.resource.data.diff(resource.data).affectedKeys()
                  .hasAny(['creatorVerified', 'creatorVerificationStatus', 'storageQuotaBytes']);
```

---

## Audit Logging

Every admin action is logged to the `admin_logs` collection:

```
admin_logs/{autoId}
  ├── action (string) — e.g., 'set_admin_role', 'approve_verification', 'broadcast'
  ├── adminUid (string)
  ├── targetUid (string?) — affected user UID if applicable
  ├── details (map) — action-specific metadata
  └── timestamp (timestamp)
```

Logs are:
- **Readable** by admins only (Firestore rules)
- **Writable** by Cloud Functions only (Admin SDK bypasses rules)
- **Not deletable** by any user (no delete rule granted)

---

## Security Vulnerabilities & Recommendations

### Current Vulnerabilities

| Issue | Severity | Description |
|-------|---------|-------------|
| ImgBB API key exposed | 🟡 Medium | Key `a9985ccf572a0e05bce242e27cf8be33` is in frontend JS. Anyone can extract it from the HTML and use it to upload images to your ImgBB account. |
| Bootstrap secret in source | 🟡 Medium | Default `novelix-admin-secure-init-2026` is in `functions/index.js`. Change it before production. |
| Drive access tokens in Firestore | 🟡 Medium | Short-lived but stored client-accessible. Users can only read their own docs (Firestore rules protect this). |
| No FCM rate limiting | 🟢 Low | `broadcastAnnouncement` has no rate limit — a compromised admin account could spam users. |
| Admin terminal trigger | 🟢 Low | 5-click logo trigger is security-through-obscurity only; actual gate is the Firebase claim check. |

### Recommended Fixes

1. **ImgBB key**: Move to Cloud Function proxy. Frontend posts image → Cloud Function → ImgBB API.
2. **Bootstrap secret**: Set via Firebase environment variable, not hardcoded.
3. **Drive tokens**: Implement server-side refresh token flow (Phase 2).
4. **Rate limiting**: Add Firebase App Check + Cloud Functions rate limiting for admin callables.

---

## Admin Dashboard Features

| Tab | Features |
|-----|---------|
| Users | Search users, view stats, grant/revoke admin |
| Verifications | Review pending creator applications, approve/reject with note |
| Publications | View all books, force-remove violating content |
| Storage | View top storage consumers, adjust quotas |
| Announcements | Compose and broadcast FCM announcements |
| Audit Logs | Full paginated audit trail |
