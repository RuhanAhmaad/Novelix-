# NOVELIX 4.0 — Firebase Features Report

Generated: 2026-11-04

---

## Firebase Services in Use

| Service | Status | Purpose |
|---------|--------|---------|
| Firebase Authentication | ✅ Active | Email/Password + Google Sign-In |
| Cloud Firestore | ✅ Active | All user, book, chapter, notification data |
| Firebase Storage | ✅ Active | PDF/EPUB uploads, cover images, avatars |
| Firebase Cloud Messaging (FCM) | ✅ Configured | Push notifications to followers |
| Cloud Functions (Gen 2) | ✅ Deployed | 7 backend functions (see below) |

---

## Cloud Functions

### 1. `setAdminRole` (Callable)
- **Trigger**: HTTPS Callable
- **Purpose**: Bootstraps the first admin user. Protected by `ADMIN_BOOTSTRAP_SECRET` env variable.
- **Input**: `{ uid, secret }`
- **Output**: Sets Firebase custom claim `{ admin: true }` on the given UID.
- **Security**: One-time bootstrap; logs action to `admin_logs`.

### 2. `onReviewWritten` (Firestore Trigger)
- **Trigger**: `books/{bookId}/reviews/{reviewId}` — onCreate / onUpdate / onDelete
- **Purpose**: Recalculates `averageRating` and `reviewCount` on the parent book document.
- **Algorithm**: Reads all reviews in the subcollection, computes mean, writes back atomically.

### 3. `onChapterPublished` (Firestore Trigger)
- **Trigger**: `books/{bookId}/chapters/{chapterId}` — onCreate
- **Purpose**: Sends FCM push notification to all followers of the book's author when a new chapter is published.
- **Flow**: Reads `users/{authorId}/followers`, collects FCM tokens from `users/{followerId}/fcm_tokens`, sends multicast message.
- **Payload**: Title = book title, Body = "New chapter: {chapterTitle}", data = `{ bookId, chapterId }`.

### 4. `onFollowCreated` (Firestore Trigger)
- **Trigger**: `users/{userId}/followers/{followerId}` — onCreate
- **Purpose**: Sends FCM notification to the followed user and writes a notification document.
- **Notification doc**: Written to `users/{userId}/notifications/{id}` with type `follow`.

### 5. `onBookStorageUpdated` (Firestore Trigger)
- **Trigger**: `books/{bookId}` — onWrite
- **Purpose**: Recalculates total storage used by the author across all their books.
- **Fields tracked**: `languages[].fileSize`, `coverSize` (bytes).
- **Output**: Writes `storageUsedBytes` to `users/{authorId}`.
- **Default estimate**: Files without `fileSize` metadata count as 2 MB.

### 6. `reviewCreatorVerification` (Callable — Admin Only)
- **Trigger**: HTTPS Callable
- **Purpose**: Allows admin to approve or reject a creator verification request.
- **Input**: `{ requestId, decision: 'approved'|'rejected', adminNote? }`
- **Security**: Checks `request.auth.token.admin == true`. Rejects all others.
- **Flow**: Updates `verification_requests/{requestId}.status`, writes `decidedAt` and `adminNote`. If approved, sets `users/{uid}.creatorVerified = true` and `creatorVerificationStatus = 'approved'`.

### 7. `broadcastAnnouncement` (Callable — Admin Only)
- **Trigger**: HTTPS Callable
- **Purpose**: Sends a platform-wide FCM topic message and writes an announcement to Firestore.
- **Input**: `{ title, body, topic?, data? }`
- **Security**: Admin claim required.
- **Default topic**: `all_users`
- **Output**: FCM topic send + `announcements/{id}` document with `title`, `body`, `createdAt`, `createdBy`.

---

## Firestore Collections

```
users/{uid}
  ├── displayName, email, photoURL, bio
  ├── creatorVerified (bool) — set by admin only
  ├── creatorVerificationStatus — pending/approved/rejected
  ├── storageUsedBytes (number) — computed by Cloud Function
  ├── storageQuotaBytes (number) — default 500 MB, set by admin
  ├── emailVerified (bool)
  ├── followers/ (subcollection)
  ├── following/ (subcollection)
  ├── notifications/ (subcollection)
  └── fcm_tokens/ (subcollection)

books/{bookId}
  ├── title, description, genre, coverURL
  ├── authorId, authorName
  ├── averageRating, reviewCount (computed)
  ├── languages[] — { lang, fileURL, fileSize }
  ├── coverSize (bytes)
  ├── chapters/ (subcollection)
  └── reviews/ (subcollection)

verification_requests/{requestId}
  ├── uid, displayName, email
  ├── reason, socialLinks
  ├── status — pending/approved/rejected
  ├── submittedAt, decidedAt
  └── adminNote

announcements/{id}
  ├── title, body, topic
  ├── createdAt, createdBy
  └── data (map)

admin_logs/{id}
  ├── action, adminUid
  ├── targetUid, details
  └── timestamp
```

---

## Security Summary

- All admin actions require Firebase custom claim `admin: true`
- `creatorVerified`, `creatorVerificationStatus`, `storageQuotaBytes` are **write-protected** in Firestore rules — only Cloud Functions can update them
- FCM tokens stored server-side under user's subcollection, never exposed to other users
- Storage rules enforce 100 MB max for PDFs, 15 MB for images

---

## Deployment Commands

```bash
# Deploy all Firebase resources
firebase deploy --project novelxa-48f15

# Deploy only functions
firebase deploy --only functions --project novelxa-48f15

# Deploy only Firestore rules + indexes
firebase deploy --only firestore --project novelxa-48f15

# Deploy only Storage rules
firebase deploy --only storage --project novelxa-48f15

# Bootstrap first admin (replace values)
# Call the setAdminRole Cloud Function with your UID and bootstrap secret
```

---

## Environment Variables for Cloud Functions

Set these in Firebase before deploying functions:

```bash
firebase functions:config:set admin.bootstrap_secret="YOUR_SECURE_SECRET" --project novelxa-48f15
```

Or using the new Gen 2 approach, set in `.env` file in the `functions/` directory:
```
ADMIN_BOOTSTRAP_SECRET=novelix-admin-secure-init-2026
```

> **Important**: Change the default `ADMIN_BOOTSTRAP_SECRET` before production deployment.
