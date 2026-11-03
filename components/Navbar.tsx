'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  Search, 
  Bell, 
  Sun, 
  Moon, 
  PlusCircle, 
  User, 
  LogOut, 
  Shield, 
  Terminal, 
  BookMarked,
  Sparkles,
  Menu,
  X
} from 'lucide-react';
import { useTheme } from './ThemeProvider';
import { createClient } from '@/utils/supabase/client';

export function Navbar() {
  const router = useRouter();
  const { theme, toggleTheme } = useTheme();
  const [user, setUser] = useState<any>(null);
  const [profile, setProfile] = useState<any>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [unreadCount, setUnreadCount] = useState(3);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const supabase = createClient();

  useEffect(() => {
    async function loadUser() {
      const { data: { user } } = await supabase.auth.getUser();
      setUser(user);
      if (user) {
        const { data: profile } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', user.id)
          .maybeSingle();
        setProfile(profile);

        // Fetch unread notifications
        const { count } = await supabase
          .from('notifications')
          .select('*', { count: 'exact', head: true })
          .eq('recipient_id', user.id)
          .eq('is_read', false);
        
        if (count !== null) setUnreadCount(count);
      }
    }
    loadUser();

    const { data: authListener } = supabase.auth.onAuthStateChange((_, session) => {
      setUser(session?.user || null);
    });

    return () => {
      authListener.subscription.unsubscribe();
    };
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setUser(null);
    setProfile(null);
    router.push('/auth/login');
  };

  return (
    <header className="sticky top-0 z-30 w-full bg-novelix-950/75 dark:bg-novelix-950/85 backdrop-blur-md border-b border-novelix-800/80 px-4 lg:px-8 py-3 transition-colors duration-200">
      <div className="flex items-center justify-between gap-4 max-w-7xl mx-auto">
        {/* Mobile Hamburger & Logo */}
        <div className="flex items-center gap-3 lg:hidden">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-novelix-900 border border-novelix-800"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
          <Link href="/" className="font-extrabold text-lg tracking-wider text-white">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-novelix-neon to-novelix-electric">
              NOVELIX
            </span>
          </Link>
        </div>

        {/* Global Search Bar */}
        <form onSubmit={handleSearchSubmit} className="hidden md:flex flex-1 max-w-md relative">
          <Search className="w-4 h-4 text-zinc-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search books, novels, authors, or genres..."
            className="w-full bg-novelix-900/90 text-sm text-white placeholder-zinc-400 pl-10 pr-10 py-2 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon focus:ring-1 focus:ring-novelix-neon transition-all"
          />
          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-zinc-400 border border-novelix-750 rounded px-1.5 py-0.5 font-mono">
            ⌘K
          </span>
        </form>

        {/* Right Action Icons */}
        <div className="flex items-center gap-2.5 sm:gap-4">
          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-novelix-900 border border-novelix-800/80 transition-all duration-200"
            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-novelix-purple" />}
          </button>

          {/* Notifications */}
          <Link
            href="/notifications"
            className="relative p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-novelix-900 border border-novelix-800/80 transition-all duration-200"
            title="Notifications"
          >
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-novelix-violet text-white text-[10px] font-bold rounded-full flex items-center justify-center animate-pulse">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </Link>

          {/* Quick Publish CTA */}
          <Link
            href="/publish"
            className="hidden sm:flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-novelix-purple to-novelix-electric hover:from-novelix-electric hover:to-novelix-neon text-white shadow-glow-sm hover:shadow-glow-md transition-all duration-300"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>Publish</span>
          </Link>

          {/* User Profile / Auth State */}
          {user ? (
            <div className="relative">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="flex items-center gap-2 p-1 pl-2 rounded-full border border-novelix-800 hover:border-novelix-neon bg-novelix-900/60 transition-all"
              >
                <span className="text-xs font-medium text-zinc-300 hidden md:block max-w-[100px] truncate">
                  {profile?.display_name || user.email?.split('@')[0]}
                </span>
                <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-novelix-purple to-novelix-neon flex items-center justify-center text-xs font-bold text-white overflow-hidden shadow-inner">
                  {profile?.avatar_url ? (
                    <img src={profile.avatar_url} alt="Avatar" className="w-full h-full object-cover" />
                  ) : (
                    <span>{(profile?.display_name || user.email || 'U')[0].toUpperCase()}</span>
                  )}
                </div>
              </button>

              {/* Profile Dropdown */}
              {isMenuOpen && (
                <div className="absolute right-0 mt-2 w-56 rounded-2xl bg-novelix-900/95 border border-novelix-800 shadow-2xl py-2 z-50 backdrop-blur-xl animate-in fade-in zoom-in-95 duration-150">
                  <div className="px-4 py-2 border-b border-novelix-800/80 mb-1">
                    <p className="text-xs font-bold text-white truncate">{profile?.display_name || 'Reader'}</p>
                    <p className="text-[11px] text-zinc-400 truncate">{user.email}</p>
                    {profile?.is_admin && (
                      <span className="inline-block mt-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-red-500/20 text-red-400 border border-red-500/30">
                        Admin Account
                      </span>
                    )}
                  </div>

                  <Link
                    href={`/author/${profile?.username || user.id}`}
                    onClick={() => setIsMenuOpen(false)}
                    className="flex items-center gap-2.5 px-4 py-2 text-xs text-zinc-300 hover:text-white hover:bg-novelix-800/60"
                  >
                    <User className="w-3.5 h-3.5 text-novelix-neon" />
                    <span>Author Profile</span>
                  </Link>

                  <Link
                    href="/library"
                    onClick={() => setIsMenuOpen(false)}
                    className="flex items-center gap-2.5 px-4 py-2 text-xs text-zinc-300 hover:text-white hover:bg-novelix-800/60"
                  >
                    <BookMarked className="w-3.5 h-3.5 text-novelix-electric" />
                    <span>My Library</span>
                  </Link>

                  <Link
                    href="/settings/developer"
                    onClick={() => setIsMenuOpen(false)}
                    className="flex items-center gap-2.5 px-4 py-2 text-xs text-zinc-300 hover:text-white hover:bg-novelix-800/60"
                  >
                    <Terminal className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Developer Console</span>
                  </Link>

                  {profile?.is_admin && (
                    <Link
                      href="/admin"
                      onClick={() => setIsMenuOpen(false)}
                      className="flex items-center gap-2.5 px-4 py-2 text-xs text-amber-300 hover:text-amber-200 hover:bg-amber-500/10"
                    >
                      <Shield className="w-3.5 h-3.5 text-amber-400" />
                      <span>Admin Dashboard</span>
                    </Link>
                  )}

                  <div className="border-t border-novelix-800/80 my-1 pt-1">
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-2.5 px-4 py-2 text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10"
                    >
                      <LogOut className="w-3.5 h-3.5" />
                      <span>Log Out</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                href="/auth/login"
                className="px-3.5 py-1.5 rounded-xl text-xs font-semibold text-zinc-300 hover:text-white hover:bg-novelix-900 border border-novelix-800 transition-all"
              >
                Log In
              </Link>
              <Link
                href="/auth/register"
                className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-novelix-electric hover:bg-novelix-violet text-white transition-all shadow-glow-sm"
              >
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Mobile Drawer Navigation */}
      {mobileMenuOpen && (
        <div className="lg:hidden mt-3 pt-3 border-t border-novelix-800/80 space-y-2 animate-in slide-in-from-top-4">
          <form onSubmit={handleSearchSubmit} className="relative pb-2">
            <Search className="w-4 h-4 text-zinc-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search books..."
              className="w-full bg-novelix-900 text-sm text-white pl-9 pr-4 py-2 rounded-xl border border-novelix-800"
            />
          </form>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <Link href="/" onClick={() => setMobileMenuOpen(false)} className="p-2.5 rounded-xl bg-novelix-900 text-white font-medium">Home</Link>
            <Link href="/explore" onClick={() => setMobileMenuOpen(false)} className="p-2.5 rounded-xl bg-novelix-900 text-white font-medium">Explore</Link>
            <Link href="/library" onClick={() => setMobileMenuOpen(false)} className="p-2.5 rounded-xl bg-novelix-900 text-white font-medium">My Library</Link>
            <Link href="/publish" onClick={() => setMobileMenuOpen(false)} className="p-2.5 rounded-xl bg-novelix-electric/30 text-novelix-neon font-medium border border-novelix-electric/40">Publish Studio</Link>
            <Link href="/dashboard" onClick={() => setMobileMenuOpen(false)} className="p-2.5 rounded-xl bg-novelix-900 text-white font-medium">Author Dashboard</Link>
            <Link href="/settings" onClick={() => setMobileMenuOpen(false)} className="p-2.5 rounded-xl bg-novelix-900 text-white font-medium">Settings</Link>
          </div>
        </div>
      )}
    </header>
  );
}
