'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Home, 
  Compass, 
  Search, 
  BookOpen, 
  Layers, 
  Sparkles, 
  BookmarkCheck, 
  UploadCloud, 
  LayoutDashboard, 
  Bell, 
  Settings, 
  ShieldAlert,
  Flame
} from 'lucide-react';

interface SidebarProps {
  isAdmin?: boolean;
}

export function Sidebar({ isAdmin = false }: SidebarProps) {
  const pathname = usePathname();

  const navigationItems = [
    { name: 'Home', href: '/', icon: Home },
    { name: 'Explore', href: '/explore', icon: Compass },
    { name: 'Search', href: '/search', icon: Search },
    { name: 'Manhwa & Comics', href: '/explore?type=manhwa', icon: Flame },
    { name: 'Book Series', href: '/explore?type=series', icon: Layers },
    { name: 'My Library', href: '/library', icon: BookmarkCheck },
  ];

  const creatorItems = [
    { name: 'Publishing Studio', href: '/publish', icon: UploadCloud, highlight: true },
    { name: 'Author Dashboard', href: '/dashboard', icon: LayoutDashboard },
  ];

  const systemItems = [
    { name: 'Notifications', href: '/notifications', icon: Bell },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  if (isAdmin) {
    systemItems.push({ name: 'Admin Console', href: '/admin', icon: ShieldAlert });
  }

  const isItemActive = (href: string) => {
    if (href === '/') return pathname === '/';
    return pathname.startsWith(href);
  };

  return (
    <aside className="hidden lg:flex flex-col w-64 border-r border-novelix-800 bg-novelix-950/80 backdrop-blur-xl shrink-0 h-screen sticky top-0 z-40 select-none">
      {/* Brand Header */}
      <div className="p-6 pb-4 flex items-center justify-between border-b border-novelix-850">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-novelix-purple via-novelix-electric to-novelix-neon flex items-center justify-center shadow-glow-sm group-hover:shadow-glow-md transition-all duration-300">
            <BookOpen className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-extrabold text-xl tracking-wider bg-clip-text text-transparent bg-gradient-to-r from-white via-purple-100 to-novelix-neon font-sans">
              NOVELIX
            </span>
            <p className="text-[10px] text-zinc-400 tracking-widest uppercase font-mono">Publish & Read</p>
          </div>
        </Link>
      </div>

      {/* Nav List */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 scrollbar-thin scrollbar-thumb-novelix-800">
        {/* Main Discovery */}
        <div>
          <div className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider px-3 mb-2">
            Discover
          </div>
          <nav className="space-y-1">
            {navigationItems.map((item) => {
              const active = isItemActive(item.href);
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center gap-3.5 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group relative ${
                    active
                      ? 'bg-gradient-to-r from-novelix-electric/20 to-novelix-purple/10 text-white shadow-sm border border-novelix-electric/30 font-semibold'
                      : 'text-zinc-400 hover:text-white hover:bg-novelix-900/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 transition-transform duration-200 group-hover:scale-110 ${active ? 'text-novelix-neon' : 'text-zinc-400 group-hover:text-novelix-neon'}`} />
                  <span>{item.name}</span>
                  {active && (
                    <div className="absolute right-2 w-1.5 h-4 rounded-full bg-novelix-neon shadow-glow-sm" />
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Creator Studio */}
        <div>
          <div className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider px-3 mb-2">
            Creator Studio
          </div>
          <nav className="space-y-1">
            {creatorItems.map((item) => {
              const active = isItemActive(item.href);
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center gap-3.5 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group relative ${
                    active
                      ? 'bg-gradient-to-r from-novelix-electric/25 to-novelix-purple/20 text-white border border-novelix-neon/40 shadow-glow-sm'
                      : 'text-zinc-400 hover:text-white hover:bg-novelix-900/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 transition-transform duration-200 group-hover:scale-110 ${active ? 'text-novelix-neon' : 'text-zinc-400 group-hover:text-novelix-neon'}`} />
                  <span>{item.name}</span>
                  {item.highlight && !active && (
                    <span className="ml-auto text-[10px] bg-novelix-purple/30 text-novelix-neon px-2 py-0.5 rounded-full font-mono border border-novelix-purple/40">
                      NEW
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Account & Administration */}
        <div>
          <div className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider px-3 mb-2">
            Preferences
          </div>
          <nav className="space-y-1">
            {systemItems.map((item) => {
              const active = isItemActive(item.href);
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center gap-3.5 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group relative ${
                    active
                      ? 'bg-gradient-to-r from-novelix-electric/20 to-novelix-purple/10 text-white border border-novelix-electric/30'
                      : 'text-zinc-400 hover:text-white hover:bg-novelix-900/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 transition-transform duration-200 group-hover:scale-110 ${active ? 'text-novelix-neon' : 'text-zinc-400 group-hover:text-novelix-neon'}`} />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Footer Banner */}
      <div className="p-4 border-t border-novelix-850">
        <div className="p-3.5 rounded-2xl bg-gradient-to-br from-novelix-900 via-novelix-850 to-novelix-purple/10 border border-novelix-800/80">
          <div className="flex items-center gap-2 mb-1.5">
            <Sparkles className="w-4 h-4 text-novelix-neon animate-pulse" />
            <span className="text-xs font-semibold text-white">NOVELIX Cloud</span>
          </div>
          <p className="text-[11px] text-zinc-400 leading-relaxed mb-2.5">
            Sync Google Drive accounts & multi-language publications.
          </p>
          <Link
            href="/publish"
            className="block text-center text-xs font-semibold py-1.5 px-3 rounded-lg bg-novelix-electric hover:bg-novelix-violet text-white transition-colors duration-200 shadow-sm"
          >
            Start Publishing
          </Link>
        </div>
      </div>
    </aside>
  );
}
