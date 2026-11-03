-- NOVELIX 2.1 — Complete Database Schema
-- Run this in Supabase SQL Editor

-- ═══════════════════════════════════════════════════════════
-- EXTENSIONS
-- ═══════════════════════════════════════════════════════════
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ═══════════════════════════════════════════════════════════
-- PROFILES
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS profiles (
  id            UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email         TEXT,
  display_name  TEXT,
  username      TEXT UNIQUE,
  bio           TEXT,
  avatar_url    TEXT,
  cover_url     TEXT,
  website       TEXT,
  social_links  JSONB DEFAULT '{}',
  is_verified   BOOLEAN DEFAULT FALSE,
  is_suspended  BOOLEAN DEFAULT FALSE,
  privacy       TEXT DEFAULT 'public' CHECK (privacy IN ('public','private')),
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_profiles_username ON profiles(username);
CREATE INDEX IF NOT EXISTS idx_profiles_display_name ON profiles(display_name);

CREATE POLICY "Profiles are viewable by everyone" ON profiles FOR SELECT USING (true);
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON profiles FOR INSERT WITH CHECK (auth.uid() = id);

-- ═══════════════════════════════════════════════════════════
-- USER ROLES
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS user_roles (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role       TEXT NOT NULL CHECK (role IN ('admin','moderator','verified_author')),
  granted_by UUID REFERENCES auth.users(id),
  granted_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, role)
);
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_user_roles_user ON user_roles(user_id);

CREATE POLICY "Admins can read all roles" ON user_roles FOR SELECT
  USING (EXISTS (SELECT 1 FROM user_roles ur WHERE ur.user_id = auth.uid() AND ur.role = 'admin'));
CREATE POLICY "Users can read own roles" ON user_roles FOR SELECT USING (user_id = auth.uid());

-- ═══════════════════════════════════════════════════════════
-- BOOKS
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS books (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  author_id      UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  title          TEXT NOT NULL,
  subtitle       TEXT,
  description    TEXT,
  content_type   TEXT DEFAULT 'book' CHECK (content_type IN ('book','novel','manga','manhwa','comic','short_story','series','educational')),
  genres         TEXT[] DEFAULT '{}',
  tags           TEXT[] DEFAULT '{}',
  cover_url      TEXT,
  status         TEXT DEFAULT 'ongoing' CHECK (status IN ('ongoing','completed','hiatus','draft')),
  publish_status TEXT DEFAULT 'draft' CHECK (publish_status IN ('draft','pending','published','rejected')),
  visibility     TEXT DEFAULT 'public' CHECK (visibility IN ('public','unlisted','private')),
  copyright      TEXT,
  avg_rating     NUMERIC(3,2) DEFAULT 0,
  view_count     BIGINT DEFAULT 0,
  read_count     BIGINT DEFAULT 0,
  bookmark_count BIGINT DEFAULT 0,
  like_count     BIGINT DEFAULT 0,
  allow_offline  BOOLEAN DEFAULT TRUE,
  published_at   TIMESTAMPTZ,
  created_at     TIMESTAMPTZ DEFAULT NOW(),
  updated_at     TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE books ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author_id);
CREATE INDEX IF NOT EXISTS idx_books_type ON books(content_type);
CREATE INDEX IF NOT EXISTS idx_books_status ON books(publish_status, visibility);
CREATE INDEX IF NOT EXISTS idx_books_created ON books(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_books_genres ON books USING GIN(genres);

CREATE POLICY "Published books are viewable by everyone" ON books FOR SELECT
  USING (visibility = 'public' AND publish_status = 'published');
CREATE POLICY "Authors can view own books" ON books FOR SELECT
  USING (author_id = auth.uid());
CREATE POLICY "Authors can insert books" ON books FOR INSERT
  WITH CHECK (auth.uid() = author_id);
CREATE POLICY "Authors can update own books" ON books FOR UPDATE
  USING (auth.uid() = author_id);
CREATE POLICY "Authors can delete own books" ON books FOR DELETE
  USING (auth.uid() = author_id);
CREATE POLICY "Admins can manage all books" ON books FOR ALL
  USING (EXISTS (SELECT 1 FROM user_roles WHERE user_id = auth.uid() AND role = 'admin'));

-- ═══════════════════════════════════════════════════════════
-- BOOK AUTHORS (collaborators)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS book_authors (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  book_id    UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
  user_id    UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  role       TEXT DEFAULT 'author' CHECK (role IN ('author','co_author','illustrator','translator','editor')),
  invited_email TEXT,
  invite_status TEXT DEFAULT 'pending' CHECK (invite_status IN ('pending','accepted','declined')),
  can_edit   BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(book_id, user_id)
);
ALTER TABLE book_authors ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_book_authors_book ON book_authors(book_id);
CREATE INDEX IF NOT EXISTS idx_book_authors_user ON book_authors(user_id);

CREATE POLICY "Book authors visible to everyone" ON book_authors FOR SELECT USING (true);
CREATE POLICY "Book owner can manage authors" ON book_authors FOR ALL
  USING (EXISTS (SELECT 1 FROM books WHERE id = book_id AND author_id = auth.uid()));

-- ═══════════════════════════════════════════════════════════
-- BOOK LANGUAGES (editions)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS book_languages (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  book_id         UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
  language        TEXT NOT NULL DEFAULT 'English',
  language_code   TEXT NOT NULL DEFAULT 'en',
  file_url        TEXT,
  file_name       TEXT,
  file_size       BIGINT,
  storage_provider TEXT DEFAULT 'supabase' CHECK (storage_provider IN ('supabase','google_drive','external')),
  drive_account_id UUID REFERENCES google_drive_accounts(id) ON DELETE SET NULL,
  drive_file_id   TEXT,
  is_default      BOOLEAN DEFAULT FALSE,
  publish_status  TEXT DEFAULT 'published',
  uploaded_at     TIMESTAMPTZ DEFAULT NOW(),
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(book_id, language_code)
);
ALTER TABLE book_languages ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_book_langs_book ON book_languages(book_id);

CREATE POLICY "Book languages viewable by everyone" ON book_languages FOR SELECT USING (
  EXISTS (SELECT 1 FROM books WHERE id = book_id AND visibility = 'public' AND publish_status = 'published')
);
CREATE POLICY "Authors can manage own book languages" ON book_languages FOR ALL
  USING (EXISTS (SELECT 1 FROM books WHERE id = book_id AND author_id = auth.uid()));

-- ═══════════════════════════════════════════════════════════
-- BOOK FILES (additional files per edition)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS book_files (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  book_id      UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
  language_id  UUID REFERENCES book_languages(id) ON DELETE SET NULL,
  file_type    TEXT DEFAULT 'pdf',
  file_url     TEXT NOT NULL,
  file_name    TEXT,
  file_size    BIGINT,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE book_files ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Book files visible to authenticated users" ON book_files FOR SELECT
  USING (auth.uid() IS NOT NULL);
CREATE POLICY "Authors manage own files" ON book_files FOR ALL
  USING (EXISTS (SELECT 1 FROM books WHERE id = book_id AND author_id = auth.uid()));

-- ═══════════════════════════════════════════════════════════
-- BOOK SERIES
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS book_series (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  author_id   UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  title       TEXT NOT NULL,
  description TEXT,
  cover_url   TEXT,
  status      TEXT DEFAULT 'ongoing',
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE book_series ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Series viewable by everyone" ON book_series FOR SELECT USING (true);
CREATE POLICY "Authors manage own series" ON book_series FOR ALL USING (author_id = auth.uid());

CREATE TABLE IF NOT EXISTS series_books (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  series_id   UUID NOT NULL REFERENCES book_series(id) ON DELETE CASCADE,
  book_id     UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
  order_index INTEGER DEFAULT 0,
  UNIQUE(series_id, book_id)
);
ALTER TABLE series_books ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Series books viewable by everyone" ON series_books FOR SELECT USING (true);
CREATE POLICY "Authors manage series books" ON series_books FOR ALL
  USING (EXISTS (SELECT 1 FROM book_series WHERE id = series_id AND author_id = auth.uid()));

-- ═══════════════════════════════════════════════════════════
-- CHAPTERS (manga/manhwa)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS chapters (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  book_id      UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
  language_id  UUID REFERENCES book_languages(id) ON DELETE SET NULL,
  title        TEXT,
  chapter_num  NUMERIC NOT NULL,
  content_url  TEXT,
  is_published BOOLEAN DEFAULT FALSE,
  view_count   BIGINT DEFAULT 0,
  published_at TIMESTAMPTZ,
  created_at   TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(book_id, chapter_num, language_id)
);
ALTER TABLE chapters ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_chapters_book ON chapters(book_id);
CREATE POLICY "Published chapters viewable" ON chapters FOR SELECT USING (is_published = true);
CREATE POLICY "Authors manage own chapters" ON chapters FOR ALL
  USING (EXISTS (SELECT 1 FROM books WHERE id = book_id AND author_id = auth.uid()));

-- ═══════════════════════════════════════════════════════════
-- CHAPTER IMAGES
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS chapter_images (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  chapter_id  UUID NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
  image_url   TEXT NOT NULL,
  page_number INTEGER NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(chapter_id, page_number)
);
ALTER TABLE chapter_images ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Chapter images viewable" ON chapter_images FOR SELECT
  USING (EXISTS (SELECT 1 FROM chapters WHERE id = chapter_id AND is_published = true));
CREATE POLICY "Authors manage images" ON chapter_images FOR ALL
  USING (EXISTS (SELECT 1 FROM chapters c JOIN books b ON b.id = c.book_id WHERE c.id = chapter_id AND b.author_id = auth.uid()));

-- ═══════════════════════════════════════════════════════════
-- GOOGLE DRIVE ACCOUNTS
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS google_drive_accounts (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  google_user_id  TEXT NOT NULL,
  account_email   TEXT NOT NULL,
  account_name    TEXT,
  label           TEXT DEFAULT 'Personal',
  is_default      BOOLEAN DEFAULT FALSE,
  access_token_enc TEXT,  -- encrypted, server-side only
  refresh_token_enc TEXT, -- encrypted, server-side only
  token_expires_at TIMESTAMPTZ,
  scopes          TEXT[],
  storage_used    BIGINT DEFAULT 0,
  storage_total   BIGINT,
  is_active       BOOLEAN DEFAULT TRUE,
  connected_at    TIMESTAMPTZ DEFAULT NOW(),
  last_used_at    TIMESTAMPTZ,
  UNIQUE(user_id, google_user_id)
);
ALTER TABLE google_drive_accounts ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_drive_user ON google_drive_accounts(user_id);

CREATE POLICY "Users can view own drive accounts" ON google_drive_accounts FOR SELECT
  USING (user_id = auth.uid());
CREATE POLICY "Users can manage own drive accounts" ON google_drive_accounts FOR ALL
  USING (user_id = auth.uid());

-- ═══════════════════════════════════════════════════════════
-- READING PROGRESS
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS reading_progress (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  book_id       UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
  language_code TEXT NOT NULL DEFAULT 'en',
  current_page  INTEGER DEFAULT 1,
  total_pages   INTEGER,
  chapter_id    UUID REFERENCES chapters(id) ON DELETE SET NULL,
  scroll_pos    NUMERIC DEFAULT 0,
  is_completed  BOOLEAN DEFAULT FALSE,
  last_read_at  TIMESTAMPTZ DEFAULT NOW(),
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, book_id, language_code)
);
ALTER TABLE reading_progress ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_reading_user ON reading_progress(user_id, last_read_at DESC);

CREATE POLICY "Users can manage own reading progress" ON reading_progress FOR ALL
  USING (user_id = auth.uid());

-- ═══════════════════════════════════════════════════════════
-- BOOKMARKS
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS bookmarks (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  book_id    UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
  page_num   INTEGER,
  note       TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, book_id)
);
ALTER TABLE bookmarks ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_bookmarks_user ON bookmarks(user_id);
CREATE POLICY "Users can manage own bookmarks" ON bookmarks FOR ALL USING (user_id = auth.uid());

-- ═══════════════════════════════════════════════════════════
-- READING LISTS
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS reading_lists (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name        TEXT NOT NULL,
  description TEXT,
  is_public   BOOLEAN DEFAULT FALSE,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE reading_lists ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public reading lists viewable" ON reading_lists FOR SELECT USING (is_public = true OR user_id = auth.uid());
CREATE POLICY "Users manage own lists" ON reading_lists FOR ALL USING (user_id = auth.uid());

CREATE TABLE IF NOT EXISTS reading_list_items (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  list_id    UUID NOT NULL REFERENCES reading_lists(id) ON DELETE CASCADE,
  book_id    UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
  added_at   TIMESTAMPTZ DEFAULT NOW(),
  notes      TEXT,
  UNIQUE(list_id, book_id)
);
ALTER TABLE reading_list_items ENABLE ROW LEVEL SECURITY;
CREATE POLICY "List items viewable based on list" ON reading_list_items FOR SELECT
  USING (EXISTS (SELECT 1 FROM reading_lists WHERE id = list_id AND (is_public = true OR user_id = auth.uid())));
CREATE POLICY "Users manage own list items" ON reading_list_items FOR ALL
  USING (EXISTS (SELECT 1 FROM reading_lists WHERE id = list_id AND user_id = auth.uid()));

-- ═══════════════════════════════════════════════════════════
-- REVIEWS
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS reviews (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  book_id    UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
  rating     INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
  content    TEXT,
  is_spoiler BOOLEAN DEFAULT FALSE,
  likes      INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, book_id)
);
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_reviews_book ON reviews(book_id, created_at DESC);
CREATE POLICY "Reviews viewable by everyone" ON reviews FOR SELECT USING (true);
CREATE POLICY "Users can write reviews" ON reviews FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own reviews" ON reviews FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own reviews" ON reviews FOR DELETE USING (auth.uid() = user_id);

-- ═══════════════════════════════════════════════════════════
-- COMMENTS
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS comments (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  book_id    UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
  parent_id  UUID REFERENCES comments(id) ON DELETE CASCADE,
  content    TEXT NOT NULL,
  likes      INTEGER DEFAULT 0,
  is_deleted BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_comments_book ON comments(book_id, created_at DESC);
CREATE POLICY "Comments viewable by everyone" ON comments FOR SELECT USING (true);
CREATE POLICY "Authenticated users can comment" ON comments FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own comments" ON comments FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own comments" ON comments FOR DELETE USING (auth.uid() = user_id);

-- ═══════════════════════════════════════════════════════════
-- FOLLOWS
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS follows (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  follower_id  UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  following_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at   TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(follower_id, following_id),
  CHECK (follower_id != following_id)
);
ALTER TABLE follows ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_follows_follower ON follows(follower_id);
CREATE INDEX IF NOT EXISTS idx_follows_following ON follows(following_id);
CREATE POLICY "Follows viewable by everyone" ON follows FOR SELECT USING (true);
CREATE POLICY "Users can manage own follows" ON follows FOR ALL USING (follower_id = auth.uid());

-- ═══════════════════════════════════════════════════════════
-- LIKES
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS likes (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  book_id    UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, book_id)
);
ALTER TABLE likes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Likes viewable by everyone" ON likes FOR SELECT USING (true);
CREATE POLICY "Users manage own likes" ON likes FOR ALL USING (user_id = auth.uid());

-- ═══════════════════════════════════════════════════════════
-- NOTIFICATIONS
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS notifications (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  type       TEXT NOT NULL CHECK (type IN ('follow','comment','review','like','publish','chapter','mention','system','moderation')),
  title      TEXT,
  message    TEXT,
  link_type  TEXT,
  link_id    UUID,
  actor_id   UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  is_read    BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_notifs_user ON notifications(user_id, is_read, created_at DESC);
CREATE POLICY "Users view own notifications" ON notifications FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users update own notifications" ON notifications FOR UPDATE USING (user_id = auth.uid());
CREATE POLICY "System can insert notifications" ON notifications FOR INSERT WITH CHECK (true);

-- ═══════════════════════════════════════════════════════════
-- ADVERTISEMENTS
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS advertisements (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_by     UUID NOT NULL REFERENCES auth.users(id),
  title          TEXT NOT NULL,
  description    TEXT,
  image_url      TEXT,
  destination_url TEXT NOT NULL,
  placement      TEXT DEFAULT 'home' CHECK (placement IN ('home','explore','reader','profile')),
  campaign_start TIMESTAMPTZ NOT NULL,
  campaign_end   TIMESTAMPTZ NOT NULL,
  is_active      BOOLEAN DEFAULT TRUE,
  impressions    BIGINT DEFAULT 0,
  clicks         BIGINT DEFAULT 0,
  created_at     TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE advertisements ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Active ads viewable by everyone" ON advertisements FOR SELECT
  USING (is_active = true AND campaign_start <= NOW() AND campaign_end >= NOW());
CREATE POLICY "Admins manage ads" ON advertisements FOR ALL
  USING (EXISTS (SELECT 1 FROM user_roles WHERE user_id = auth.uid() AND role = 'admin'));

-- ═══════════════════════════════════════════════════════════
-- AD EVENTS
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS ad_events (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ad_id      UUID NOT NULL REFERENCES advertisements(id) ON DELETE CASCADE,
  user_id    UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  event_type TEXT NOT NULL CHECK (event_type IN ('impression','click')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE ad_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Ad events insertable by everyone" ON ad_events FOR INSERT WITH CHECK (true);
CREATE POLICY "Admins view ad events" ON ad_events FOR SELECT
  USING (EXISTS (SELECT 1 FROM user_roles WHERE user_id = auth.uid() AND role = 'admin'));

-- ═══════════════════════════════════════════════════════════
-- REPORTS
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS reports (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reporter_id  UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  target_type  TEXT NOT NULL CHECK (target_type IN ('book','comment','review','user','chapter')),
  target_id    UUID NOT NULL,
  reason       TEXT NOT NULL,
  details      TEXT,
  status       TEXT DEFAULT 'pending' CHECK (status IN ('pending','reviewed','resolved','dismissed')),
  resolved_by  UUID REFERENCES auth.users(id),
  created_at   TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can create reports" ON reports FOR INSERT WITH CHECK (auth.uid() = reporter_id);
CREATE POLICY "Admins view all reports" ON reports FOR SELECT
  USING (EXISTS (SELECT 1 FROM user_roles WHERE user_id = auth.uid() AND role IN ('admin','moderator')));
CREATE POLICY "Admins manage reports" ON reports FOR UPDATE
  USING (EXISTS (SELECT 1 FROM user_roles WHERE user_id = auth.uid() AND role IN ('admin','moderator')));

-- ═══════════════════════════════════════════════════════════
-- ADMIN LOGS
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS admin_logs (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  admin_id   UUID NOT NULL REFERENCES auth.users(id),
  action     TEXT NOT NULL,
  target_type TEXT,
  target_id  UUID,
  details    JSONB DEFAULT '{}',
  ip_address TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE admin_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Admins view logs" ON admin_logs FOR SELECT
  USING (EXISTS (SELECT 1 FROM user_roles WHERE user_id = auth.uid() AND role = 'admin'));
CREATE POLICY "System inserts logs" ON admin_logs FOR INSERT WITH CHECK (true);

-- ═══════════════════════════════════════════════════════════
-- STORAGE BUCKETS
-- ═══════════════════════════════════════════════════════════
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES
  ('book-files', 'book-files', true, 52428800, ARRAY['application/pdf','image/jpeg','image/png','image/webp']),
  ('avatars', 'avatars', true, 5242880, ARRAY['image/jpeg','image/png','image/webp']),
  ('chapter-images', 'chapter-images', true, 10485760, ARRAY['image/jpeg','image/png','image/webp','image/gif'])
ON CONFLICT (id) DO NOTHING;

-- Storage RLS
CREATE POLICY "Book files publicly readable" ON storage.objects FOR SELECT
  USING (bucket_id = 'book-files');
CREATE POLICY "Authenticated users can upload book files" ON storage.objects FOR INSERT
  WITH CHECK (bucket_id = 'book-files' AND auth.uid() IS NOT NULL);
CREATE POLICY "Users can update own book files" ON storage.objects FOR UPDATE
  USING (bucket_id = 'book-files' AND auth.uid()::text = (storage.foldername(name))[1]);
CREATE POLICY "Avatars publicly readable" ON storage.objects FOR SELECT
  USING (bucket_id = 'avatars');
CREATE POLICY "Authenticated users upload avatars" ON storage.objects FOR INSERT
  WITH CHECK (bucket_id = 'avatars' AND auth.uid() IS NOT NULL);
CREATE POLICY "Chapter images publicly readable" ON storage.objects FOR SELECT
  USING (bucket_id = 'chapter-images');
CREATE POLICY "Authors upload chapter images" ON storage.objects FOR INSERT
  WITH CHECK (bucket_id = 'chapter-images' AND auth.uid() IS NOT NULL);

-- ═══════════════════════════════════════════════════════════
-- FUNCTIONS & TRIGGERS
-- ═══════════════════════════════════════════════════════════

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
BEGIN
  INSERT INTO public.profiles (id, email, display_name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1))
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$;
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Update book avg_rating on review insert/update/delete
CREATE OR REPLACE FUNCTION update_book_rating()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  UPDATE books SET
    avg_rating = (SELECT AVG(rating)::NUMERIC(3,2) FROM reviews WHERE book_id = COALESCE(NEW.book_id, OLD.book_id)),
    updated_at = NOW()
  WHERE id = COALESCE(NEW.book_id, OLD.book_id);
  RETURN NULL;
END;
$$;
DROP TRIGGER IF EXISTS on_review_change ON reviews;
CREATE TRIGGER on_review_change
  AFTER INSERT OR UPDATE OR DELETE ON reviews
  FOR EACH ROW EXECUTE FUNCTION update_book_rating();

-- Increment book view count
CREATE OR REPLACE FUNCTION increment_view_count(book_id UUID)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
  UPDATE books SET view_count = view_count + 1, updated_at = NOW() WHERE id = book_id;
END;
$$;

-- Update bookmark_count on bookmarks change
CREATE OR REPLACE FUNCTION update_bookmark_count()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE books SET bookmark_count = bookmark_count + 1 WHERE id = NEW.book_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE books SET bookmark_count = GREATEST(0, bookmark_count - 1) WHERE id = OLD.book_id;
  END IF;
  RETURN NULL;
END;
$$;
DROP TRIGGER IF EXISTS on_bookmark_change ON bookmarks;
CREATE TRIGGER on_bookmark_change
  AFTER INSERT OR DELETE ON bookmarks
  FOR EACH ROW EXECUTE FUNCTION update_bookmark_count();

-- Update like_count on likes change
CREATE OR REPLACE FUNCTION update_like_count()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE books SET like_count = like_count + 1 WHERE id = NEW.book_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE books SET like_count = GREATEST(0, like_count - 1) WHERE id = OLD.book_id;
  END IF;
  RETURN NULL;
END;
$$;
DROP TRIGGER IF EXISTS on_like_change ON likes;
CREATE TRIGGER on_like_change
  AFTER INSERT OR DELETE ON likes
  FOR EACH ROW EXECUTE FUNCTION update_like_count();

-- Auto-notify followers on new chapter
CREATE OR REPLACE FUNCTION notify_followers_on_chapter()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY DEFINER AS $$
DECLARE
  author_id UUID;
  follower RECORD;
  book_title TEXT;
BEGIN
  IF NEW.is_published = true AND (OLD IS NULL OR OLD.is_published = false) THEN
    SELECT b.author_id, b.title INTO author_id, book_title FROM books b WHERE b.id = NEW.book_id;
    FOR follower IN SELECT follower_id FROM follows WHERE following_id = author_id LOOP
      INSERT INTO notifications (user_id, type, title, message, link_type, link_id, actor_id)
      VALUES (
        follower.follower_id,
        'chapter',
        'New Chapter Published',
        'Chapter ' || NEW.chapter_num || ' of "' || book_title || '" is now available',
        'book',
        NEW.book_id,
        author_id
      );
    END LOOP;
  END IF;
  RETURN NEW;
END;
$$;
DROP TRIGGER IF EXISTS on_chapter_published ON chapters;
CREATE TRIGGER on_chapter_published
  AFTER INSERT OR UPDATE ON chapters
  FOR EACH ROW EXECUTE FUNCTION notify_followers_on_chapter();

-- Auto-notify on new follower
CREATE OR REPLACE FUNCTION notify_on_follow()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY DEFINER AS $$
DECLARE
  follower_name TEXT;
BEGIN
  SELECT display_name INTO follower_name FROM profiles WHERE id = NEW.follower_id;
  INSERT INTO notifications (user_id, type, title, message, actor_id)
  VALUES (NEW.following_id, 'follow', 'New Follower', (follower_name || ' started following you'), NEW.follower_id);
  RETURN NEW;
END;
$$;
DROP TRIGGER IF EXISTS on_new_follow ON follows;
CREATE TRIGGER on_new_follow
  AFTER INSERT ON follows
  FOR EACH ROW EXECUTE FUNCTION notify_on_follow();

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;
CREATE TRIGGER update_books_updated_at BEFORE UPDATE ON books FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_reviews_updated_at BEFORE UPDATE ON reviews FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ═══════════════════════════════════════════════════════════
-- REALTIME — Enable for key tables
-- ═══════════════════════════════════════════════════════════
ALTER PUBLICATION supabase_realtime ADD TABLE books;
ALTER PUBLICATION supabase_realtime ADD TABLE chapters;
ALTER PUBLICATION supabase_realtime ADD TABLE reviews;
ALTER PUBLICATION supabase_realtime ADD TABLE comments;
ALTER PUBLICATION supabase_realtime ADD TABLE notifications;
ALTER PUBLICATION supabase_realtime ADD TABLE follows;
ALTER PUBLICATION supabase_realtime ADD TABLE likes;
ALTER PUBLICATION supabase_realtime ADD TABLE advertisements;
