'use client';

import React, { useState } from 'react';
import { useParams } from 'next/navigation';
import { BookCard } from '@/components/BookCard';
import { SAMPLE_BOOKS } from '@/utils/sampleData';
import { 
  CheckCircle2, 
  Globe, 
  Twitter, 
  Instagram, 
  UserPlus, 
  Check, 
  BookOpen, 
  Layers, 
  Flame, 
  Calendar 
} from 'lucide-react';

export default function AuthorProfilePage() {
  const params = useParams();
  const username = (params.username as string) || 'celeste_vane';

  const [isFollowing, setIsFollowing] = useState(false);
  const [followerCount, setFollowerCount] = useState(2840);
  const [activeTab, setActiveTab] = useState<'books' | 'series' | 'favorites'>('books');

  const author = {
    username: username,
    displayName: username.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
    bio: 'Dark fantasy novelist, world-builder, and creator of the Midnight Castle series. Translating epics across 4 languages.',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300&q=80',
    banner: 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1600&q=80',
    isVerified: true,
    website: 'https://novelix.io',
    twitter: '@novelix_author',
    instagram: '@novelix_stories',
    following: 142,
    streak: 19,
    joinedDate: 'January 2025',
  };

  const toggleFollow = () => {
    setIsFollowing(!isFollowing);
    setFollowerCount((prev) => (isFollowing ? prev - 1 : prev + 1));
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Banner & Avatar Header */}
      <div className="rounded-3xl overflow-hidden border border-novelix-800 bg-novelix-900 shadow-xl relative">
        {/* Banner */}
        <div className="h-48 sm:h-64 w-full relative overflow-hidden">
          <img
            src={author.banner}
            alt="Banner"
            className="w-full h-full object-cover opacity-60"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-novelix-950 via-novelix-950/40 to-transparent" />
        </div>

        {/* Profile Info Overlay */}
        <div className="p-6 sm:p-8 relative -mt-20 flex flex-col sm:flex-row items-center sm:items-end justify-between gap-6">
          <div className="flex flex-col sm:flex-row items-center sm:items-end gap-5 text-center sm:text-left">
            <div className="w-28 h-28 sm:w-32 sm:h-32 rounded-3xl overflow-hidden border-4 border-novelix-950 shadow-2xl relative bg-novelix-950">
              <img
                src={author.avatar}
                alt={author.displayName}
                className="w-full h-full object-cover"
              />
            </div>

            <div className="space-y-1">
              <div className="flex items-center gap-2 justify-center sm:justify-start">
                <h1 className="text-xl sm:text-2xl font-extrabold text-white">
                  {author.displayName}
                </h1>
                {author.isVerified && (
                  <CheckCircle2 className="w-5 h-5 text-novelix-neon fill-novelix-neon/20" />
                )}
              </div>
              <p className="text-xs text-zinc-400 font-mono">@{author.username}</p>

              {/* Follower Stats */}
              <div className="flex items-center gap-4 text-xs text-zinc-300 pt-1 justify-center sm:justify-start">
                <span>
                  <strong className="text-white">{followerCount.toLocaleString()}</strong> Followers
                </span>
                <span>
                  <strong className="text-white">{author.following}</strong> Following
                </span>
                <span className="flex items-center gap-1 text-amber-400 font-bold">
                  <Flame className="w-3.5 h-3.5 fill-amber-400" />
                  {author.streak}d Streak
                </span>
              </div>
            </div>
          </div>

          {/* Follow CTA */}
          <button
            onClick={toggleFollow}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-xs font-bold transition-all shadow-glow-sm ${
              isFollowing
                ? 'bg-novelix-800 text-zinc-300 hover:bg-zinc-700'
                : 'bg-novelix-electric hover:bg-novelix-violet text-white'
            }`}
          >
            {isFollowing ? <Check className="w-4 h-4" /> : <UserPlus className="w-4 h-4" />}
            <span>{isFollowing ? 'Following' : 'Follow Creator'}</span>
          </button>
        </div>

        {/* Bio and Links */}
        <div className="px-6 sm:px-8 pb-6 text-xs text-zinc-300 space-y-3">
          <p className="max-w-2xl leading-relaxed">{author.bio}</p>

          <div className="flex flex-wrap items-center gap-4 pt-1 text-zinc-400">
            <span className="flex items-center gap-1.5 hover:text-white">
              <Globe className="w-3.5 h-3.5 text-novelix-neon" />
              <span>{author.website}</span>
            </span>
            <span className="flex items-center gap-1.5 hover:text-white">
              <Twitter className="w-3.5 h-3.5 text-sky-400" />
              <span>{author.twitter}</span>
            </span>
            <span className="flex items-center gap-1.5 hover:text-white">
              <Instagram className="w-3.5 h-3.5 text-pink-400" />
              <span>{author.instagram}</span>
            </span>
            <span className="flex items-center gap-1.5 text-zinc-500">
              <Calendar className="w-3.5 h-3.5" />
              <span>Joined {author.joinedDate}</span>
            </span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-4 border-b border-novelix-800 text-sm font-semibold">
        <button
          onClick={() => setActiveTab('books')}
          className={`pb-3 px-1 relative transition-colors ${
            activeTab === 'books' ? 'text-white' : 'text-zinc-400 hover:text-zinc-300'
          }`}
        >
          <span>Published Works ({SAMPLE_BOOKS.slice(0, 4).length})</span>
          {activeTab === 'books' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-novelix-neon shadow-glow-sm" />
          )}
        </button>

        <button
          onClick={() => setActiveTab('series')}
          className={`pb-3 px-1 relative transition-colors ${
            activeTab === 'series' ? 'text-white' : 'text-zinc-400 hover:text-zinc-300'
          }`}
        >
          <span>Franchise Series (1)</span>
          {activeTab === 'series' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-novelix-neon shadow-glow-sm" />
          )}
        </button>
      </div>

      {/* Publications Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
        {SAMPLE_BOOKS.slice(0, 4).map((b) => (
          <BookCard key={b.id} book={b} />
        ))}
      </div>
    </div>
  );
}
