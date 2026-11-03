'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Compass, PlusCircle, BookmarkCheck, User } from 'lucide-react';

export function BottomNav() {
  const pathname = usePathname();

  // Hide bottom nav in reader mode for immersive reading
  if (pathname.startsWith('/read/') || pathname.startsWith('/manhwa/')) {
    return null;
  }

  const navItems = [
    { label: 'Home', href: '/', icon: Home },
    { label: 'Explore', href: '/explore', icon: Compass },
    { label: 'Publish', href: '/publish', icon: PlusCircle, highlight: true },
    { label: 'Library', href: '/library', icon: BookmarkCheck },
    { label: 'Settings', href: '/settings', icon: User },
  ];

  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-novelix-950/95 backdrop-blur-xl border-t border-novelix-800/80 px-2 py-2">
      <div className="flex items-center justify-around">
        {navItems.map((item) => {
          const active = item.href === '/' ? pathname === '/' : pathname.startsWith(item.href);
          const Icon = item.icon;
          return (
            <Link
              key={item.label}
              href={item.href}
              className={`flex flex-col items-center gap-1 py-1 px-3 rounded-xl transition-all ${
                item.highlight
                  ? 'text-novelix-neon'
                  : active
                  ? 'text-white'
                  : 'text-zinc-400 hover:text-zinc-300'
              }`}
            >
              {item.highlight ? (
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-novelix-purple to-novelix-electric flex items-center justify-center text-white shadow-glow-sm">
                  <Icon className="w-4 h-4" />
                </div>
              ) : (
                <Icon className={`w-5 h-5 ${active ? 'text-novelix-neon' : ''}`} />
              )}
              <span className="text-[10px] font-medium">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
