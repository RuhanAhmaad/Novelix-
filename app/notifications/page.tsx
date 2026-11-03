'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { 
  Bell, 
  UserPlus, 
  BookOpen, 
  MessageSquare, 
  CheckCircle, 
  Sparkles, 
  Trash2, 
  CheckCheck 
} from 'lucide-react';

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([
    {
      id: 'notif-1',
      type: 'new_follower',
      title: 'New Follower Alert',
      message: 'Celeste Vane (@celeste_vane) started following your author profile.',
      time: '10 minutes ago',
      is_read: false,
      link: '/author/celeste_vane',
      icon: UserPlus,
      color: 'text-novelix-neon bg-novelix-electric/20',
    },
    {
      id: 'notif-2',
      type: 'collaboration_invite',
      title: 'Author Collaboration Invitation',
      message: 'Dr. Tariq Al-Mansoor invited you to co-author "The Lost Empire" translation in Arabic.',
      time: '2 hours ago',
      is_read: false,
      link: '/publish',
      icon: BookOpen,
      color: 'text-emerald-400 bg-emerald-500/20',
    },
    {
      id: 'notif-3',
      type: 'comment',
      title: 'New Chapter Discussion',
      message: 'Kareem replied to your comment on "The Midnight Castle — Chapter 1".',
      time: '1 day ago',
      is_read: true,
      link: '/book/b1000000-0000-0000-0000-000000000001',
      icon: MessageSquare,
      color: 'text-sky-400 bg-sky-500/20',
    },
    {
      id: 'notif-4',
      type: 'announcement',
      title: 'Platform Update: Multi-Drive Support v1.0',
      message: 'You can now link multiple Google Drive accounts with seamless AES-256 token encryption.',
      time: '3 days ago',
      is_read: true,
      link: '/settings',
      icon: Sparkles,
      color: 'text-amber-400 bg-amber-500/20',
    },
  ]);

  const markAllRead = () => {
    setNotifications(notifications.map((n) => ({ ...n, is_read: true })));
  };

  const clearAll = () => {
    setNotifications([]);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-2.5">
            <Bell className="w-6 h-6 text-novelix-neon" />
            Notifications
          </h1>
          <p className="text-xs text-zinc-400 mt-0.5">Stay updated with your readers, collaborators, and releases.</p>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <button
            onClick={markAllRead}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-novelix-900 border border-novelix-800 text-zinc-300 hover:text-white"
          >
            <CheckCheck className="w-3.5 h-3.5" />
            <span>Mark all read</span>
          </button>
          <button
            onClick={clearAll}
            className="p-2 rounded-xl bg-novelix-900 border border-novelix-800 text-zinc-400 hover:text-red-400"
            title="Clear all"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Notifications list */}
      {notifications.length > 0 ? (
        <div className="space-y-3">
          {notifications.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.id}
                href={item.link}
                className={`p-4 rounded-2xl border transition-all flex items-start gap-4 block ${
                  item.is_read
                    ? 'bg-novelix-900/30 border-novelix-800/60 opacity-80'
                    : 'bg-novelix-900/80 border-novelix-neon/40 shadow-sm'
                }`}
              >
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${item.color}`}>
                  <Icon className="w-5 h-5" />
                </div>

                <div className="flex-1 space-y-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-white truncate">{item.title}</h4>
                    <span className="text-[10px] text-zinc-500 font-mono shrink-0">{item.time}</span>
                  </div>
                  <p className="text-xs text-zinc-300 leading-relaxed">{item.message}</p>
                </div>
              </Link>
            );
          })}
        </div>
      ) : (
        <div className="p-12 text-center rounded-2xl bg-novelix-900/40 border border-novelix-800 space-y-2">
          <Bell className="w-8 h-8 text-zinc-500 mx-auto" />
          <h3 className="text-sm font-bold text-white">All caught up!</h3>
          <p className="text-xs text-zinc-400">No new notifications at this time.</p>
        </div>
      )}
    </div>
  );
}
