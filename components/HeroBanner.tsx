'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { BookOpen, Star, Plus, Globe, Flame, Sparkles } from 'lucide-react';

export function HeroBanner() {
  const [inLibrary, setInLibrary] = useState(false);

  const featured = {
    id: 'f1000000-0000-0000-0000-000000000001',
    title: 'The Midnight Castle: Eclipse of the Void',
    subtitle: 'Book I of The Obsidian Chronicles',
    description:
      'In a realm where celestial darkness devours memory, one banished scholar unlocks the forbidden sigils of the forgotten gods. A groundbreaking dark fantasy saga available in English, Arabic, Urdu, and Spanish with full high-definition illustrations.',
    cover:
      'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&auto=format&fit=crop&q=80',
    banner:
      'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1600&auto=format&fit=crop&q=80',
    genre: 'Dark Fantasy & Supernatural',
    rating: '4.98',
    reviewsCount: '3,842',
    languages: ['English', 'Urdu', 'Arabic', 'Spanish'],
    author: 'Aria Sterling & Zayn Al-Khaleel',
    type: 'Novel & Series',
  };

  return (
    <div className="relative rounded-3xl overflow-hidden border border-novelix-800 bg-novelix-950 shadow-2xl mb-8 group">
      {/* Background Graphic & Backdrop Glow */}
      <div
        className="absolute inset-0 bg-cover bg-center opacity-30 group-hover:scale-105 transition-transform duration-700 blur-[2px]"
        style={{ backgroundImage: `url(${featured.banner})` }}
      />
      <div className="absolute inset-0 bg-gradient-to-r from-novelix-950 via-novelix-950/90 to-transparent" />
      <div className="absolute inset-0 bg-gradient-to-t from-novelix-950 via-transparent to-transparent" />

      {/* Content Container */}
      <div className="relative z-10 p-6 sm:p-10 lg:p-12 flex flex-col md:flex-row items-center gap-8 justify-between">
        {/* Text Section */}
        <div className="max-w-2xl space-y-4">
          {/* Top Tags */}
          <div className="flex flex-wrap items-center gap-2.5">
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-novelix-neon text-novelix-950 flex items-center gap-1.5 shadow-glow-sm">
              <Sparkles className="w-3.5 h-3.5" />
              FEATURED MASTERPIECE
            </span>
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-novelix-900/80 border border-novelix-800 text-zinc-300">
              {featured.genre}
            </span>
            <div className="flex items-center gap-1 text-amber-400 text-xs font-bold bg-novelix-900/80 px-2.5 py-1 rounded-full border border-novelix-800">
              <Star className="w-3.5 h-3.5 fill-amber-400" />
              <span>{featured.rating}</span>
              <span className="text-zinc-400 font-normal">({featured.reviewsCount})</span>
            </div>
          </div>

          {/* Title & Subtitle */}
          <div>
            <h1 className="text-2xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-tight">
              {featured.title}
            </h1>
            <p className="text-sm sm:text-base text-novelix-neon font-medium mt-1 font-serif italic">
              {featured.subtitle}
            </p>
          </div>

          {/* Description */}
          <p className="text-sm text-zinc-300 leading-relaxed line-clamp-3">
            {featured.description}
          </p>

          {/* Authors & Multi-Languages */}
          <div className="flex flex-wrap items-center gap-4 text-xs text-zinc-400 pt-1">
            <div>
              <span className="text-zinc-400">Authors: </span>
              <span className="text-white font-semibold">{featured.author}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Globe className="w-3.5 h-3.5 text-novelix-electric" />
              <span className="text-white font-medium">{featured.languages.join(' • ')}</span>
            </div>
          </div>

          {/* Action CTAs */}
          <div className="flex flex-wrap items-center gap-3 pt-3">
            <Link
              href={`/read/${featured.id}`}
              className="flex items-center gap-2 px-6 py-3 rounded-xl font-bold text-sm bg-gradient-to-r from-novelix-purple via-novelix-electric to-novelix-neon text-white shadow-glow-md hover:shadow-glow-lg hover:scale-105 transition-all duration-300"
            >
              <BookOpen className="w-4 h-4" />
              <span>Start Reading</span>
            </Link>

            <button
              onClick={() => setInLibrary(!inLibrary)}
              className={`flex items-center gap-2 px-5 py-3 rounded-xl font-semibold text-sm border transition-all ${
                inLibrary
                  ? 'bg-novelix-surface text-novelix-neon border-novelix-neon/40'
                  : 'bg-novelix-900/80 hover:bg-novelix-850 text-white border-novelix-800'
              }`}
            >
              <Plus className={`w-4 h-4 ${inLibrary ? 'rotate-45' : ''} transition-transform`} />
              <span>{inLibrary ? 'In Library' : 'Add to Library'}</span>
            </button>

            <Link
              href={`/book/${featured.id}`}
              className="px-4 py-3 rounded-xl text-xs font-semibold text-zinc-400 hover:text-white transition-colors"
            >
              View Editions & Details →
            </Link>
          </div>
        </div>

        {/* Book 3D-Style Presentation Cover */}
        <div className="shrink-0 relative">
          <div className="w-48 sm:w-56 aspect-[2/3] rounded-2xl overflow-hidden shadow-2xl border-2 border-novelix-neon/30 transform md:rotate-2 group-hover:rotate-0 transition-transform duration-500 relative">
            <img
              src={featured.cover}
              alt={featured.title}
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
            <div className="absolute bottom-3 left-3 right-3 text-center">
              <span className="text-[10px] uppercase font-mono tracking-widest text-novelix-neon bg-black/70 px-2 py-0.5 rounded backdrop-blur-md">
                Official Release
              </span>
            </div>
          </div>
          {/* Subtle Glow behind cover */}
          <div className="absolute -inset-2 bg-novelix-electric/30 blur-2xl -z-10 rounded-full" />
        </div>
      </div>
    </div>
  );
}
