# NOVELIX 2.2 — Supabase to Google Firebase Migration Report

**Date:** 2026-11-03  
**Target:** NOVELIX Android & Web Platform  
**Target Project:** `novelxa-48f15`  
**Package:** `com.novelix.app`  

---

## 1. Executive Summary

The NOVELIX platform has been completely migrated from Supabase to Google Firebase in accordance with the NOVELIX 2.2 specification. All backend services—Identity, Database, Object Storage, Push Notifications, Security Rules, and Serverless Operations—are now managed by Firebase.

The original NOVELIX visual identity (deep black `#070709`, electric violet `#8b5cf6`, gold `#f59e0b`, glassmorphism, responsive mobile layout, PDF reader, and 5-click retro developer terminal) has been 100% preserved and upgraded.

---

## 2. Configuration & Credentials Verification

The attached `google-services.json` was verified and placed into `android/app/google-services.json`:

```json
{
  "project_info": {
    "project_number": "239783323113",
    "firebase_url": "https://novelxa-48f15-default-rtdb.firebaseio.com",
    "project_id": "novelxa-48f15",
    "storage_bucket": "novelxa-48f15.firebasestorage.app"
  },
  "client": [
    {
      "client_info": {
        "mobilesdk_app_id": "1:239783323113:android:72ab9f84efe4b4957f5778",
        "android_client_info": {
          "package_name": "com.novelix.app"
        }
      },
      "api_key": [{ "current_key": "AIzaSyDzlkwY8Xcyyp-fh_JS_z2ob4xgc4YnLps" }]
    }
  ]
}
```

- **Android Package:** `com.novelix.app` (Match verified)
- **Firebase Project ID:** `novelxa-48f15`
- **Firebase Storage Bucket:** `novelxa-48f15.firebasestorage.app`
- **Web API Key:** `AIzaSyDzlkwY8Xcyyp-fh_JS_z2ob4xgc4YnLps`
- **Auth Domain:** `novelxa-48f15.firebaseapp.com`

---

## 3. Detailed Component Migration

| Service | Supabase Implementation (v2.1) | Firebase Implementation (v2.2) |
|---|---|---|
| **Authentication** | Supabase Auth (`@supabase/supabase-js`) | **Firebase Authentication** (`firebase.auth()`) with Email/Password & Google Sign-In |
| **Realtime Database** | PostgreSQL + Realtime channels (`supabase.channel`) | **Cloud Firestore** (`firebase.firestore()`) with atomic listeners (`onSnapshot`) & offline disk persistence |
| **Media Storage** | Supabase Storage (`storage.from('book-files')`) | **Firebase Storage** (`storage.ref('books/{id}/pdfs')`) with direct binary upload |
| **Security Rules** | PostgreSQL Row-Level Security (RLS) | **Firestore Security Rules** (`firestore.rules`) & **Storage Rules** (`storage.rules`) |
| **Serverless Logic** | PostgreSQL triggers & Edge Functions | **Cloud Functions for Firebase** (`functions/index.js`) for review aggregation, follower alerts, and custom admin claims |
| **Push Notifications** | Supabase DB inserts | **Firebase Cloud Messaging (FCM)** + in-app Firestore notifications subcollection |

---

## 4. Firestore Database Schema

### `users/{userId}`
- `uid`: string (matches Firebase Auth UID)
- `email`: string
- `displayName`: string
- `photoURL`: string
- `coverURL`: string
- `bio`: string
- `isAdmin`: boolean
- `createdAt`: Timestamp
- `updatedAt`: Timestamp
- **Subcollections:**
  - `bookmarks/{bookId}`
  - `likes/{bookId}`
  - `reading_progress/{bookId}`
  - `notifications/{notifId}`
  - `reading_lists/{listId}`

### `books/{bookId}`
- `id`: string
- `title`: string
- `description`: string
- `contentType`: string (`book`, `novel`, `manga`, `manhwa`, `comic`, `short_story`, `series`, `educational`)
- `genres`: array of strings
- `coverUrl`: string (Firebase Storage URL or ImgBB fallback)
- `status`: string (`ongoing`, `completed`, `hiatus`, `draft`)
- `visibility`: string (`public`, `unlisted`, `private`)
- `publishStatus`: string (`draft`, `published`, `archived`)
- `languages`: array of objects `{ language, languageCode, fileUrl, fileName, fileSize, uploadedAt }`
- `authorId`: string
- `authorName`: string
- `authorPhoto`: string
- `viewCount`: number (atomic increment)
- `likeCount`: number (atomic increment)
- `bookmarkCount`: number (atomic increment)
- `avgRating`: number (computed by Cloud Function)
- `ratingCount`: number
- `createdAt`: Timestamp
- `updatedAt`: Timestamp
- **Subcollections:**
  - `chapters/{chapterId}` (manhwa/manga images)
  - `reviews/{userId}` (rating 1-5, review content)
  - `comments/{commentId}`

### `authors/{authorId}/followers/{followerId}`
- Stores follower relationships between readers and authors.

### `advertisements/{adId}`
- `title`, `description`, `imageUrl`, `destinationUrl`, `placement`, `campaignStart`, `campaignEnd`, `isActive`, `impressions`, `clicks`

### `admin_users/{userId}`
- Privileged administrator documents checked server-side for dashboard operations.

---

## 5. Security Rules Deployed

1. **`firestore.rules`**:
   - Profiles: Readable by all, writable only by owner (`request.auth.uid == userId`). Privileged fields (`isAdmin`, `role`) cannot be modified by clients.
   - Books: Public books readable by all; drafting and edits restricted to `authorId == request.auth.uid` or admin claim.
   - User subcollections (bookmarks, likes, progress, notifications): Strictly restricted to `request.auth.uid == userId`.
   - Admin collections (`admin_logs`, `admin_settings`, `admin_users`): Restricted to verified admin custom token claim.

2. **`storage.rules`**:
   - File types enforced (PDFs: `application/pdf` <= 50MB; Images: `image/*` <= 10MB).
   - Authors can write only to their designated paths.

---

## 6. What Was Removed / Deprecated

- Removed `@supabase/supabase-js` and `@supabase/ssr` from `package.json`.
- Removed Supabase client initialization from client-side bundles.
- Removed Supabase OAuth redirect URL from `android/app/src/main/AndroidManifest.xml`, replaced with Firebase Auth handler (`novelxa-48f15.firebaseapp.com`).
- Deprecated legacy `.env.local` Supabase parameters, replaced with Firebase project variables.
- Legacy Supabase SQL migration files are preserved in `supabase/` as historical reference and backup as requested.
