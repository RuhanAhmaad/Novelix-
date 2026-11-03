'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { BookCard } from '@/components/BookCard';
import { SAMPLE_BOOKS } from '@/utils/sampleData';
import { 
  BookmarkCheck, 
  BookOpen, 
  CheckCircle2, 
  Clock, 
  Heart, 
  Download, 
  FolderPlus, 
  Sparkles 
} from 'lucide-react';

export default function LibraryPage() {
  const [activeTab, setActiveTab] = useState<
    'reading' | 'completed' | 'want_to_read' | 'favorites' | 'bookmarks' | 'history'
  >('reading');

  const tabs = [
    { id: 'reading', label: 'Currently Reading', count: 2, icon: BookOpen },
    { id: 'want_to_read', label: 'Want to Read', count: 4, icon: Clock },
    { id: 'favorites', label: 'Favorites', count: 3, icon: Heart },
    { id: 'completed', label: 'Completed', count: 1, icon: CheckCircle2 },
    { id: 'bookmarks', label: 'Bookmarks', count: 5, icon: BookmarkCheck },
  ];

  const getTabBooks = () => {
    switch (activeTab) {
      case 'reading':
        return SAMPLE_BOOKS.slice(0, 2);
      case 'want_to_read':
        return SAMPLE_BOOKS.slice(2, 6);
      case 'favorites':
        return SAMPLE_BOOKS.slice(0, 3);
      case 'completed':
        return SAMPLE_BOOKS.slice(4, 5);
      case 'bookmarks':
        return SAMPLE_BOOKS.slice(1, 4);
      default:
        return SAMPLE_BOOKS;
    }
  };

  const displayedBooks = getTabBooks();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-3">
            <BookmarkCheck className="w-7 h-7 text-novelix-neon" />
            My Personal Library
          </h1>
          <p className="text-xs sm:text-sm text-zinc-400 mt-1">
            Your reading progress, synchronized bookmarks, offline downloads, and collections.
          </p>
        </div>

        <button className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-novelix-900 border border-novelix-800 hover:border-novelix-neon text-white transition-colors w-fit">
          <FolderPlus className="w-4 h-4 text-novelix-neon" />
          <span>New Collection</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-novelix-800/80">
        {tabs.map((tab) => {
          const active = activeTab === tab.id;
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                active
                  ? 'bg-novelix-electric/20 text-white border border-novelix-electric/40 shadow-glow-sm'
                  : 'text-zinc-400 hover:text-white hover:bg-novelix-900'
              }`}
            >
              <Icon className={`w-3.5 h-3.5 ${active ? 'text-novelix-neon' : ''}`} />
              <span>{tab.label}</span>
              <span className="text-[10px] bg-novelix-950 px-1.5 py-0.2 rounded-full font-mono text-zinc-400">
                {tab.count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Book Grid */}
      {displayedBooks.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {displayedBooks.map((book) => (
            <BookCard key={book.id} book={book} />
          ))}
        </div>
      ) : (
        <div className="p-12 text-center rounded-2xl bg-novelix-900/40 border border-novelix-800 space-y-3">
          <BookOpen className="w-8 h-8 text-zinc-500 mx-auto" />
          <h3 className="text-sm font-bold text-white">This shelf is currently empty</h3>
          <p className="text-xs text-zinc-400">Explore published works to add them to your shelf.</p>
          <Link
            href="/explore"
            className="inline-block px-4 py-2 rounded-xl text-xs font-semibold bg-novelix-electric text-white"
          >
            Browse Catalog
          </Link>
        </div>
      )}
    </div>
  );
}
