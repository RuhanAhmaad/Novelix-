'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { createClient } from '@/utils/supabase/client';
import { BookOpen, Mail, ArrowLeft, CheckCircle2, AlertCircle } from 'lucide-react';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const supabase = createClient();

  const handleReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const siteUrl = window.location.origin;
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${siteUrl}/auth/callback?next=/settings`,
      });

      if (error) throw error;
      setSent(true);
    } catch (err: any) {
      setErrorMessage(err.message || 'Password reset request failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-novelix-900/90 border border-novelix-800 rounded-3xl p-6 sm:p-8 shadow-2xl backdrop-blur-xl space-y-6">
        <Link
          href="/auth/login"
          className="inline-flex items-center gap-1.5 text-xs text-zinc-400 hover:text-white"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Login</span>
        </Link>

        {sent ? (
          <div className="text-center space-y-3 py-4">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
            <h2 className="text-lg font-bold text-white">Reset Link Dispatched</h2>
            <p className="text-xs text-zinc-300 leading-relaxed">
              If an account exists with <strong className="text-white">{email}</strong>, you will receive an email with instructions to securely choose a new password.
            </p>
          </div>
        ) : (
          <>
            <div className="text-center space-y-2">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-novelix-purple to-novelix-neon flex items-center justify-center mx-auto shadow-glow-sm">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-xl font-bold text-white">Recover Your Password</h1>
              <p className="text-xs text-zinc-400">
                Enter your email address and we will send you a recovery link.
              </p>
            </div>

            {errorMessage && (
              <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/20 text-xs text-red-300 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            <form onSubmit={handleReset} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-zinc-300 mb-1">Email Address</label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="reader@novelix.io"
                    className="w-full bg-novelix-950 text-xs text-white pl-9 pr-3 py-2.5 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-novelix-purple to-novelix-neon text-white shadow-glow-sm hover:shadow-glow-md transition-all disabled:opacity-50"
              >
                {isLoading ? 'Sending...' : 'Send Recovery Link'}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
