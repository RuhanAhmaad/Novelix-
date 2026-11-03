# NOVELIX 2.1 — Feature Status

> Last updated: 2026-11-03  
> Version: 2.1.0  
> Build status: CI/CD via GitHub Actions

---

## Legend

| Status | Meaning |
|--------|---------|
| ✅ VERIFIED | Feature implemented, backend integrated, tested, and confirmed working |
| 🟢 IMPLEMENTED | Feature is implemented and connected to backend |
| 🟡 IN PROGRESS | Partially implemented |
| ⚙️ CONFIGURATION REQUIRED | Feature requires external service credentials or setup |
| 🔴 NOT STARTED | Feature has not been started |

---

## Phase 1 — Authentication

| Feature | Status | Notes |
|---------|--------|-------|
| Email registration | 🟢 IMPLEMENTED | Supabase Auth — real signup, email confirmation |
| Email login | 🟢 IMPLEMENTED | Supabase Auth — real credentials required |
| Google OAuth | ⚙️ CONFIGURATION REQUIRED | Requires `GOOGLE_CLIENT_ID` in Supabase Auth providers. Set up at supabase.co → Authentication → Providers → Google |
| Password reset | 🟢 IMPLEMENTED | Supabase sends real reset email |
| Email verification | 🟢 IMPLEMENTED | Confirmation email sent on signup |
| Persistent session | 🟢 IMPLEMENTED | Auto-refresh tokens, `persistSession: true` |
| Auto profile creation | 🟢 IMPLEMENTED | DB trigger `on_auth_user_created` creates profile row |
| Session recovery | 🟢 IMPLEMENTED | `supabase.auth.getSession()` on app start |
| Sign out | 🟢 IMPLEMENTED | Clears server session |
| No local auth fallback | ✅ VERIFIED | No localStorage user creation — Supabase is authoritative |

---

## Phase 2 — Real-Time Subscriptions

| Feature | Status | Notes |
|---------|--------|-------|
| Books realtime channel | 🟢 IMPLEMENTED | `supabase_realtime` publication enabled |
| Notifications realtime | 🟢 IMPLEMENTED | Per-user channel with filter |
| Reviews realtime | 🟢 IMPLEMENTED | Live review updates in book detail |
| New book appears instantly | 🟢 IMPLEMENTED | INSERT event → `handleBooksRealtime()` |
| Book deletion propagates | 🟢 IMPLEMENTED | DELETE event → remove from STATE |
| Subscription cleanup | 🟢 IMPLEMENTED | `cleanupRealtime()` removes all channels |
| LIVE indicator | 🟢 IMPLEMENTED | Shows when channel status = SUBSCRIBED |

---

## Phase 3 — Book Publishing

| Feature | Status | Notes |
|---------|--------|-------|
| Publish book | 🟢 IMPLEMENTED | Real INSERT to `books` table |
| Cover upload (ImgBB) | 🟢 IMPLEMENTED | Real POST to api.imgbb.com |
| PDF upload (Supabase Storage) | 🟢 IMPLEMENTED | `book-files` bucket |
| Multiple language editions | 🟢 IMPLEMENTED | `book_languages` table |
| Content types (8 types) | 🟢 IMPLEMENTED | book, novel, manga, manhwa, comic, story, series, edu |
| Multiple genres (up to 5) | 🟢 IMPLEMENTED | Stored as `TEXT[]` in DB |
| Draft saving | 🟢 IMPLEMENTED | `publish_status = 'draft'` |
| Visibility settings | 🟢 IMPLEMENTED | public / unlisted / private |
| Publication status | 🟢 IMPLEMENTED | ongoing / completed / hiatus |
| Edit publication | 🟡 IN PROGRESS | UI needed; DB supports it |
| Delete publication | 🟢 IMPLEMENTED | Real DELETE from `books` |
| Multiple authors / roles | 🟡 IN PROGRESS | `book_authors` table ready; invite UI pending |
| Author invitation system | 🔴 NOT STARTED | Email invite flow not yet implemented |
| Scheduled publishing | 🔴 NOT STARTED | Requires server-side cron job |

---

## Phase 4 — ImgBB Cover Upload

| Feature | Status | Notes |
|---------|--------|-------|
| Image selection | 🟢 IMPLEMENTED | Native `<input type="file">` |
| Image preview | 🟢 IMPLEMENTED | `URL.createObjectURL()` |
| Upload to ImgBB | 🟢 IMPLEMENTED | Real multipart POST to api.imgbb.com |
| Upload progress | 🟡 IN PROGRESS | Visual indicator pending |
| Error handling | 🟢 IMPLEMENTED | Shows actual error if upload fails |
| No fake success | ✅ VERIFIED | Only stores URL on confirmed response |
| API key placement | ⚙️ CONFIGURATION REQUIRED | Key is in client — move to server-side endpoint for production security |

---

## Phase 5 — PDF Reader

| Feature | Status | Notes |
|---------|--------|-------|
| PDF.js integration | 🟢 IMPLEMENTED | CDN v3.11.174 |
| Page rendering | 🟢 IMPLEMENTED | Canvas-based rendering |
| Page navigation (prev/next) | 🟢 IMPLEMENTED | |
| Progress slider | 🟢 IMPLEMENTED | Range input synced to page |
| Zoom in/out | 🟢 IMPLEMENTED | Scale from 0.5x to 4x |
| Fullscreen reader | 🟢 IMPLEMENTED | Fixed overlay |
| Reading progress saved | 🟢 IMPLEMENTED | Upserted to `reading_progress` table |
| Resume reading | 🟢 IMPLEMENTED | Progress loaded from DB |
| Language switching | 🟢 IMPLEMENTED | Switch edition → reload PDF |
| Reader themes | 🟡 IN PROGRESS | Theme switcher UI pending |
| Mobile gestures | 🟡 IN PROGRESS | Pinch-to-zoom pending |
| PDF error handling | 🟢 IMPLEMENTED | Shows real error message |

---

## Phase 6 — Manhwa/Manga Reader

| Feature | Status | Notes |
|---------|--------|-------|
| Fullscreen reader | 🟢 IMPLEMENTED | Fixed overlay |
| Vertical scroll | 🟢 IMPLEMENTED | Native scroll |
| Chapter images | 🟢 IMPLEMENTED | Renders from `chapter_images.image_url` |
| PDF fallback | 🟢 IMPLEMENTED | Falls back to PDF reader if no images |
| Chapter navigation | 🟡 IN PROGRESS | Prev/next placeholders |
| Chapter list | 🔴 NOT STARTED | Chapter browser UI pending |
| Chapter image uploads | 🔴 NOT STARTED | Upload UI for authors pending |

---

## Phase 7 — Social System

| Feature | Status | Notes |
|---------|--------|-------|
| Bookmarks | 🟢 IMPLEMENTED | Real `bookmarks` table |
| Likes | 🟢 IMPLEMENTED | Real `likes` table, no duplicates |
| Reviews with ratings | 🟢 IMPLEMENTED | 1–5 stars, real DB insert |
| Duplicate prevention | 🟢 IMPLEMENTED | UNIQUE constraint on DB |
| Comments | 🟡 IN PROGRESS | Table exists; UI pending |
| Comment replies | 🔴 NOT STARTED | |
| Follow / Unfollow | 🟡 IN PROGRESS | `follows` table ready; UI button pending on profiles |
| Notifications | 🟢 IMPLEMENTED | Real-time via Supabase |
| Reading lists | 🟢 IMPLEMENTED | Create/view lists |
| Content reporting | 🔴 NOT STARTED | |

---

## Phase 8 — User Profiles

| Feature | Status | Notes |
|---------|--------|-------|
| Auto-created profile | 🟢 IMPLEMENTED | DB trigger on auth.users insert |
| Display name & bio | 🟢 IMPLEMENTED | Editable in Settings tab |
| Avatar upload (ImgBB) | 🟢 IMPLEMENTED | |
| Cover image upload | 🟢 IMPLEMENTED | |
| Published works list | 🟢 IMPLEMENTED | Real query from `books` table |
| Follower / following stats | 🟢 IMPLEMENTED | Real count from `follows` table |
| View count stats | 🟢 IMPLEMENTED | Sum from `books.view_count` |
| Analytics tab | 🟢 IMPLEMENTED | DB-derived only |
| Privacy settings | 🟡 IN PROGRESS | DB field exists; enforcement pending |

---

## Phase 9 — Admin Dashboard

| Feature | Status | Notes |
|---------|--------|-------|
| Role verification | 🟢 IMPLEMENTED | Checks `user_roles` table on every open |
| User list | 🟢 IMPLEMENTED | Real query from `profiles` |
| Book list + delete | 🟢 IMPLEMENTED | Admin can delete any book |
| Reports list | 🟢 IMPLEMENTED | Real `reports` table |
| Admin logs | 🟢 IMPLEMENTED | Real `admin_logs` table |
| No frontend-only gate | ✅ VERIFIED | Admin panel checks DB role — not localStorage |
| Publication approval | 🟡 IN PROGRESS | Status update UI pending |
| Author verification | 🔴 NOT STARTED | |
| Advertisement management | 🔴 NOT STARTED | UI pending |
| Platform analytics | 🟡 IN PROGRESS | Basic stats implemented |

---

## Phase 10 — Developer Terminal

| Feature | Status | Notes |
|---------|--------|-------|
| 5-click logo activation | 🟢 IMPLEMENTED | |
| `help` command | 🟢 IMPLEMENTED | |
| `status` command | 🟢 IMPLEMENTED | Checks real connection |
| `db` command | 🟢 IMPLEMENTED | Real Supabase query |
| `reload` command | 🟢 IMPLEMENTED | Refreshes book list |
| `admin` command | 🟢 IMPLEMENTED | Opens admin (role-gated) |
| `version`, `user`, `auth` | 🟢 IMPLEMENTED | |
| `cache`, `clear`, `exit` | 🟢 IMPLEMENTED | |
| No secrets exposed | ✅ VERIFIED | No tokens/keys printed |
| No auth bypass | ✅ VERIFIED | Terminal cannot escalate privileges |

---

## Phase 11 — Google Drive

| Feature | Status | Notes |
|---------|--------|-------|
| `google_drive_accounts` table | 🟢 IMPLEMENTED | Full schema with encrypted token fields |
| Multiple accounts per user | 🟢 IMPLEMENTED | DB supports it |
| Connect account OAuth | ⚙️ CONFIGURATION REQUIRED | Requires `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` |
| Token encryption | ⚙️ CONFIGURATION REQUIRED | `TOKEN_ENCRYPTION_SECRET` env var needed |
| Disconnect account | 🟢 IMPLEMENTED | Real DB delete |
| Browse Drive files | ⚙️ CONFIGURATION REQUIRED | Requires OAuth tokens from connected account |
| No fake accounts | ✅ VERIFIED | No hardcoded Drive accounts |

---

## Phase 12 — No Fake Data

| Requirement | Status |
|-------------|--------|
| No DEFAULT_PUBLICATIONS | ✅ VERIFIED |
| No hardcoded authors | ✅ VERIFIED |
| No fake ratings | ✅ VERIFIED |
| No local auth fallback | ✅ VERIFIED |
| Empty state shown when DB empty | ✅ VERIFIED |
| All data from Supabase | ✅ VERIFIED |

---

## Supabase Database

| Table | Status |
|-------|--------|
| profiles | 🟢 Created with triggers |
| user_roles | 🟢 Created with RLS |
| books | 🟢 Created with RLS + triggers |
| book_authors | 🟢 Created |
| book_languages | 🟢 Created |
| book_files | 🟢 Created |
| book_series | 🟢 Created |
| series_books | 🟢 Created |
| chapters | 🟢 Created |
| chapter_images | 🟢 Created |
| google_drive_accounts | 🟢 Created |
| reading_progress | 🟢 Created |
| bookmarks | 🟢 Created |
| reading_lists | 🟢 Created |
| reading_list_items | 🟢 Created |
| reviews | 🟢 Created |
| comments | 🟢 Created |
| follows | 🟢 Created |
| likes | 🟢 Created |
| notifications | 🟢 Created |
| advertisements | 🟢 Created |
| ad_events | 🟢 Created |
| reports | 🟢 Created |
| admin_logs | 🟢 Created |

---

## Required Configuration (Before Going Live)

```env
# Supabase (already configured)
NEXT_PUBLIC_SUPABASE_URL=https://gzwpfvhmjweeydiwdsga.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=sb_publishable_APwu-OfPQmtnj-f-pwxfZw_OxiwM8A1

# Google OAuth — set in Supabase Dashboard → Auth → Providers → Google
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret

# ImgBB (currently client-side — move to server for production)
IMGBB_API_KEY=a9985ccf572a0e05bce242e27cf8be33

# Token encryption (for Google Drive OAuth tokens)
TOKEN_ENCRYPTION_SECRET=32-char-random-secret
```

### Steps to activate Google OAuth:
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create OAuth 2.0 Client ID (Web Application)
3. Add redirect URI: `https://gzwpfvhmjweeydiwdsga.supabase.co/auth/v1/callback`
4. Copy Client ID + Secret → Supabase Dashboard → Authentication → Providers → Google

---

## Android APK

| Item | Status |
|------|--------|
| Capacitor 8 integration | ✅ VERIFIED |
| App ID `com.novelix.app` | ✅ VERIFIED |
| Java 21 / Node 22 build | ✅ VERIFIED |
| GitHub Actions CI | ✅ VERIFIED |
| Safe area insets | 🟢 IMPLEMENTED |
| Android back navigation | 🟢 IMPLEMENTED |
| Offline banner | 🟢 IMPLEMENTED |
| Splash screen | ✅ VERIFIED |

---

*NOVELIX 2.1 — READ BEYOND LIMITS. CREATE WITHOUT BOUNDARIES.*
