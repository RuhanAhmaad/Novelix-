'use client';

import React, { useState, useEffect } from 'react';
import { DeveloperTerminal } from '@/components/DeveloperTerminal';
import { createClient } from '@/utils/supabase/client';
import { 
  Settings as SettingsIcon, 
  Terminal, 
  User, 
  HardDrive, 
  ShieldCheck, 
  Globe, 
  Save, 
  CheckCircle2, 
  Trash2, 
  Plus 
} from 'lucide-react';

export default function SettingsPage() {
  const [clickCount, setClickCount] = useState(0);
  const [isTerminalOpen, setIsTerminalOpen] = useState(false);
  const [displayName, setDisplayName] = useState('Aria Sterling');
  const [username, setUsername] = useState('aria_sterling');
  const [bio, setBio] = useState('Author of dark fantasy and supernatural adventures.');
  const [readingPrivacy, setReadingPrivacy] = useState<'public' | 'followers' | 'private'>('public');
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Google Drive Accounts state
  const [driveAccounts, setDriveAccounts] = useState<any[]>([
    {
      id: 'acc-1',
      account_name: 'Personal Google Drive',
      email: 'creator.personal@gmail.com',
      is_primary: true,
    },
    {
      id: 'acc-2',
      account_name: 'Publishing Cloud Drive',
      email: 'novelix.press@gmail.com',
      is_primary: false,
    },
  ]);

  // Handle 5-click easter egg trigger for Developer Terminal
  const handleVersionClick = () => {
    const next = clickCount + 1;
    setClickCount(next);

    if (next >= 5) {
      setIsTerminalOpen(true);
      setClickCount(0);
    }
  };

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2000);
  };

  const handleConnectDrive = () => {
    const name = prompt('Enter a label for this Google Drive account:', 'Backup Drive');
    if (name) {
      window.location.href = `/api/drive/auth?accountName=${encodeURIComponent(name)}`;
    }
  };

  const setPrimaryDrive = (id: string) => {
    setDriveAccounts(
      driveAccounts.map((a) => ({
        ...a,
        is_primary: a.id === id,
      }))
    );
  };

  const disconnectDrive = (id: string) => {
    setDriveAccounts(driveAccounts.filter((a) => a.id !== id));
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-3">
          <SettingsIcon className="w-7 h-7 text-novelix-neon" />
          Settings & Account
        </h1>
        <p className="text-xs sm:text-sm text-zinc-400 mt-1">
          Manage your author profile, connected Google Drive accounts, and reading preferences.
        </p>
      </div>

      {saveSuccess && (
        <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-2 text-xs font-semibold text-emerald-300">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>Profile preferences saved successfully!</span>
        </div>
      )}

      {/* Profile Form */}
      <form onSubmit={handleSaveProfile} className="p-6 rounded-3xl bg-novelix-900/60 border border-novelix-800 space-y-5">
        <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2 border-b border-novelix-800 pb-2">
          <User className="w-4 h-4 text-novelix-neon" />
          Author Profile Information
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-zinc-300 mb-1">Display Name</label>
            <input
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className="w-full bg-novelix-950 text-xs text-white px-3 py-2 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-zinc-300 mb-1">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-novelix-950 text-xs text-white px-3 py-2 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-bold text-zinc-300 mb-1">Author Bio</label>
          <textarea
            rows={3}
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            className="w-full bg-novelix-950 text-xs text-white p-3 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon resize-none"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-zinc-300 mb-1">Reading Activity Privacy</label>
          <select
            value={readingPrivacy}
            onChange={(e) => setReadingPrivacy(e.target.value as any)}
            className="w-full sm:w-60 bg-novelix-950 text-xs text-white px-3 py-2 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
          >
            <option value="public">Public (Everyone can see reads)</option>
            <option value="followers">Followers Only</option>
            <option value="private">Private</option>
          </select>
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            className="flex items-center gap-1.5 px-5 py-2 rounded-xl text-xs font-bold bg-novelix-electric hover:bg-novelix-violet text-white transition-colors shadow-glow-sm"
          >
            <Save className="w-3.5 h-3.5" />
            <span>Save Profile</span>
          </button>
        </div>
      </form>

      {/* Google Drive Multi-Account Management */}
      <div className="p-6 rounded-3xl bg-novelix-900/60 border border-novelix-800 space-y-4">
        <div className="flex items-center justify-between border-b border-novelix-800 pb-2">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <HardDrive className="w-4 h-4 text-novelix-neon" />
            Connected Google Drive Accounts
          </h2>
          <button
            onClick={handleConnectDrive}
            className="flex items-center gap-1 text-xs font-semibold text-novelix-neon hover:underline"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Connect Another Account</span>
          </button>
        </div>

        <p className="text-xs text-zinc-400">
          Store PDF books across multiple Google Drives. OAuth refresh tokens are encrypted on the server with AES-256.
        </p>

        <div className="space-y-2.5">
          {driveAccounts.map((account) => (
            <div
              key={account.id}
              className="p-3.5 rounded-2xl bg-novelix-950 border border-novelix-800 flex items-center justify-between"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-white">{account.account_name}</span>
                  {account.is_primary && (
                    <span className="text-[9px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-1.5 py-0.2 rounded font-mono">
                      Primary Storage
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-zinc-500 font-mono mt-0.5">{account.email}</p>
              </div>

              <div className="flex items-center gap-2">
                {!account.is_primary && (
                  <button
                    onClick={() => setPrimaryDrive(account.id)}
                    className="text-xs text-zinc-400 hover:text-white px-2 py-1 rounded bg-novelix-900"
                  >
                    Set Primary
                  </button>
                )}
                <button
                  onClick={() => disconnectDrive(account.id)}
                  className="p-1.5 text-zinc-500 hover:text-red-400"
                  title="Disconnect"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Developer Mode & App Version Trigger */}
      <div className="p-6 rounded-3xl bg-novelix-900/40 border border-novelix-800 text-center space-y-3">
        <div className="flex items-center justify-center gap-2 text-zinc-400 text-xs">
          <Terminal className="w-4 h-4 text-emerald-400" />
          <span>System Information</span>
        </div>

        {/* 5-click easter egg trigger */}
        <div
          onClick={handleVersionClick}
          className="cursor-pointer select-none inline-block p-3 rounded-2xl bg-novelix-950 hover:bg-novelix-900 border border-novelix-800 transition-all group"
          title="Click 5 times for Developer Terminal"
        >
          <p className="text-xs font-mono text-emerald-400 group-hover:text-emerald-300">
            NOVELIX Enterprise v1.0.0-PROD
          </p>
          <p className="text-[10px] text-zinc-500 font-mono mt-0.5">
            Build 2026.11 // Click {5 - clickCount} more times to launch terminal
          </p>
        </div>

        <div className="pt-2">
          <button
            onClick={() => setIsTerminalOpen(true)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 hover:bg-emerald-500/20 transition-colors"
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>Launch Developer Terminal</span>
          </button>
        </div>
      </div>

      {/* Secret Developer Terminal Modal */}
      <DeveloperTerminal
        isOpen={isTerminalOpen}
        onClose={() => setIsTerminalOpen(false)}
      />
    </div>
  );
}
