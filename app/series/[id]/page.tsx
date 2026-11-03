'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { SAMPLE_BOOKS } from '@/utils/sampleData';
import { Layers, BookOpen, Star, CheckCircle, Clock, Globe } from 'lucide-react';

export default function SeriesDetailsPage() {
  const params = useParams();

  const series = {
    id: params.id as string,
    title: 'The Dark Kingdom Saga',
    status: 'Ongoing',
    description:
      'A multi-generational dark fantasy chronicle detailing the collapse of the celestial barrier and the rise of the void armies. Spanning across three continents and four official translations.',
    cover_url:
      'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&q=80',
    authors: ['Aria Sterling', 'Zayn Al-Khaleel'],
    totalBooks: 3,
    books: [
      {
        order: 1,
        id: 'b1000000-0000-0000-0000-000000000001',
        title: 'Book 1: The Beginning of the Void',
        pages: 342,
        rating: 4.9,
        status: 'Available',
        cover: 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=400&q=80',
      },
      {
        order: 2,
        id: 'b1000000-0000-0000-0000-000000000002',
        title: 'Book 2: The Lost Empire',
        pages: 410,
        rating: 4.88,
        status: 'Available',
        cover: 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=400&q=80',
      },
      {
        order: 3,
        id: 'b1000000-0000-0000-0000-000000000003',
        title: 'Book 3: The Final War',
        pages: 388,
        rating: 4.95,
        status: 'Releasing Soon',
        cover: 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&q=80',
      },
    ],
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Series Hero Header */}
      <div className="flex flex-col sm:flex-row gap-6 items-start p-6 rounded-3xl bg-novelix-900 border border-novelix-800">
        <img
          src={series.cover_url}
          alt={series.title}
          className="w-40 aspect-[2/3] rounded-2xl object-cover shadow-xl border border-novelix-800 shrink-0"
        />

        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-novelix-electric/20 text-novelix-neon border border-novelix-electric/30">
              Official Franchise Series
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              {series.status}
            </span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">{series.title}</h1>
          <p className="text-xs text-zinc-400 leading-relaxed">{series.description}</p>

          <div className="text-xs text-zinc-400 pt-1">
            <span>Creators: </span>
            <span className="text-white font-semibold">{series.authors.join(' & ')}</span>
          </div>
        </div>
      </div>

      {/* Ordered Reading Sequence */}
      <div className="space-y-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <Layers className="w-5 h-5 text-novelix-neon" />
          Reading Sequence & Volumes
        </h2>

        <div className="space-y-3">
          {series.books.map((b) => (
            <div
              key={b.id}
              className="p-4 rounded-2xl bg-novelix-900/60 border border-novelix-800 hover:border-novelix-neon/40 flex items-center justify-between gap-4 transition-all"
            >
              <div className="flex items-center gap-4">
                <span className="w-8 h-8 rounded-xl bg-novelix-800 text-novelix-neon font-mono font-bold flex items-center justify-center text-xs">
                  0{b.order}
                </span>
                <img src={b.cover} alt={b.title} className="w-12 h-16 rounded-lg object-cover" />
                <div>
                  <h3 className="text-sm font-bold text-white">{b.title}</h3>
                  <p className="text-[11px] text-zinc-400">{b.pages} pages • Rating {b.rating}</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Link
                  href={`/read/${b.id}`}
                  className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-novelix-electric hover:bg-novelix-violet text-white transition-colors"
                >
                  Read Volume
                </Link>
                <Link
                  href={`/book/${b.id}`}
                  className="px-3 py-1.5 rounded-xl text-xs font-medium bg-novelix-800 text-zinc-300 hover:text-white"
                >
                  Details
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
