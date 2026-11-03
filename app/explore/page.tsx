'use client';

import React, { useState, useMemo } from 'react';
import { BookCard } from '@/components/BookCard';
import { SAMPLE_BOOKS, CATEGORIES } from '@/utils/sampleData';
import { 
  Filter, 
  Search, 
  SlidersHorizontal, 
  Globe, 
  Sparkles, 
  RotateCcw,
  BookOpen
} from 'lucide-react';

export default function ExplorePage() {
  const [search, setSearch] = useState('');
  const [selectedGenre, setSelectedGenre] = useState<string>('All');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('All');
  const [selectedType, setSelectedType] = useState<string>('All');
  const [sortBy, setSortBy] = useState<string>('popular');

  const languages = [
    { code: 'All', name: 'All Languages' },
    { code: 'en', name: 'English' },
    { code: 'ur', name: 'Urdu' },
    { code: 'ar', name: 'Arabic' },
    { code: 'es', name: 'Spanish' },
    { code: 'ja', name: 'Japanese' },
    { code: 'ko', name: 'Korean' },
    { code: 'fr', name: 'French' },
  ];

  const types = [
    { value: 'All', label: 'All Publications' },
    { value: 'novel', label: 'Novels & Books' },
    { value: 'manhwa', label: 'Manhwa' },
    { value: 'manga', label: 'Manga' },
    { value: 'comic', label: 'Comics' },
    { value: 'educational', label: 'Educational' },
  ];

  const filteredBooks = useMemo(() => {
    return SAMPLE_BOOKS.filter((book) => {
      // Search filter
      const matchesSearch =
        !search ||
        book.title.toLowerCase().includes(search.toLowerCase()) ||
        book.subtitle?.toLowerCase().includes(search.toLowerCase()) ||
        book.authors?.some((a) => a.name.toLowerCase().includes(search.toLowerCase()));

      // Genre filter
      const matchesGenre =
        selectedGenre === 'All' ||
        book.primary_genre.toLowerCase() === selectedGenre.toLowerCase();

      // Language filter
      const matchesLanguage =
        selectedLanguage === 'All' ||
        book.primary_language === selectedLanguage ||
        book.additional_languages?.includes(selectedLanguage);

      // Type filter
      const matchesType =
        selectedType === 'All' || book.publication_type === selectedType;

      return matchesSearch && matchesGenre && matchesLanguage && matchesType;
    }).sort((a, b) => {
      if (sortBy === 'popular') return (b.view_count || 0) - (a.view_count || 0);
      if (sortBy === 'rating') return (b.rating || 0) - (a.rating || 0);
      if (sortBy === 'newest') return b.title.localeCompare(a.title);
      return 0;
    });
  }, [search, selectedGenre, selectedLanguage, selectedType, sortBy]);

  const resetFilters = () => {
    setSearch('');
    setSelectedGenre('All');
    setSelectedLanguage('All');
    setSelectedType('All');
    setSortBy('popular');
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
          <Sparkles className="w-7 h-7 text-novelix-neon" />
          Explore & Discover Library
        </h1>
        <p className="text-xs sm:text-sm text-zinc-400 mt-1">
          Browse masterworks across 16 genres, multiple languages, and digital formats.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-5 rounded-2xl bg-novelix-900/80 border border-novelix-800 space-y-4">
        {/* Search Input */}
        <div className="relative">
          <Search className="w-4 h-4 text-zinc-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by book title, author name, or keywords..."
            className="w-full bg-novelix-950 text-sm text-white placeholder-zinc-400 pl-10 pr-4 py-2.5 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
          />
        </div>

        {/* Filters Dropdowns */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          {/* Genre select */}
          <div>
            <label className="block text-[10px] uppercase font-bold text-zinc-400 mb-1">Genre</label>
            <select
              value={selectedGenre}
              onChange={(e) => setSelectedGenre(e.target.value)}
              className="w-full bg-novelix-950 text-white rounded-xl border border-novelix-800 px-3 py-2 focus:outline-none focus:border-novelix-neon"
            >
              <option value="All">All 16 Genres</option>
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          {/* Language select */}
          <div>
            <label className="block text-[10px] uppercase font-bold text-zinc-400 mb-1">Language Edition</label>
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="w-full bg-novelix-950 text-white rounded-xl border border-novelix-800 px-3 py-2 focus:outline-none focus:border-novelix-neon"
            >
              {languages.map((l) => (
                <option key={l.code} value={l.code}>{l.name}</option>
              ))}
            </select>
          </div>

          {/* Type select */}
          <div>
            <label className="block text-[10px] uppercase font-bold text-zinc-400 mb-1">Format Type</label>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="w-full bg-novelix-950 text-white rounded-xl border border-novelix-800 px-3 py-2 focus:outline-none focus:border-novelix-neon"
            >
              {types.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>

          {/* Sort By */}
          <div>
            <label className="block text-[10px] uppercase font-bold text-zinc-400 mb-1">Sort By</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full bg-novelix-950 text-white rounded-xl border border-novelix-800 px-3 py-2 focus:outline-none focus:border-novelix-neon"
            >
              <option value="popular">Most Popular</option>
              <option value="rating">Highest Rated</option>
              <option value="newest">Recently Published</option>
            </select>
          </div>
        </div>

        {/* Active Filters count & reset button */}
        <div className="flex items-center justify-between pt-2 border-t border-novelix-800/80 text-xs text-zinc-400">
          <span>Found {filteredBooks.length} publications</span>
          <button
            onClick={resetFilters}
            className="flex items-center gap-1 text-novelix-neon hover:underline"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Reset Filters</span>
          </button>
        </div>
      </div>

      {/* Book Grid */}
      {filteredBooks.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {filteredBooks.map((book) => (
            <BookCard key={book.id} book={book} />
          ))}
        </div>
      ) : (
        <div className="p-12 text-center rounded-2xl bg-novelix-900/40 border border-novelix-800 space-y-3">
          <BookOpen className="w-10 h-10 text-zinc-400 mx-auto" />
          <h3 className="text-base font-bold text-white">No publications matched your criteria</h3>
          <p className="text-xs text-zinc-400">Try adjusting your filters or search keywords.</p>
          <button
            onClick={resetFilters}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-novelix-electric text-white"
          >
            Clear Filters
          </button>
        </div>
      )}
    </div>
  );
}
