# NOVELIX — Read Beyond Limits. Create Without Boundaries.

A digital publishing platform for books, novels, comics, manga, and manhwa with multi-language synchronization, multi-author collaboration rights, and Google Drive cloud storage.

---

## 🌟 Platform Highlights

- **Multi-Language Publishing**: Link multiple language translations (English, Urdu, Arabic, Spanish, Japanese, Korean, French) to a single publication, each with its own PDF file and language-specific progress tracking.
- **Multiple Authors & Collaborators**: Add co-authors, translators, illustrators, and editors to publications with granular permissions.
- **Google Drive Multi-Account Sync**: Connect multiple Google Drive accounts (Personal, Publisher, Backup) with server-side AES-256-GCM token encryption and non-public proxy streaming.
- **ImgBB Cover Upload System**: Instant cover upload with validation (JPG, PNG, WebP up to 16MB), real-time progress, preview, replace, and remove capabilities.
- **Advanced PDF Reader**: Fullscreen reading, zoom controls, page jump, bookmarks, reading themes (Dark, Warm Sepia, Paper White), and publisher-controlled download permissions.
- **Continuous Manhwa & Webtoon Viewer**: Vertical scrolling webtoon strip mode + page-by-page mode with chapter navigation.
- **Personal Library**: Shelves for Currently Reading, Want to Read, Favorites, Completed, Bookmarks, and Custom Collections.
- **Author Analytics Dashboard**: Live metrics for views, active readers, download statistics, and publication drafts.
- **Developer Terminal & Secret Admin Portal**: Interactive green-screen terminal triggered via 5 clicks in Settings with server-verified Supabase authentication.
- **Advertisement Campaign Engine**: Privacy-preserving sponsored ad placements across the Homepage, Explore catalog, and In-feed book cards with impression/click counters.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Framework** | Next.js 14 (App Router) & TypeScript |
| **Styling & UI** | Tailwind CSS with Dark Luxury Charcoal/Electric Violet Design |
| **Database & Auth** | Supabase (PostgreSQL with Row Level Security, SSR Cookies, & Auth) |
| **PDF Rendering** | PDF.js (`pdfjs-dist`) with HTML5 Canvas renderer |
| **File Storage** | Google Drive API v3 (Multipart Uploads) & ImgBB API v1 |
| **Icons & Motion** | Lucide Icons & Framer Motion |
| **Security** | AES-256-GCM Token Encryption, Server Route Guards, RLS Policies |

---

## 🚀 Environment Configuration

Create a `.env.local` file at the root:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://gzwpfvhmjweeydiwdsga.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=sb_publishable_APwu-OfPQmtnj-f-pwxfZw_OxiwM8A1
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_APwu-OfPQmtnj-f-pwxfZw_OxiwM8A1
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# ImgBB API
IMGBB_API_KEY=a9985ccf572a0e05bce242e27cf8be33
NEXT_PUBLIC_IMGBB_API_KEY=a9985ccf572a0e05bce242e27cf8be33

# Google Drive OAuth Integration
GOOGLE_CLIENT_ID=your_google_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id_here.apps.googleusercontent.com

# Token Encryption Secret (32-character string)
TOKEN_ENCRYPTION_SECRET=novelix-super-secure-aes256-key-32chars!

# App Site URL
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

---

## 🗄️ Database Setup & SQL Migrations

The database migration and starter seed data are located in:
1. `supabase/migrations/20240101000000_novelix_schema.sql` (Tables, Foreign Keys, Indexes, Triggers, and RLS Policies)
2. `supabase/seed.sql` (Sample Advertisements and initial platform records)

To run the migrations directly via Supabase CLI:
```bash
supabase db push
```
Or execute the script in the **Supabase Dashboard SQL Editor**.

---

## 📖 Navigation & Routes

| Route | Purpose |
|---|---|
| `/` | Homepage with Hero Banner, Trending Novels, Popular Manhwa, Categories, and Right Panel |
| `/explore` | Discovery catalog with 16 genres and multi-language filters |
| `/search` | Universal catalog search across titles, authors, genres, and languages |
| `/book/[id]` | Book details with synopsis, multi-author credits, language editions, and reviews |
| `/series/[id]` | Franchise book series with chronological volume sequence |
| `/read/[id]` | Advanced PDF Reader with PDF.js canvas, theme switcher, and bookmarks |
| `/manhwa/[id]` | Webtoon continuous vertical scroll & page reader |
| `/author/[username]` | Author profile with verified badge, followers, bio, and catalog |
| `/library` | Personal library shelves and reading progress |
| `/publish` | Publishing Studio with all 20 fields and Google Drive sync |
| `/dashboard` | Author analytics, views, and publication drafts |
| `/settings` | Profile preferences, connected Google Drive accounts, and easter-egg terminal |
| `/settings/developer` | Fullscreen Developer Diagnostics Console |
| `/admin` | Administration panel for content moderation, author verification, and ads |
| `/auth/login` | Email/Password & Google OAuth authentication |
| `/auth/register` | User and Author registration |
| `/auth/forgot-password` | Password recovery |

---

## 💻 Development Commands

```bash
# Install dependencies
pnpm install

# Start local development server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start
```

---

## 🛡️ Security Best Practices

1. **OAuth Refresh Tokens**: Refresh tokens from Google Drive are never delivered to the client; they are stored encrypted using `AES-256-GCM` via `utils/crypto.ts`.
2. **Drive Streaming Proxy**: PDF access is streamed through `/api/drive/file/[fileId]`, ensuring Google Drive files are never made publicly searchable or guessable.
3. **Admin Verification**: Access to `/admin` is verified server-side in `utils/supabase/middleware.ts` against the `profiles.is_admin` column and `user_roles` table.
4. **ImgBB API Protection**: ImgBB upload requests pass through `/api/upload/cover`, enforcing file size (max 16MB) and MIME-type integrity checks.
