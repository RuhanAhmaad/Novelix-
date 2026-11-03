'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { SAMPLE_BOOKS } from '@/utils/sampleData';
import { 
  LayoutDashboard, 
  Eye, 
  Download, 
  Users, 
  TrendingUp, 
  PlusCircle, 
  Edit3, 
  MoreVertical, 
  FileText, 
  Globe, 
  Clock 
} from 'lucide-react';

export default function AuthorDashboardPage() {
  const [activeTab, setActiveTab] = useState<'published' | 'drafts' | 'analytics'>('published');

  const stats = [
    { label: 'Total Reads & Views', value: '142,850', change: '+18.4%', icon: Eye },
    { label: 'Active Readers', value: '12,420', change: '+12.1%', icon: Users },
    { label: 'Total Downloads', value: '8,910', change: '+9.3%', icon: Download },
    { label: 'Global Languages', value: '4 Editions', change: 'En, Ur, Ar, Es', icon: Globe },
  ];

  const myBooks = SAMPLE_BOOKS.slice(0, 3);

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-3">
            <LayoutDashboard className="w-7 h-7 text-novelix-neon" />
            Author Analytics & Studio Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-zinc-400 mt-1">
            Real-time telemetry, reader retention, and publication performance across editions.
          </p>
        </div>

        <Link
          href="/publish"
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-novelix-purple via-novelix-electric to-novelix-neon text-white shadow-glow-sm hover:shadow-glow-md transition-all w-fit"
        >
          <PlusCircle className="w-4 h-4" />
          <span>New Publication</span>
        </Link>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <div
              key={i}
              className="p-4 sm:p-5 rounded-2xl bg-novelix-900/60 border border-novelix-800 space-y-2 relative overflow-hidden"
            >
              <div className="flex items-center justify-between text-zinc-400">
                <span className="text-xs font-medium">{stat.label}</span>
                <Icon className="w-4 h-4 text-novelix-neon" />
              </div>
              <div className="text-xl sm:text-2xl font-extrabold text-white font-mono">
                {stat.value}
              </div>
              <div className="text-[10px] text-emerald-400 font-mono font-medium flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                <span>{stat.change} vs last month</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Content Management Tabs */}
      <div className="space-y-4">
        <div className="flex items-center gap-4 border-b border-novelix-800 text-sm font-semibold">
          <button
            onClick={() => setActiveTab('published')}
            className={`pb-3 px-1 relative transition-colors ${
              activeTab === 'published' ? 'text-white' : 'text-zinc-400 hover:text-zinc-300'
            }`}
          >
            <span>Published Publications ({myBooks.length})</span>
            {activeTab === 'published' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-novelix-neon shadow-glow-sm" />
            )}
          </button>

          <button
            onClick={() => setActiveTab('drafts')}
            className={`pb-3 px-1 relative transition-colors ${
              activeTab === 'drafts' ? 'text-white' : 'text-zinc-400 hover:text-zinc-300'
            }`}
          >
            <span>Drafts (1)</span>
            {activeTab === 'drafts' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-novelix-neon shadow-glow-sm" />
            )}
          </button>
        </div>

        {/* Publications List */}
        {activeTab === 'published' && (
          <div className="space-y-3">
            {myBooks.map((book) => (
              <div
                key={book.id}
                className="p-4 rounded-2xl bg-novelix-900/40 border border-novelix-800 hover:border-novelix-neon/40 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="flex items-center gap-4">
                  <img
                    src={book.cover_url}
                    alt={book.title}
                    className="w-12 h-16 rounded-xl object-cover border border-novelix-800"
                  />
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-white">{book.title}</span>
                      <span className="text-[10px] uppercase font-mono px-1.5 py-0.2 rounded bg-novelix-800 text-novelix-neon">
                        {book.publication_type}
                      </span>
                    </div>
                    <p className="text-[11px] text-zinc-400 font-mono mt-0.5">
                      {book.view_count?.toLocaleString()} views • 4 Languages • Rated {book.rating}★
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-auto">
                  <Link
                    href={`/book/${book.id}`}
                    className="px-3 py-1.5 rounded-xl text-xs font-medium bg-novelix-800 hover:bg-novelix-750 text-white transition-colors"
                  >
                    View Page
                  </Link>
                  <Link
                    href={`/read/${book.id}`}
                    className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-novelix-electric/30 text-novelix-neon hover:bg-novelix-electric hover:text-white transition-colors"
                  >
                    Open Reader
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'drafts' && (
          <div className="p-4 rounded-2xl bg-novelix-900/40 border border-novelix-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-16 rounded-xl bg-novelix-950 border border-novelix-800 flex items-center justify-center text-zinc-500 text-xs">
                Draft
              </div>
              <div>
                <h3 className="text-xs font-bold text-white">The Void Chronicles — Chapter 4 Draft</h3>
                <p className="text-[10px] text-zinc-500 font-mono">Last edited yesterday at 11:20 PM</p>
              </div>
            </div>
            <Link
              href="/publish"
              className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-novelix-electric text-white"
            >
              Resume Editing
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
