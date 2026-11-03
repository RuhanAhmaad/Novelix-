-- ====================================================================
-- NOVELIX PLATFORM DATABASE SCHEMA
-- Advanced Digital Publishing Platform
-- ====================================================================

-- 1. Enable UUID Extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Profiles Table
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username TEXT UNIQUE NOT NULL,
  display_name TEXT NOT NULL,
  bio TEXT,
  avatar_url TEXT,
  banner_url TEXT,
  is_verified BOOLEAN DEFAULT FALSE,
  is_admin BOOLEAN DEFAULT FALSE,
  website TEXT,
  twitter TEXT,
  instagram TEXT,
  reading_privacy TEXT DEFAULT 'public' CHECK (reading_privacy IN ('public', 'followers', 'private')),
  streak_count INTEGER DEFAULT 0,
  last_read_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. User Roles Table
CREATE TABLE IF NOT EXISTS public.user_roles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('admin', 'moderator', 'author', 'reader')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, role)
);

-- 4. Books Table
CREATE TABLE IF NOT EXISTS public.books (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  subtitle TEXT,
  description TEXT,
  cover_url TEXT,
  publication_type TEXT NOT NULL CHECK (publication_type IN ('book', 'series', 'novel', 'short_story', 'manhwa', 'manga', 'comic', 'educational')),
  primary_genre TEXT NOT NULL,
  genres TEXT[] DEFAULT '{}',
  primary_language TEXT NOT NULL DEFAULT 'en',
  additional_languages TEXT[] DEFAULT '{}',
  publisher_name TEXT,
  publication_date DATE DEFAULT CURRENT_DATE,
  age_rating TEXT DEFAULT 'all' CHECK (age_rating IN ('all', '13+', '16+', '18+')),
  tags TEXT[] DEFAULT '{}',
  copyright_info TEXT,
  status TEXT DEFAULT 'published' CHECK (status IN ('draft', 'published', 'scheduled', 'archived')),
  visibility TEXT DEFAULT 'public' CHECK (visibility IN ('public', 'unlisted', 'private')),
  allow_download BOOLEAN DEFAULT FALSE,
  is_featured BOOLEAN DEFAULT FALSE,
  view_count BIGINT DEFAULT 0,
  download_count BIGINT DEFAULT 0,
  created_by UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Book Authors (Multi-Author Support & Permissions)
CREATE TABLE IF NOT EXISTS public.book_authors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  book_id UUID NOT NULL REFERENCES public.books(id) ON DELETE CASCADE,
  user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
  author_name TEXT NOT NULL,
  avatar_url TEXT,
  role TEXT NOT NULL DEFAULT 'Author' CHECK (role IN ('Author', 'Co-Author', 'Illustrator', 'Translator', 'Editor', 'Publisher')),
  is_owner BOOLEAN DEFAULT FALSE,
  can_edit BOOLEAN DEFAULT FALSE,
  status TEXT DEFAULT 'accepted' CHECK (status IN ('pending', 'accepted', 'declined')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Book Languages Table
CREATE TABLE IF NOT EXISTS public.book_languages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  book_id UUID NOT NULL REFERENCES public.books(id) ON DELETE CASCADE,
  language_code TEXT NOT NULL,
  language_name TEXT NOT NULL,
  is_default BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(book_id, language_code)
);

-- 7. Book Files (Multi-Language PDF & Storage Management)
CREATE TABLE IF NOT EXISTS public.book_files (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  book_id UUID NOT NULL REFERENCES public.books(id) ON DELETE CASCADE,
  language_code TEXT NOT NULL,
  file_source TEXT DEFAULT 'google_drive' CHECK (file_source IN ('google_drive', 'supabase_storage', 'direct_url', 'upload')),
  file_name TEXT NOT NULL,
  file_size BIGINT DEFAULT 0,
  mime_type TEXT DEFAULT 'application/pdf',
  drive_file_id TEXT,
  drive_account_id UUID,
  public_url TEXT,
  pages_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. Book Series Table
CREATE TABLE IF NOT EXISTS public.book_series (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  description TEXT,
  cover_url TEXT,
  status TEXT DEFAULT 'ongoing' CHECK (status IN ('ongoing', 'completed', 'hiatus')),
  genres TEXT[] DEFAULT '{}',
  created_by UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. Series Books (Ordering inside a series)
CREATE TABLE IF NOT EXISTS public.series_books (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  series_id UUID NOT NULL REFERENCES public.book_series(id) ON DELETE CASCADE,
  book_id UUID NOT NULL REFERENCES public.books(id) ON DELETE CASCADE,
  sequence_order INTEGER NOT NULL DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(series_id, book_id)
);

-- 10. Chapters (Manhwa, Comics & Web Novels)
CREATE TABLE IF NOT EXISTS public.chapters (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  book_id UUID NOT NULL REFERENCES public.books(id) ON DELETE CASCADE,
  chapter_number NUMERIC(6, 2) NOT NULL,
  title TEXT NOT NULL,
  language_code TEXT DEFAULT 'en',
  season_number INTEGER DEFAULT 1,
  content_text TEXT,
  view_count BIGINT DEFAULT 0,
  published_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 11. Chapter Images (Vertical scroll Manhwa/Comic pages)
CREATE TABLE IF NOT EXISTS public.chapter_images (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  chapter_id UUID NOT NULL REFERENCES public.chapters(id) ON DELETE CASCADE,
  image_url TEXT NOT NULL,
  page_number INTEGER NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 12. Google Drive Accounts (Multi-Account Integration)
CREATE TABLE IF NOT EXISTS public.google_drive_accounts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  account_name TEXT NOT NULL,
  email TEXT NOT NULL,
  encrypted_refresh_token TEXT NOT NULL,
  is_primary BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 13. Reading Progress (Language-specific tracking)
CREATE TABLE IF NOT EXISTS public.reading_progress (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  book_id UUID NOT NULL REFERENCES public.books(id) ON DELETE CASCADE,
  language_code TEXT DEFAULT 'en',
  current_page INTEGER DEFAULT 1,
  total_pages INTEGER DEFAULT 1,
  completion_percentage NUMERIC(5, 2) DEFAULT 0.00,
  last_read_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, book_id, language_code)
);

-- 14. Bookmarks
CREATE TABLE IF NOT EXISTS public.bookmarks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  book_id UUID NOT NULL REFERENCES public.books(id) ON DELETE CASCADE,
  chapter_id UUID REFERENCES public.chapters(id) ON DELETE CASCADE,
  language_code TEXT DEFAULT 'en',
  page_number INTEGER,
  note TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 15. Reviews
CREATE TABLE IF NOT EXISTS public.reviews (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  book_id UUID NOT NULL REFERENCES public.books(id) ON DELETE CASCADE,
  rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
  title TEXT,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, book_id)
);

-- 16. Comments (Book & Chapter Discussions)
CREATE TABLE IF NOT EXISTS public.comments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  book_id UUID NOT NULL REFERENCES public.books(id) ON DELETE CASCADE,
  chapter_id UUID REFERENCES public.chapters(id) ON DELETE CASCADE,
  parent_id UUID REFERENCES public.comments(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  likes_count INTEGER DEFAULT 0,
  is_moderated BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 17. Follows (Author follower network)
CREATE TABLE IF NOT EXISTS public.follows (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  follower_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  following_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(follower_id, following_id)
);

-- 18. Likes
CREATE TABLE IF NOT EXISTS public.likes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  book_id UUID REFERENCES public.books(id) ON DELETE CASCADE,
  comment_id UUID REFERENCES public.comments(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 19. Notifications
CREATE TABLE IF NOT EXISTS public.notifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  recipient_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  sender_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
  type TEXT NOT NULL,
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  link TEXT,
  is_read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 20. Reading Lists & Custom Collections
CREATE TABLE IF NOT EXISTS public.reading_lists (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  is_private BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.reading_list_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  list_id UUID NOT NULL REFERENCES public.reading_lists(id) ON DELETE CASCADE,
  book_id UUID NOT NULL REFERENCES public.books(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(list_id, book_id)
);

-- 21. Advertisements
CREATE TABLE IF NOT EXISTS public.advertisements (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  description TEXT,
  image_url TEXT NOT NULL,
  target_url TEXT NOT NULL,
  placement TEXT NOT NULL CHECK (placement IN ('homepage_banner', 'explore_banner', 'between_cards', 'book_details', 'author_dashboard')),
  is_active BOOLEAN DEFAULT TRUE,
  start_date TIMESTAMPTZ DEFAULT NOW(),
  end_date TIMESTAMPTZ,
  impressions_count BIGINT DEFAULT 0,
  clicks_count BIGINT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 22. Ad Events (Analytics without exposing PII)
CREATE TABLE IF NOT EXISTS public.ad_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  ad_id UUID NOT NULL REFERENCES public.advertisements(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL CHECK (event_type IN ('impression', 'click')),
  user_id UUID,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 23. Reports
CREATE TABLE IF NOT EXISTS public.reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  reporter_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
  content_type TEXT NOT NULL CHECK (content_type IN ('book', 'chapter', 'comment', 'review', 'user')),
  content_id UUID NOT NULL,
  reason TEXT NOT NULL,
  details TEXT,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'resolved', 'dismissed')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 24. Admin Activity Logs
CREATE TABLE IF NOT EXISTS public.admin_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  admin_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
  action TEXT NOT NULL,
  target_type TEXT NOT NULL,
  target_id UUID,
  details JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ====================================================================
-- INDEXES FOR PERFORMANCE
-- ====================================================================
CREATE INDEX IF NOT EXISTS idx_books_status_visibility ON public.books(status, visibility);
CREATE INDEX IF NOT EXISTS idx_books_primary_genre ON public.books(primary_genre);
CREATE INDEX IF NOT EXISTS idx_books_created_by ON public.books(created_by);
CREATE INDEX IF NOT EXISTS idx_books_views ON public.books(view_count DESC);
CREATE INDEX IF NOT EXISTS idx_book_authors_book_id ON public.book_authors(book_id);
CREATE INDEX IF NOT EXISTS idx_book_authors_user_id ON public.book_authors(user_id);
CREATE INDEX IF NOT EXISTS idx_book_files_book_id ON public.book_files(book_id);
CREATE INDEX IF NOT EXISTS idx_chapters_book_id ON public.chapters(book_id, chapter_number);
CREATE INDEX IF NOT EXISTS idx_reading_progress_user ON public.reading_progress(user_id, last_read_at DESC);
CREATE INDEX IF NOT EXISTS idx_reviews_book ON public.reviews(book_id);
CREATE INDEX IF NOT EXISTS idx_comments_book ON public.comments(book_id);
CREATE INDEX IF NOT EXISTS idx_notifications_recipient ON public.notifications(recipient_id, is_read, created_at DESC);

-- ====================================================================
-- AUTOMATIC PROFILE CREATION TRIGGER
-- ====================================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, username, display_name, avatar_url)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'username', SPLIT_PART(NEW.email, '@', 1) || '_' || SUBSTR(NEW.id::text, 1, 6)),
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name', SPLIT_PART(NEW.email, '@', 1)),
    COALESCE(NEW.raw_user_meta_data->>'avatar_url', NEW.raw_user_meta_data->>'picture', 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150')
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ====================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ====================================================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.books ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.book_authors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.book_languages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.book_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.book_series ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.series_books ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chapters ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chapter_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.google_drive_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reading_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bookmarks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.follows ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reading_lists ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reading_list_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.advertisements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ad_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.admin_logs ENABLE ROW LEVEL SECURITY;

-- Helper functions for RLS
CREATE OR REPLACE FUNCTION public.is_admin(user_id UUID)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.profiles WHERE id = user_id AND is_admin = true
    UNION
    SELECT 1 FROM public.user_roles WHERE user_id = user_id AND role = 'admin'
  );
$$ LANGUAGE sql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.can_edit_book(p_book_id UUID, p_user_id UUID)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.books WHERE id = p_book_id AND created_by = p_user_id
    UNION
    SELECT 1 FROM public.book_authors WHERE book_id = p_book_id AND user_id = p_user_id AND can_edit = true AND status = 'accepted'
    UNION
    SELECT 1 FROM public.profiles WHERE id = p_user_id AND is_admin = true
  );
$$ LANGUAGE sql SECURITY DEFINER;

-- Profiles: Anyone can view, user can edit own
CREATE POLICY "Public profiles are viewable by everyone" ON public.profiles FOR SELECT USING (true);
CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id);

-- Books: Public books viewable by anyone, unlisted with link, drafts only by authors/collaborators
CREATE POLICY "Books viewable by public if published" ON public.books FOR SELECT
  USING (
    visibility = 'public' AND status = 'published'
    OR auth.uid() = created_by
    OR public.can_edit_book(id, auth.uid())
    OR public.is_admin(auth.uid())
  );
CREATE POLICY "Authors can insert books" ON public.books FOR INSERT WITH CHECK (auth.uid() = created_by);
CREATE POLICY "Authorized authors can update books" ON public.books FOR UPDATE
  USING (auth.uid() = created_by OR public.can_edit_book(id, auth.uid()));
CREATE POLICY "Owners can delete books" ON public.books FOR DELETE
  USING (auth.uid() = created_by OR public.is_admin(auth.uid()));

-- Book Authors
CREATE POLICY "Book authors are viewable by everyone" ON public.book_authors FOR SELECT USING (true);
CREATE POLICY "Book owners can manage authors" ON public.book_authors FOR ALL
  USING (public.can_edit_book(book_id, auth.uid()));

-- Book Languages & Files
CREATE POLICY "Languages viewable by everyone" ON public.book_languages FOR SELECT USING (true);
CREATE POLICY "Languages editable by book editors" ON public.book_languages FOR ALL
  USING (public.can_edit_book(book_id, auth.uid()));

CREATE POLICY "Book files viewable if book is visible" ON public.book_files FOR SELECT USING (true);
CREATE POLICY "Book files editable by book editors" ON public.book_files FOR ALL
  USING (public.can_edit_book(book_id, auth.uid()));

-- Chapters & Images
CREATE POLICY "Chapters viewable by public" ON public.chapters FOR SELECT USING (true);
CREATE POLICY "Chapters editable by book editors" ON public.chapters FOR ALL
  USING (public.can_edit_book(book_id, auth.uid()));

CREATE POLICY "Chapter images viewable by public" ON public.chapter_images FOR SELECT USING (true);
CREATE POLICY "Chapter images editable by book editors" ON public.chapter_images FOR ALL
  USING (EXISTS (SELECT 1 FROM public.chapters c WHERE c.id = chapter_id AND public.can_edit_book(c.book_id, auth.uid())));

-- Google Drive Accounts (Strict Privacy)
CREATE POLICY "Users can only view their own drive accounts" ON public.google_drive_accounts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own drive accounts" ON public.google_drive_accounts FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own drive accounts" ON public.google_drive_accounts FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own drive accounts" ON public.google_drive_accounts FOR DELETE USING (auth.uid() = user_id);

-- Reading Progress & Bookmarks (Personal)
CREATE POLICY "Users can view own reading progress" ON public.reading_progress FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can upsert own reading progress" ON public.reading_progress FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own bookmarks" ON public.bookmarks FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own bookmarks" ON public.bookmarks FOR ALL USING (auth.uid() = user_id);

-- Reviews & Comments
CREATE POLICY "Reviews viewable by everyone" ON public.reviews FOR SELECT USING (true);
CREATE POLICY "Authenticated users can create reviews" ON public.reviews FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own reviews" ON public.reviews FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own reviews" ON public.reviews FOR DELETE USING (auth.uid() = user_id OR public.is_admin(auth.uid()));

CREATE POLICY "Comments viewable by everyone" ON public.comments FOR SELECT USING (true);
CREATE POLICY "Authenticated users can create comments" ON public.comments FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own comments" ON public.comments FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own comments" ON public.comments FOR DELETE USING (auth.uid() = user_id OR public.is_admin(auth.uid()));

-- Social: Follows & Likes
CREATE POLICY "Follows viewable by everyone" ON public.follows FOR SELECT USING (true);
CREATE POLICY "Users can manage their follows" ON public.follows FOR ALL USING (auth.uid() = follower_id);

CREATE POLICY "Likes viewable by everyone" ON public.likes FOR SELECT USING (true);
CREATE POLICY "Users can manage their likes" ON public.likes FOR ALL USING (auth.uid() = user_id);

-- Notifications
CREATE POLICY "Users can view own notifications" ON public.notifications FOR SELECT USING (auth.uid() = recipient_id);
CREATE POLICY "Users can update own notifications" ON public.notifications FOR UPDATE USING (auth.uid() = recipient_id);

-- Advertisements
CREATE POLICY "Active ads viewable by everyone" ON public.advertisements FOR SELECT USING (is_active = true OR public.is_admin(auth.uid()));
CREATE POLICY "Admins can manage advertisements" ON public.advertisements FOR ALL USING (public.is_admin(auth.uid()));

CREATE POLICY "Anyone can log ad events" ON public.ad_events FOR INSERT WITH CHECK (true);

-- Reports & Admin Logs
CREATE POLICY "Users can create reports" ON public.reports FOR INSERT WITH CHECK (auth.uid() = reporter_id);
CREATE POLICY "Admins can view and manage reports" ON public.reports FOR ALL USING (public.is_admin(auth.uid()));

CREATE POLICY "Admins can view admin logs" ON public.admin_logs FOR SELECT USING (public.is_admin(auth.uid()));
