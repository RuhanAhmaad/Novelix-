'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { DeveloperTerminal } from '@/components/DeveloperTerminal';
import { ArrowLeft, Terminal, ShieldAlert } from 'lucide-react';

export default function DeveloperSettingsPage() {
  const [terminalOpen, setTerminalOpen] = useState(true);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <Link
          href="/settings"
          className="flex items-center gap-2 text-xs font-semibold text-zinc-400 hover:text-white"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Settings</span>
        </Link>
        <span className="text-xs font-mono text-emerald-400 flex items-center gap-1.5">
          <Terminal className="w-4 h-4" />
          Developer Diagnostic Console
        </span>
      </div>

      <div className="p-8 rounded-3xl bg-black border-2 border-emerald-500/40 text-center space-y-4 shadow-[0_0_40px_rgba(16,185,129,0.15)]">
        <Terminal className="w-12 h-12 text-emerald-400 mx-auto" />
        <h1 className="text-xl font-bold font-mono text-emerald-300">NOVELIX CORE CONSOLE</h1>
        <p className="text-xs font-mono text-zinc-400 max-w-md mx-auto leading-relaxed">
          Interactive debugging shell, telemetry diagnostics, and secure administrative authentication portal.
        </p>

        <button
          onClick={() => setTerminalOpen(true)}
          className="px-6 py-2.5 rounded-xl text-xs font-mono font-bold bg-emerald-500 hover:bg-emerald-400 text-black uppercase tracking-wider transition-colors"
        >
          Open Shell Window
        </button>
      </div>

      <DeveloperTerminal
        isOpen={terminalOpen}
        onClose={() => setTerminalOpen(false)}
      />
    </div>
  );
}
