'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { SAMPLE_BOOKS, SAMPLE_SAMPLE_PDF } from '@/utils/sampleData';
import { createClient } from '@/utils/supabase/client';
import { 
  BookOpen, 
  Star, 
  Globe, 
  Download, 
  Heart, 
  Share2, 
  ShieldCheck, 
  UserPlus, 
  Calendar, 
  FileText, 
  Layers, 
  MessageSquare,
  Sparkles,
  Check,
  Send
} from 'lucide-react';

export default function BookDetailsPage() {
  const params = useParams();
  const bookId = params.id as string;

  const [book, setBook] = useState<any>(null);
  const [isLiked, setIsLiked] = useState(false);
  const [inLibrary, setInLibrary] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [newReviewText, setNewReviewText] = useState('');
  const [newRating, setNewRating] = useState(5);
  const [reviewsList, setReviewsList] = useState<any[]>([
    {
      id: 'rev-1',
      user: 'Evelyn Gray',
      avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=120',
      rating: 5,
      date: '2 days ago',
      content: 'Absolutely mesmerizing world-building. The multi-language translation in Urdu was impeccably done with poetic nuance!',
    },
    {
      id: 'rev-2',
      user: 'Kareem Mansour',
      avatar: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=120',
      rating: 5,
      date: '1 week ago',
      content: 'A thrilling story. The Google Drive sync and PDF reading experience is smooth and lightning fast.',
    },
  ]);

  const supabase = createClient();

  useEffect(() => {
    // Find matching book in SAMPLE_BOOKS or fetch from Supabase
    async function loadBookData() {
      try {
        const { data: dbBook } = await supabase
          .from('books')
          .select('*, book_authors(*), book_languages(*), book_files(*)')
          .eq('id', bookId)
          .maybeSingle();

        if (dbBook) {
          setBook(dbBook);
          return;
        }
      } catch (e) {}

      // Fallback to sample
      const sample = SAMPLE_BOOKS.find((b) => b.id === bookId) || SAMPLE_BOOKS[0];
      setBook({
        id: sample.id,
        title: sample.title,
        subtitle: sample.subtitle,
        description:
          'In a realm fractured by celestial silence, scholars decipher ancient manuscripts in secret observatories. As ancient forces awaken, forbidden treaties and spellbooks emerge from oblivion. Experience an epic tale translated with master craftsmanship.',
        cover_url: sample.cover_url,
        publication_type: sample.publication_type,
        primary_genre: sample.primary_genre,
        genres: [sample.primary_genre, 'Supernatural', 'Adventure'],
        primary_language: sample.primary_language,
        additional_languages: sample.additional_languages || ['ur', 'ar', 'es'],
        publisher_name: 'NOVELIX Premier Press',
        publication_date: '2026-02-14',
        age_rating: '13+',
        copyright_info: '© 2026 Authors. Licensed exclusively to NOVELIX.',
        tags: ['Fantasy', 'Forbidden Sigils', 'Epic Quest', 'Multi-Language'],
        allow_download: true,
        view_count: sample.view_count || 14200,
        authors: sample.authors || [
          { name: 'Aria Sterling', role: 'Author' },
          { name: 'Zayn Al-Khaleel', role: 'Co-Author' },
        ],
      });
    }

    loadBookData();
  }, [bookId]);

  if (!book) {
    return (
      <div className="py-20 text-center">
        <div className="w-8 h-8 border-4 border-novelix-electric border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-xs text-zinc-400">Loading publication details...</p>
      </div>
    );
  }

  const isManhwa = ['manhwa', 'manga', 'comic'].includes(book.publication_type?.toLowerCase());
  const readerPath = isManhwa ? `/manhwa/${book.id}` : `/read/${book.id}?lang=${selectedLanguage}`;

  const languageEditions = [
    { code: 'en', name: 'English', file: 'English_Master_Edition.pdf' },
    { code: 'ur', name: 'Urdu (اردو)', file: 'Urdu_Translation_Vol1.pdf' },
    { code: 'ar', name: 'Arabic (العربية)', file: 'Arabic_Edition_Final.pdf' },
    { code: 'es', name: 'Spanish (Español)', file: 'Spanish_Edicion.pdf' },
  ];

  const handleAddReview = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newReviewText.trim()) return;

    const newRev = {
      id: `rev-${Date.now()}`,
      user: 'You (Reader)',
      avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=120',
      rating: newRating,
      date: 'Just now',
      content: newReviewText.trim(),
    };

    setReviewsList([newRev, ...reviewsList]);
    setNewReviewText('');
  };

  return (
    <div className="space-y-12">
      {/* Top Banner Overview */}
      <div className="flex flex-col lg:flex-row gap-8 items-start">
        {/* Cover presentation */}
        <div className="w-full sm:w-72 shrink-0 mx-auto lg:mx-0">
          <div className="aspect-[2/3] w-full rounded-2xl overflow-hidden shadow-2xl border border-novelix-800 bg-novelix-950 relative group">
            <img
              src={book.cover_url}
              alt={book.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            />
            <div className="absolute top-3 left-3 bg-black/70 backdrop-blur-md px-2.5 py-1 rounded text-[10px] font-bold uppercase tracking-wider text-novelix-neon border border-novelix-800">
              {book.publication_type}
            </div>
          </div>

          {/* Action buttons below cover */}
          <div className="mt-4 space-y-2">
            <Link
              href={readerPath}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-bold text-sm bg-gradient-to-r from-novelix-purple via-novelix-electric to-novelix-neon text-white shadow-glow-md hover:shadow-glow-lg transition-all"
            >
              <BookOpen className="w-4 h-4" />
              <span>Read Now ({languageEditions.find((l) => l.code === selectedLanguage)?.name.split(' ')[0]})</span>
            </Link>

            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => setInLibrary(!inLibrary)}
                className={`py-2 px-3 rounded-xl text-xs font-semibold border flex items-center justify-center gap-1.5 transition-colors ${
                  inLibrary
                    ? 'bg-novelix-surface text-novelix-neon border-novelix-neon/40'
                    : 'bg-novelix-900 text-zinc-300 hover:text-white border-novelix-800'
                }`}
              >
                <Check className={`w-3.5 h-3.5 ${inLibrary ? 'text-novelix-neon' : 'hidden'}`} />
                <span>{inLibrary ? 'In Library' : '+ Library'}</span>
              </button>

              <button
                onClick={() => setIsLiked(!isLiked)}
                className={`py-2 px-3 rounded-xl text-xs font-semibold border flex items-center justify-center gap-1.5 transition-colors ${
                  isLiked
                    ? 'bg-rose-500/20 text-rose-400 border-rose-500/30'
                    : 'bg-novelix-900 text-zinc-300 hover:text-white border-novelix-800'
                }`}
              >
                <Heart className={`w-3.5 h-3.5 ${isLiked ? 'fill-rose-500 text-rose-500' : ''}`} />
                <span>{isLiked ? 'Liked' : 'Like'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Detailed Book Specs */}
        <div className="flex-1 space-y-6">
          {/* Title & Badges */}
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-novelix-electric/20 text-novelix-neon border border-novelix-electric/30">
                {book.primary_genre}
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-novelix-900 text-zinc-300 border border-novelix-800">
                Rated {book.age_rating}
              </span>
              <div className="flex items-center gap-1 text-amber-400 text-xs font-bold bg-novelix-900 px-2.5 py-0.5 rounded-full border border-novelix-800">
                <Star className="w-3.5 h-3.5 fill-amber-400" />
                <span>4.9</span>
                <span className="text-zinc-500">(1,240 reviews)</span>
              </div>
            </div>

            <h1 className="text-2xl sm:text-4xl font-extrabold text-white leading-tight">
              {book.title}
            </h1>
            {book.subtitle && (
              <p className="text-base text-novelix-neon font-medium mt-1 font-serif italic">
                {book.subtitle}
              </p>
            )}
          </div>

          {/* Authors List (Multi-Author Support) */}
          <div className="p-4 rounded-2xl bg-novelix-900/60 border border-novelix-800 space-y-2">
            <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">
              Authors & Contributors
            </h3>
            <div className="flex flex-wrap items-center gap-4">
              {book.authors?.map((author: any, i: number) => (
                <div key={i} className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-full bg-novelix-800 border border-novelix-700 flex items-center justify-center text-xs font-bold text-white">
                    {author.name[0]}
                  </div>
                  <div>
                    <Link
                      href={`/author/${author.name.toLowerCase().replace(/\s+/g, '_')}`}
                      className="text-xs font-bold text-white hover:text-novelix-neon transition-colors"
                    >
                      {author.name}
                    </Link>
                    <p className="text-[10px] text-novelix-neon font-mono">{author.role || 'Author'}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Multi-Language Editions Selector */}
          <div className="p-4 rounded-2xl bg-novelix-900/60 border border-novelix-800 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Globe className="w-4 h-4 text-novelix-neon" />
                <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                  Select Language Edition
                </h3>
              </div>
              <span className="text-[11px] text-zinc-400 font-mono">
                {languageEditions.length} Editions Available
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {languageEditions.map((ed) => (
                <button
                  key={ed.code}
                  onClick={() => setSelectedLanguage(ed.code)}
                  className={`p-3 rounded-xl text-left border transition-all flex items-center justify-between ${
                    selectedLanguage === ed.code
                      ? 'bg-novelix-electric/20 border-novelix-neon text-white font-bold shadow-glow-sm'
                      : 'bg-novelix-950/60 hover:bg-novelix-950 border-novelix-800/80 text-zinc-300'
                  }`}
                >
                  <div className="truncate">
                    <p className="text-xs">{ed.name}</p>
                    <p className="text-[10px] text-zinc-500 font-mono truncate">{ed.file}</p>
                  </div>
                  {selectedLanguage === ed.code && <Check className="w-4 h-4 text-novelix-neon shrink-0" />}
                </button>
              ))}
            </div>
          </div>

          {/* Synopsis */}
          <div className="space-y-2">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Synopsis</h3>
            <p className="text-sm text-zinc-300 leading-relaxed">{book.description}</p>
          </div>

          {/* Metadata details */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs pt-4 border-t border-novelix-800/80">
            <div>
              <span className="text-zinc-500 block">Publisher</span>
              <span className="text-white font-medium">{book.publisher_name || 'Independent'}</span>
            </div>
            <div>
              <span className="text-zinc-500 block">Published Date</span>
              <span className="text-white font-medium">{book.publication_date}</span>
            </div>
            <div>
              <span className="text-zinc-500 block">Copyright</span>
              <span className="text-white font-medium truncate block">{book.copyright_info}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Community Reviews & Ratings Section */}
      <div className="pt-8 border-t border-novelix-800 space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-novelix-neon" />
            <h2 className="text-lg font-bold text-white">Community Reviews & Discussions</h2>
          </div>
          <span className="text-xs text-zinc-400 font-mono">{reviewsList.length} reviews</span>
        </div>

        {/* Add Review Form */}
        <form onSubmit={handleAddReview} className="p-4 rounded-2xl bg-novelix-900 border border-novelix-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-white">Leave a Review</span>
            <div className="flex items-center gap-1">
              {[1, 2, 3, 4, 5].map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setNewRating(s)}
                  className="p-1"
                >
                  <Star
                    className={`w-4 h-4 ${
                      s <= newRating ? 'fill-amber-400 text-amber-400' : 'text-zinc-600'
                    }`}
                  />
                </button>
              ))}
            </div>
          </div>

          <textarea
            value={newReviewText}
            onChange={(e) => setNewReviewText(e.target.value)}
            rows={3}
            placeholder="Share your thoughts on characters, translation quality, and storyline..."
            className="w-full bg-novelix-950 text-xs text-white p-3 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon resize-none"
          />

          <div className="flex justify-end">
            <button
              type="submit"
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-novelix-electric hover:bg-novelix-violet text-white transition-colors"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Post Review</span>
            </button>
          </div>
        </form>

        {/* Reviews List */}
        <div className="space-y-3">
          {reviewsList.map((rev) => (
            <div key={rev.id} className="p-4 rounded-2xl bg-novelix-900/40 border border-novelix-800/80 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <img src={rev.avatar} alt={rev.user} className="w-8 h-8 rounded-full object-cover" />
                  <div>
                    <p className="text-xs font-bold text-white">{rev.user}</p>
                    <p className="text-[10px] text-zinc-500 font-mono">{rev.date}</p>
                  </div>
                </div>
                <div className="flex items-center gap-1 text-amber-400">
                  {Array.from({ length: rev.rating }).map((_, i) => (
                    <Star key={i} className="w-3 h-3 fill-amber-400" />
                  ))}
                </div>
              </div>
              <p className="text-xs text-zinc-300 leading-relaxed">{rev.content}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
