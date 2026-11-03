'use client';

import React from 'react';
import { usePathname } from 'next/navigation';
import { Sidebar } from './Sidebar';
import { Navbar } from './Navbar';
import { BottomNav } from './BottomNav';

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isReaderMode = pathname.startsWith('/read/') || pathname.startsWith('/manhwa/');

  if (isReaderMode) {
    return <main className="min-h-screen bg-novelix-950">{children}</main>;
  }

  return (
    <div className="flex min-h-screen bg-novelix-950 text-zinc-100 selection:bg-novelix-purple selection:text-white">
      {/* Desktop Left Sidebar */}
      <Sidebar />

      {/* Main Flow */}
      <div className="flex-1 flex flex-col min-w-0 pb-16 lg:pb-0">
        <Navbar />
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>

      {/* Mobile Bottom Navigation */}
      <BottomNav />
    </div>
  );
}
