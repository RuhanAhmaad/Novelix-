# NOVELIX — Premium UI Redesign & Architecture Report

**Project:** NOVELIX 4.0 Digital Publishing Platform  
**Target Platform:** Android (Capacitor Native) & Web  
**Visual Style:** Luxury Editorial Dark Mode (OLED Black, Midnight Violet, Electric Amethyst)  
**Date:** November 4, 2026  

---

## 1. Visual Identity & Design System

The NOVELIX UI has been redesigned to reflect a luxury editorial publishing platform, replacing generic UI components with custom-crafted, GPU-accelerated surfaces.

### Color Palette
- **Background Root (`app-bg`):** `#0B0B10` — Pure deep obsidian canvas.
- **Sub-surface (`app-sub`):** `#14141D` — Elevated slate container layer.
- **Card Surface (`app-surface`):** `#1B1B27` — Interactive editorial element surface.
- **Structural Border (`app-border`):** `#262638` — Hairline borders (1px) with subtle ambient separation.
- **Primary Accent (`app-primary`):** `#9270FF` — Electric amethyst glow.
- **Secondary Accent (`app-secondary`):** `#B9A4FF` — Soft lavender typography and pill highlight.
- **Status Green:** `#34A853` — Connected state with animated radar pulse.
- **Typography:**
  - Headlines & Brand: `Manrope` (Geometric modern editorial sans)
  - Editorial Accents: `Playfair Display` (Classic serif for literary titles)
  - Body & UI Controls: `Inter` (High-legibility sans-serif)

### Hardware Acceleration & Compositing
All interactive cards, modals, and navigation components implement 3D transforms:
- `transform: translateZ(0);` and `backface-visibility: hidden;` to force GPU layer compositing.
- Fast interactive tap feedback: `scale3d(0.97, 0.97, 1)` on active press.
- Smooth transitions with cubic bezier easing: `cubic-bezier(0.2, 0.9, 0.3, 1)`.

---

## 2. Comprehensive 14-Screen Improvements

### 1. Splash Screen & Onboarding
- **Redesign:** Hardware-accelerated entrance with a pulsing electric glow backdrop (`pulse-glow`).
- **Brand Geometry:** Custom SVG geometric emblem with amethyst stroke and golden dot accent.
- **Motion:** Animated progress track with smooth fade/scale transition into the main application.

### 2. Login & Registration Modal (`#authModal`)
- **Redesign:** Multi-mode tabbed interface supporting Sign In, Register, and Forgot Password recovery.
- **Inputs:** Floating labels, password visibility toggles (`👁`), remember session checkbox.
- **Google OAuth:** Native branded Google Sign-In button with official four-color SVG glyph.
- **Security:** In-app validation with clear error feedback and zero exposure of internal Firebase errors.

### 3. Home & Discovery (`#page-home`)
- **Hero Shelf:** "Featured Releases" horizontal smooth-scrolling carousel with dark editorial gradients.
- **Format Filter Pills:** Quick filters for Books, Novels, Manhwa, Manga, and Comics with active glow.
- **Search:** Instant search bar with debounced query execution across titles, genres, and authors.
- **Skeletons:** Animated two-phase wave shimmer (`skeleton-box`) during async Firestore fetching.

### 4. Book & Novel Details (`#bookDetailModal`)
- **Modal Sheet:** Bottom sheet with 85vh maximum height and momentum scrolling.
- **Artwork:** High-resolution cover artwork container with 3D drop-shadow.
- **Metadata:** Star rating, readership count, format badges, and synopsis text block.
- **Edition Picker:** Multi-edition selection list (Language editions, formats, file sizes).
- **Actions:** "Start Reading" and "Bookmark" with live Firestore state sync.

### 5. PDF Reader (`#readerModal` — Engine A)
- **Engine:** PDF.js v3.11 with dedicated worker thread.
- **Viewport:** High-contrast reading viewport with zoom controls (`+` / `-` from 80% to 250%).
- **Navigation:** Header page indicator (`X / Total`), Previous/Next pagination buttons.
- **Persistence:** Reading progress automatically synced to `users/{uid}/reading_progress/{bookId}`.

### 6. Manhwa & Comic Reader (`#readerModal` — Engine B)
- **Scroll Engine:** Vertical continuous waterfall layout optimized for webtoons and manhwa.
- **Responsive:** Centered maximum-width container (`max-w-xl`) preventing pixel distortion on tablets.
- **Touch Navigation:** Tap zones for smooth continuous scrolling.

### 7. Publishing Studio (`#page-publish`)
- **Multi-Edition Publisher:** Dynamic edition manager allowing authors to publish multiple formats.
- **Drive Cloud Link:** Direct button to import manuscripts directly from connected Google Drive.
- **Real-time Quota Tracker:** Storage bar showing total quota (500 MB), space used, and draft space.
- **Artwork Upload:** Dual-channel cover upload (local asset and ImgBB cloud hosting).

### 8. Author Profile (`#page-profile`)
- **Banner & Avatar:** Photo upload via ImgBB with fallback letter avatar.
- **Verified Creator Badge:** Amethyst `★ Verified Creator` badge for authenticated authors.
- **5-Metric Grid:** Published Works, Total Chapters, Followers, Following, and Read counts.
- **Tabs:** Published works showcase, Reading library, Reviews, and Author biography.

### 9. Reader Profile (`#page-profile`)
- **Tabs:** Private library bookmarks, user reading statistics, and user reviews.
- **Settings Access:** Direct shortcut to security, notification preferences, and storage settings.

### 10. Library & Bookmarks (`#page-library`)
- **Subtabs:** "Continue Reading" (showing current reading page and resume button) and "Bookmarks".
- **Real-time Sync:** Firestore snapshot listener instantly updates whenever bookmarks are added.
- **Empty States:** Custom empty state card with shortcut to explore new titles.

### 11. Google Drive Connection Screen (`#settingsSec-drive` & `#page-drive`)
- **Dedicated Hub:** Full-page screen (`#page-drive`) and Settings integration.
- **Connect Button:** Gradient button (`#4285F4` to `#34A853`) initiating server-side OAuth flow in system browser.
- **Multi-Account Card:** Displays connected Google account email, profile image/initials, and status dot.
- **File Browser (`#drivePickerModal`):** Search filter, multi-account switcher dropdown, and PDF list.
- **Import Progress Bar:** Animated progress shimmer showing sync status during manuscript import.
- **Real Actions:** Browse files, import manuscript, and disconnect account.

### 12. Notifications Center (`#notifModal`)
- **Sheet Modal:** 80vh bottom sheet with unread indicators and "Mark All as Read" action.
- **Categories:** Broadcast announcements, new chapter alerts, and creator verification updates.

### 13. Settings Console (`#settingsModal`)
- **Sections:**
  - Account Profile (Display name, @handle, password update, email verification)
  - Google Drive (Multi-account integration)
  - Storage & Quota (500 MB quota visualization)
  - Notifications (FCM device permissions and alert toggles)
  - Visual Theme (Dark Slate vs Pure OLED Black, font family switcher)
  - Platform About & Build information

### 14. Admin Dashboard (`#adminDashboardModal`)
- **Security Guard:** Restricted to users with custom claim or bootstrap key.
- **Console Tabs:** Users management, Creator verification approvals, Content moderation, Storage policy, and Audit Logs.

---

## 3. Error Handling Architecture (Part 3)

### Global Error Overlay (`#globalErrorOverlay`)
- Clean full-screen modal with icon, human-readable title, detailed explanation, and optional error code.
- **Working Actions:**
  - "Try Again" button: executes the registered retry callback.
  - "Back to Home" button: resets navigation and safely returns to `#page-home`.
- **Never shows raw stack traces:** Sanitizes backend errors and network faults into clean guidance.

### Error Catalog Coverage
| Error Scenario | User-Facing Title | Remediation Action |
|----------------|-------------------|-------------------|
| **Page Not Found** | Page Not Found | Dedicated 404 view with Home & Catalog buttons |
| **Internet Offline** | No Internet Connection | In-app cache mode banner with auto-reconnect |
| **Auth Expiration** | Authentication Required | Modal sign-in prompt preserving draft state |
| **OAuth Mismatch/Denial**| Google Authorization Issue | Explains system browser requirement with retry |
| **Missing Functions** | Cloud Service Unavailable | Explains pending deployment without crashing |
| **Permission Denied** | Permission Denied | Informs user of missing creator/admin credentials |
| **PDF Import Failure** | PDF Import Failed | Checks size quota and file validity with retry |
| **Server Fault** | Cloud Backend Error | Displays clean message with retry action |
