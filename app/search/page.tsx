'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { BookCard } from '@/components/BookCard';
import { SAMPLE_BOOKS } from '@/utils/sampleData';
import { Search, Sparkles, BookOpen, User, Layers } from 'lucide-react';

function SearchContent() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  const [query, setQuery] = useState(initialQuery);

  useEffect(() => {
    setQuery(searchParams.get('q') || '');
  }, [searchParams]);

  const results = SAMPLE_BOOKS.filter((b) => {
    if (!query.trim()) return true;
    const q = query.toLowerCase();
    const titleMatch = b.title.toLowerCase().includes(q);
    const subtitleMatch = b.subtitle?.toLowerCase().includes(q);
    const genreMatch = b.primary_genre.toLowerCase().includes(q);
    const authorMatch = b.authors?.some((a) => a.name.toLowerCase().includes(q));
    const langMatch =
      b.primary_language.toLowerCase().includes(q) ||
      b.additional_languages?.some((l) => l.toLowerCase().includes(q));

    return titleMatch || subtitleMatch || genreMatch || authorMatch || langMatch;
  });

  return (
    <div className="space-y-8">
      {/* Search Header */}
      <div className="max-w-2xl">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-3">
          <Search className="w-7 h-7 text-novelix-neon" />
          Universal Catalog Search
        </h1>
        <p className="text-xs sm:text-sm text-zinc-400 mt-1">
          Search titles, authors, franchises, series, genres, and language translations.
        </p>

        <div className="relative mt-4">
          <Search className="w-5 h-5 text-zinc-400 absolute left-4 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type book title, author, or genre..."
            className="w-full bg-novelix-900 text-white placeholder-zinc-400 pl-12 pr-4 py-3 rounded-2xl border border-novelix-800 focus:outline-none focus:border-novelix-neon focus:ring-1 focus:ring-novelix-neon shadow-lg text-sm"
            autoFocus
          />
        </div>
      </div>

      {/* Results Header */}
      <div className="flex items-center justify-between border-b border-novelix-800/80 pb-3">
        <p className="text-xs font-semibold text-zinc-300">
          Showing <span className="text-novelix-neon font-bold">{results.length}</span> publications for &ldquo;{query || 'All'}&rdquo;
        </p>
      </div>

      {/* Grid */}
      {results.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {results.map((book) => (
            <BookCard key={book.id} book={book} />
          ))}
        </div>
      ) : (
        <div className="p-12 text-center rounded-2xl bg-novelix-900/40 border border-novelix-800 space-y-3">
          <BookOpen className="w-10 h-10 text-zinc-400 mx-auto" />
          <h3 className="text-base font-bold text-white">No results found</h3>
          <p className="text-xs text-zinc-400">Try searching with a different term, or explore our curated collections.</p>
        </div>
      )}
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={
      <div className="py-20 text-center">
        <div className="w-8 h-8 border-4 border-novelix-electric border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-xs text-zinc-400">Loading catalog search...</p>
      </div>
    }>
      <SearchContent />
    </Suspense>
  );
}
