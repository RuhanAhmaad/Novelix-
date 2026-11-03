'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Flame, Star, Award, TrendingUp, Sparkles, UserPlus, Check } from 'lucide-react';
import { createClient } from '@/utils/supabase/client';

export function RightPanel() {
  const [followingMap, setFollowingMap] = useState<Record<string, boolean>>({});
  const [streak, setStreak] = useState(7);
  const supabase = createClient();

  // Top Authors sample
  const authors = [
    {
      id: 'author-1',
      username: 'celeste_vane',
      name: 'Celeste Vane',
      genre: 'Dark Fantasy',
      avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=120',
      booksCount: 14,
    },
    {
      id: 'author-2',
      username: 'jin_woo_studio',
      name: 'Jin-Woo Art Studio',
      genre: 'Action Manhwa',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=120',
      booksCount: 8,
    },
    {
      id: 'author-3',
      username: 'dr_tariq_almansoor',
      name: 'Dr. Tariq Al-Mansoor',
      genre: 'Historical & Islamic Literature',
      avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=120',
      booksCount: 19,
    },
  ];

  const toggleFollow = async (authorId: string) => {
    const isFollowed = followingMap[authorId];
    setFollowingMap((prev) => ({ ...prev, [authorId]: !isFollowed }));

    try {
      await fetch('/api/social/follow', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ authorId }),
      });
    } catch {
      // Revert if failed
      setFollowingMap((prev) => ({ ...prev, [authorId]: isFollowed }));
    }
  };

  return (
    <aside className="hidden xl:flex flex-col w-80 border-l border-novelix-800 bg-novelix-950/40 p-6 space-y-6 shrink-0 h-screen sticky top-0 overflow-y-auto scrollbar-thin">
      {/* Daily Reading Streak */}
      <div className="p-4 rounded-2xl bg-gradient-to-br from-novelix-900 to-novelix-850 border border-novelix-800 shadow-sm relative overflow-hidden">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center">
              <Flame className="w-4 h-4 text-amber-400 fill-amber-400 animate-pulse" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-white">Daily Streak</h4>
              <p className="text-[10px] text-zinc-400">Keep reading every day</p>
            </div>
          </div>
          <span className="text-xl font-extrabold text-amber-400 font-mono">{streak}d</span>
        </div>

        {/* 7-day visual pills */}
        <div className="flex items-center justify-between gap-1 mt-3">
          {['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((day, i) => (
            <div key={i} className="flex flex-col items-center gap-1">
              <div
                className={`w-7 h-7 rounded-lg flex items-center justify-center text-[10px] font-bold ${
                  i < 5
                    ? 'bg-gradient-to-tr from-novelix-purple to-novelix-electric text-white shadow-glow-sm'
                    : i === 5
                    ? 'bg-novelix-neon text-novelix-950 font-extrabold'
                    : 'bg-novelix-800 text-zinc-400'
                }`}
              >
                {day}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Popular Authors */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Award className="w-3.5 h-3.5 text-novelix-neon" />
            Popular Creators
          </h3>
          <Link href="/explore" className="text-[11px] text-novelix-neon hover:underline">
            View all
          </Link>
        </div>

        <div className="space-y-3">
          {authors.map((author) => {
            const isFollowed = followingMap[author.id];
            return (
              <div
                key={author.id}
                className="flex items-center justify-between p-2.5 rounded-xl bg-novelix-900/40 hover:bg-novelix-900/80 border border-novelix-800/60 transition-all duration-200"
              >
                <Link href={`/author/${author.username}`} className="flex items-center gap-3 min-w-0">
                  <img
                    src={author.avatar}
                    alt={author.name}
                    className="w-10 h-10 rounded-full object-cover border border-novelix-800"
                  />
                  <div className="min-w-0">
                    <p className="text-xs font-bold text-white truncate hover:text-novelix-neon transition-colors">
                      {author.name}
                    </p>
                    <p className="text-[10px] text-zinc-400 truncate">{author.genre}</p>
                    <span className="text-[9px] text-novelix-electric font-mono">
                      {author.booksCount} published
                    </span>
                  </div>
                </Link>

                <button
                  onClick={() => toggleFollow(author.id)}
                  className={`p-1.5 rounded-lg text-xs font-semibold transition-all ${
                    isFollowed
                      ? 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
                      : 'bg-novelix-electric/20 text-novelix-neon hover:bg-novelix-electric hover:text-white border border-novelix-electric/30'
                  }`}
                  title={isFollowed ? 'Unfollow' : 'Follow'}
                >
                  {isFollowed ? <Check className="w-3.5 h-3.5" /> : <UserPlus className="w-3.5 h-3.5" />}
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Featured Community Reading List */}
      <div className="p-4 rounded-2xl bg-gradient-to-tr from-novelix-900 via-novelix-purple/10 to-transparent border border-novelix-800/80">
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="w-4 h-4 text-novelix-neon" />
          <h4 className="text-xs font-bold text-white">Staff Picked Anthology</h4>
        </div>
        <p className="text-[11px] text-zinc-400 leading-relaxed mb-3">
          Explore curated manhwa & dark fantasy novels translated across 6 languages.
        </p>
        <Link
          href="/explore?tag=anthology"
          className="inline-block text-xs font-semibold text-novelix-neon hover:text-white transition-colors"
        >
          Explore Collection →
        </Link>
      </div>
    </aside>
  );
}
