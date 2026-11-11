#!/usr/bin/env python3
"""
Part 2 patch for VIP Admin suite and Push notifications
"""

GEN_FILE = "scripts/generate_4.py"

with open(GEN_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Inject inAppPushBanner and driveConnectModal right after <body>
body_tag = '<body>'

body_insert = """<body>

<!-- ════════════════════════════════════════════════════════
     IN-APP HEADS-UP PUSH NOTIFICATION BANNER
═══════════════════════════════════════════════════════════ -->
<div id="inAppPushBanner" class="fixed top-3 left-3 right-3 z-[99999] pointer-events-auto transform -translate-y-40 transition-all duration-300 ease-out flex items-center gap-3 p-3.5 rounded-2xl bg-[#0F0F18]/95 backdrop-blur-xl border border-[#FFD700]/30 shadow-[0_12px_40px_rgba(0,0,0,0.85),0_0_20px_rgba(255,215,0,0.2)] text-white cursor-pointer" onclick="handleInAppPushBannerClicked()">
  <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-[#FFD700] to-[#E5C07B] flex items-center justify-center flex-shrink-0 shadow-md text-[#0B0B10]">
    <svg viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5"><path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2zm-2 1H8v-6c0-2.48 1.51-4.5 4-4.5s4 2.02 4 4.5v6z"/></svg>
  </div>
  <div class="flex-1 min-w-0">
    <div class="flex items-center justify-between gap-1 mb-0.5">
      <span class="text-[10px] uppercase font-bold tracking-wider text-[#FFD700] flex items-center gap-1.5">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
        NOVELIX PUSH • JUST NOW
      </span>
      <button type="button" onclick="event.stopPropagation(); dismissInAppPushBanner()" class="text-xs text-app-muted hover:text-white px-1">✕</button>
    </div>
    <h5 id="pushBannerTitle" class="text-xs font-bold text-white truncate">New Notification</h5>
    <p id="pushBannerBody" class="text-[11px] text-app-muted truncate">A new release has been announced.</p>
  </div>
</div>

<!-- ════════════════════════════════════════════════════════
     GOOGLE DRIVE SMART CONNECT & FAST PUBLISHING MODAL
═══════════════════════════════════════════════════════════ -->
<div id="driveConnectModal" class="modal-backdrop" onclick="if(event.target===this)closeDriveConnectModal()">
  <div class="modal-sheet max-h-[85vh] flex flex-col p-6">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2.5">
        <div class="w-9 h-9 rounded-xl flex items-center justify-center bg-gradient-to-br from-[#4285F4] to-[#34A853] text-white">
          <svg viewBox="0 0 24 24" class="w-5 h-5 fill-white"><path d="M12.01 1.99c-5.52 0-10 4.48-10 10s4.48 10 10 10 10-4.48 10-10-4.48-10-10-10zm-1.01 16.51l-4.5-4.5 1.41-1.41 3.09 3.09 7.09-7.09 1.41 1.41-8.5 8.5z"/></svg>
        </div>
        <div>
          <h3 class="font-display font-bold text-sm text-white">Google Drive Cloud Connect</h3>
          <p class="text-[10px] text-app-muted">Fast & Free Publishing System</p>
        </div>
      </div>
      <button onclick="closeDriveConnectModal()" class="w-7 h-7 rounded-full surface-card flex items-center justify-center text-app-muted hover:text-white">✕</button>
    </div>

    <!-- Option 1: Fast Direct Publishing -->
    <div class="p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 mb-3 space-y-2">
      <div class="flex items-center gap-1.5 text-xs font-bold text-emerald-400">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
        <span>Fast Direct Publishing Active</span>
      </div>
      <p class="text-[11px] text-emerald-200 leading-relaxed">
        You do <b>not</b> need to authorize or link your personal Google account! In NOVELIX 11.0, you can simply paste any Google Drive link directly into the Publishing Studio.
      </p>
      <button onclick="closeDriveConnectModal(); navigateTo('publish');" class="btn-primary text-xs w-full py-2.5 font-bold flex items-center justify-center gap-2">
        <span>📋 Open Publishing Studio & Paste Link</span>
      </button>
    </div>

    <!-- Option 2: 1-Click Google Auth -->
    <div class="surface-card p-4 space-y-2.5">
      <h4 class="text-xs font-semibold text-white">Link Personal Google Account</h4>
      <p class="text-[11px] text-app-muted leading-relaxed">
        Sign in with Google to link your author identity and remember your account across devices. Powered directly by Google Firebase Auth.
      </p>
      <button onclick="connectGoogleDriveDirect()" class="google-sign-in-btn w-full">
        <svg viewBox="0 0 24 24" class="w-4 h-4 flex-shrink-0">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
        <span>Connect via Google Auth</span>
      </button>
    </div>
  </div>
</div>
"""

if body_tag in content:
    content = content.replace(body_tag, body_insert, 1)
    print("Injected inAppPushBanner and driveConnectModal successfully")
else:
    print("WARNING: <body> tag not found")

# 2. Replace lines 1775-1797 with VIP Obsidian & Gold Header and Tab Navigation
old_modal_header = """<div id="adminDashboardModal" class="modal-fullscreen flex-col bg-[#07070A] text-[#F5F3FA]" style="display: none !important; visibility: hidden !important;">
  <div class="safe-top bg-app-sub border-b border-app-border px-4 py-3 flex items-center justify-between flex-shrink-0">
    <div class="flex items-center gap-2">
      <span class="w-6 h-6 rounded bg-red-500/20 text-red-400 flex items-center justify-center text-xs font-bold">★</span>
      <div>
        <h3 class="font-display font-bold text-sm text-white">NOVELIX 6.0 Admin Console</h3>
        <p class="text-[10px] text-app-muted">Protected Server-Side Management Subsystem</p>
      </div>
    </div>
    <button onclick="closeAdminDashboard()" class="btn-secondary text-xs px-3 py-1.5">Close Console</button>
  </div>

  <!-- 8 Core Management Tabs -->
  <div class="px-4 py-2 bg-app-surface border-b border-app-border flex gap-1.5 overflow-x-auto flex-shrink-0 scrollbar-none">
    <button onclick="switchAdminTab('users')" class="admin-tab-btn pill-tag" data-tab="users" style="background:#9270FF; color:#0B0B10">Users</button>
    <button onclick="switchAdminTab('books')" class="admin-tab-btn pill-tag" data-tab="books">Books</button>
    <button onclick="switchAdminTab('publications')" class="admin-tab-btn pill-tag" data-tab="publications">Publications</button>
    <button onclick="switchAdminTab('reports')" class="admin-tab-btn pill-tag" data-tab="reports">Reports / Analytics</button>
    <button onclick="switchAdminTab('comments')" class="admin-tab-btn pill-tag" data-tab="comments">Comments / Reviews</button>
    <button onclick="switchAdminTab('ads')" class="admin-tab-btn pill-tag" data-tab="ads">Ads & Sponsorship</button>
    <button onclick="switchAdminTab('storage')" class="admin-tab-btn pill-tag" data-tab="storage">Storage Quotas</button>
    <button onclick="switchAdminTab('config')" class="admin-tab-btn pill-tag" data-tab="config">System Config</button>
  </div>"""

new_modal_header = """<div id="adminDashboardModal" class="modal-fullscreen flex-col bg-[#08080E] text-[#F5F3FA]" style="display: none !important; visibility: hidden !important;">
  <!-- VIP Obsidian & Gold Header -->
  <div class="p-4 border-b border-[#FFD700]/30 bg-gradient-to-r from-[#14141E] via-[#0E0E18] to-[#14141E] flex items-center justify-between shadow-lg flex-shrink-0">
    <div class="flex items-center gap-2.5">
      <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-[#FFD700] to-[#E5C07B] flex items-center justify-center text-[#0B0B10] font-black text-sm shadow-[0_0_15px_rgba(255,215,0,0.4)]">
        👑
      </div>
      <div>
        <div class="flex items-center gap-2">
          <h3 class="font-display font-extrabold text-sm text-white tracking-wide">NOVELIX VIP EXECUTIVE SUITE</h3>
          <span class="px-2 py-0.5 rounded-full text-[9px] font-bold bg-[#FFD700]/20 text-[#FFD700] border border-[#FFD700]/35 shadow-sm">● VIP ACTIVE</span>
        </div>
        <p class="text-[10px] text-app-muted">Master Administration Console • Unrestricted Access • Spark Free Tier Active</p>
      </div>
    </div>
    <div class="flex items-center gap-2">
      <button onclick="switchAdminTab('notifications')" class="btn-primary text-xs px-3 py-1.5 font-bold bg-gradient-to-r from-[#FFD700] to-[#E5C07B] text-[#0B0B10] flex items-center gap-1.5 shadow">
        <svg viewBox="0 0 24 24" fill="currentColor" class="w-3.5 h-3.5"><path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2zm-2 1H8v-6c0-2.48 1.51-4.5 4-4.5s4 2.02 4 4.5v6z"/></svg>
        <span>Broadcast</span>
      </button>
      <button onclick="closeAdminDashboard()" class="btn-secondary text-xs px-3 py-1.5">Close Console</button>
    </div>
  </div>

  <!-- VIP Tab Navigation -->
  <div class="p-3 bg-[#0B0B12] border-b border-[#232334] flex gap-1.5 overflow-x-auto scrollbar-none flex-shrink-0">
    <button onclick="switchAdminTab('reports')" class="admin-tab-btn pill-tag" data-tab="reports" style="background:#FFD700; color:#0B0B10; font-weight:700">📊 Overview</button>
    <button onclick="switchAdminTab('notifications')" class="admin-tab-btn pill-tag text-[#FFD700] border border-[#FFD700]/30" data-tab="notifications">🚀 Push Broadcast</button>
    <button onclick="switchAdminTab('books')" class="admin-tab-btn pill-tag" data-tab="books">📚 Books</button>
    <button onclick="switchAdminTab('users')" class="admin-tab-btn pill-tag" data-tab="users">👥 Users</button>
    <button onclick="switchAdminTab('publications')" class="admin-tab-btn pill-tag" data-tab="publications">✍️ Creators</button>
    <button onclick="switchAdminTab('comments')" class="admin-tab-btn pill-tag" data-tab="comments">💬 Reviews</button>
    <button onclick="switchAdminTab('ads')" class="admin-tab-btn pill-tag" data-tab="ads">📢 Sponsors</button>
    <button onclick="switchAdminTab('storage')" class="admin-tab-btn pill-tag" data-tab="storage">⚙️ Storage</button>
    <button onclick="switchAdminTab('config')" class="admin-tab-btn pill-tag" data-tab="config">🔒 Audit</button>
  </div>"""

if old_modal_header in content:
    content = content.replace(old_modal_header, new_modal_header, 1)
    print("Replaced adminDashboardModal header with VIP Executive Suite header successfully")
else:
    print("WARNING: old_modal_header not found")

with open(GEN_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Updated {GEN_FILE} successfully (Length: {len(content)})")
