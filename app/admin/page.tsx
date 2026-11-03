'use client';

import React, { useState, useEffect } from 'react';
import { SAMPLE_BOOKS } from '@/utils/sampleData';
import { createClient } from '@/utils/supabase/client';
import { 
  ShieldAlert, 
  Users, 
  BookOpen, 
  FileText, 
  Eye, 
  Download, 
  Flag, 
  Sparkles, 
  Megaphone, 
  Trash2, 
  CheckCircle, 
  XCircle, 
  Plus, 
  Star,
  HardDrive
} from 'lucide-react';

export default function AdminDashboardPage() {
  const [activeTab, setActiveTab] = useState<'moderation' | 'users' | 'ads' | 'reports' | 'announcements'>('moderation');
  const [booksList, setBooksList] = useState(SAMPLE_BOOKS);
  const [announcementText, setAnnouncementText] = useState('');
  const [announcementSent, setAnnouncementSent] = useState(false);

  // Advertisement Campaigns State
  const [ads, setAds] = useState([
    {
      id: 'ad-1',
      title: 'Novelix Premium Pass',
      placement: 'homepage_banner',
      impressions: 14200,
      clicks: 890,
      active: true,
      targetUrl: '/settings',
    },
    {
      id: 'ad-2',
      title: 'Creator Publishing Contest 2026',
      placement: 'between_cards',
      impressions: 8900,
      clicks: 470,
      active: true,
      targetUrl: '/publish',
    },
    {
      id: 'ad-3',
      title: 'Mechanical Keyboards for Writers',
      placement: 'book_details',
      impressions: 6300,
      clicks: 240,
      active: false,
      targetUrl: 'https://example.com',
    },
  ]);

  // Reports
  const [reports, setReports] = useState([
    {
      id: 'rep-1',
      contentTitle: 'Chapter 2 Spoiler Commentary',
      type: 'Comment',
      reason: 'Harassment & Spoilers',
      reportedBy: 'user_4829',
      status: 'pending',
    },
    {
      id: 'rep-2',
      contentTitle: 'Unlicensed Artwork Upload',
      type: 'Book Cover',
      reason: 'Copyright Claim',
      reportedBy: 'artist_studio',
      status: 'pending',
    },
  ]);

  // Users
  const [users, setUsers] = useState([
    { id: 'u1', name: 'Aria Sterling', email: 'aria@novelix.io', role: 'Author', verified: true, status: 'Active' },
    { id: 'u2', name: 'Dr. Tariq Al-Mansoor', email: 'tariq@novelix.io', role: 'Author', verified: true, status: 'Active' },
    { id: 'u3', name: 'Jin-Woo Art Studio', email: 'jinwoo@manhwa.kr', role: 'Author', verified: true, status: 'Active' },
    { id: 'u4', name: 'SpamBot_99', email: 'bot@spam.io', role: 'Reader', verified: false, status: 'Suspended' },
  ]);

  const toggleFeatureBook = (id: string) => {
    setBooksList(
      booksList.map((b) => (b.id === id ? { ...b, is_featured: !b.is_featured } : b))
    );
  };

  const removeBook = (id: string) => {
    setBooksList(booksList.filter((b) => b.id !== id));
  };

  const toggleAdActive = (id: string) => {
    setAds(ads.map((a) => (a.id === id ? { ...a, active: !a.active } : a)));
  };

  const toggleUserVerified = (id: string) => {
    setUsers(users.map((u) => (u.id === id ? { ...u, verified: !u.verified } : u)));
  };

  const toggleUserSuspended = (id: string) => {
    setUsers(
      users.map((u) =>
        u.id === id
          ? { ...u, status: u.status === 'Active' ? 'Suspended' : 'Active' }
          : u
      )
    );
  };

  const resolveReport = (id: string) => {
    setReports(reports.filter((r) => r.id !== id));
  };

  const handleCreateAnnouncement = (e: React.FormEvent) => {
    e.preventDefault();
    if (!announcementText.trim()) return;
    setAnnouncementSent(true);
    setTimeout(() => {
      setAnnouncementSent(false);
      setAnnouncementText('');
    }, 2000);
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-wider mb-1">
            <ShieldAlert className="w-4 h-4" />
            <span>Administrator Security Clearance Level 1</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            Platform Administration Console
          </h1>
          <p className="text-xs sm:text-sm text-zinc-400 mt-1">
            Supervise publications, enforce Row Level Security compliance, moderate reports, and manage advertisements.
          </p>
        </div>
      </div>

      {/* Global Telemetry Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl bg-novelix-900 border border-novelix-800 space-y-1">
          <p className="text-xs text-zinc-400">Total Users</p>
          <p className="text-xl font-bold font-mono text-white">24,910</p>
          <span className="text-[10px] text-emerald-400 font-mono">+412 today</span>
        </div>
        <div className="p-4 rounded-2xl bg-novelix-900 border border-novelix-800 space-y-1">
          <p className="text-xs text-zinc-400">Total Publications</p>
          <p className="text-xl font-bold font-mono text-white">1,842</p>
          <span className="text-[10px] text-novelix-neon font-mono">48 pending</span>
        </div>
        <div className="p-4 rounded-2xl bg-novelix-900 border border-novelix-800 space-y-1">
          <p className="text-xs text-zinc-400">Total PDF Editions</p>
          <p className="text-xl font-bold font-mono text-white">5,190</p>
          <span className="text-[10px] text-sky-400 font-mono">Synced on Drive</span>
        </div>
        <div className="p-4 rounded-2xl bg-novelix-900 border border-novelix-800 space-y-1">
          <p className="text-xs text-zinc-400">Pending Flags</p>
          <p className="text-xl font-bold font-mono text-amber-400">{reports.length}</p>
          <span className="text-[10px] text-amber-300 font-mono">Action required</span>
        </div>
      </div>

      {/* Admin Navigation Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-novelix-800 text-xs font-semibold">
        {[
          { id: 'moderation', label: 'Publication Moderation' },
          { id: 'users', label: 'User & Author Management' },
          { id: 'ads', label: 'Advertisement Campaigns' },
          { id: 'reports', label: `Reported Content (${reports.length})` },
          { id: 'announcements', label: 'Global Announcements' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-3.5 py-2 rounded-xl whitespace-nowrap transition-all ${
              activeTab === tab.id
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                : 'text-zinc-400 hover:text-white hover:bg-novelix-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab: Publication Moderation */}
      {activeTab === 'moderation' && (
        <div className="space-y-4">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">
            Review & Moderate Publications
          </h2>

          <div className="space-y-3">
            {booksList.map((book) => (
              <div
                key={book.id}
                className="p-4 rounded-2xl bg-novelix-900/60 border border-novelix-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
              >
                <div className="flex items-center gap-3">
                  <img src={book.cover_url} alt={book.title} className="w-12 h-16 rounded-xl object-cover" />
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-white">{book.title}</span>
                      {book.is_featured && (
                        <span className="text-[9px] bg-amber-500/20 text-amber-300 border border-amber-500/30 px-1.5 py-0.2 rounded font-mono">
                          FEATURED
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-zinc-400">
                      Genre: {book.primary_genre} • {book.publication_type} • {book.view_count || 1200} views
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-auto text-xs">
                  <button
                    onClick={() => toggleFeatureBook(book.id)}
                    className={`flex items-center gap-1 px-3 py-1.5 rounded-xl font-medium border ${
                      book.is_featured
                        ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                        : 'bg-novelix-900 text-zinc-400 border-novelix-800 hover:text-white'
                    }`}
                  >
                    <Star className="w-3.5 h-3.5" />
                    <span>{book.is_featured ? 'Featured' : 'Feature'}</span>
                  </button>

                  <button
                    onClick={() => removeBook(book.id)}
                    className="p-1.5 rounded-xl bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20"
                    title="Remove publication"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab: Users & Verification */}
      {activeTab === 'users' && (
        <div className="space-y-4">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">
            User Accounts & Author Verification
          </h2>

          <div className="space-y-3">
            {users.map((u) => (
              <div
                key={u.id}
                className="p-4 rounded-2xl bg-novelix-900/60 border border-novelix-800 flex items-center justify-between gap-4"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white">{u.name}</span>
                    {u.verified && (
                      <span className="text-[9px] bg-novelix-electric/30 text-novelix-neon px-1.5 py-0.2 rounded font-mono">
                        VERIFIED CREATOR
                      </span>
                    )}
                    {u.status === 'Suspended' && (
                      <span className="text-[9px] bg-red-500/20 text-red-400 px-1.5 py-0.2 rounded font-mono">
                        SUSPENDED
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-zinc-500 font-mono mt-0.5">{u.email} • Role: {u.role}</p>
                </div>

                <div className="flex items-center gap-2 text-xs">
                  <button
                    onClick={() => toggleUserVerified(u.id)}
                    className="px-3 py-1.5 rounded-xl bg-novelix-900 text-zinc-300 hover:text-white border border-novelix-800"
                  >
                    {u.verified ? 'Revoke Badge' : 'Grant Verified'}
                  </button>
                  <button
                    onClick={() => toggleUserSuspended(u.id)}
                    className={`px-3 py-1.5 rounded-xl border ${
                      u.status === 'Suspended'
                        ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                        : 'bg-red-500/20 text-red-400 border-red-500/40'
                    }`}
                  >
                    {u.status === 'Suspended' ? 'Unsuspend' : 'Suspend'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab: Advertisements Management */}
      {activeTab === 'ads' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">
              Sponsored Advertisement Campaigns
            </h2>
            <button
              onClick={() => {
                const title = prompt('Enter advertisement title:');
                if (title) {
                  setAds([
                    ...ads,
                    {
                      id: `ad-${Date.now()}`,
                      title,
                      placement: 'homepage_banner',
                      impressions: 0,
                      clicks: 0,
                      active: true,
                      targetUrl: '/settings',
                    },
                  ]);
                }
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-novelix-electric text-white"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Create Ad</span>
            </button>
          </div>

          <div className="space-y-3">
            {ads.map((ad) => (
              <div
                key={ad.id}
                className="p-4 rounded-2xl bg-novelix-900/60 border border-novelix-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white">{ad.title}</span>
                    <span className="text-[10px] uppercase font-mono px-1.5 py-0.2 rounded bg-novelix-800 text-zinc-300">
                      {ad.placement}
                    </span>
                  </div>
                  <p className="text-[11px] text-zinc-400 font-mono mt-0.5">
                    {ad.impressions.toLocaleString()} Impressions • {ad.clicks.toLocaleString()} Clicks • CTR:{' '}
                    {ad.impressions > 0 ? ((ad.clicks / ad.impressions) * 100).toFixed(1) : 0}%
                  </p>
                </div>

                <button
                  onClick={() => toggleAdActive(ad.id)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-semibold border ${
                    ad.active
                      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                      : 'bg-zinc-800 text-zinc-400 border-zinc-700'
                  }`}
                >
                  {ad.active ? 'Active' : 'Paused'}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab: Reports */}
      {activeTab === 'reports' && (
        <div className="space-y-4">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">
            Reported Content & Violations
          </h2>

          <div className="space-y-3">
            {reports.map((rep) => (
              <div
                key={rep.id}
                className="p-4 rounded-2xl bg-novelix-900/60 border border-novelix-800 flex items-center justify-between gap-4"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white">{rep.contentTitle}</span>
                    <span className="text-[9px] bg-red-500/20 text-red-400 px-1.5 py-0.2 rounded font-mono">
                      {rep.type}
                    </span>
                  </div>
                  <p className="text-[11px] text-zinc-400 mt-0.5">
                    Reason: <strong className="text-zinc-200">{rep.reason}</strong> • Flagged by {rep.reportedBy}
                  </p>
                </div>

                <div className="flex items-center gap-2 text-xs">
                  <button
                    onClick={() => resolveReport(rep.id)}
                    className="px-3 py-1.5 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                  >
                    Dismiss
                  </button>
                  <button
                    onClick={() => resolveReport(rep.id)}
                    className="px-3 py-1.5 rounded-xl bg-red-500/20 text-red-300 border border-red-500/30"
                  >
                    Delete Content
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab: Announcements */}
      {activeTab === 'announcements' && (
        <div className="space-y-4 max-w-xl">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Megaphone className="w-4 h-4 text-novelix-neon" />
            Broadcast Global Announcement
          </h2>

          {announcementSent && (
            <div className="p-3 rounded-xl bg-emerald-500/20 text-emerald-300 text-xs font-bold">
              Announcement broadcast to all user notification feeds!
            </div>
          )}

          <form onSubmit={handleCreateAnnouncement} className="space-y-3">
            <textarea
              rows={4}
              value={announcementText}
              onChange={(e) => setAnnouncementText(e.target.value)}
              placeholder="Write message to send to all registered readers and authors..."
              className="w-full bg-novelix-950 text-xs text-white p-3 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
            />
            <button
              type="submit"
              className="px-5 py-2 rounded-xl text-xs font-bold bg-novelix-electric hover:bg-novelix-violet text-white transition-colors"
            >
              Broadcast Now
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
