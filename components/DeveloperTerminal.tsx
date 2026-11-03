'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Terminal as TerminalIcon, X, ShieldAlert, Lock, CheckCircle2 } from 'lucide-react';
import { createClient } from '@/utils/supabase/client';

interface DeveloperTerminalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function DeveloperTerminal({ isOpen, onClose }: DeveloperTerminalProps) {
  const router = useRouter();
  const [history, setHistory] = useState<string[]>([
    'NOVELIX SYSTEM TERMINAL [Version 1.0.0-PROD]',
    '(c) 2026 NOVELIX Digital Publishing Platform. All rights reserved.',
    '',
    'Type "help" to see available commands.',
  ]);
  const [inputVal, setInputVal] = useState('');
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [showAdminLogin, setShowAdminLogin] = useState(false);
  const [adminEmail, setAdminEmail] = useState('');
  const [adminPassword, setAdminPassword] = useState('');
  const [authStatus, setAuthStatus] = useState<string | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);

  const terminalEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history, showAdminLogin]);

  if (!isOpen) return null;

  const handleCommand = async (cmd: string) => {
    const trimmed = cmd.trim().toLowerCase();
    const newHistory = [...history, `> ${cmd}`];

    if (!trimmed) {
      setHistory(newHistory);
      return;
    }

    setCommandHistory((prev) => [...prev, cmd]);
    setHistoryIndex(-1);

    switch (trimmed) {
      case 'help':
        newHistory.push(
          'Available commands:',
          '  help      - Displays list of system commands',
          '  version   - Prints current software release and build target',
          '  status    - Checks Supabase database & storage subsystem health',
          '  clear     - Clears the terminal buffer',
          '  admin     - Access secure administrator verification portal',
          '  exit      - Close this terminal session'
        );
        break;

      case 'version':
        newHistory.push(
          'NOVELIX Core Engine v1.0.0',
          'Runtime: Next.js 14 App Router + Supabase SSR',
          'Database: PostgreSQL with Row-Level Security',
          'Storage: Google Drive Multi-Account API v3 & ImgBB CDN'
        );
        break;

      case 'status':
        newHistory.push(
          '[SYSTEM TELEMETRY]',
          '  Database: ONLINE (gzwpfvhmjweeydiwdsga.supabase.co)',
          '  Auth Engine: SECURE (Row-Level Security Active)',
          '  ImgBB Gateway: ONLINE',
          '  Google OAuth Protocol: ENABLED',
          '  PDF.js Canvas Engine: OPERATIONAL'
        );
        break;

      case 'clear':
        setHistory([]);
        return;

      case 'exit':
        onClose();
        return;

      case 'admin':
        newHistory.push(
          'INITIALIZING SECURE ADMINISTRATIVE LOGIN PROTOCOL...',
          'Authenticating against Supabase server-side role verification.',
          'Please input authorized credentials below:'
        );
        setShowAdminLogin(true);
        break;

      default:
        newHistory.push(
          `Command not recognized: "${cmd}". Type "help" for a list of valid commands.`
        );
        break;
    }

    setHistory(newHistory);
  };

  const handleAdminAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsVerifying(true);
    setAuthStatus('Verifying credentials with Supabase Auth & RLS...');

    try {
      const supabase = createClient();
      const { data, error } = await supabase.auth.signInWithPassword({
        email: adminEmail,
        password: adminPassword,
      });

      if (error || !data.user) {
        setAuthStatus(`Authentication failed: ${error?.message || 'Invalid credentials'}`);
        setIsVerifying(false);
        return;
      }

      // Verify admin role in profiles or user_roles
      const { data: profile } = await supabase
        .from('profiles')
        .select('is_admin')
        .eq('id', data.user.id)
        .maybeSingle();

      if (profile?.is_admin) {
        setAuthStatus('ACCESS GRANTED. Welcome Administrator. Redirecting...');
        setTimeout(() => {
          onClose();
          router.push('/admin');
        }, 1200);
      } else {
        setAuthStatus('ACCESS DENIED: Account does not possess administrator privileges.');
        setIsVerifying(false);
      }
    } catch (err: any) {
      setAuthStatus(`Authorization error: ${err.message}`);
      setIsVerifying(false);
    }
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleCommand(inputVal);
      setInputVal('');
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (commandHistory.length > 0) {
        const nextIdx = historyIndex + 1;
        if (nextIdx < commandHistory.length) {
          setHistoryIndex(nextIdx);
          setInputVal(commandHistory[commandHistory.length - 1 - nextIdx]);
        }
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex > 0) {
        const nextIdx = historyIndex - 1;
        setHistoryIndex(nextIdx);
        setInputVal(commandHistory[commandHistory.length - 1 - nextIdx]);
      } else {
        setHistoryIndex(-1);
        setInputVal('');
      }
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-2xl bg-black border-2 border-emerald-500/50 rounded-2xl shadow-[0_0_50px_rgba(16,185,129,0.25)] flex flex-col h-[520px] overflow-hidden font-mono text-emerald-400">
        {/* Terminal Header */}
        <div className="flex items-center justify-between px-4 py-3 bg-zinc-950 border-b border-emerald-500/30 text-xs">
          <div className="flex items-center gap-2">
            <TerminalIcon className="w-4 h-4 text-emerald-400" />
            <span className="font-bold tracking-wider text-emerald-300">
              NOVELIX ROOT TERMINAL // v1.0.0
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-zinc-400 hover:text-emerald-300 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Console Output Area */}
        <div className="flex-1 p-4 overflow-y-auto space-y-1 text-xs select-text scrollbar-thin scrollbar-thumb-emerald-950">
          {history.map((line, idx) => (
            <div key={idx} className="whitespace-pre-wrap leading-relaxed">
              {line}
            </div>
          ))}

          {/* Admin Login Dialog inside terminal */}
          {showAdminLogin && (
            <div className="mt-4 p-4 border border-emerald-500/40 rounded-xl bg-emerald-950/20 max-w-md space-y-3">
              <div className="flex items-center gap-2 text-emerald-300 font-bold">
                <ShieldAlert className="w-4 h-4" />
                <span>ADMINISTRATOR IDENTITY CHALLENGE</span>
              </div>
              <form onSubmit={handleAdminAuth} className="space-y-2.5">
                <div>
                  <label className="block text-[10px] uppercase text-zinc-400">Admin Email</label>
                  <input
                    type="email"
                    value={adminEmail}
                    onChange={(e) => setAdminEmail(e.target.value)}
                    required
                    placeholder="admin@novelix.io"
                    className="w-full bg-black border border-emerald-500/50 rounded px-2.5 py-1.5 text-xs text-emerald-300 focus:outline-none focus:border-emerald-400"
                  />
                </div>
                <div>
                  <label className="block text-[10px] uppercase text-zinc-400">Passphrase</label>
                  <input
                    type="password"
                    value={adminPassword}
                    onChange={(e) => setAdminPassword(e.target.value)}
                    required
                    placeholder="••••••••••••"
                    className="w-full bg-black border border-emerald-500/50 rounded px-2.5 py-1.5 text-xs text-emerald-300 focus:outline-none focus:border-emerald-400"
                  />
                </div>
                <button
                  type="submit"
                  disabled={isVerifying}
                  className="w-full py-2 rounded bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-xs tracking-wider uppercase transition-colors disabled:opacity-50"
                >
                  {isVerifying ? 'Authenticating...' : 'Authenticate & Enter'}
                </button>
              </form>
              {authStatus && (
                <p className="text-[11px] text-amber-300 mt-2 font-bold">{authStatus}</p>
              )}
            </div>
          )}

          <div ref={terminalEndRef} />
        </div>

        {/* Input Prompt */}
        {!showAdminLogin && (
          <div className="px-4 py-2.5 bg-black border-t border-emerald-500/30 flex items-center gap-2 text-xs">
            <span className="text-emerald-500 font-bold">root@novelix:~$</span>
            <input
              ref={inputRef}
              type="text"
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              onKeyDown={onKeyDown}
              className="flex-1 bg-transparent text-emerald-300 focus:outline-none caret-emerald-400"
              placeholder=""
              autoFocus
            />
          </div>
        )}
      </div>
    </div>
  );
}
