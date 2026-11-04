# NOVELIX 4.0 — Push Notification Setup Guide

Generated: 2026-11-04

---

## Overview

NOVELIX 4.0 uses **Firebase Cloud Messaging (FCM)** for push notifications. Notifications are sent when:
- A followed author publishes a new chapter
- Another user follows you
- An admin broadcasts a platform announcement

---

## FCM Configuration

### Firebase Project Settings

1. Go to [Firebase Console](https://console.firebase.google.com) → Project `novelxa-48f15`
2. Navigate to **Project Settings → Cloud Messaging**
3. Confirm:
   - **Server key** is present (used by Cloud Functions automatically via Admin SDK)
   - **Android** app `com.novelix.app` is registered

### Android FCM Setup (Capacitor)

FCM works automatically on Android via the `google-services.json` file already in `android/app/`. The file contains the `messaging_sender_id: 239783323113`.

For the full native FCM experience (background notifications), install the Capacitor Push Notifications plugin:

```bash
pnpm add @capacitor/push-notifications
npx cap sync android
```

Then add to `android/app/src/main/AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
```

---

## Token Registration

When a user logs in, the app registers their FCM token to Firestore:

```
users/{uid}/fcm_tokens/{tokenId}
  ├── token (string)   — the FCM registration token
  ├── platform (string) — 'android' | 'web' | 'ios'
  └── updatedAt (timestamp)
```

The Cloud Function `onChapterPublished` and `onFollowCreated` read these tokens to send targeted notifications.

---

## Notification Types

| Type | Trigger | Cloud Function | FCM Topic |
|------|---------|---------------|-----------|
| New chapter | Chapter created in Firestore | `onChapterPublished` | Direct (token-based) |
| New follower | Follow doc created | `onFollowCreated` | Direct (token-based) |
| Announcement | Admin broadcasts | `broadcastAnnouncement` | `all_users` topic |

---

## FCM Topic Subscription

For announcements, users should be subscribed to the `all_users` FCM topic. This can be done client-side:

```javascript
// In app startup (after FCM token obtained)
messaging.subscribeToTopic(token, 'all_users')
```

Or server-side via Admin SDK in a Cloud Function.

---

## Notification Preferences (In-App)

Users can manage notification preferences in **Settings → Notifications**:

| Preference | Firestore Field | Default |
|-----------|----------------|---------|
| New chapter alerts | `notifNewChapter` | true |
| New follower alerts | `notifNewFollower` | true |
| Announcements | `notifAnnouncements` | true |
| Email notifications | `notifEmail` | false |

These are stored at `users/{uid}.notifNewChapter`, etc.

The Cloud Functions respect these preferences:
- If `notifNewChapter == false`, the `onChapterPublished` function skips sending to that user
- If `notifNewFollower == false`, the `onFollowCreated` function skips sending to that user

---

## In-App Notification Center

NOVELIX 4.0 includes a real-time notification center accessible via the bell icon:

- Displays notifications from `users/{uid}/notifications/` subcollection
- Supports **Mark all as read** (updates `read: true` on all docs)
- Supports **Delete** individual notifications
- Real-time listener via Firestore `onSnapshot`

### Notification Document Structure

```
users/{uid}/notifications/{notifId}
  ├── type (string) — 'follow' | 'chapter' | 'announcement' | 'verification'
  ├── title (string)
  ├── body (string)
  ├── read (bool) — default false
  ├── createdAt (timestamp)
  ├── data (map) — { bookId?, chapterId?, fromUid? }
  └── iconType (string) — for UI rendering
```

---

## Testing Notifications

### Method 1: Firebase Console
1. Go to Firebase Console → **Engage → Messaging**
2. Click **New campaign → Firebase Notification Messages**
3. Fill in title and body
4. Under **Target**, choose **Topic** → `all_users`
5. Click **Review** → **Publish**

### Method 2: Admin Dashboard (In-App)
1. Open NOVELIX app as admin user
2. Click the NOVELIX logo 5 times to open the retro terminal
3. Type `admin` to open the Admin Dashboard
4. Navigate to **Announcements** tab
5. Fill in title, body, and optional topic
6. Click **Broadcast Announcement**

### Method 3: Direct API Call
```bash
curl -X POST https://us-central1-novelxa-48f15.cloudfunctions.net/broadcastAnnouncement \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ID_TOKEN" \
  -d '{"data": {"title": "Test", "body": "Test notification", "topic": "all_users"}}'
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Notifications not received on Android | Check `POST_NOTIFICATIONS` permission in AndroidManifest |
| FCM token not saved | Check Firestore rules for `fcm_tokens` subcollection |
| Cloud Function not triggered | Check Firebase Functions logs: `firebase functions:log` |
| Background notifications not shown | Install `@capacitor/push-notifications` native plugin |
