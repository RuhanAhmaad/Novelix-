'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Star, Globe, Eye, BookOpen, Heart, Flame } from 'lucide-react';

export interface BookItem {
  id: string;
  title: string;
  subtitle?: string;
  cover_url?: string;
  publication_type: string;
  primary_genre: string;
  primary_language: string;
  additional_languages?: string[];
  view_count?: number;
  rating?: number;
  reviews_count?: number;
  authors?: { name: string; role?: string }[];
  is_featured?: boolean;
}

interface BookCardProps {
  book: BookItem;
  priority?: boolean;
}

export function BookCard({ book, priority = false }: BookCardProps) {
  const [isLiked, setIsLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(Math.floor(Math.random() * 45) + 12);

  const fallbackCover =
    'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=600&auto=format&fit=crop&q=80';

  const languagesCount = (book.additional_languages?.length || 0) + 1;
  const isManhwa = ['manhwa', 'manga', 'comic'].includes(book.publication_type?.toLowerCase());
  const readUrl = isManhwa ? `/manhwa/${book.id}` : `/read/${book.id}`;

  const toggleLike = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsLiked(!isLiked);
    setLikeCount((prev) => (isLiked ? prev - 1 : prev + 1));

    try {
      await fetch('/api/social/like', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bookId: book.id }),
      });
    } catch {
      // optimistic
    }
  };

  return (
    <div className="group relative rounded-2xl bg-novelix-900/60 hover:bg-novelix-900 border border-novelix-800/80 hover:border-novelix-neon/50 p-3 transition-all duration-300 hover:shadow-glow-md flex flex-col justify-between">
      {/* Cover image wrapper */}
      <Link href={`/book/${book.id}`} className="relative aspect-[2/3] w-full rounded-xl overflow-hidden block bg-novelix-950 mb-3 shadow-inner">
        <img
          src={book.cover_url || fallbackCover}
          alt={book.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          loading={priority ? 'eager' : 'lazy'}
        />

        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-novelix-950/90 via-transparent to-black/30 opacity-70 group-hover:opacity-40 transition-opacity" />

        {/* Top Badges */}
        <div className="absolute top-2 left-2 right-2 flex items-center justify-between z-10 pointer-events-none">
          <span className="px-2 py-0.5 rounded-md text-[10px] font-bold tracking-wider uppercase bg-novelix-950/80 backdrop-blur-md text-novelix-neon border border-novelix-800">
            {book.publication_type}
          </span>

          <button
            onClick={toggleLike}
            className="pointer-events-auto p-1.5 rounded-full bg-novelix-950/70 backdrop-blur-md text-zinc-300 hover:text-rose-400 hover:scale-110 transition-all border border-novelix-800/60"
            title="Like book"
          >
            <Heart className={`w-3.5 h-3.5 ${isLiked ? 'text-rose-500 fill-rose-500' : ''}`} />
          </button>
        </div>

        {/* Bottom Badges on Image */}
        <div className="absolute bottom-2 left-2 right-2 flex items-center justify-between text-[11px] text-zinc-300 z-10">
          <div className="flex items-center gap-1 bg-black/60 backdrop-blur-md px-1.5 py-0.5 rounded text-[10px] font-medium">
            <Globe className="w-3 h-3 text-novelix-neon" />
            <span>{languagesCount} {languagesCount === 1 ? 'Lang' : 'Langs'}</span>
          </div>

          <div className="flex items-center gap-1 bg-black/60 backdrop-blur-md px-1.5 py-0.5 rounded text-[10px] text-amber-400 font-bold">
            <Star className="w-3 h-3 fill-amber-400" />
            <span>{book.rating || '4.9'}</span>
          </div>
        </div>
      </Link>

      {/* Book Information */}
      <div className="flex-1 flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-1.5 mb-1">
            <span className="text-[10px] font-medium text-novelix-electric uppercase tracking-wide">
              {book.primary_genre}
            </span>
          </div>

          <Link href={`/book/${book.id}`} className="block">
            <h3 className="text-sm font-bold text-white group-hover:text-novelix-neon transition-colors line-clamp-1">
              {book.title}
            </h3>
          </Link>

          {book.subtitle && (
            <p className="text-[11px] text-zinc-400 line-clamp-1 mt-0.5">{book.subtitle}</p>
          )}

          <p className="text-[11px] text-zinc-400 mt-1 line-clamp-1">
            By {book.authors?.[0]?.name || 'NOVELIX Creator'}
          </p>
        </div>

        {/* Quick Read Button */}
        <div className="mt-3 pt-2 border-t border-novelix-800/60 flex items-center justify-between gap-2">
          <div className="flex items-center gap-1 text-[10px] text-zinc-400 font-mono">
            <Eye className="w-3 h-3" />
            <span>{book.view_count || 1240}</span>
          </div>

          <Link
            href={readUrl}
            className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-novelix-electric/20 text-novelix-neon hover:bg-novelix-electric hover:text-white transition-colors border border-novelix-electric/30"
          >
            <BookOpen className="w-3 h-3" />
            <span>Read</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
