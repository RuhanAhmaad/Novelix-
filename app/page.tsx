'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { HeroBanner } from '@/components/HeroBanner';
import { BookCard } from '@/components/BookCard';
import { RightPanel } from '@/components/RightPanel';
import { AdBanner } from '@/components/AdBanner';
import { SAMPLE_BOOKS, CATEGORIES } from '@/utils/sampleData';
import { createClient } from '@/utils/supabase/client';
import { 
  Flame, 
  Sparkles, 
  BookOpen, 
  Layers, 
  ChevronRight, 
  TrendingUp, 
  Clock 
} from 'lucide-react';

export default function HomePage() {
  const [books, setBooks] = useState(SAMPLE_BOOKS);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const supabase = createClient();

  useEffect(() => {
    async function loadBooks() {
      try {
        const { data, error } = await supabase
          .from('books')
          .select('*, book_authors(author_name, role)')
          .eq('status', 'published')
          .eq('visibility', 'public')
          .order('view_count', { ascending: false });

        if (data && data.length > 0) {
          const mapped = data.map((b: any) => ({
            id: b.id,
            title: b.title,
            subtitle: b.subtitle,
            cover_url: b.cover_url,
            publication_type: b.publication_type,
            primary_genre: b.primary_genre,
            primary_language: b.primary_language,
            additional_languages: b.additional_languages,
            view_count: b.view_count,
            rating: 4.9,
            authors: b.book_authors?.map((a: any) => ({ name: a.author_name, role: a.role })) || [],
          }));
          setBooks(mapped);
        }
      } catch (e) {
        // Fallback to rich SAMPLE_BOOKS
      }
    }
    loadBooks();
  }, []);

  const trendingNovels = books.filter((b) => ['novel', 'book'].includes(b.publication_type));
  const popularManhwa = books.filter((b) => ['manhwa', 'manga', 'comic'].includes(b.publication_type));
  const newReleases = [...books].reverse();

  return (
    <div className="flex gap-8">
      {/* Center Flow */}
      <div className="flex-1 min-w-0 space-y-10">
        {/* Animated Hero Banner */}
        <HeroBanner />

        {/* Categories Bar */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-novelix-neon" />
              Browse by Category
            </h2>
            <Link href="/explore" className="text-xs text-novelix-neon hover:underline flex items-center gap-1">
              <span>All 16 Genres</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
            <button
              onClick={() => setSelectedCategory(null)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                selectedCategory === null
                  ? 'bg-novelix-neon text-novelix-950 shadow-glow-sm'
                  : 'bg-novelix-900 text-zinc-300 hover:text-white border border-novelix-800'
              }`}
            >
              All Genres
            </button>
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap transition-all ${
                  selectedCategory === cat
                    ? 'bg-novelix-neon text-novelix-950 font-bold shadow-glow-sm'
                    : 'bg-novelix-900 text-zinc-400 hover:text-white border border-novelix-800 hover:border-novelix-700'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Trending Novels Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-novelix-neon" />
              <h2 className="text-lg font-extrabold text-white">Trending Novels & Stories</h2>
            </div>
            <Link href="/explore?type=novel" className="text-xs font-semibold text-novelix-neon hover:underline">
              View all
            </Link>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {trendingNovels.slice(0, 4).map((book) => (
              <BookCard key={book.id} book={book} />
            ))}
          </div>
        </div>

        {/* In-feed Sponsored Placement */}
        <AdBanner placement="between_cards" />

        {/* Popular Manhwa & Comics Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Flame className="w-5 h-5 text-amber-400" />
              <h2 className="text-lg font-extrabold text-white">Popular Manhwa, Manga & Webtoons</h2>
            </div>
            <Link href="/explore?type=manhwa" className="text-xs font-semibold text-novelix-neon hover:underline">
              Explore All Series
            </Link>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {popularManhwa.map((book) => (
              <BookCard key={book.id} book={book} />
            ))}
          </div>
        </div>

        {/* New Releases */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-novelix-electric" />
              <h2 className="text-lg font-extrabold text-white">New Global Releases</h2>
            </div>
            <Link href="/explore?sort=newest" className="text-xs font-semibold text-novelix-neon hover:underline">
              See more
            </Link>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {newReleases.slice(0, 4).map((book) => (
              <BookCard key={book.id} book={book} />
            ))}
          </div>
        </div>
      </div>

      {/* Right Desktop Discovery Panel */}
      <RightPanel />
    </div>
  );
}
