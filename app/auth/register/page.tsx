'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { createClient } from '@/utils/supabase/client';
import { BookOpen, UserPlus, Mail, Lock, User, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isAuthor, setIsAuthor] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isRegistered, setIsRegistered] = useState(false);

  const supabase = createClient();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const siteUrl = window.location.origin;
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: name,
            username: name.toLowerCase().replace(/\s+/g, '_') + '_' + Math.floor(Math.random() * 1000),
            is_author: isAuthor,
          },
          emailRedirectTo: `${siteUrl}/auth/callback`,
        },
      });

      if (error) throw error;

      setIsRegistered(true);
    } catch (err: any) {
      setErrorMessage(err.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSignup = async () => {
    try {
      const siteUrl = window.location.origin;
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${siteUrl}/auth/callback`,
        },
      });
      if (error) throw error;
    } catch (err: any) {
      setErrorMessage(err.message || 'Google signup failed');
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-novelix-900/90 border border-novelix-800 rounded-3xl p-6 sm:p-8 shadow-2xl backdrop-blur-xl space-y-6">
        {isRegistered ? (
          <div className="text-center space-y-4 py-4">
            <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-bold text-white">Registration Successful!</h2>
            <p className="text-xs text-zinc-300 leading-relaxed">
              We sent a confirmation link to <strong className="text-white">{email}</strong>. Please check your inbox to activate your account.
            </p>
            <Link
              href="/auth/login"
              className="inline-block px-5 py-2 rounded-xl text-xs font-semibold bg-novelix-electric text-white mt-2"
            >
              Go to Login
            </Link>
          </div>
        ) : (
          <>
            <div className="text-center space-y-2">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-novelix-purple via-novelix-electric to-novelix-neon flex items-center justify-center mx-auto shadow-glow-sm">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-extrabold text-white">Create Your Account</h1>
              <p className="text-xs text-zinc-400">
                Join readers and creators worldwide on NOVELIX.
              </p>
            </div>

            {errorMessage && (
              <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/20 text-xs text-red-300 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            <button
              onClick={handleGoogleSignup}
              type="button"
              className="w-full flex items-center justify-center gap-3 py-2.5 px-4 rounded-xl bg-novelix-950 hover:bg-novelix-850 text-white border border-novelix-800 text-xs font-semibold transition-all"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
              </svg>
              <span>Sign Up with Google</span>
            </button>

            <div className="flex items-center gap-3 text-xs text-zinc-500">
              <div className="h-px bg-novelix-800 flex-1" />
              <span>or register with email</span>
              <div className="h-px bg-novelix-800 flex-1" />
            </div>

            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-zinc-300 mb-1">Your Full Name</label>
                <div className="relative">
                  <User className="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    placeholder="Aria Sterling"
                    className="w-full bg-novelix-950 text-xs text-white pl-9 pr-3 py-2.5 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-zinc-300 mb-1">Email Address</label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="aria@novelix.io"
                    className="w-full bg-novelix-950 text-xs text-white pl-9 pr-3 py-2.5 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-zinc-300 mb-1">Password</label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    minLength={6}
                    placeholder="At least 6 characters"
                    className="w-full bg-novelix-950 text-xs text-white pl-9 pr-3 py-2.5 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="authorCheck"
                  checked={isAuthor}
                  onChange={(e) => setIsAuthor(e.target.checked)}
                  className="rounded bg-novelix-950 border-novelix-800 text-novelix-purple"
                />
                <label htmlFor="authorCheck" className="text-xs text-zinc-300 cursor-pointer">
                  I plan to publish original stories, novels, or manhwa
                </label>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-novelix-purple via-novelix-electric to-novelix-neon text-white shadow-glow-sm hover:shadow-glow-md transition-all disabled:opacity-50"
              >
                <UserPlus className="w-4 h-4" />
                <span>{isLoading ? 'Creating Account...' : 'Create Account'}</span>
              </button>
            </form>

            <p className="text-center text-xs text-zinc-400">
              Already have an account?{' '}
              <Link href="/auth/login" className="text-novelix-neon font-bold hover:underline">
                Sign In
              </Link>
            </p>
          </>
        )}
      </div>
    </div>
  );
}
