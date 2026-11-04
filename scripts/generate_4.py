import os

HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="theme-color" content="#0B0B10">
  <title>NOVELIX 4.0 — Digital Publishing Platform</title>

  <!-- Typography: Inter, Manrope, Playfair Display -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap" rel="stylesheet">

  <!-- Firebase Web SDK (v10 compat) -->
  <script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-app-compat.js"></script>
  <script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-auth-compat.js"></script>
  <script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-firestore-compat.js"></script>
  <script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-storage-compat.js"></script>
  <script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-messaging-compat.js"></script>

  <!-- PDF.js Reader -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>

  <!-- Google API Client for Google Drive Integration -->
  <script src="https://accounts.google.com/gsi/client" async defer></script>

  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>

  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            app: {
              bg: '#0B0B10',
              sub: '#14141D',
              surface: '#1B1B27',
              border: '#262638',
              primary: '#9270FF',
              secondary: '#B9A4FF',
              text: '#F5F3FA',
              muted: '#9693A4',
              disabled: '#5E5B6E'
            }
          },
          fontFamily: {
            sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
            display: ['Manrope', 'sans-serif'],
            serif: ['Playfair Display', 'Georgia', 'serif']
          }
        }
      }
    };
  </script>

  <style>
    :root {
      --sat: env(safe-area-inset-top, 0px);
      --sab: env(safe-area-inset-bottom, 0px);
      --sal: env(safe-area-inset-left, 0px);
      --sar: env(safe-area-inset-right, 0px);
    }
    * {
      -webkit-tap-highlight-color: transparent;
      user-select: none;
      box-sizing: border-box;
    }
    input, textarea, select {
      user-select: text;
    }
    body {
      background-color: #0B0B10;
      color: #F5F3FA;
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      min-height: 100vh;
      overflow-x: hidden;
      padding-top: calc(58px + var(--sat));
      padding-bottom: calc(68px + var(--sab));
    }
    .safe-top { padding-top: var(--sat); }
    .safe-bottom { padding-bottom: var(--sab); }

    /* Luxury Editorial Card Surfaces */
    .surface-card {
      background: #14141D;
      border: 1px solid #262638;
      border-radius: 14px;
      transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .surface-card:active {
      transform: scale(0.985);
      border-color: rgba(146, 112, 255, 0.4);
    }
    .surface-card-static {
      background: #14141D;
      border: 1px solid #262638;
      border-radius: 14px;
    }
    .surface-elevated {
      background: #1B1B27;
      border: 1px solid rgba(146, 112, 255, 0.18);
      border-radius: 14px;
    }

    /* Buttons */
    .btn-primary {
      background: #9270FF;
      color: #0B0B10;
      font-weight: 600;
      border-radius: 10px;
      transition: all 0.2s ease;
      box-shadow: 0 4px 14px rgba(146, 112, 255, 0.25);
    }
    .btn-primary:active {
      transform: scale(0.97);
      background: #B9A4FF;
    }
    .btn-secondary {
      background: #1B1B27;
      color: #F5F3FA;
      border: 1px solid #262638;
      font-weight: 500;
      border-radius: 10px;
      transition: all 0.2s ease;
    }
    .btn-secondary:active {
      background: #262638;
      border-color: #9270FF;
    }
    .btn-ghost {
      background: transparent;
      color: #9693A4;
      transition: color 0.2s ease;
    }
    .btn-ghost:hover, .btn-ghost:active {
      color: #F5F3FA;
    }

    /* Input & Select */
    input[type="text"], input[type="email"], input[type="password"], textarea, select {
      background: #14141D;
      border: 1px solid #262638;
      color: #F5F3FA;
      border-radius: 10px;
      transition: border-color 0.2s ease;
    }
    input:focus, textarea:focus, select:focus {
      outline: none;
      border-color: #9270FF;
      box-shadow: 0 0 0 2px rgba(146, 112, 255, 0.15);
    }

    /* Pill Tags */
    .pill-tag {
      background: rgba(146, 112, 255, 0.08);
      border: 1px solid rgba(146, 112, 255, 0.2);
      color: #B9A4FF;
      font-size: 11px;
      font-weight: 500;
      padding: 3px 9px;
      border-radius: 20px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }

    /* Navigation Bar */
    .glass-nav {
      background: rgba(11, 11, 16, 0.94);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border-top: 1px solid #262638;
    }
    .glass-header {
      background: rgba(11, 11, 16, 0.94);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border-bottom: 1px solid #262638;
    }

    /* Splash Screen */
    #splashScreen {
      position: fixed;
      inset: 0;
      background-color: #0B0B10;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      transition: opacity 0.45s cubic-bezier(0.16, 1, 0.3, 1), transform 0.45s cubic-bezier(0.16, 1, 0.3, 1);
    }
    #splashScreen.hide {
      opacity: 0;
      transform: scale(1.04);
      pointer-events: none;
    }
    .pulse-glow {
      animation: pulseGlow 2.4s ease-in-out infinite;
    }
    @keyframes pulseGlow {
      0%, 100% { transform: scale(1); opacity: 0.85; filter: drop-shadow(0 0 15px rgba(146, 112, 255, 0.3)); }
      50% { transform: scale(1.03); opacity: 1; filter: drop-shadow(0 0 25px rgba(146, 112, 255, 0.6)); }
    }

    /* Skeleton Wave */
    .skeleton-box {
      background: linear-gradient(90deg, #14141D 25%, #1B1B27 50%, #14141D 75%);
      background-size: 200% 100%;
      animation: skeletonWave 1.6s ease-in-out infinite;
      border-radius: 12px;
    }
    @keyframes skeletonWave {
      0% { background-position: 200% 0; }
      100% { background-position: -200% 0; }
    }

    /* Pages Container */
    .app-page { display: none; }
    .app-page.active { display: block; }

    /* Modals Backdrop */
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.82);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      z-index: 100;
      display: flex;
      align-items: flex-end;
      justify-content: center;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.25s ease;
    }
    .modal-backdrop.open {
      opacity: 1;
      pointer-events: auto;
    }
    .modal-sheet {
      background: #14141D;
      border: 1px solid #262638;
      border-radius: 20px 20px 0 0;
      width: 100%;
      max-width: 640px;
      max-height: 90vh;
      display: flex;
      flex-direction: column;
      transform: translateY(100%);
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .modal-backdrop.open .modal-sheet {
      transform: translateY(0);
    }

    /* Fullscreen Modal */
    .modal-fullscreen {
      position: fixed;
      inset: 0;
      background: #0B0B10;
      z-index: 110;
      display: none;
      flex-direction: column;
    }
    .modal-fullscreen.open { display: flex; }

    /* Toast Notification */
    #toastBar {
      position: fixed;
      bottom: calc(76px + var(--sab));
      left: 50%;
      transform: translateX(-50%) translateY(30px);
      background: #1B1B27;
      border: 1px solid #9270FF;
      color: #F5F3FA;
      padding: 10px 18px;
      border-radius: 24px;
      font-size: 12px;
      font-weight: 500;
      z-index: 150;
      opacity: 0;
      pointer-events: none;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: 0 8px 24px rgba(0,0,0,0.5);
    }
    #toastBar.show {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }

    /* Developer Terminal */
    #devTerminal {
      position: fixed;
      inset: 0;
      background: #08080C;
      z-index: 300;
      display: none;
      flex-direction: column;
      font-family: monospace;
      color: #10B981;
    }
    #devTerminal.open { display: flex; }

    /* Custom Scrollbars */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #262638; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #9270FF; }
  </style>
</head>
<body>

<!-- ════════════════════════════════════════════════════════
     1. CUSTOM ANIMATED SPLASH SCREEN
═══════════════════════════════════════════════════════════ -->
<div id="splashScreen">
  <div class="relative flex flex-col items-center">
    <div class="absolute -inset-10 bg-app-primary/10 rounded-full blur-3xl pointer-events-none"></div>
    <div class="pulse-glow relative flex items-center justify-center w-24 h-24 mb-4">
      <svg viewBox="0 0 80 80" class="w-full h-full" fill="none">
        <rect width="80" height="80" rx="20" fill="#14141D" stroke="#262638" stroke-width="2"/>
        <path d="M22 60V20L58 60V20" stroke="#9270FF" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="58" cy="22" r="3.5" fill="#B9A4FF"/>
      </svg>
    </div>
    <h1 class="font-display font-bold text-2xl tracking-widest text-white">NOVELIX</h1>
    <p class="text-[11px] font-medium tracking-wider text-app-muted mt-1 uppercase">Editorial Publishing</p>
    <div class="w-16 h-0.5 bg-app-border rounded-full mt-6 overflow-hidden">
      <div class="w-full h-full bg-app-primary -translate-x-full animate-[progressPulse_1.2s_ease-in-out_infinite]"></div>
    </div>
  </div>
</div>

<!-- ════════════════════════════════════════════════════════
     2. EDITORIAL GLASS HEADER
═══════════════════════════════════════════════════════════ -->
<header class="glass-header fixed top-0 left-0 right-0 z-40 safe-top px-4 flex items-center justify-between" style="height: calc(58px + var(--sat))">
  <!-- Brand Wordmark & 5-Click Terminal Trigger -->
  <div id="headerLogoArea" class="flex items-center gap-2.5 cursor-pointer">
    <div class="w-7 h-7 rounded-lg bg-app-surface border border-app-border flex items-center justify-center text-app-primary font-display font-extrabold text-sm">
      N
    </div>
    <span class="font-display font-bold text-base tracking-wider text-white">NOVELIX</span>
    <span id="headerLivePill" class="hidden text-[9px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">LIVE</span>
  </div>

  <!-- Actions: Search, Notifications, Settings, Profile -->
  <div class="flex items-center gap-2">
    <!-- Notifications Button -->
    <button onclick="openNotifModal()" id="headerNotifBtn" class="relative w-8 h-8 rounded-full surface-card flex items-center justify-center text-app-muted hover:text-white" aria-label="Notifications">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="w-4 h-4">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
        <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
      </svg>
      <span id="notifBadgeDot" class="hidden absolute top-1 right-1 w-2 h-2 rounded-full bg-app-primary"></span>
    </button>

    <!-- Settings Button -->
    <button onclick="openSettingsModal()" id="headerSettingsBtn" class="w-8 h-8 rounded-full surface-card flex items-center justify-center text-app-muted hover:text-white" aria-label="Settings">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="w-4 h-4">
        <circle cx="12" cy="12" r="3"/>
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
      </svg>
    </button>

    <!-- User Profile Avatar / Sign In Button -->
    <div id="headerAuthArea">
      <button onclick="openAuthModal()" id="headerAuthBtn" class="btn-primary text-xs px-3 py-1.5">Sign In</button>
      <button onclick="switchPage('profile')" id="headerUserAvatar" class="hidden w-8 h-8 rounded-full overflow-hidden border border-app-border bg-app-surface flex items-center justify-center">
        <img id="headerAvatarImg" src="" class="w-full h-full object-cover hidden" alt="Avatar">
        <span id="headerAvatarFallback" class="font-display font-bold text-xs text-app-primary">U</span>
      </button>
    </div>
  </div>
</header>

<!-- ════════════════════════════════════════════════════════
     3. TOAST MESSAGES
═══════════════════════════════════════════════════════════ -->
<div id="toastBar"><span id="toastText">Action completed</span></div>

<!-- ════════════════════════════════════════════════════════
     4. MAIN VIEWS
═══════════════════════════════════════════════════════════ -->
<main id="appMainContainer">

  <!-- ── 4A. HOME PAGE ── -->
  <section id="page-home" class="app-page active">
    <!-- Featured Hero Shelf -->
    <div id="featuredShelf" class="px-4 pt-4 pb-2">
      <div class="flex items-center justify-between mb-3">
        <h2 class="font-display font-bold text-sm tracking-wide text-white uppercase">Featured Releases</h2>
        <span class="text-[11px] text-app-muted">Curated</span>
      </div>
      <div id="featuredCarousel" class="flex gap-3 overflow-x-auto pb-2 scroll-smooth">
        <!-- Rendered dynamically -->
      </div>
    </div>

    <!-- Continue Reading Shelf -->
    <div id="continueReadingShelf" class="hidden px-4 py-3">
      <div class="flex items-center justify-between mb-2.5">
        <h3 class="font-display font-semibold text-xs text-white">Continue Reading</h3>
        <button onclick="switchPage('library')" class="text-[11px] text-app-primary">View All</button>
      </div>
      <div id="continueReadingList" class="space-y-2">
        <!-- Rendered dynamically -->
      </div>
    </div>

    <!-- Category Pills -->
    <div class="px-4 py-3 overflow-x-auto flex gap-2">
      <button onclick="filterCategory('all')" class="cat-pill pill-tag" data-cat="all" style="background:#9270FF; color:#0B0B10">All Works</button>
      <button onclick="filterCategory('book')" class="cat-pill pill-tag" data-cat="book">Books</button>
      <button onclick="filterCategory('novel')" class="cat-pill pill-tag" data-cat="novel">Novels</button>
      <button onclick="filterCategory('manhwa')" class="cat-pill pill-tag" data-cat="manhwa">Manhwa</button>
      <button onclick="filterCategory('manga')" class="cat-pill pill-tag" data-cat="manga">Manga</button>
      <button onclick="filterCategory('comic')" class="cat-pill pill-tag" data-cat="comic">Comics</button>
    </div>

    <!-- Search Bar -->
    <div class="px-4 py-2">
      <div class="relative">
        <input type="text" id="homeSearchInput" placeholder="Search titles, authors, or genres..." class="w-full pl-9 pr-4 py-2.5 text-xs rounded-xl" oninput="handleHomeSearch(this.value)">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4 text-app-muted absolute left-3 top-3">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
      </div>
    </div>

    <!-- Catalog Grid -->
    <div class="px-4 py-3">
      <div class="flex items-center justify-between mb-3">
        <h3 class="font-display font-semibold text-xs text-white">Trending Publications</h3>
        <span id="shelfGridCount" class="text-[11px] text-app-muted">0 works</span>
      </div>
      <div id="homeBooksGrid" class="grid grid-cols-2 gap-3.5">
        <!-- Rendered dynamically -->
      </div>
      <div id="homeEmptyState" class="hidden text-center py-12">
        <p class="text-xs text-app-muted">No publications match your filter.</p>
      </div>
    </div>
  </section>

  <!-- ── 4B. EXPLORE PAGE ── -->
  <section id="page-explore" class="app-page">
    <div class="px-4 pt-4 pb-2">
      <h2 class="font-display font-bold text-lg text-white mb-1">Explore Library</h2>
      <p class="text-xs text-app-muted mb-4">Discover works across multiple genres and creative mediums.</p>
      <div id="exploreGenresGrid" class="grid grid-cols-2 gap-2 mb-4">
        <!-- Genres -->
      </div>
      <div id="exploreResultsGrid" class="grid grid-cols-2 gap-3.5">
        <!-- Rendered dynamically -->
      </div>
    </div>
  </section>

  <!-- ── 4C. LIBRARY PAGE ── -->
  <section id="page-library" class="app-page">
    <div class="px-4 pt-4 pb-2">
      <h2 class="font-display font-bold text-lg text-white mb-1">Your Library</h2>
      <p class="text-xs text-app-muted mb-4">Synchronized bookmarks, downloads, and reading progress.</p>
      
      <div id="libraryAuthGuard" class="hidden surface-card-static p-6 text-center">
        <p class="text-xs text-app-muted mb-3">Sign in to sync your bookmarks across devices.</p>
        <button onclick="openAuthModal()" class="btn-primary text-xs px-4 py-2">Sign In</button>
      </div>

      <div id="libraryContent" class="hidden">
        <div class="flex gap-2 mb-4">
          <button onclick="switchLibTab('reading')" class="lib-subtab pill-tag" data-tab="reading" style="background:#9270FF; color:#0B0B10">Continue Reading</button>
          <button onclick="switchLibTab('bookmarks')" class="lib-subtab pill-tag" data-tab="bookmarks">Bookmarks</button>
        </div>
        <div id="libraryList" class="space-y-2.5"></div>
        <div id="libraryEmpty" class="hidden text-center py-10 text-xs text-app-muted">No saved titles in this section yet.</div>
      </div>
    </div>
  </section>

  <!-- ── 4D. PUBLISHING STUDIO ── -->
  <section id="page-publish" class="app-page">
    <div class="px-4 pt-4 pb-4">
      <div class="flex items-center justify-between mb-1">
        <h2 class="font-display font-bold text-lg text-white">Publishing Studio</h2>
        <span class="pill-tag text-[10px]">Cloud Creator</span>
      </div>
      <p class="text-xs text-app-muted mb-4">Deploy digital publications with multiple language editions and PDF assets.</p>

      <!-- Auth Guard for Studio -->
      <div id="publishAuthGuard" class="hidden surface-card-static p-6 text-center my-4">
        <p class="text-xs text-app-muted mb-3">Sign in with an author account to publish and manage works.</p>
        <button onclick="openAuthModal()" class="btn-primary text-xs px-4 py-2">Sign In</button>
      </div>

      <!-- Real Publishing Form & Storage Meter -->
      <div id="publishFormContainer" class="hidden">
        
        <!-- REAL-TIME STORAGE METER CARD -->
        <div class="surface-elevated p-4 mb-4">
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-xs font-semibold text-white flex items-center gap-1.5">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5 text-app-primary"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
              Publishing Storage
            </span>
            <span id="storageMeterRatio" class="text-xs text-app-muted">0 MB / 500 MB</span>
          </div>
          <div class="w-full h-2 rounded-full bg-app-sub overflow-hidden mb-2">
            <div id="storageProgressBar" class="h-full bg-app-primary transition-all duration-300" style="width: 0%"></div>
          </div>
          <div class="flex items-center justify-between text-[11px] text-app-muted">
            <span id="storageRemainingText">Remaining: 500.0 MB</span>
            <span id="storageDraftEstimate" class="text-app-secondary">Draft: 0.0 MB</span>
          </div>
          <div id="storageQuotaAlert" class="hidden mt-2 p-2 rounded-lg bg-red-500/10 border border-red-500/30 text-[11px] text-red-300">
            Insufficient publishing storage. Please free up space or contact support to increase your quota.
          </div>
        </div>

        <form id="publishingForm" class="space-y-4" onsubmit="handlePublishSubmit(event)">
          <!-- Content Format Selector -->
          <div>
            <label class="block text-xs font-semibold text-app-muted uppercase tracking-wider mb-2">Format</label>
            <div class="grid grid-cols-4 gap-2" id="formatSelectorGrid">
              <button type="button" onclick="selectContentFormat('book')" class="format-btn surface-card p-2 text-center text-xs font-medium" data-fmt="book" style="border-color:#9270FF; background:#1B1B27">Book</button>
              <button type="button" onclick="selectContentFormat('novel')" class="format-btn surface-card p-2 text-center text-xs font-medium" data-fmt="novel">Novel</button>
              <button type="button" onclick="selectContentFormat('manhwa')" class="format-btn surface-card p-2 text-center text-xs font-medium" data-fmt="manhwa">Manhwa</button>
              <button type="button" onclick="selectContentFormat('manga')" class="format-btn surface-card p-2 text-center text-xs font-medium" data-fmt="manga">Manga</button>
              <button type="button" onclick="selectContentFormat('comic')" class="format-btn surface-card p-2 text-center text-xs font-medium" data-fmt="comic">Comic</button>
              <button type="button" onclick="selectContentFormat('short_story')" class="format-btn surface-card p-2 text-center text-xs font-medium" data-fmt="short_story">Fiction</button>
              <button type="button" onclick="selectContentFormat('series')" class="format-btn surface-card p-2 text-center text-xs font-medium" data-fmt="series">Series</button>
              <button type="button" onclick="selectContentFormat('educational')" class="format-btn surface-card p-2 text-center text-xs font-medium" data-fmt="educational">Edu</button>
            </div>
            <input type="hidden" id="selectedFormatInput" value="book">
          </div>

          <!-- Cover Artwork Upload -->
          <div>
            <label class="block text-xs font-semibold text-app-muted uppercase tracking-wider mb-2">Cover Artwork</label>
            <div onclick="document.getElementById('coverFileInput').click()" class="surface-card p-4 text-center cursor-pointer border-dashed flex flex-col items-center justify-center min-h-[130px]">
              <div id="coverUploadPreview" class="hidden w-20 h-28 rounded-lg overflow-hidden mb-2 shadow"><img id="coverUploadImg" class="w-full h-full object-cover" alt="Cover Preview"></div>
              <div id="coverUploadPlaceholder">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5 mx-auto mb-1 text-app-primary"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                <p class="text-xs text-white">Select Cover Artwork</p>
                <p class="text-[10px] text-app-muted">JPG, PNG, WebP</p>
              </div>
            </div>
            <input type="file" id="coverFileInput" accept="image/*" class="hidden" onchange="handleCoverFileSelected(this)">
          </div>

          <!-- Title & Synopsis -->
          <div>
            <label class="block text-xs font-semibold text-app-muted uppercase tracking-wider mb-1">Publication Title</label>
            <input type="text" id="publishTitleInput" required placeholder="Enter publication title..." class="w-full px-3 py-2 text-xs">
          </div>
          <div>
            <label class="block text-xs font-semibold text-app-muted uppercase tracking-wider mb-1">Synopsis</label>
            <textarea id="publishSynopsisInput" required rows="3" placeholder="Provide a concise synopsis..." class="w-full px-3 py-2 text-xs resize-none"></textarea>
          </div>

          <!-- Genres -->
          <div>
            <label class="block text-xs font-semibold text-app-muted uppercase tracking-wider mb-1.5">Genres (Up to 4)</label>
            <div class="flex flex-wrap gap-1.5" id="genrePillContainer">
              <button type="button" onclick="togglePublishGenre(this, 'Fantasy')" class="genre-selector pill-tag cursor-pointer">Fantasy</button>
              <button type="button" onclick="togglePublishGenre(this, 'Sci-Fi')" class="genre-selector pill-tag cursor-pointer">Sci-Fi</button>
              <button type="button" onclick="togglePublishGenre(this, 'Mystery')" class="genre-selector pill-tag cursor-pointer">Mystery</button>
              <button type="button" onclick="togglePublishGenre(this, 'Romance')" class="genre-selector pill-tag cursor-pointer">Romance</button>
              <button type="button" onclick="togglePublishGenre(this, 'Thriller')" class="genre-selector pill-tag cursor-pointer">Thriller</button>
              <button type="button" onclick="togglePublishGenre(this, 'Adventure')" class="genre-selector pill-tag cursor-pointer">Adventure</button>
              <button type="button" onclick="togglePublishGenre(this, 'Educational')" class="genre-selector pill-tag cursor-pointer">Educational</button>
            </div>
          </div>

          <!-- Language Editions / Documents -->
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <label class="block text-xs font-semibold text-app-muted uppercase tracking-wider">Editions & Documents (PDF)</label>
              <button type="button" onclick="openDrivePickerForPublish()" class="text-[11px] text-app-primary flex items-center gap-1">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3 h-3"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                Import from Drive
              </button>
            </div>
            <div id="editionRows" class="space-y-2"></div>
            <button type="button" onclick="addEditionRow()" class="mt-2 btn-secondary text-xs w-full py-2">+ Add Language Edition</button>
          </div>

          <!-- Status & Visibility -->
          <div class="grid grid-cols-2 gap-2.5">
            <div>
              <label class="block text-xs font-semibold text-app-muted uppercase tracking-wider mb-1">Status</label>
              <select id="publishStatusSelect" class="w-full px-2.5 py-2 text-xs">
                <option value="ongoing">Ongoing</option>
                <option value="completed">Completed</option>
                <option value="draft">Draft</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-app-muted uppercase tracking-wider mb-1">Visibility</label>
              <select id="publishVisibilitySelect" class="w-full px-2.5 py-2 text-xs">
                <option value="public">Public</option>
                <option value="unlisted">Unlisted</option>
              </select>
            </div>
          </div>

          <!-- Submit Buttons -->
          <div class="pt-2 flex gap-2.5">
            <button type="button" onclick="handlePublishSubmit(null, 'draft')" class="btn-secondary text-xs flex-1 py-2.5">Save Draft</button>
            <button type="submit" id="publishSubmitBtn" class="btn-primary text-xs flex-1 py-2.5">Publish Work</button>
          </div>
        </form>
      </div>
    </div>
  </section>

  <!-- ── 4E. COMPLETE PROFILE REDESIGN ── -->
  <section id="page-profile" class="app-page">
    <div id="profileAuthGuard" class="hidden px-5 pt-12 text-center">
      <div class="w-12 h-12 rounded-full bg-app-surface mx-auto mb-3 flex items-center justify-center text-app-primary">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-6 h-6"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
      </div>
      <h3 class="font-display font-bold text-base text-white mb-1">Author & Reader Profile</h3>
      <p class="text-xs text-app-muted mb-4 max-w-xs mx-auto">Sign in to manage your publications, verification, and settings.</p>
      <button onclick="openAuthModal()" class="btn-primary text-xs px-5 py-2.5">Sign In</button>
    </div>

    <div id="profileMainContent" class="hidden pb-8">
      <!-- Profile Header / Banner -->
      <div class="h-28 bg-app-surface relative">
        <div class="absolute -bottom-10 left-4 flex items-end gap-3.5">
          <!-- Avatar with ImgBB upload button -->
          <div class="relative">
            <div class="w-20 h-20 rounded-2xl bg-app-sub border-2 border-app-bg overflow-hidden shadow-xl flex items-center justify-center">
              <span id="profileAvatarLetter" class="font-display font-extrabold text-2xl text-app-primary">U</span>
              <img id="profileAvatarPhoto" class="w-full h-full object-cover hidden" alt="Avatar">
            </div>
            <button onclick="document.getElementById('avatarFileInput').click()" class="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-app-primary text-black flex items-center justify-center shadow" title="Update Profile Photo">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="w-3 h-3"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/></svg>
            </button>
            <input type="file" id="avatarFileInput" accept="image/*" class="hidden" onchange="handleProfileAvatarUpload(this)">
          </div>
        </div>
      </div>

      <div class="px-4 pt-12">
        <!-- Display Name & Badges -->
        <div class="flex items-start justify-between mb-1.5">
          <div>
            <div class="flex items-center gap-1.5 flex-wrap">
              <h3 id="profileNameDisplay" class="font-display font-bold text-base text-white">Author Name</h3>
              <!-- Verification Badges -->
              <span id="badgeEmailVerified" class="hidden text-[10px] px-1.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-medium">✓ Email Verified</span>
              <span id="badgeCreatorVerified" class="hidden text-[10px] px-1.5 py-0.5 rounded-full bg-app-primary/10 text-app-secondary border border-app-primary/40 font-semibold">★ Verified Creator</span>
            </div>
            <p id="profileHandleDisplay" class="text-xs text-app-primary mt-0.5">@author</p>
            <p id="profileEmailDisplay" class="text-[11px] text-app-muted"></p>
          </div>

          <div class="flex items-center gap-1.5">
            <button onclick="openEditProfileModal()" class="btn-secondary text-[11px] px-2.5 py-1.5">Edit Profile</button>
            <button onclick="openSettingsModal()" class="btn-secondary text-[11px] px-2.5 py-1.5 flex items-center gap-1">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3 h-3"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
              Settings
            </button>
          </div>
        </div>

        <p id="profileBioDisplay" class="text-xs text-app-muted leading-relaxed mb-4">No biography entered yet.</p>

        <!-- Verification Banner if not verified -->
        <div id="creatorVerificationBanner" class="surface-elevated p-3 mb-4 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-app-primary">★</span>
            <div>
              <p class="text-xs font-semibold text-white">Creator Verification</p>
              <p id="creatorStatusSummary" class="text-[10px] text-app-muted">Unlock official verified author status and publishing tools.</p>
            </div>
          </div>
          <button id="btnRequestVerification" onclick="openVerificationModal()" class="btn-primary text-[10px] px-2.5 py-1">Apply Now</button>
        </div>

        <!-- 5-Statistic Bar -->
        <div class="grid grid-cols-5 gap-1.5 mb-5">
          <div class="surface-card-static p-2 text-center">
            <div id="statPublishedCount" class="font-display font-bold text-xs text-white">0</div>
            <div class="text-[9px] text-app-muted mt-0.5">Works</div>
          </div>
          <div class="surface-card-static p-2 text-center">
            <div id="statChaptersCount" class="font-display font-bold text-xs text-white">0</div>
            <div class="text-[9px] text-app-muted mt-0.5">Chapters</div>
          </div>
          <div class="surface-card-static p-2 text-center">
            <div id="statFollowersCount" class="font-display font-bold text-xs text-white">0</div>
            <div class="text-[9px] text-app-muted mt-0.5">Followers</div>
          </div>
          <div class="surface-card-static p-2 text-center">
            <div id="statFollowingCount" class="font-display font-bold text-xs text-white">0</div>
            <div class="text-[9px] text-app-muted mt-0.5">Following</div>
          </div>
          <div class="surface-card-static p-2 text-center">
            <div id="statTotalViews" class="font-display font-bold text-xs text-white">0</div>
            <div class="text-[9px] text-app-muted mt-0.5">Reads</div>
          </div>
        </div>

        <!-- Profile Tabs -->
        <div class="flex gap-1.5 mb-3 overflow-x-auto">
          <button onclick="switchProfileTab('works')" class="prof-tab pill-tag" data-tab="works" style="background:#9270FF; color:#0B0B10">Published</button>
          <button onclick="switchProfileTab('library')" class="prof-tab pill-tag" data-tab="library">Library</button>
          <button onclick="switchProfileTab('reviews')" class="prof-tab pill-tag" data-tab="reviews">Reviews</button>
          <button onclick="switchProfileTab('about')" class="prof-tab pill-tag" data-tab="about">About</button>
        </div>

        <div id="profileTabContentWorks" class="space-y-2.5"></div>
        <div id="profileTabContentLibrary" class="hidden space-y-2.5"></div>
        <div id="profileTabContentReviews" class="hidden space-y-2.5"></div>
        <div id="profileTabContentAbout" class="hidden surface-card-static p-4 space-y-3">
          <div>
            <h4 class="text-xs font-semibold text-app-muted uppercase tracking-wider mb-1">Author Bio</h4>
            <p id="aboutBioText" class="text-xs text-white leading-relaxed">—</p>
          </div>
          <div>
            <h4 class="text-xs font-semibold text-app-muted uppercase tracking-wider mb-1">Joined Date</h4>
            <p id="aboutJoinedDate" class="text-xs text-white">—</p>
          </div>
          <div>
            <h4 class="text-xs font-semibold text-app-muted uppercase tracking-wider mb-1">Creator Status</h4>
            <p id="aboutCreatorStatus" class="text-xs text-white">—</p>
          </div>
        </div>
      </div>
    </div>
  </section>

</main>

<!-- ════════════════════════════════════════════════════════
     5. EDITORIAL BOTTOM NAVIGATION
═══════════════════════════════════════════════════════════ -->
<nav class="glass-nav fixed bottom-0 left-0 right-0 z-40 flex items-center justify-around safe-bottom" style="height: calc(64px + var(--sab)); padding-top: 8px">
  <button onclick="switchPage('home')" id="nav-home" class="nav-item flex flex-col items-center justify-center gap-1 flex-1 py-1" style="color: #9270FF">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
    <span class="text-[10px] font-medium tracking-tight">Home</span>
  </button>
  <button onclick="switchPage('explore')" id="nav-explore" class="nav-item flex flex-col items-center justify-center gap-1 flex-1 py-1 text-app-muted">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>
    <span class="text-[10px] font-medium tracking-tight">Explore</span>
  </button>
  <button onclick="switchPage('library')" id="nav-library" class="nav-item flex flex-col items-center justify-center gap-1 flex-1 py-1 text-app-muted">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
    <span class="text-[10px] font-medium tracking-tight">Library</span>
  </button>
  <button onclick="switchPage('publish')" id="nav-publish" class="nav-item flex flex-col items-center justify-center gap-1 flex-1 py-1 text-app-muted">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
    <span class="text-[10px] font-medium tracking-tight">Publish</span>
  </button>
  <button onclick="switchPage('profile')" id="nav-profile" class="nav-item flex flex-col items-center justify-center gap-1 flex-1 py-1 text-app-muted">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
    <span class="text-[10px] font-medium tracking-tight">Profile</span>
  </button>
</nav>

<!-- ════════════════════════════════════════════════════════
     6. NOVELIX 4.0 SETTINGS MODAL
═══════════════════════════════════════════════════════════ -->
<div id="settingsModal" class="modal-backdrop" onclick="if(event.target===this)closeSettingsModal()">
  <div class="modal-sheet h-[88vh]">
    <!-- Modal Header -->
    <div class="px-4 py-3 border-b border-app-border flex items-center justify-between flex-shrink-0">
      <div class="flex items-center gap-2">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4 text-app-primary"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
        <h3 class="font-display font-bold text-sm text-white">Application Settings</h3>
      </div>
      <button onclick="closeSettingsModal()" class="w-7 h-7 rounded-full surface-card flex items-center justify-center text-app-muted hover:text-white">✕</button>
    </div>

    <!-- Navigation Tabs -->
    <div class="px-4 py-2 border-b border-app-border flex gap-1.5 overflow-x-auto flex-shrink-0">
      <button onclick="switchSettingsSection('account')" class="settings-nav-btn pill-tag" data-sec="account" style="background:#9270FF; color:#0B0B10">Account</button>
      <button onclick="switchSettingsSection('drive')" class="settings-nav-btn pill-tag" data-sec="drive">Connected Services</button>
      <button onclick="switchSettingsSection('storage')" class="settings-nav-btn pill-tag" data-sec="storage">Storage & Publishing</button>
      <button onclick="switchSettingsSection('notifications')" class="settings-nav-btn pill-tag" data-sec="notifications">Notifications</button>
      <button onclick="switchSettingsSection('appearance')" class="settings-nav-btn pill-tag" data-sec="appearance">Appearance</button>
      <button onclick="switchSettingsSection('about')" class="settings-nav-btn pill-tag" data-sec="about">About</button>
    </div>

    <!-- Scrollable Body -->
    <div class="p-4 overflow-y-auto flex-1 space-y-4">
      
      <!-- SECTION: ACCOUNT -->
      <div id="settingsSec-account" class="settings-section space-y-4">
        <div class="surface-card-static p-4 space-y-3">
          <h4 class="text-xs font-semibold text-white">Account Information</h4>
          <div class="text-xs text-app-muted">
            <p>Email: <span id="setAccEmail" class="text-white font-mono">—</span></p>
            <p class="mt-1">User ID: <span id="setAccUid" class="text-app-secondary font-mono text-[10px]">—</span></p>
            <p class="mt-1">Role: <span id="setAccRole" class="text-white">Reader</span></p>
          </div>
          <!-- Email Verification Status & Action -->
          <div class="pt-2 border-t border-app-border flex items-center justify-between">
            <div>
              <p class="text-xs font-medium text-white">Email Verification</p>
              <p id="setEmailVerifyStatusText" class="text-[11px] text-amber-400">Not verified</p>
            </div>
            <button id="btnSendVerifyEmail" onclick="executeSendVerificationEmail()" class="btn-secondary text-[11px] px-3 py-1.5">Verify Email</button>
          </div>
        </div>

        <!-- Change Password -->
        <div class="surface-card-static p-4 space-y-3">
          <h4 class="text-xs font-semibold text-white">Security & Password</h4>
          <input type="password" id="changePasswordNew" placeholder="New Password (min 6 characters)" class="w-full px-3 py-2 text-xs">
          <button onclick="executeChangePassword()" class="btn-secondary text-xs w-full py-2">Update Password</button>
        </div>

        <!-- Logout & Delete Account -->
        <div class="surface-card-static p-4 space-y-2.5">
          <button onclick="signOutUser(); closeSettingsModal()" class="btn-secondary text-xs w-full py-2.5 text-white">Log Out</button>
          <button onclick="executeDeleteAccount()" class="text-xs w-full py-2 text-red-400 hover:text-red-300">Delete Account & Data</button>
        </div>
      </div>

      <!-- SECTION: CONNECTED SERVICES (GOOGLE DRIVE) -->
      <div id="settingsSec-drive" class="settings-section hidden space-y-4">
        <div class="surface-card-static p-4 space-y-3">
          <div class="flex items-center justify-between">
            <h4 class="text-xs font-semibold text-white">Google Drive Integration</h4>
            <span class="text-[10px] text-app-secondary">Official Drive API</span>
          </div>
          <p class="text-xs text-app-muted">Connect your Google Drive account to import manuscripts, books, and PDFs directly into the publishing studio.</p>
          
          <button onclick="initiateGoogleDriveConnection()" class="btn-primary text-xs w-full py-2.5 flex items-center justify-center gap-2">
            <svg viewBox="0 0 24 24" class="w-4 h-4 fill-current"><path d="M12.01 1.99c-5.52 0-10 4.48-10 10s4.48 10 10 10 10-4.48 10-10-4.48-10-10-10zm-1.01 16.51l-4.5-4.5 1.41-1.41 3.09 3.09 7.09-7.09 1.41 1.41-8.5 8.5z"/></svg>
            Connect Google Drive Account
          </button>
        </div>

        <!-- Connected Accounts List -->
        <div>
          <h4 class="text-xs font-semibold text-app-muted uppercase tracking-wider mb-2">Connected Accounts</h4>
          <div id="connectedDriveList" class="space-y-2">
            <div class="surface-card-static p-3 text-center text-xs text-app-muted">No Google Drive accounts connected yet.</div>
          </div>
        </div>
      </div>

      <!-- SECTION: STORAGE & PUBLISHING -->
      <div id="settingsSec-storage" class="settings-section hidden space-y-4">
        <div class="surface-card-static p-4 space-y-3">
          <h4 class="text-xs font-semibold text-white">Storage Capacity & Quota</h4>
          <div class="flex items-center justify-between text-xs">
            <span class="text-app-muted">Total Publishing Quota</span>
            <span id="setStorageTotal" class="text-white font-semibold">500.0 MB</span>
          </div>
          <div class="flex items-center justify-between text-xs">
            <span class="text-app-muted">Storage Used</span>
            <span id="setStorageUsed" class="text-white font-semibold">0.0 MB</span>
          </div>
          <div class="flex items-center justify-between text-xs">
            <span class="text-app-muted">Remaining Space</span>
            <span id="setStorageRemaining" class="text-app-primary font-semibold">500.0 MB</span>
          </div>
          <div class="w-full h-2 rounded-full bg-app-sub overflow-hidden">
            <div id="setStorageBar" class="h-full bg-app-primary" style="width: 0%"></div>
          </div>
        </div>

        <div class="surface-card-static p-4 space-y-2">
          <h4 class="text-xs font-semibold text-white">Publishing Policies</h4>
          <p class="text-[11px] text-app-muted leading-relaxed">• Maximum PDF asset size: 100 MB per publication edition.</p>
          <p class="text-[11px] text-app-muted leading-relaxed">• Cover artwork limit: 15 MB (JPG, PNG, WebP).</p>
          <p class="text-[11px] text-app-muted leading-relaxed">• Quota is recalculated automatically upon asset deletion.</p>
        </div>
      </div>

      <!-- SECTION: NOTIFICATIONS -->
      <div id="settingsSec-notifications" class="settings-section hidden space-y-4">
        <div class="surface-card-static p-4 space-y-3">
          <div class="flex items-center justify-between">
            <h4 class="text-xs font-semibold text-white">Push Notifications (FCM)</h4>
            <span id="pushPermissionBadge" class="text-[10px] px-2 py-0.5 rounded-full bg-app-sub text-app-muted font-mono">Default</span>
          </div>
          <p class="text-xs text-app-muted">Receive live notifications for new chapters, author releases, and account security alerts.</p>
          <button onclick="requestPushNotificationPermission()" class="btn-secondary text-xs w-full py-2">Enable Device Notifications</button>
        </div>

        <div class="surface-card-static p-4 space-y-3">
          <h4 class="text-xs font-semibold text-white mb-2">Notification Preferences</h4>
          <label class="flex items-center justify-between cursor-pointer">
            <span class="text-xs text-app-muted">New Publication Releases</span>
            <input type="checkbox" id="prefNotifNewBook" checked class="rounded border-app-border text-app-primary">
          </label>
          <label class="flex items-center justify-between cursor-pointer">
            <span class="text-xs text-app-muted">Followed Author Updates</span>
            <input type="checkbox" id="prefNotifFollow" checked class="rounded border-app-border text-app-primary">
          </label>
          <label class="flex items-center justify-between cursor-pointer">
            <span class="text-xs text-app-muted">New Chapters in Saved Works</span>
            <input type="checkbox" id="prefNotifChapters" checked class="rounded border-app-border text-app-primary">
          </label>
          <label class="flex items-center justify-between cursor-pointer">
            <span class="text-xs text-app-muted">Account Security Alerts</span>
            <input type="checkbox" id="prefNotifSecurity" checked class="rounded border-app-border text-app-primary">
          </label>
        </div>
      </div>

      <!-- SECTION: APPEARANCE -->
      <div id="settingsSec-appearance" class="settings-section hidden space-y-4">
        <div class="surface-card-static p-4 space-y-3">
          <h4 class="text-xs font-semibold text-white">Visual Theme</h4>
          <div class="grid grid-cols-2 gap-2">
            <button onclick="setAppTheme('dark')" class="p-3 rounded-xl border border-app-primary bg-app-sub text-center text-xs text-white">Slate Dark (Default)</button>
            <button onclick="setAppTheme('oled')" class="p-3 rounded-xl border border-app-border bg-black text-center text-xs text-app-muted">OLED Pure Black</button>
          </div>
        </div>

        <div class="surface-card-static p-4 space-y-3">
          <h4 class="text-xs font-semibold text-white">Reading Font Family</h4>
          <select id="prefReadingFont" class="w-full px-3 py-2 text-xs" onchange="updateReadingFontPreference(this.value)">
            <option value="Inter">Inter (Sans-Serif)</option>
            <option value="Playfair Display">Playfair Display (Editorial Serif)</option>
            <option value="Manrope">Manrope (Geometric Modern)</option>
          </select>
        </div>

        <div class="surface-card-static p-4 space-y-2">
          <label class="flex items-center justify-between cursor-pointer">
            <span class="text-xs text-white">Reduce Animations</span>
            <input type="checkbox" id="prefReduceMotion" class="rounded border-app-border text-app-primary">
          </label>
        </div>
      </div>

      <!-- SECTION: ABOUT -->
      <div id="settingsSec-about" class="settings-section hidden space-y-4">
        <div class="surface-card-static p-4 space-y-2 text-center">
          <div class="w-10 h-10 rounded-xl bg-app-surface border border-app-border mx-auto flex items-center justify-center font-display font-extrabold text-app-primary">N</div>
          <h4 class="font-display font-bold text-sm text-white">NOVELIX 4.0</h4>
          <p class="text-[11px] text-app-muted">Editorial Digital Publishing Platform</p>
          <p class="text-[10px] font-mono text-app-secondary">Build 4.0.0-PROD • Firebase Native</p>
        </div>

        <div class="surface-card-static p-4 space-y-2 text-xs text-app-muted">
          <p><strong class="text-white">Privacy Policy:</strong> NOVELIX respects your intellectual property and reading privacy. Data is encrypted in transit and at rest using Google Cloud Firebase.</p>
          <p class="pt-2"><strong class="text-white">Support:</strong> For assistance, contact support@novelix.app</p>
        </div>
      </div>

    </div>
  </div>
</div>

<!-- ════════════════════════════════════════════════════════
     7. GOOGLE DRIVE FILE PICKER MODAL
═══════════════════════════════════════════════════════════ -->
<div id="drivePickerModal" class="modal-backdrop" onclick="if(event.target===this)closeDrivePickerModal()">
  <div class="modal-sheet h-[80vh]">
    <div class="px-4 py-3 border-b border-app-border flex items-center justify-between">
      <h3 class="font-display font-bold text-sm text-white flex items-center gap-2">
        <svg viewBox="0 0 24 24" class="w-4 h-4 fill-app-primary"><path d="M12.01 1.99c-5.52 0-10 4.48-10 10s4.48 10 10 10 10-4.48 10-10-4.48-10-10-10zm-1.01 16.51l-4.5-4.5 1.41-1.41 3.09 3.09 7.09-7.09 1.41 1.41-8.5 8.5z"/></svg>
        Select PDF from Google Drive
      </h3>
      <button onclick="closeDrivePickerModal()" class="w-7 h-7 rounded-full surface-card flex items-center justify-center text-app-muted hover:text-white">✕</button>
    </div>
    <div class="p-3 border-b border-app-border">
      <input type="text" id="driveSearchInput" placeholder="Filter Drive files..." class="w-full px-3 py-2 text-xs" oninput="filterDriveFileList(this.value)">
    </div>
    <div id="driveFilesContainer" class="p-4 overflow-y-auto flex-1 space-y-2">
      <!-- Drive files rendered here -->
    </div>
  </div>
</div>

<!-- ════════════════════════════════════════════════════════
     8. CREATOR VERIFICATION REQUEST MODAL
═══════════════════════════════════════════════════════════ -->
<div id="verificationModal" class="modal-backdrop" onclick="if(event.target===this)closeVerificationModal()">
  <div class="modal-sheet">
    <div class="px-4 py-3 border-b border-app-border flex items-center justify-between">
      <h3 class="font-display font-bold text-sm text-white flex items-center gap-2">
        <span class="text-app-primary">★</span> Apply for Creator Verification
      </h3>
      <button onclick="closeVerificationModal()" class="w-7 h-7 rounded-full surface-card flex items-center justify-center text-app-muted hover:text-white">✕</button>
    </div>
    <form class="p-4 space-y-3" onsubmit="submitCreatorVerificationRequest(event)">
      <p class="text-xs text-app-muted">Submit your creator portfolio for administrative review. Approved authors receive the NOVELIX Creator Badge and priority distribution.</p>
      <div>
        <label class="block text-xs font-semibold text-app-muted mb-1">Author / Pen Name</label>
        <input type="text" id="verifAuthorName" required class="w-full px-3 py-2 text-xs">
      </div>
      <div>
        <label class="block text-xs font-semibold text-app-muted mb-1">Portfolio or Prior Publication Links</label>
        <input type="text" id="verifPortfolioUrl" placeholder="https://..." required class="w-full px-3 py-2 text-xs">
      </div>
      <div>
        <label class="block text-xs font-semibold text-app-muted mb-1">Primary Writing Genres</label>
        <input type="text" id="verifGenres" placeholder="e.g. Fantasy, Mystery, Cyberpunk" required class="w-full px-3 py-2 text-xs">
      </div>
      <div>
        <label class="block text-xs font-semibold text-app-muted mb-1">Creator Statement / Motivation</label>
        <textarea id="verifStatement" required rows="3" placeholder="Tell us about your upcoming works on NOVELIX..." class="w-full px-3 py-2 text-xs resize-none"></textarea>
      </div>
      <button type="submit" id="btnSubmitVerification" class="btn-primary text-xs w-full py-2.5">Submit Application</button>
    </form>
  </div>
</div>

<!-- ════════════════════════════════════════════════════════
     9. EDIT PROFILE MODAL
═══════════════════════════════════════════════════════════ -->
<div id="editProfileModal" class="modal-backdrop" onclick="if(event.target===this)closeEditProfileModal()">
  <div class="modal-sheet">
    <div class="px-4 py-3 border-b border-app-border flex items-center justify-between">
      <h3 class="font-display font-bold text-sm text-white">Edit Profile Details</h3>
      <button onclick="closeEditProfileModal()" class="w-7 h-7 rounded-full surface-card flex items-center justify-center text-app-muted hover:text-white">✕</button>
    </div>
    <form class="p-4 space-y-3" onsubmit="executeSaveProfileDetails(event)">
      <div>
        <label class="block text-xs font-semibold text-app-muted mb-1">Display Name</label>
        <input type="text" id="editProfileName" required class="w-full px-3 py-2 text-xs">
      </div>
      <div>
        <label class="block text-xs font-semibold text-app-muted mb-1">Unique Username (@handle)</label>
        <input type="text" id="editProfileHandle" required placeholder="authorname" class="w-full px-3 py-2 text-xs">
        <p id="handleValidationMsg" class="text-[10px] text-app-muted mt-0.5">Alphanumeric, no spaces.</p>
      </div>
      <div>
        <label class="block text-xs font-semibold text-app-muted mb-1">Author Bio</label>
        <textarea id="editProfileBio" rows="2" class="w-full px-3 py-2 text-xs resize-none"></textarea>
      </div>
      <div>
        <label class="block text-xs font-semibold text-app-muted mb-1">Website or Social Link</label>
        <input type="text" id="editProfileWebsite" placeholder="https://..." class="w-full px-3 py-2 text-xs">
      </div>
      <button type="submit" id="btnSaveProfileDetails" class="btn-primary text-xs w-full py-2.5">Save Changes</button>
    </form>
  </div>
</div>

<!-- ════════════════════════════════════════════════════════
     10. NOTIFICATION CENTER MODAL
═══════════════════════════════════════════════════════════ -->
<div id="notifModal" class="modal-backdrop" onclick="if(event.target===this)closeNotifModal()">
  <div class="modal-sheet h-[80vh]">
    <div class="px-4 py-3 border-b border-app-border flex items-center justify-between flex-shrink-0">
      <div class="flex items-center gap-2">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4 text-app-primary"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
        <h3 class="font-display font-bold text-sm text-white">Notifications</h3>
      </div>
      <div class="flex items-center gap-2">
        <button onclick="markAllNotificationsRead()" class="text-[11px] text-app-primary font-medium">Mark Read</button>
        <button onclick="closeNotifModal()" class="w-7 h-7 rounded-full surface-card flex items-center justify-center text-app-muted hover:text-white">✕</button>
      </div>
    </div>
    <div class="p-4 overflow-y-auto flex-1 space-y-2" id="notifItemsContainer">
      <!-- Rendered dynamically -->
    </div>
    <div id="notifEmptyBox" class="hidden p-8 text-center text-xs text-app-muted">
      No notifications right now.
    </div>
  </div>
</div>

<!-- ════════════════════════════════════════════════════════
     11. ADMIN DASHBOARD MODAL
═══════════════════════════════════════════════════════════ -->
<div id="adminDashboardModal" class="modal-fullscreen">
  <div class="safe-top bg-app-sub border-b border-app-border px-4 py-3 flex items-center justify-between flex-shrink-0">
    <div class="flex items-center gap-2">
      <span class="w-6 h-6 rounded bg-red-500/20 text-red-400 flex items-center justify-center text-xs font-bold">★</span>
      <h3 class="font-display font-bold text-sm text-white">NOVELIX 4.0 Admin Console</h3>
    </div>
    <button onclick="closeAdminDashboard()" class="btn-secondary text-xs px-3 py-1.5">Close Console</button>
  </div>

  <div class="px-4 py-2 bg-app-surface border-b border-app-border flex gap-1.5 overflow-x-auto flex-shrink-0">
    <button onclick="switchAdminTab('users')" class="admin-tab-btn pill-tag" data-tab="users" style="background:#9270FF; color:#0B0B10">Users</button>
    <button onclick="switchAdminTab('verifications')" class="admin-tab-btn pill-tag" data-tab="verifications">Verifications</button>
    <button onclick="switchAdminTab('publications')" class="admin-tab-btn pill-tag" data-tab="publications">Publications</button>
    <button onclick="switchAdminTab('storage')" class="admin-tab-btn pill-tag" data-tab="storage">Storage Quotas</button>
    <button onclick="switchAdminTab('announcements')" class="admin-tab-btn pill-tag" data-tab="announcements">Broadcast</button>
    <button onclick="switchAdminTab('logs')" class="admin-tab-btn pill-tag" data-tab="logs">Audit Logs</button>
  </div>

  <div class="p-4 overflow-y-auto flex-1">
    <!-- Admin Tab: Users -->
    <div id="adminTab-users" class="admin-tab-content space-y-3">
      <div class="flex items-center justify-between">
        <h4 class="text-xs font-semibold text-white">User Accounts</h4>
        <button onclick="loadAdminUsersList()" class="btn-secondary text-[11px] px-2.5 py-1">Refresh</button>
      </div>
      <div id="adminUsersTable" class="space-y-2"></div>
    </div>

    <!-- Admin Tab: Verifications -->
    <div id="adminTab-verifications" class="admin-tab-content hidden space-y-3">
      <div class="flex items-center justify-between">
        <h4 class="text-xs font-semibold text-white">Pending Creator Verifications</h4>
        <button onclick="loadAdminVerificationsList()" class="btn-secondary text-[11px] px-2.5 py-1">Refresh</button>
      </div>
      <div id="adminVerificationsTable" class="space-y-2"></div>
    </div>

    <!-- Admin Tab: Publications -->
    <div id="adminTab-publications" class="admin-tab-content hidden space-y-3">
      <div class="flex items-center justify-between">
        <h4 class="text-xs font-semibold text-white">Content Moderation</h4>
        <button onclick="loadAdminPublicationsList()" class="btn-secondary text-[11px] px-2.5 py-1">Refresh</button>
      </div>
      <div id="adminPublicationsTable" class="space-y-2"></div>
    </div>

    <!-- Admin Tab: Storage -->
    <div id="adminTab-storage" class="admin-tab-content hidden space-y-3">
      <h4 class="text-xs font-semibold text-white">Storage Quota Configurations</h4>
      <div class="surface-card-static p-4 space-y-3">
        <label class="block text-xs font-semibold text-app-muted">Default User Publishing Quota (MB)</label>
        <input type="number" id="adminDefaultQuotaInput" value="500" class="w-full px-3 py-2 text-xs">
        <button onclick="saveAdminQuotaSetting()" class="btn-primary text-xs w-full py-2">Update Quota Policy</button>
      </div>
    </div>

    <!-- Admin Tab: Announcements -->
    <div id="adminTab-announcements" class="admin-tab-content hidden space-y-3">
      <h4 class="text-xs font-semibold text-white">Broadcast Platform Announcement</h4>
      <div class="surface-card-static p-4 space-y-3">
        <input type="text" id="adminAnnounceTitle" placeholder="Announcement Title" class="w-full px-3 py-2 text-xs">
        <textarea id="adminAnnounceBody" rows="3" placeholder="Message to all registered readers and creators..." class="w-full px-3 py-2 text-xs resize-none"></textarea>
        <button onclick="sendAdminAnnouncement()" class="btn-primary text-xs w-full py-2">Broadcast to Network</button>
      </div>
    </div>

    <!-- Admin Tab: Logs -->
    <div id="adminTab-logs" class="admin-tab-content hidden space-y-3">
      <div class="flex items-center justify-between">
        <h4 class="text-xs font-semibold text-white">Security Audit Log</h4>
        <button onclick="loadAdminAuditLogs()" class="btn-secondary text-[11px] px-2.5 py-1">Refresh</button>
      </div>
      <div id="adminLogsContainer" class="font-mono text-[11px] space-y-1.5"></div>
    </div>
  </div>
</div>

<!-- ════════════════════════════════════════════════════════
     12. AUTHENTICATION MODAL (REDESIGNED)
═══════════════════════════════════════════════════════════ -->
<div id="authModal" class="modal-backdrop" onclick="if(event.target===this)closeAuthModal()">
  <div class="modal-sheet">
    <div class="p-6">
      <div class="text-center mb-5">
        <div class="w-10 h-10 rounded-xl bg-app-surface border border-app-border mx-auto mb-2 flex items-center justify-center font-display font-extrabold text-app-primary">N</div>
        <h3 class="font-display font-bold text-lg text-white">NOVELIX</h3>
        <p class="text-xs text-app-muted">Global Editorial Reading Ecosystem</p>
      </div>

      <!-- Tab Switcher -->
      <div class="flex bg-app-sub p-1 rounded-xl mb-4">
        <button type="button" id="authTabLogin" onclick="setAuthMode('login')" class="flex-1 py-2 text-xs font-semibold rounded-lg bg-app-surface text-white">Sign In</button>
        <button type="button" id="authTabRegister" onclick="setAuthMode('register')" class="flex-1 py-2 text-xs font-semibold rounded-lg text-app-muted">Register</button>
      </div>

      <!-- Login Form -->
      <form id="authLoginForm" class="space-y-3" onsubmit="event.preventDefault(); executeEmailLogin()">
        <div>
          <label class="block text-xs font-semibold text-app-muted mb-1">Email</label>
          <input type="email" id="loginEmailInput" required placeholder="reader@novelix.app" class="w-full px-3.5 py-2.5 text-xs">
        </div>
        <div>
          <label class="block text-xs font-semibold text-app-muted mb-1">Password</label>
          <div class="relative">
            <input type="password" id="loginPasswordInput" required placeholder="••••••••" class="w-full px-3.5 py-2.5 text-xs pr-10">
            <button type="button" onclick="togglePasswordVisibility('loginPasswordInput')" class="absolute right-3 top-2.5 text-app-muted text-xs">👁</button>
          </div>
        </div>
        <div class="flex items-center justify-between text-xs">
          <label class="flex items-center gap-1.5 cursor-pointer text-app-muted">
            <input type="checkbox" id="loginRememberMe" class="rounded border-app-border text-app-primary"> Remember session
          </label>
          <button type="button" onclick="showForgotPasswordForm()" class="text-app-primary hover:underline">Forgot password?</button>
        </div>
        <button type="submit" id="btnActionLogin" class="btn-primary text-xs w-full py-2.5 font-semibold">Sign In</button>
      </form>

      <!-- Registration Form -->
      <form id="authRegisterForm" class="hidden space-y-3" onsubmit="event.preventDefault(); executeEmailRegister()">
        <div>
          <label class="block text-xs font-semibold text-app-muted mb-1">Author / Pen Name</label>
          <input type="text" id="regNameInput" required placeholder="Your Display Name" class="w-full px-3.5 py-2.5 text-xs">
        </div>
        <div>
          <label class="block text-xs font-semibold text-app-muted mb-1">Email</label>
          <input type="email" id="regEmailInput" required placeholder="author@novelix.app" class="w-full px-3.5 py-2.5 text-xs">
        </div>
        <div>
          <label class="block text-xs font-semibold text-app-muted mb-1">Password</label>
          <div class="relative">
            <input type="password" id="regPasswordInput" required placeholder="At least 6 characters" class="w-full px-3.5 py-2.5 text-xs pr-10">
            <button type="button" onclick="togglePasswordVisibility('regPasswordInput')" class="absolute right-3 top-2.5 text-app-muted text-xs">👁</button>
          </div>
        </div>
        <label class="flex items-center gap-1.5 text-[11px] text-app-muted cursor-pointer">
          <input type="checkbox" required class="rounded border-app-border text-app-primary">
          I accept the Terms of Service & Privacy Policy
        </label>
        <button type="submit" id="btnActionRegister" class="btn-primary text-xs w-full py-2.5 font-semibold">Create Account</button>
      </form>

      <!-- Forgot Password Form -->
      <form id="authForgotForm" class="hidden space-y-3" onsubmit="event.preventDefault(); executePasswordReset()">
        <p class="text-xs text-app-muted leading-relaxed">Enter your registered email address and we will dispatch a password recovery link.</p>
        <div>
          <label class="block text-xs font-semibold text-app-muted mb-1">Account Email</label>
          <input type="email" id="forgotEmailInput" required placeholder="your.email@example.com" class="w-full px-3.5 py-2.5 text-xs">
        </div>
        <button type="submit" id="btnActionReset" class="btn-primary text-xs w-full py-2.5 font-semibold">Send Reset Link</button>
        <button type="button" onclick="setAuthMode('login')" class="text-xs text-center w-full text-app-muted hover:text-white pt-1">Return to Sign In</button>
      </form>

      <!-- Divider -->
      <div class="relative my-4 text-center">
        <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-app-border"></div></div>
        <span class="relative bg-app-sub px-3 text-[10px] uppercase tracking-wider text-app-muted">Or continue with</span>
      </div>

      <!-- Real Google Sign-In Button (Capacitor Android Native & Web) -->
      <button onclick="executeGoogleAuth()" class="surface-card w-full py-2.5 px-4 flex items-center justify-center gap-2.5 hover:border-app-primary">
        <svg viewBox="0 0 24 24" class="w-4 h-4">
          <path fill="#EA4335" d="M12 5c1.6 0 3 .6 4.1 1.7l3.1-3.1C17.3 1.8 14.8 1 12 1 7.5 1 3.7 3.6 1.9 7.3l3.7 2.9C6.5 7.4 9 5 12 5z"/>
          <path fill="#4285F4" d="M23.5 12.3c0-.8-.1-1.7-.2-2.3H12v4.5h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.8z"/>
          <path fill="#FBBC05" d="M5.6 14.8c-.3-.8-.4-1.8-.4-2.8s.2-2 .4-2.8L1.9 6.3C.7 8.7 0 10.3 0 12s.7 3.3 1.9 5.7l3.7-2.9z"/>
          <path fill="#34A853" d="M12 23c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3 0-5.5-2-6.4-4.8L1.9 16.4C3.7 20.4 7.5 23 12 23z"/>
        </svg>
        <span class="text-xs font-semibold text-white">Continue with Google</span>
      </button>
    </div>
  </div>
</div>

<!-- ════════════════════════════════════════════════════════
     13. BOOK DETAIL MODAL
═══════════════════════════════════════════════════════════ -->
<div id="bookDetailModal" class="modal-backdrop" onclick="if(event.target===this)closeBookDetailModal()">
  <div class="modal-sheet h-[85vh]">
    <div class="p-4 overflow-y-auto flex-1">
      <div class="flex gap-4 mb-4">
        <div class="w-24 h-36 rounded-xl overflow-hidden bg-app-surface flex-shrink-0 shadow-lg">
          <img id="detailCoverImg" src="" class="w-full h-full object-cover" alt="Cover">
        </div>
        <div class="flex-1 min-w-0">
          <span id="detailFormatTag" class="pill-tag text-[10px] mb-1">Book</span>
          <h2 id="detailTitle" class="font-display font-bold text-base text-white leading-tight mb-1">Title</h2>
          <p id="detailAuthor" class="text-xs text-app-primary font-medium mb-2">Author</p>
          <div class="flex items-center gap-2 text-xs text-app-muted">
            <span id="detailRating">★ 4.8</span>
            <span>•</span>
            <span id="detailReadsCount">0 reads</span>
          </div>
        </div>
      </div>

      <p id="detailSynopsis" class="text-xs text-app-muted leading-relaxed mb-4">Synopsis text...</p>

      <!-- Available Language Editions / Documents -->
      <div class="mb-4">
        <h4 class="text-xs font-semibold text-white uppercase tracking-wider mb-2">Language Editions</h4>
        <div id="detailEditionsList" class="space-y-1.5"></div>
      </div>

      <!-- Action Buttons -->
      <div class="flex gap-2">
        <button id="btnStartReading" onclick="launchActiveReader()" class="btn-primary text-xs flex-1 py-2.5 font-semibold">Start Reading</button>
        <button id="btnBookmarkDetail" onclick="toggleDetailBookmark()" class="btn-secondary text-xs px-3 py-2.5">Bookmark</button>
      </div>
    </div>
  </div>
</div>

<!-- ════════════════════════════════════════════════════════
     14. DUAL ENGINE READER MODAL (PDF.JS & MANHWA CONTINUOUS)
═══════════════════════════════════════════════════════════ -->
<div id="readerModal" class="modal-fullscreen">
  <div class="safe-top bg-app-sub/90 backdrop-blur border-b border-app-border px-4 py-2.5 flex items-center justify-between flex-shrink-0">
    <div class="flex items-center gap-2 truncate">
      <button onclick="closeReaderModal()" class="w-8 h-8 rounded-full surface-card flex items-center justify-center text-white">←</button>
      <h3 id="readerTitle" class="font-display font-semibold text-xs text-white truncate">Reading</h3>
    </div>
    <div class="flex items-center gap-1.5">
      <span id="readerPageIndicator" class="text-[11px] text-app-muted font-mono">1 / 1</span>
    </div>
  </div>

  <div id="readerViewport" class="flex-1 overflow-y-auto flex items-center justify-center bg-[#07070A] p-2">
    <canvas id="pdfRenderCanvas" class="max-w-full shadow-2xl rounded-sm"></canvas>
    <div id="manhwaScrollContainer" class="hidden w-full max-w-xl mx-auto space-y-1"></div>
  </div>

  <div class="safe-bottom bg-app-sub/95 border-t border-app-border px-4 py-2 flex items-center justify-between flex-shrink-0">
    <button onclick="changeReaderPage(-1)" class="btn-secondary text-xs px-3 py-1.5">Previous</button>
    <div class="flex items-center gap-2">
      <button onclick="zoomReader(-0.2)" class="w-7 h-7 rounded surface-card text-xs text-white font-mono">-</button>
      <button onclick="zoomReader(0.2)" class="w-7 h-7 rounded surface-card text-xs text-white font-mono">+</button>
    </div>
    <button onclick="changeReaderPage(1)" class="btn-secondary text-xs px-3 py-1.5">Next</button>
  </div>
</div>

<!-- ════════════════════════════════════════════════════════
     15. DEVELOPER & ADMIN TERMINAL (5-CLICK LOGO TRIGGER)
═══════════════════════════════════════════════════════════ -->
<div id="devTerminal">
  <div class="safe-top bg-black/60 px-4 py-2.5 flex items-center justify-between border-b border-emerald-900/40">
    <div class="flex items-center gap-2">
      <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
      <span class="text-xs font-bold tracking-widest text-emerald-400">NOVELIX 4.0 DEVELOPER CONSOLE</span>
    </div>
    <button onclick="closeTerminal()" class="text-xs text-emerald-500 hover:text-white font-mono">[EXIT]</button>
  </div>
  <div id="terminalLogBody" class="flex-1 p-4 overflow-y-auto space-y-1 text-xs"></div>
  <div class="safe-bottom p-3 bg-black/80 border-t border-emerald-900/40 flex items-center gap-2">
    <span class="text-emerald-400 font-bold">$</span>
    <input type="text" id="terminalCmdInput" placeholder="Type command (status, db, user, admin, exit)..." class="flex-1 bg-transparent border-0 text-emerald-300 font-mono text-xs focus:ring-0 p-0" onkeydown="handleTerminalKey(event)">
  </div>
</div>

<!-- ════════════════════════════════════════════════════════
     16. NOVELIX 4.0 CORE JAVASCRIPT CONTROLLER
═══════════════════════════════════════════════════════════ -->
<script>
'use strict';

// ────────────────────────────────────────────────────────
// FIREBASE CONFIGURATION (novelxa-48f15)
// ────────────────────────────────────────────────────────
const FIREBASE_CONFIG = {
  apiKey: "AIzaSyDzlkwY8Xcyyp-fh_JS_z2ob4xgc4YnLps",
  authDomain: "novelxa-48f15.firebaseapp.com",
  projectId: "novelxa-48f15",
  storageBucket: "novelxa-48f15.firebasestorage.app",
  messagingSenderId: "239783323113",
  appId: "1:239783323113:android:72ab9f84efe4b4957f5778",
  databaseURL: "https://novelxa-48f15-default-rtdb.firebaseio.com"
};

const GOOGLE_CLIENT_ID = "239783323113-r33bjnuc153ghsgpshg8vp3mktqj6t36.apps.googleusercontent.com"; // Firebase Auth
const GOOGLE_DRIVE_CLIENT_ID = "23165793827-un6a2kh299r2e7rroj9nivoku5josvlh.apps.googleusercontent.com"; // Google Drive OAuth Client
const IMGBB_KEY = 'a9985ccf572a0e05bce242e27cf8be33';

// Default storage quota per user in bytes (500 MB)
const DEFAULT_QUOTA_BYTES = 500 * 1024 * 1024;

// Initialize Firebase App
let auth, db, storage, messaging;
try {
  if (!firebase.apps.length) {
    firebase.initializeApp(FIREBASE_CONFIG);
  }
  auth = firebase.auth();
  db = firebase.firestore();
  storage = firebase.storage();
  try {
    if (firebase.messaging.isSupported()) {
      messaging = firebase.messaging();
    }
  } catch(e) {}

  db.enablePersistence({ synchronizeTabs: true }).catch(() => {});
} catch(err) {
  console.warn('Firebase init warning:', err);
}

// ────────────────────────────────────────────────────────
// RUNTIME STATE
// ────────────────────────────────────────────────────────
const APP_STATE = {
  user: null,
  profile: null,
  activePage: 'home',
  activeCategory: 'all',
  exploreCategory: 'all',
  allBooks: [],
  selectedBook: null,
  selectedEdition: null,
  selectedFormat: 'book',
  selectedGenres: [],
  publishEditions: [],
  pdfDocument: null,
  pdfPageNumber: 1,
  pdfZoomScale: 1.35,
  pdfIsRendering: false,
  logoClicks: 0,
  logoLastClickTime: 0,
  realtimeBooksUnsub: null,
  notifUnsub: null,
  profileUnsub: null,
  storageUsedBytes: 0,
  storageQuotaBytes: DEFAULT_QUOTA_BYTES,
  connectedDriveAccounts: [],
  activeDriveFiles: []
};

// ────────────────────────────────────────────────────────
// LIFECYCLE INITIALIZATION
// ────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  setupLogoTerminalTrigger();
  setupOnlineOfflineListeners();
  addEditionRow();
  showInitialHomeSkeletons();

  // Firebase Auth Redirect Resolution (For Android Google Sign-In)
  if (auth) {
    auth.getRedirectResult().then(async (result) => {
      if (result && result.user) {
        showToast('Google authentication successful');
        closeAuthModal();
      }
    }).catch((err) => {
      console.warn('Redirect auth notice:', err);
      if (err && err.code && err.code !== 'auth/null-user') {
        showToast(err.message);
      }
    });

    // Observer
    auth.onAuthStateChanged(async (firebaseUser) => {
      APP_STATE.user = firebaseUser;
      if (firebaseUser) {
        await handleUserAuthenticated(firebaseUser);
      } else {
        handleUserLoggedOut();
      }
    });
  }

  // Real-Time Firestore Synchronization
  startFirestoreBooksFeed();

  // Dismiss Splash smoothly once UI is loaded
  setTimeout(() => {
    const splash = document.getElementById('splashScreen');
    if (splash) splash.classList.add('hide');
  }, 750);
});

// ────────────────────────────────────────────────────────
// AUTHENTICATION & USER PROFILE CONTROLLER
// ────────────────────────────────────────────────────────
async function handleUserAuthenticated(user) {
  // Realtime Profile Listener
  if (APP_STATE.profileUnsub) APP_STATE.profileUnsub();
  APP_STATE.profileUnsub = db.collection('users').doc(user.uid).onSnapshot(async (doc) => {
    if (!doc.exists) {
      const defaultProfile = {
        uid: user.uid,
        email: user.email,
        displayName: user.displayName || user.email.split('@')[0],
        handle: user.email.split('@')[0].toLowerCase().replace(/[^a-z0-9]/g, ''),
        photoURL: user.photoURL || '',
        bio: 'NOVELIX Author & Reader',
        creatorVerified: false,
        creatorVerificationStatus: 'none',
        storageQuotaBytes: DEFAULT_QUOTA_BYTES,
        storageUsedBytes: 0,
        createdAt: firebase.firestore.FieldValue.serverTimestamp()
      };
      await db.collection('users').doc(user.uid).set(defaultProfile, { merge: true });
      APP_STATE.profile = defaultProfile;
    } else {
      APP_STATE.profile = doc.data();
    }
    updateProfileBadgesAndUI();
    recalculateStorageQuota();
  });

  // UI Header Elements
  document.getElementById('headerAuthBtn')?.classList.add('hidden');
  document.getElementById('headerUserAvatar')?.classList.remove('hidden');
  document.getElementById('headerNotifBtn')?.classList.remove('hidden');

  updateHeaderAvatarVisual();
  startNotificationsFeed(user.uid);
  loadConnectedDriveAccounts();

  // Refresh current view if needed
  if (APP_STATE.activePage === 'library') loadLibraryContent();
  if (APP_STATE.activePage === 'profile') loadProfileContent();
  if (APP_STATE.activePage === 'publish') updatePublishAccessState();
}

function handleUserLoggedOut() {
  APP_STATE.profile = null;
  if (APP_STATE.notifUnsub) { APP_STATE.notifUnsub(); APP_STATE.notifUnsub = null; }
  if (APP_STATE.profileUnsub) { APP_STATE.profileUnsub(); APP_STATE.profileUnsub = null; }

  document.getElementById('headerAuthBtn')?.classList.remove('hidden');
  document.getElementById('headerUserAvatar')?.classList.add('hidden');
  document.getElementById('headerNotifBtn')?.classList.add('hidden');

  if (APP_STATE.activePage === 'library') loadLibraryContent();
  if (APP_STATE.activePage === 'profile') loadProfileContent();
  if (APP_STATE.activePage === 'publish') updatePublishAccessState();
}

function updateHeaderAvatarVisual() {
  const img = document.getElementById('headerAvatarImg');
  const fallback = document.getElementById('headerAvatarFallback');
  const p = APP_STATE.profile || {};
  if (p.photoURL) {
    img.src = p.photoURL;
    img.classList.remove('hidden');
    fallback.classList.add('hidden');
  } else {
    fallback.textContent = (p.displayName || APP_STATE.user?.email || 'U')[0].toUpperCase();
    img.classList.add('hidden');
    fallback.classList.remove('hidden');
  }
}

/**
 * Real-time Verified Status Indicator updates
 */
function updateProfileBadgesAndUI() {
  const user = APP_STATE.user;
  const p = APP_STATE.profile || {};
  if (!user) return;

  // 1. Email Verification Badge
  const isEmailVerified = user.emailVerified;
  const emailBadge = document.getElementById('badgeEmailVerified');
  const emailVerifyText = document.getElementById('setEmailVerifyStatusText');
  const btnVerifyEmail = document.getElementById('btnSendVerifyEmail');
  if (emailBadge) emailBadge.classList.toggle('hidden', !isEmailVerified);
  if (emailVerifyText) {
    emailVerifyText.textContent = isEmailVerified ? 'Verified' : 'Not verified';
    emailVerifyText.className = isEmailVerified ? 'text-[11px] text-emerald-400 font-semibold' : 'text-[11px] text-amber-400';
  }
  if (btnVerifyEmail) btnVerifyEmail.classList.toggle('hidden', isEmailVerified);

  // 2. Creator Verification Badge
  const isCreatorVerified = p.creatorVerified === true;
  const creatorBadge = document.getElementById('badgeCreatorVerified');
  const verifBanner = document.getElementById('creatorVerificationBanner');
  const statusSummary = document.getElementById('creatorStatusSummary');
  const btnReq = document.getElementById('btnRequestVerification');

  if (creatorBadge) creatorBadge.classList.toggle('hidden', !isCreatorVerified);
  if (verifBanner) {
    if (isCreatorVerified) {
      verifBanner.classList.add('hidden');
    } else {
      verifBanner.classList.remove('hidden');
      if (p.creatorVerificationStatus === 'pending') {
        if (statusSummary) statusSummary.textContent = 'Your creator verification application is under review.';
        if (btnReq) { btnReq.textContent = 'Pending Review'; btnReq.disabled = true; }
      } else {
        if (statusSummary) statusSummary.textContent = 'Unlock official verified author status and publishing tools.';
        if (btnReq) { btnReq.textContent = 'Apply Now'; btnReq.disabled = false; }
      }
    }
  }

  // 3. User info in settings
  document.getElementById('setAccEmail').textContent = user.email || '—';
  document.getElementById('setAccUid').textContent = user.uid || '—';
  document.getElementById('setAccRole').textContent = isCreatorVerified ? 'Verified Creator' : (p.role || 'Reader');
}

/**
 * Send Email Verification
 */
async function executeSendVerificationEmail() {
  if (!APP_STATE.user) return;
  try {
    await APP_STATE.user.sendEmailVerification();
    showToast('Verification email dispatched to your inbox');
  } catch(e) {
    showToast(e.message);
  }
}

/**
 * Google Sign-In Execution
 */
async function executeGoogleAuth() {
  if (!auth) { showToast('Authentication engine unavailable'); return; }
  try {
    const provider = new firebase.auth.GoogleAuthProvider();
    provider.addScope('email');
    provider.addScope('profile');
    provider.setCustomParameters({ prompt: 'select_account' });

    const isCapacitor = window.Capacitor && (window.Capacitor.isNativePlatform ? window.Capacitor.isNativePlatform() : window.Capacitor.platform !== 'web');

    if (isCapacitor) {
      await auth.signInWithRedirect(provider);
    } else {
      try {
        await auth.signInWithPopup(provider);
        showToast('Signed in with Google');
        closeAuthModal();
      } catch(popupErr) {
        if (popupErr.code === 'auth/popup-blocked' || popupErr.code === 'auth/operation-not-supported-in-this-environment') {
          await auth.signInWithRedirect(provider);
        } else {
          throw popupErr;
        }
      }
    }
  } catch(error) {
    showToast(error.message || 'Google authentication error');
  }
}

async function executeEmailLogin() {
  const email = document.getElementById('loginEmailInput').value.trim();
  const password = document.getElementById('loginPasswordInput').value;
  if (!email || !password) { showToast('Enter email and password'); return; }

  setButtonLoading('btnActionLogin', true, 'Signing in...');
  try {
    await auth.signInWithEmailAndPassword(email, password);
    showToast('Signed in successfully');
    closeAuthModal();
  } catch(err) {
    showToast(err.message);
  } finally {
    setButtonLoading('btnActionLogin', false, 'Sign In');
  }
}

async function executeEmailRegister() {
  const name = document.getElementById('regNameInput').value.trim();
  const email = document.getElementById('regEmailInput').value.trim();
  const password = document.getElementById('regPasswordInput').value;
  if (!name || !email || !password) { showToast('Please complete all registration fields'); return; }
  if (password.length < 6) { showToast('Password must be at least 6 characters'); return; }

  setButtonLoading('btnActionRegister', true, 'Creating account...');
  try {
    const cred = await auth.createUserWithEmailAndPassword(email, password);
    if (cred.user) {
      await cred.user.updateProfile({ displayName: name });
      const handle = name.toLowerCase().replace(/[^a-z0-9]/g, '');
      await db.collection('users').doc(cred.user.uid).set({
        uid: cred.user.uid,
        email: email,
        displayName: name,
        handle: handle,
        creatorVerified: false,
        storageQuotaBytes: DEFAULT_QUOTA_BYTES,
        createdAt: firebase.firestore.FieldValue.serverTimestamp()
      }, { merge: true });
    }
    showToast('Account created successfully');
    closeAuthModal();
  } catch(err) {
    showToast(err.message);
  } finally {
    setButtonLoading('btnActionRegister', false, 'Create Account');
  }
}

async function executePasswordReset() {
  const email = document.getElementById('forgotEmailInput').value.trim();
  if (!email) { showToast('Please enter your email address'); return; }

  setButtonLoading('btnActionReset', true, 'Sending...');
  try {
    await auth.sendPasswordResetEmail(email);
    showToast('Password reset link sent to your email');
    setAuthMode('login');
  } catch(err) {
    showToast(err.message);
  } finally {
    setButtonLoading('btnActionReset', false, 'Send Reset Link');
  }
}

async function executeChangePassword() {
  if (!APP_STATE.user) return;
  const newPass = document.getElementById('changePasswordNew').value;
  if (!newPass || newPass.length < 6) { showToast('Password must be at least 6 characters'); return; }
  try {
    await APP_STATE.user.updatePassword(newPass);
    document.getElementById('changePasswordNew').value = '';
    showToast('Password updated successfully');
  } catch(e) {
    showToast(e.message);
  }
}

async function executeDeleteAccount() {
  if (!confirm('Are you sure you want to permanently delete your NOVELIX account and data? This cannot be undone.')) return;
  try {
    await db.collection('users').doc(APP_STATE.user.uid).delete();
    await APP_STATE.user.delete();
    showToast('Account deleted');
    closeSettingsModal();
    switchPage('home');
  } catch(e) {
    showToast(e.message);
  }
}

async function signOutUser() {
  try {
    await auth.signOut();
    showToast('Signed out successfully');
    switchPage('home');
  } catch(err) {
    showToast(err.message);
  }
}

function openAuthModal() {
  if (APP_STATE.user) { switchPage('profile'); return; }
  document.getElementById('authModal').classList.add('open');
}
function closeAuthModal() { document.getElementById('authModal').classList.remove('open'); }

function setAuthMode(mode) {
  const isLogin = mode === 'login';
  const isReg = mode === 'register';
  document.getElementById('authLoginForm').classList.toggle('hidden', !isLogin);
  document.getElementById('authRegisterForm').classList.toggle('hidden', !isReg);
  document.getElementById('authForgotForm').classList.add('hidden');

  document.getElementById('authTabLogin').className = isLogin ? 'flex-1 py-2 text-xs font-semibold rounded-lg bg-app-surface text-white' : 'flex-1 py-2 text-xs font-semibold rounded-lg text-app-muted';
  document.getElementById('authTabRegister').className = isReg ? 'flex-1 py-2 text-xs font-semibold rounded-lg bg-app-surface text-white' : 'flex-1 py-2 text-xs font-semibold rounded-lg text-app-muted';
}

function showForgotPasswordForm() {
  document.getElementById('authLoginForm').classList.add('hidden');
  document.getElementById('authRegisterForm').classList.add('hidden');
  document.getElementById('authForgotForm').classList.remove('hidden');
}

function togglePasswordVisibility(inputId) {
  const input = document.getElementById(inputId);
  if (!input) return;
  input.type = input.type === 'password' ? 'text' : 'password';
}

// ────────────────────────────────────────────────────────
// REAL-TIME PUBLISHING STORAGE METER
// ────────────────────────────────────────────────────────
async function recalculateStorageQuota() {
  if (!APP_STATE.user) return;
  const myBooks = APP_STATE.allBooks.filter(b => b.authorId === APP_STATE.user.uid);
  let usedBytes = 0;

  myBooks.forEach(b => {
    if (Array.isArray(b.languages)) {
      b.languages.forEach(l => {
        if (typeof l.fileSize === 'number') usedBytes += l.fileSize;
        else if (l.fileUrl) usedBytes += 2 * 1024 * 1024;
      });
    }
    if (b.coverUrl) usedBytes += (typeof b.coverSize === 'number' ? b.coverSize : 250 * 1024);
  });

  APP_STATE.storageUsedBytes = usedBytes;
  APP_STATE.storageQuotaBytes = (APP_STATE.profile && APP_STATE.profile.storageQuotaBytes) || DEFAULT_QUOTA_BYTES;

  const totalMB = (APP_STATE.storageQuotaBytes / (1024 * 1024)).toFixed(1);
  const usedMB = (usedBytes / (1024 * 1024)).toFixed(1);
  const remainingBytes = Math.max(0, APP_STATE.storageQuotaBytes - usedBytes);
  const remainingMB = (remainingBytes / (1024 * 1024)).toFixed(1);
  const percent = Math.min(100, Math.round((usedBytes / APP_STATE.storageQuotaBytes) * 100));

  // Update Publishing Screen Meter
  const ratioEl = document.getElementById('storageMeterRatio');
  const barEl = document.getElementById('storageProgressBar');
  const remEl = document.getElementById('storageRemainingText');
  if (ratioEl) ratioEl.textContent = `${usedMB} MB / ${totalMB} MB`;
  if (barEl) {
    barEl.style.width = `${percent}%`;
    barEl.style.backgroundColor = percent > 90 ? '#EF4444' : (percent > 75 ? '#F59E0B' : '#9270FF');
  }
  if (remEl) remEl.textContent = `Remaining: ${remainingMB} MB`;

  // Update Settings Screen Meter
  document.getElementById('setStorageTotal').textContent = `${totalMB} MB`;
  document.getElementById('setStorageUsed').textContent = `${usedMB} MB (${percent}%)`;
  document.getElementById('setStorageRemaining').textContent = `${remainingMB} MB`;
  const setBar = document.getElementById('setStorageBar');
  if (setBar) setBar.style.width = `${percent}%`;

  updateDraftStorageEstimate();
}

function updateDraftStorageEstimate() {
  let draftBytes = 0;
  const coverFile = document.getElementById('coverFileInput')?.files[0];
  if (coverFile) draftBytes += coverFile.size;

  APP_STATE.publishEditions.forEach(ed => {
    if (ed.file) draftBytes += ed.file.size;
  });

  const draftMB = (draftBytes / (1024 * 1024)).toFixed(1);
  const remainingBytes = Math.max(0, APP_STATE.storageQuotaBytes - APP_STATE.storageUsedBytes);
  const estRemainingBytes = remainingBytes - draftBytes;
  const estRemainingMB = (Math.max(0, estRemainingBytes) / (1024 * 1024)).toFixed(1);

  const draftEl = document.getElementById('storageDraftEstimate');
  const alertEl = document.getElementById('storageQuotaAlert');
  const submitBtn = document.getElementById('publishSubmitBtn');

  if (draftEl) draftEl.textContent = `Draft: ${draftMB} MB • Est. Remaining: ${estRemainingMB} MB`;

  if (estRemainingBytes < 0) {
    alertEl?.classList.remove('hidden');
    if (submitBtn) { submitBtn.disabled = true; submitBtn.classList.add('opacity-50'); }
  } else {
    alertEl?.classList.add('hidden');
    if (submitBtn) { submitBtn.disabled = false; submitBtn.classList.remove('opacity-50'); }
  }
}

// ────────────────────────────────────────────────────────
// GOOGLE DRIVE MULTI-ACCOUNT INTEGRATION
// ────────────────────────────────────────────────────────
// GOOGLE DRIVE CLOUD INTEGRATION (OAUTH 2.0 & BACKEND FLOW)
// ────────────────────────────────────────────────────────
const CANONICAL_DRIVE_REDIRECT_URI = "https://us-central1-novelxa-48f15.cloudfunctions.net/googleDriveCallback";

// Listen for OAuth callback completion via postMessage from popup
if (typeof window !== 'undefined') {
  window.addEventListener('message', async (event) => {
    if (event.data && event.data.type === 'NOVELIX_DRIVE_CONNECTED') {
      showToast(`Google Drive connected: ${event.data.email || ''}`);
      if (typeof loadConnectedDriveAccounts === 'function') {
        await loadConnectedDriveAccounts();
      }
    } else if (event.data && event.data.type === 'NOVELIX_DRIVE_ERROR') {
      showToast(`Drive connection failed: ${event.data.message || 'Unknown error'}`);
    }
  });
}

async function initiateGoogleDriveConnection() {
  if (!APP_STATE.user) { openAuthModal(); return; }

  showToast('Initiating Google Drive Authorization...');

  // Strategy 1: Try secure backend OAuth 2.0 Authorization Code Flow
  try {
    const getAuthUrlFn = functions.httpsCallable('getGoogleDriveAuthUrl');
    const res = await getAuthUrlFn({ redirectUri: CANONICAL_DRIVE_REDIRECT_URI });
    if (res.data && res.data.authUrl) {
      const popup = window.open(res.data.authUrl, 'NOVELIX_Google_Drive_Connect', 'width=540,height=680,menubar=no,toolbar=no');
      if (popup) {
        const timer = setInterval(() => {
          if (popup.closed) {
            clearInterval(timer);
            loadConnectedDriveAccounts();
          }
        }, 1000);
        return;
      }
    }
  } catch (backendErr) {
    console.log('Backend OAuth initiation unavailable or pending deployment, falling back to client GIS:', backendErr.message);
  }

  // Strategy 2: Client GIS Token Client Flow (direct browser fallback)
  if (window.google && window.google.accounts && window.google.accounts.oauth2) {
    const tokenClient = google.accounts.oauth2.initTokenClient({
      client_id: GOOGLE_DRIVE_CLIENT_ID,
      scope: 'https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/userinfo.email',
      callback: async (tokenResponse) => {
        if (tokenResponse && tokenResponse.access_token) {
          await handleGoogleDriveTokenSuccess(tokenResponse.access_token);
        }
      }
    });
    tokenClient.requestAccessToken({ prompt: 'select_account' });
  } else {
    showToast('Google Drive authentication service loading...');
  }
}

async function handleGoogleDriveTokenSuccess(accessToken) {
  try {
    // Fetch connected user info
    const res = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
      headers: { Authorization: `Bearer ${accessToken}` }
    });
    const info = await res.json();
    const email = info.email || 'connected.account@gmail.com';
    const accId = email.replace(/[^a-zA-Z0-9]/g, '_');

    await db.collection('users').doc(APP_STATE.user.uid).collection('drive_accounts').doc(accId).set({
      id: accId,
      email: email,
      name: info.name || 'Google Account',
      accessToken: accessToken,
      connectedAt: firebase.firestore.FieldValue.serverTimestamp(),
      status: 'active'
    });

    showToast(`Google Drive account connected: ${email}`);
    loadConnectedDriveAccounts();
  } catch(e) {
    showToast(`Drive connection error: ${e.message}`);
  }
}

async function loadConnectedDriveAccounts() {
  if (!APP_STATE.user) return;
  const listEl = document.getElementById('connectedDriveList');
  const snap = await db.collection('users').doc(APP_STATE.user.uid).collection('drive_accounts').get();
  
  const accounts = [];
  snap.forEach(d => accounts.push(d.data()));
  APP_STATE.connectedDriveAccounts = accounts;

  if (!accounts.length) {
    listEl.innerHTML = `<div class="surface-card-static p-3 text-center text-xs text-app-muted">No Google Drive accounts connected yet.</div>`;
    return;
  }

  listEl.innerHTML = accounts.map(acc => `
    <div class="surface-card p-3 flex items-center justify-between">
      <div class="truncate">
        <p class="text-xs font-semibold text-white truncate">${escapeHtml(acc.email)}</p>
        <span class="text-[10px] text-emerald-400">Connected • Ready to Import</span>
      </div>
      <div class="flex items-center gap-2">
        <button onclick="browseDriveAccountFiles('${acc.id}')" class="btn-secondary text-[11px] px-2.5 py-1">Browse Files</button>
        <button onclick="disconnectDriveAccount('${acc.id}')" class="text-xs text-red-400 p-1 hover:text-red-300">✕</button>
      </div>
    </div>
  `).join('');
}

async function disconnectDriveAccount(accId) {
  if (!confirm('Disconnect this Google Drive account?')) return;
  try {
    const disconnectFn = functions.httpsCallable('disconnectGoogleDriveAccount');
    await disconnectFn({ accountId: accId });
  } catch(e) {
    await db.collection('users').doc(APP_STATE.user.uid).collection('drive_accounts').doc(accId).delete();
  }
  showToast('Account disconnected');
  loadConnectedDriveAccounts();
}

async function browseDriveAccountFiles(accId) {
  let acc = APP_STATE.connectedDriveAccounts.find(a => a.id === accId);
  if (!acc) return;

  let token = acc.accessToken;

  // If token is missing, request fresh token from backend callable
  if (!token) {
    try {
      showToast('Fetching Drive access credentials...');
      const getTokenFn = functions.httpsCallable('getGoogleDriveAccessToken');
      const res = await getTokenFn({ accountId: accId });
      if (res.data && res.data.accessToken) {
        token = res.data.accessToken;
        acc.accessToken = token;
      }
    } catch(err) {
      console.warn('Could not refresh token from backend:', err.message);
    }
  }

  if (!token) {
    showToast('Drive token expired. Re-authenticating...');
    initiateGoogleDriveConnection();
    return;
  }

  openDrivePickerModal();
  const container = document.getElementById('driveFilesContainer');
  container.innerHTML = `<div class="skeleton-box h-12 mb-2"></div><div class="skeleton-box h-12"></div>`;

  try {
    const res = await fetch(`https://www.googleapis.com/drive/v3/files?q=mimeType='application/pdf' and trashed=false&fields=files(id,name,size,modifiedTime)&pageSize=30`, {
      headers: { Authorization: `Bearer ${acc.accessToken}` }
    });
    const data = await res.json();
    APP_STATE.activeDriveFiles = data.files || [];
    renderDriveFilesList(APP_STATE.activeDriveFiles, acc.accessToken);
  } catch(e) {
    container.innerHTML = `<div class="p-4 text-center text-xs text-red-400">Error loading Drive files: ${escapeHtml(e.message)}</div>`;
  }
}

function renderDriveFilesList(files, token) {
  const container = document.getElementById('driveFilesContainer');
  if (!files.length) {
    container.innerHTML = `<div class="p-6 text-center text-xs text-app-muted">No PDF documents discovered in this Drive account.</div>`;
    return;
  }

  container.innerHTML = files.map(f => {
    const sizeMB = f.size ? (f.size / (1024 * 1024)).toFixed(1) + ' MB' : 'PDF';
    return `
      <div class="surface-card p-3 flex items-center justify-between">
        <div class="truncate flex items-center gap-2.5">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4 text-app-primary flex-shrink-0"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          <div class="truncate">
            <h5 class="font-display font-medium text-xs text-white truncate">${escapeHtml(f.name)}</h5>
            <span class="text-[10px] text-app-muted">${sizeMB}</span>
          </div>
        </div>
        <button onclick="importDriveFileToStudio('${f.id}', '${escapeHtml(f.name)}', ${f.size || 0}, '${token}')" class="btn-primary text-[11px] px-3 py-1 flex-shrink-0">Import</button>
      </div>
    `;
  }).join('');
}

function filterDriveFileList(query) {
  const q = query.toLowerCase();
  const filtered = APP_STATE.activeDriveFiles.filter(f => f.name.toLowerCase().includes(q));
  renderDriveFilesList(filtered);
}

function openDrivePickerForPublish() {
  if (!APP_STATE.connectedDriveAccounts.length) {
    openSettingsModal();
    switchSettingsSection('drive');
    showToast('Please connect a Google Drive account first');
    return;
  }
  browseDriveAccountFiles(APP_STATE.connectedDriveAccounts[0].id);
}

async function importDriveFileToStudio(fileId, fileName, fileSize, token) {
  closeDrivePickerModal();
  switchPage('publish');
  showToast(`Downloading "${fileName}" from Google Drive...`);

  try {
    const res = await fetch(`https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const blob = await res.blob();
    const importedFile = new File([blob], fileName, { type: 'application/pdf' });

    // Append as a new language edition row
    const idx = APP_STATE.publishEditions.length;
    addEditionRow();
    APP_STATE.publishEditions[idx].file = importedFile;
    const label = document.getElementById(`edFileLabel-${idx}`);
    if (label) label.textContent = `[Drive] ${fileName} (${(importedFile.size / (1024*1024)).toFixed(1)} MB)`;

    recalculateStorageQuota();
    showToast('Manuscript imported successfully into Publishing Studio');
  } catch(e) {
    showToast(`Drive import error: ${e.message}`);
  }
}

function openDrivePickerModal() { document.getElementById('drivePickerModal').classList.add('open'); }
function closeDrivePickerModal() { document.getElementById('drivePickerModal').classList.remove('open'); }

// ────────────────────────────────────────────────────────
// CREATOR VERIFICATION REQUEST SYSTEM
// ────────────────────────────────────────────────────────
function openVerificationModal() {
  if (!APP_STATE.user) { openAuthModal(); return; }
  document.getElementById('verifAuthorName').value = APP_STATE.profile?.displayName || '';
  document.getElementById('verificationModal').classList.add('open');
}
function closeVerificationModal() { document.getElementById('verificationModal').classList.remove('open'); }

async function submitCreatorVerificationRequest(event) {
  event.preventDefault();
  if (!APP_STATE.user) return;

  const authorName = document.getElementById('verifAuthorName').value.trim();
  const portfolio = document.getElementById('verifPortfolioUrl').value.trim();
  const genres = document.getElementById('verifGenres').value.trim();
  const statement = document.getElementById('verifStatement').value.trim();

  setButtonLoading('btnSubmitVerification', true, 'Submitting...');
  try {
    const reqRef = db.collection('verification_requests').doc();
    await reqRef.set({
      id: reqRef.id,
      userId: APP_STATE.user.uid,
      userEmail: APP_STATE.user.email,
      authorName: authorName,
      portfolioUrl: portfolio,
      genres: genres,
      statement: statement,
      status: 'pending',
      submittedAt: firebase.firestore.FieldValue.serverTimestamp()
    });

    await db.collection('users').doc(APP_STATE.user.uid).set({
      creatorVerificationStatus: 'pending'
    }, { merge: true });

    showToast('Creator verification request submitted for admin review');
    closeVerificationModal();
  } catch(e) {
    showToast(e.message);
  } finally {
    setButtonLoading('btnSubmitVerification', false, 'Submit Application');
  }
}

// ────────────────────────────────────────────────────────
// EDIT PROFILE & IMGBB AVATAR UPLOAD
// ────────────────────────────────────────────────────────
function openEditProfileModal() {
  if (!APP_STATE.user) return;
  const p = APP_STATE.profile || {};
  document.getElementById('editProfileName').value = p.displayName || '';
  document.getElementById('editProfileHandle').value = p.handle || '';
  document.getElementById('editProfileBio').value = p.bio || '';
  document.getElementById('editProfileWebsite').value = p.website || '';
  document.getElementById('editProfileModal').classList.add('open');
}
function closeEditProfileModal() { document.getElementById('editProfileModal').classList.remove('open'); }

async function executeSaveProfileDetails(event) {
  event.preventDefault();
  if (!APP_STATE.user) return;

  const name = document.getElementById('editProfileName').value.trim();
  const handle = document.getElementById('editProfileHandle').value.trim().toLowerCase().replace(/[^a-z0-9]/g, '');
  const bio = document.getElementById('editProfileBio').value.trim();
  const website = document.getElementById('editProfileWebsite').value.trim();

  setButtonLoading('btnSaveProfileDetails', true, 'Saving...');
  try {
    // Update Firestore
    await db.collection('users').doc(APP_STATE.user.uid).set({
      displayName: name,
      handle: handle,
      bio: bio,
      website: website,
      updatedAt: firebase.firestore.FieldValue.serverTimestamp()
    }, { merge: true });

    await APP_STATE.user.updateProfile({ displayName: name });
    showToast('Profile details updated');
    closeEditProfileModal();
  } catch(e) {
    showToast(e.message);
  } finally {
    setButtonLoading('btnSaveProfileDetails', false, 'Save Changes');
  }
}

async function handleProfileAvatarUpload(input) {
  const file = input.files[0];
  if (!file || !APP_STATE.user) return;

  if (file.size > 5 * 1024 * 1024) {
    showToast('Profile image must be under 5 MB');
    return;
  }

  showToast('Uploading profile picture...');
  try {
    let photoURL = '';
    // Primary: ImgBB Cloud API
    if (IMGBB_KEY) {
      try {
        const fd = new FormData();
        fd.append('image', file);
        const res = await fetch(`https://api.imgbb.com/1/upload?key=${IMGBB_KEY}`, { method: 'POST', body: fd });
        const data = await res.json();
        if (data && data.success) {
          photoURL = data.data.url;
        }
      } catch(imgbbErr) {
        console.warn('ImgBB proxy note:', imgbbErr);
      }
    }

    // Fallback: Firebase Storage
    if (!photoURL) {
      const snap = await storage.ref(`avatars/${APP_STATE.user.uid}/${Date.now()}.jpg`).put(file);
      photoURL = await snap.ref.getDownloadURL();
    }

    await db.collection('users').doc(APP_STATE.user.uid).set({ photoURL: photoURL }, { merge: true });
    await APP_STATE.user.updateProfile({ photoURL: photoURL });
    showToast('Profile photo updated successfully');
  } catch(e) {
    showToast(`Upload failed: ${e.message}`);
  }
}

// ────────────────────────────────────────────────────────
// REAL-TIME NOTIFICATIONS CENTER
// ────────────────────────────────────────────────────────
function startNotificationsFeed(uid) {
  if (APP_STATE.notifUnsub) APP_STATE.notifUnsub();
  APP_STATE.notifUnsub = db.collection('users').doc(uid).collection('notifications')
    .orderBy('createdAt', 'desc')
    .limit(30)
    .onSnapshot(snap => {
      let unread = 0;
      const list = [];
      snap.forEach(d => {
        const data = d.data();
        if (!data.isRead) unread++;
        list.push({ id: d.id, ...data });
      });

      document.getElementById('notifBadgeDot')?.classList.toggle('hidden', unread === 0);

      const box = document.getElementById('notifItemsContainer');
      const empty = document.getElementById('notifEmptyBox');
      if (!list.length) {
        box.innerHTML = '';
        empty?.classList.remove('hidden');
        return;
      }
      empty?.classList.add('hidden');
      box.innerHTML = list.map(n => `
        <div class="surface-card p-3 flex items-start justify-between gap-3 ${!n.isRead ? 'border-app-primary/50 bg-app-surface' : ''}">
          <div class="flex-1 min-w-0">
            <h5 class="font-display font-semibold text-xs text-white mb-0.5">${escapeHtml(n.title || 'Notification')}</h5>
            <p class="text-[11px] text-app-muted leading-relaxed">${escapeHtml(n.message || '')}</p>
          </div>
          <button onclick="deleteNotificationItem('${n.id}')" class="text-xs text-app-muted hover:text-white p-1">✕</button>
        </div>
      `).join('');
    });
}

async function markAllNotificationsRead() {
  if (!APP_STATE.user) return;
  const snap = await db.collection('users').doc(APP_STATE.user.uid).collection('notifications').where('isRead', '==', false).get();
  const batch = db.batch();
  snap.forEach(d => batch.update(d.ref, { isRead: true }));
  await batch.commit();
  showToast('Notifications marked as read');
}

async function deleteNotificationItem(notifId) {
  if (!APP_STATE.user) return;
  await db.collection('users').doc(APP_STATE.user.uid).collection('notifications').doc(notifId).delete();
}

async function requestPushNotificationPermission() {
  if (!('Notification' in window)) {
    showToast('Notifications not supported in this environment');
    return;
  }
  const perm = await Notification.requestPermission();
  document.getElementById('pushPermissionBadge').textContent = perm;
  if (perm === 'granted') {
    showToast('Push notifications enabled for this device');
    if (messaging && APP_STATE.user) {
      try {
        const token = await messaging.getToken();
        if (token) {
          await db.collection('users').doc(APP_STATE.user.uid).collection('fcm_tokens').doc(token).set({
            token: token,
            device: navigator.userAgent,
            updatedAt: firebase.firestore.FieldValue.serverTimestamp()
          });
        }
      } catch(e) {}
    }
  } else {
    showToast('Notification permission was not granted');
  }
}

function openNotifModal() { document.getElementById('notifModal').classList.add('open'); }
function closeNotifModal() { document.getElementById('notifModal').classList.remove('open'); }

// ────────────────────────────────────────────────────────
// SETTINGS CONTROLLER
// ────────────────────────────────────────────────────────
function openSettingsModal() { document.getElementById('settingsModal').classList.add('open'); }
function closeSettingsModal() { document.getElementById('settingsModal').classList.remove('open'); }

function switchSettingsSection(secId) {
  document.querySelectorAll('.settings-section').forEach(s => s.classList.add('hidden'));
  document.getElementById(`settingsSec-${secId}`)?.classList.remove('hidden');

  document.querySelectorAll('.settings-nav-btn').forEach(btn => {
    const isMatch = btn.dataset.sec === secId;
    btn.style.background = isMatch ? '#9270FF' : 'rgba(146, 112, 255, 0.08)';
    btn.style.color = isMatch ? '#0B0B10' : '#B9A4FF';
  });
}

function setAppTheme(theme) {
  if (theme === 'oled') {
    document.body.style.backgroundColor = '#000000';
    showToast('OLED Pure Black enabled');
  } else {
    document.body.style.backgroundColor = '#0B0B10';
    showToast('Dark Slate theme active');
  }
}

function updateReadingFontPreference(font) {
  document.body.style.fontFamily = `'${font}', sans-serif`;
  showToast(`Reading font set to ${font}`);
}

// ────────────────────────────────────────────────────────
// DEVELOPER & ADMIN TERMINAL WITH SECURE DASHBOARD
// ────────────────────────────────────────────────────────
function setupLogoTerminalTrigger() {
  const logo = document.getElementById('headerLogoArea');
  logo?.addEventListener('click', () => {
    const now = Date.now();
    if (now - APP_STATE.logoLastClickTime > 2000) APP_STATE.logoClicks = 0;
    APP_STATE.logoLastClickTime = now;
    APP_STATE.logoClicks++;
    if (APP_STATE.logoClicks >= 5) {
      APP_STATE.logoClicks = 0;
      openTerminal();
    }
  });
}

function openTerminal() {
  document.getElementById('devTerminal').classList.add('open');
  const body = document.getElementById('terminalLogBody');
  body.innerHTML = '';
  writeTerm('NOVELIX 4.0 RUNTIME CONSOLE');
  writeTerm('═══════════════════════════════════════════');
  writeTerm(`Project: ${FIREBASE_CONFIG.projectId}`);
  writeTerm(`User: ${APP_STATE.user ? APP_STATE.user.email : 'Guest'}`);
  writeTerm('Commands: status, db, user, admin, clear, exit');
  document.getElementById('terminalCmdInput').focus();
}

function closeTerminal() { document.getElementById('devTerminal').classList.remove('open'); }

function writeTerm(msg) {
  const body = document.getElementById('terminalLogBody');
  const div = document.createElement('div');
  div.textContent = `> ${msg}`;
  body.appendChild(div);
}

async function handleTerminalKey(e) {
  if (e.key !== 'Enter') return;
  const input = document.getElementById('terminalCmdInput');
  const cmd = input.value.trim().toLowerCase();
  input.value = '';
  if (!cmd) return;
  writeTerm(`$ ${cmd}`);

  if (cmd === 'exit') closeTerminal();
  else if (cmd === 'clear') document.getElementById('terminalLogBody').innerHTML = '';
  else if (cmd === 'status') {
    writeTerm(`Active Page: ${APP_STATE.activePage}`);
    writeTerm(`Storage: ${(APP_STATE.storageUsedBytes/(1024*1024)).toFixed(1)} / ${(APP_STATE.storageQuotaBytes/(1024*1024)).toFixed(1)} MB`);
    writeTerm(`Drive Accounts: ${APP_STATE.connectedDriveAccounts.length}`);
  } else if (cmd === 'db') {
    const t0 = Date.now();
    db.collection('books').limit(1).get().then(() => {
      writeTerm(`Cloud Firestore OK (${Date.now() - t0}ms)`);
    }).catch(e => writeTerm(`DB Error: ${e.message}`));
  } else if (cmd === 'user') {
    writeTerm(JSON.stringify(APP_STATE.profile || APP_STATE.user || {}, null, 2));
  } else if (cmd === 'admin') {
    writeTerm('Checking administrator credentials...');
    if (!APP_STATE.user) {
      writeTerm('Authentication required. Opening login...');
      closeTerminal();
      openAuthModal();
      return;
    }
    // Check if user has admin claim or is marked admin
    const idTokenResult = await APP_STATE.user.getIdTokenResult();
    const isAdmin = (idTokenResult.claims && idTokenResult.claims.admin) || (APP_STATE.profile && APP_STATE.profile.isAdmin);
    if (isAdmin) {
      writeTerm('Access GRANTED: Opening Admin Console...');
      setTimeout(() => {
        closeTerminal();
        openAdminDashboard();
      }, 500);
    } else {
      writeTerm('PERMISSION DENIED: Account lacks administrator claim.');
    }
  } else {
    writeTerm(`Unknown command: "${cmd}".`);
  }
}

// ────────────────────────────────────────────────────────
// ADMIN DASHBOARD CONTROLLER
// ────────────────────────────────────────────────────────
function openAdminDashboard() {
  document.getElementById('adminDashboardModal').classList.add('open');
  loadAdminUsersList();
}
function closeAdminDashboard() { document.getElementById('adminDashboardModal').classList.remove('open'); }

function switchAdminTab(tabId) {
  document.querySelectorAll('.admin-tab-content').forEach(t => t.classList.add('hidden'));
  document.getElementById(`adminTab-${tabId}`)?.classList.remove('hidden');

  document.querySelectorAll('.admin-tab-btn').forEach(btn => {
    const isMatch = btn.dataset.tab === tabId;
    btn.style.background = isMatch ? '#9270FF' : 'rgba(146, 112, 255, 0.08)';
    btn.style.color = isMatch ? '#0B0B10' : '#B9A4FF';
  });

  if (tabId === 'users') loadAdminUsersList();
  if (tabId === 'verifications') loadAdminVerificationsList();
  if (tabId === 'publications') loadAdminPublicationsList();
  if (tabId === 'logs') loadAdminAuditLogs();
}

async function loadAdminUsersList() {
  const table = document.getElementById('adminUsersTable');
  table.innerHTML = `<div class="skeleton-box h-10 mb-2"></div>`;
  const snap = await db.collection('users').limit(50).get();
  const users = [];
  snap.forEach(d => users.push({ id: d.id, ...d.data() }));

  table.innerHTML = users.map(u => `
    <div class="surface-card p-3 flex items-center justify-between">
      <div class="truncate">
        <p class="text-xs font-semibold text-white truncate">${escapeHtml(u.displayName || u.email)}</p>
        <span class="text-[10px] text-app-muted">${escapeHtml(u.email)} • Role: ${u.role || 'reader'}</span>
      </div>
      <div class="flex items-center gap-1.5">
        <button onclick="toggleUserSuspension('${u.id}', ${u.isSuspended ? 'false' : 'true'})" class="btn-secondary text-[10px] px-2 py-1 ${u.isSuspended ? 'text-red-400' : ''}">
          ${u.isSuspended ? 'Restore' : 'Suspend'}
        </button>
      </div>
    </div>
  `).join('');
}

async function toggleUserSuspension(uid, suspend) {
  await db.collection('users').doc(uid).set({ isSuspended: suspend }, { merge: true });
  await db.collection('admin_logs').add({
    action: suspend ? 'SUSPEND_USER' : 'RESTORE_USER',
    targetUid: uid,
    adminId: APP_STATE.user.uid,
    timestamp: firebase.firestore.FieldValue.serverTimestamp()
  });
  showToast(suspend ? 'User account suspended' : 'User account restored');
  loadAdminUsersList();
}

async function loadAdminVerificationsList() {
  const table = document.getElementById('adminVerificationsTable');
  table.innerHTML = `<div class="skeleton-box h-10 mb-2"></div>`;
  const snap = await db.collection('verification_requests').where('status', '==', 'pending').get();
  const reqs = [];
  snap.forEach(d => reqs.push({ id: d.id, ...d.data() }));

  if (!reqs.length) {
    table.innerHTML = `<div class="p-6 text-center text-xs text-app-muted">No pending creator verification applications.</div>`;
    return;
  }

  table.innerHTML = reqs.map(r => `
    <div class="surface-card p-3 space-y-2">
      <div class="flex items-start justify-between">
        <div>
          <h5 class="text-xs font-semibold text-white">${escapeHtml(r.authorName)}</h5>
          <p class="text-[10px] text-app-muted">${escapeHtml(r.userEmail)} • ${escapeHtml(r.genres)}</p>
        </div>
        <div class="flex gap-1.5">
          <button onclick="decideVerification('${r.id}', '${r.userId}', 'approve')" class="btn-primary text-[10px] px-2.5 py-1">Approve</button>
          <button onclick="decideVerification('${r.id}', '${r.userId}', 'reject')" class="btn-secondary text-[10px] px-2.5 py-1 text-red-400">Reject</button>
        </div>
      </div>
      <p class="text-[11px] text-app-muted leading-relaxed">${escapeHtml(r.statement)}</p>
      <a href="${escapeHtml(r.portfolioUrl)}" target="_blank" class="text-[10px] text-app-primary underline block truncate">Portfolio: ${escapeHtml(r.portfolioUrl)}</a>
    </div>
  `).join('');
}

async function decideVerification(reqId, targetUid, decision) {
  const isApprove = decision === 'approve';
  await db.collection('verification_requests').doc(reqId).update({
    status: isApprove ? 'verified' : 'rejected',
    reviewedAt: firebase.firestore.FieldValue.serverTimestamp(),
    reviewedBy: APP_STATE.user.uid
  });

  await db.collection('users').doc(targetUid).set({
    creatorVerified: isApprove,
    creatorVerificationStatus: isApprove ? 'verified' : 'rejected'
  }, { merge: true });

  await db.collection('users').doc(targetUid).collection('notifications').add({
    title: isApprove ? 'Creator Verification Approved!' : 'Verification Update',
    message: isApprove ? 'Congratulations! Your NOVELIX Creator status has been verified.' : 'Your creator application was not approved at this time.',
    isRead: false,
    createdAt: firebase.firestore.FieldValue.serverTimestamp()
  });

  await db.collection('admin_logs').add({
    action: isApprove ? 'APPROVE_CREATOR' : 'REJECT_CREATOR',
    targetUid: targetUid,
    requestId: reqId,
    adminId: APP_STATE.user.uid,
    timestamp: firebase.firestore.FieldValue.serverTimestamp()
  });

  showToast(`Creator application ${decision}d`);
  loadAdminVerificationsList();
}

async function loadAdminPublicationsList() {
  const table = document.getElementById('adminPublicationsTable');
  table.innerHTML = APP_STATE.allBooks.map(b => `
    <div class="surface-card p-3 flex items-center justify-between">
      <div class="truncate">
        <h5 class="text-xs font-semibold text-white truncate">${escapeHtml(b.title)}</h5>
        <span class="text-[10px] text-app-muted">${escapeHtml(b.authorName)} • ${formatLabel(b.contentType)}</span>
      </div>
      <button onclick="moderateDeleteBook('${b.id}')" class="text-xs text-red-400 hover:text-red-300 p-1">Remove</button>
    </div>
  `).join('');
}

async function moderateDeleteBook(bookId) {
  if (!confirm('Remove this publication as a content moderator?')) return;
  await db.collection('books').doc(bookId).delete();
  await db.collection('admin_logs').add({
    action: 'MODERATE_DELETE_BOOK',
    bookId: bookId,
    adminId: APP_STATE.user.uid,
    timestamp: firebase.firestore.FieldValue.serverTimestamp()
  });
  showToast('Publication removed by moderator');
  loadAdminPublicationsList();
}

async function saveAdminQuotaSetting() {
  const mb = parseInt(document.getElementById('adminDefaultQuotaInput').value);
  if (!mb || mb < 50) return;
  await db.collection('admin_settings').doc('storage').set({
    defaultQuotaBytes: mb * 1024 * 1024,
    updatedAt: firebase.firestore.FieldValue.serverTimestamp(),
    updatedBy: APP_STATE.user.uid
  }, { merge: true });
  showToast('Default quota policy updated');
}

async function sendAdminAnnouncement() {
  const title = document.getElementById('adminAnnounceTitle').value.trim();
  const body = document.getElementById('adminAnnounceBody').value.trim();
  if (!title || !body) return;

  await db.collection('announcements').add({
    title: title,
    message: body,
    adminId: APP_STATE.user.uid,
    createdAt: firebase.firestore.FieldValue.serverTimestamp()
  });

  await db.collection('admin_logs').add({
    action: 'BROADCAST_ANNOUNCEMENT',
    title: title,
    adminId: APP_STATE.user.uid,
    timestamp: firebase.firestore.FieldValue.serverTimestamp()
  });

  document.getElementById('adminAnnounceTitle').value = '';
  document.getElementById('adminAnnounceBody').value = '';
  showToast('Platform announcement broadcasted');
}

async function loadAdminAuditLogs() {
  const container = document.getElementById('adminLogsContainer');
  const snap = await db.collection('admin_logs').orderBy('timestamp', 'desc').limit(40).get();
  const logs = [];
  snap.forEach(d => logs.push(d.data()));

  container.innerHTML = logs.map(l => `
    <div class="surface-card-static p-2">
      <span class="text-app-secondary">[${l.action}]</span>
      <span class="text-app-muted">${l.adminId ? l.adminId.slice(0,6) : 'SYS'}</span>: ${escapeHtml(l.title || l.targetUid || l.bookId || '')}
    </div>
  `).join('');
}

// ────────────────────────────────────────────────────────
// PUBLISHING STUDIO CONTROLLER
// ────────────────────────────────────────────────────────
function selectContentFormat(fmt) {
  APP_STATE.selectedFormat = fmt;
  document.getElementById('selectedFormatInput').value = fmt;
  document.querySelectorAll('.format-btn').forEach(btn => {
    const isMatch = btn.dataset.fmt === fmt;
    btn.style.borderColor = isMatch ? '#9270FF' : '#262638';
    btn.style.background = isMatch ? '#1B1B27' : '#14141D';
  });
}

function handleCoverFileSelected(input) {
  const file = input.files[0];
  if (!file) return;
  document.getElementById('coverUploadImg').src = URL.createObjectURL(file);
  document.getElementById('coverUploadPreview').classList.remove('hidden');
  document.getElementById('coverUploadPlaceholder').classList.add('hidden');
  updateDraftStorageEstimate();
}

function addEditionRow() {
  const container = document.getElementById('editionRows');
  if (!container) return;
  const idx = APP_STATE.publishEditions.length;
  APP_STATE.publishEditions.push({ language: 'English', file: null });

  const div = document.createElement('div');
  div.id = `pubEditionRow-${idx}`;
  div.className = 'surface-card p-3 space-y-2';
  div.innerHTML = `
    <div class="flex items-center justify-between">
      <span class="text-xs font-semibold text-white">Edition #${idx + 1}</span>
      ${idx > 0 ? `<button type="button" onclick="removeEditionRow(${idx})" class="text-xs text-red-400 hover:text-red-300">Remove</button>` : ''}
    </div>
    <select id="edLangSelect-${idx}" class="w-full px-2.5 py-1.5 text-xs" onchange="APP_STATE.publishEditions[${idx}].language = this.value">
      <option value="English">English</option>
      <option value="Spanish">Spanish</option>
      <option value="French">French</option>
      <option value="Arabic">Arabic</option>
      <option value="Japanese">Japanese</option>
      <option value="Korean">Korean</option>
      <option value="German">German</option>
    </select>
    <div onclick="document.getElementById('edFileInput-${idx}').click()" class="surface-card p-2.5 flex items-center gap-2 cursor-pointer border-dashed">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4 text-app-primary"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
      <span id="edFileLabel-${idx}" class="text-xs text-app-muted truncate flex-1">Select Manuscript PDF</span>
    </div>
    <input type="file" id="edFileInput-${idx}" accept=".pdf" class="hidden" onchange="handleEditionPdfSelected(this, ${idx})">
  `;
  container.appendChild(div);
}

function handleEditionPdfSelected(input, idx) {
  const file = input.files[0];
  if (!file) return;
  APP_STATE.publishEditions[idx].file = file;
  document.getElementById(`edFileLabel-${idx}`).textContent = `${file.name} (${(file.size / (1024*1024)).toFixed(1)} MB)`;
  updateDraftStorageEstimate();
}

function removeEditionRow(idx) {
  APP_STATE.publishEditions.splice(idx, 1);
  document.getElementById(`pubEditionRow-${idx}`)?.remove();
  updateDraftStorageEstimate();
}

function togglePublishGenre(btn, genre) {
  const idx = APP_STATE.selectedGenres.indexOf(genre);
  if (idx > -1) {
    APP_STATE.selectedGenres.splice(idx, 1);
    btn.style.background = 'rgba(146, 112, 255, 0.08)';
    btn.style.color = '#B9A4FF';
  } else {
    if (APP_STATE.selectedGenres.length >= 4) { showToast('Maximum 4 genres permitted'); return; }
    APP_STATE.selectedGenres.push(genre);
    btn.style.background = '#9270FF';
    btn.style.color = '#0B0B10';
  }
}

async function uploadMediaFile(file, path) {
  try {
    const snap = await storage.ref(path).put(file);
    return await snap.ref.getDownloadURL();
  } catch(err) {
    if (file.type.startsWith('image/') && IMGBB_KEY) {
      const fd = new FormData();
      fd.append('image', file);
      const res = await fetch(`https://api.imgbb.com/1/upload?key=${IMGBB_KEY}`, { method:'POST', body: fd });
      const data = await res.json();
      if (data && data.success) return data.data.url;
    }
    throw err;
  }
}

async function handlePublishSubmit(event, forceStatus) {
  if (event) event.preventDefault();
  if (!APP_STATE.user) { openAuthModal(); return; }

  const title = document.getElementById('publishTitleInput').value.trim();
  const desc = document.getElementById('publishSynopsisInput').value.trim();
  const status = forceStatus || document.getElementById('publishStatusSelect').value;
  const visibility = document.getElementById('publishVisibilitySelect').value;
  const coverFile = document.getElementById('coverFileInput').files[0];

  if (!title || !desc) { showToast('Please enter title and synopsis'); return; }

  setButtonLoading('publishSubmitBtn', true, 'Uploading...');

  try {
    const bookId = db.collection('books').doc().id;
    let coverUrl = '';
    let coverSize = coverFile ? coverFile.size : 0;

    if (coverFile) {
      coverUrl = await uploadMediaFile(coverFile, `covers/${bookId}/${Date.now()}.jpg`);
    }

    const languages = [];
    for (let i = 0; i < APP_STATE.publishEditions.length; i++) {
      const ed = APP_STATE.publishEditions[i];
      let fileUrl = '';
      if (ed.file) {
        fileUrl = await uploadMediaFile(ed.file, `books/${bookId}/pdfs/${ed.language}_${Date.now()}.pdf`);
      }
      languages.push({
        language: ed.language,
        fileUrl: fileUrl,
        fileName: ed.file ? ed.file.name : '',
        fileSize: ed.file ? ed.file.size : 0,
        uploadedAt: new Date().toISOString()
      });
    }

    await db.collection('books').doc(bookId).set({
      id: bookId,
      title: title,
      description: desc,
      contentType: APP_STATE.selectedFormat,
      genres: APP_STATE.selectedGenres,
      coverUrl: coverUrl,
      coverSize: coverSize,
      status: status,
      visibility: visibility,
      publishStatus: status === 'draft' ? 'draft' : 'published',
      languages: languages,
      authorId: APP_STATE.user.uid,
      authorName: APP_STATE.profile?.displayName || APP_STATE.user.email.split('@')[0],
      authorPhoto: APP_STATE.profile?.photoURL || '',
      viewCount: 0,
      likeCount: 0,
      bookmarkCount: 0,
      avgRating: 0,
      createdAt: firebase.firestore.FieldValue.serverTimestamp(),
      updatedAt: firebase.firestore.FieldValue.serverTimestamp()
    });

    showToast('Publication published live to NOVELIX');
    resetPublishForm();
    switchPage('home');
  } catch(err) {
    showToast(`Publication failed: ${err.message}`);
  } finally {
    setButtonLoading('publishSubmitBtn', false, 'Publish Work');
  }
}

function resetPublishForm() {
  document.getElementById('publishingForm').reset();
  document.getElementById('coverUploadPreview').classList.add('hidden');
  document.getElementById('coverUploadPlaceholder').classList.remove('hidden');
  document.getElementById('editionRows').innerHTML = '';
  APP_STATE.publishEditions = [];
  APP_STATE.selectedGenres = [];
  addEditionRow();
}

function updatePublishAccessState() {
  const isAuth = !!APP_STATE.user;
  document.getElementById('publishAuthGuard')?.classList.toggle('hidden', isAuth);
  document.getElementById('publishFormContainer')?.classList.toggle('hidden', !isAuth);
  if (isAuth) recalculateStorageQuota();
}

// ────────────────────────────────────────────────────────
// REALTIME FIRESTORE DATA FEEDS
// ────────────────────────────────────────────────────────
function startFirestoreBooksFeed() {
  if (!db) return;
  if (APP_STATE.realtimeBooksUnsub) APP_STATE.realtimeBooksUnsub();

  APP_STATE.realtimeBooksUnsub = db.collection('books')
    .where('visibility', '==', 'public')
    .where('publishStatus', '==', 'published')
    .orderBy('createdAt', 'desc')
    .limit(60)
    .onSnapshot((snapshot) => {
      document.getElementById('headerLivePill')?.classList.remove('hidden');
      const books = [];
      snapshot.forEach(doc => books.push({ id: doc.id, ...doc.data() }));
      APP_STATE.allBooks = books;
      renderHomeShelfViews();
      if (APP_STATE.activePage === 'explore') renderExploreGridView();
      recalculateStorageQuota();
    }, (err) => {
      loadBooksFallbackFeed();
    });
}

async function loadBooksFallbackFeed() {
  try {
    const snap = await db.collection('books').where('publishStatus', '==', 'published').limit(30).get();
    const books = [];
    snap.forEach(doc => books.push({ id: doc.id, ...doc.data() }));
    APP_STATE.allBooks = books;
    renderHomeShelfViews();
  } catch(e) {
    document.getElementById('homeEmptyState')?.classList.remove('hidden');
  }
}

function renderHomeShelfViews() {
  const books = APP_STATE.allBooks;
  const emptyState = document.getElementById('homeEmptyState');
  const grid = document.getElementById('homeBooksGrid');
  const carousel = document.getElementById('featuredCarousel');

  if (!books.length) {
    emptyState?.classList.remove('hidden');
    grid.innerHTML = '';
    carousel.innerHTML = '';
    document.getElementById('featuredShelf')?.classList.add('hidden');
    document.getElementById('shelfGridCount').textContent = '0 works';
    return;
  }

  emptyState?.classList.add('hidden');
  document.getElementById('featuredShelf')?.classList.remove('hidden');

  // Featured Carousel
  const featured = [...books].sort((a,b) => (b.viewCount||0) - (a.viewCount||0)).slice(0, 5);
  carousel.innerHTML = featured.map(b => renderEditorialFeaturedCard(b)).join('');

  // Main Trending Grid
  renderHomeCategoryGrid();

  // Continue Reading (if user is logged in)
  if (APP_STATE.user) loadContinueReadingShelf();
}

function renderEditorialFeaturedCard(book) {
  const cover = book.coverUrl || '';
  return `
    <div onclick="openBookDetail('${escapeHtml(book.id)}')" class="surface-card flex-shrink-0 w-64 p-3 cursor-pointer group relative overflow-hidden">
      <div class="h-40 rounded-xl overflow-hidden bg-app-surface mb-2.5 relative">
        ${cover ? `<img src="${escapeHtml(cover)}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300">` : '<div class="w-full h-full flex items-center justify-center font-display font-bold text-2xl text-app-muted">NOVELIX</div>'}
        <span class="absolute top-2 left-2 pill-tag text-[9px] uppercase tracking-wider backdrop-blur-md bg-black/60">${formatLabel(book.contentType)}</span>
      </div>
      <h4 class="font-display font-bold text-xs text-white truncate mb-0.5">${escapeHtml(book.title)}</h4>
      <p class="text-[11px] text-app-muted truncate mb-2">${escapeHtml(book.authorName || 'Author')}</p>
      <div class="flex items-center justify-between text-[10px] text-app-secondary">
        <span>★ ${book.avgRating ? book.avgRating.toFixed(1) : '4.8'}</span>
        <span>${formatCompactNum(book.viewCount || 0)} reads</span>
      </div>
    </div>
  `;
}

function renderBookCard(book) {
  const cover = book.coverUrl || '';
  return `
    <div onclick="openBookDetail('${escapeHtml(book.id)}')" class="surface-card p-2.5 cursor-pointer flex flex-col justify-between">
      <div>
        <div class="aspect-[2/3] rounded-xl overflow-hidden bg-app-surface mb-2 relative">
          ${cover ? `<img src="${escapeHtml(cover)}" class="w-full h-full object-cover">` : '<div class="w-full h-full flex items-center justify-center font-display text-sm text-app-muted">N</div>'}
          <span class="absolute top-1.5 left-1.5 pill-tag text-[8px] uppercase tracking-wider">${formatLabel(book.contentType)}</span>
        </div>
        <h4 class="font-display font-semibold text-xs text-white line-clamp-1 mb-0.5">${escapeHtml(book.title)}</h4>
        <p class="text-[10px] text-app-muted truncate mb-1.5">${escapeHtml(book.authorName || 'Author')}</p>
      </div>
      <div class="flex items-center justify-between text-[10px] text-app-secondary pt-1 border-t border-app-border/40">
        <span>★ ${book.avgRating ? book.avgRating.toFixed(1) : '4.8'}</span>
        <span>${formatCompactNum(book.viewCount || 0)}</span>
      </div>
    </div>
  `;
}

function renderHomeCategoryGrid() {
  let books = APP_STATE.allBooks;
  if (APP_STATE.activeCategory !== 'all') {
    books = books.filter(b => b.contentType === APP_STATE.activeCategory);
  }
  document.getElementById('shelfGridCount').textContent = `${books.length} work${books.length === 1 ? '' : 's'}`;
  const grid = document.getElementById('homeBooksGrid');
  if (!books.length) {
    grid.innerHTML = `<div class="col-span-2 text-center py-10 text-xs text-app-muted">No works in this category yet.</div>`;
    return;
  }
  grid.innerHTML = books.map(b => renderBookCard(b)).join('');
}

function filterCategory(cat) {
  APP_STATE.activeCategory = cat;
  document.querySelectorAll('.cat-pill').forEach(btn => {
    const isMatch = btn.dataset.cat === cat;
    btn.style.background = isMatch ? '#9270FF' : 'rgba(146, 112, 255, 0.08)';
    btn.style.color = isMatch ? '#0B0B10' : '#B9A4FF';
  });
  renderHomeCategoryGrid();
}

function handleHomeSearch(val) {
  const q = val.trim().toLowerCase();
  const grid = document.getElementById('homeBooksGrid');
  if (!q) { renderHomeCategoryGrid(); return; }
  const matches = APP_STATE.allBooks.filter(b => 
    (b.title && b.title.toLowerCase().includes(q)) ||
    (b.authorName && b.authorName.toLowerCase().includes(q)) ||
    (b.genres && b.genres.some(g => g.toLowerCase().includes(q)))
  );
  document.getElementById('shelfGridCount').textContent = `${matches.length} found`;
  if (!matches.length) {
    grid.innerHTML = `<div class="col-span-2 text-center py-10 text-xs text-app-muted">No publications matching "${escapeHtml(val)}"</div>`;
    return;
  }
  grid.innerHTML = matches.map(b => renderBookCard(b)).join('');
}

async function loadContinueReadingShelf() {
  if (!APP_STATE.user) return;
  const container = document.getElementById('continueReadingShelf');
  const list = document.getElementById('continueReadingList');
  const snap = await db.collection('users').doc(APP_STATE.user.uid).collection('reading_progress').orderBy('lastReadAt', 'desc').limit(2).get();
  
  if (snap.empty) { container.classList.add('hidden'); return; }
  container.classList.remove('hidden');

  const items = [];
  snap.forEach(d => items.push({ id: d.id, ...d.data() }));

  list.innerHTML = items.map(item => `
    <div onclick="openBookDetail('${escapeHtml(item.id)}')" class="surface-card p-3 flex items-center justify-between cursor-pointer">
      <div class="flex items-center gap-3 min-w-0">
        <div class="w-10 h-14 rounded-lg overflow-hidden bg-app-surface flex-shrink-0">
          ${item.coverUrl ? `<img src="${escapeHtml(item.coverUrl)}" class="w-full h-full object-cover">` : ''}
        </div>
        <div class="truncate">
          <h5 class="font-display font-semibold text-xs text-white truncate">${escapeHtml(item.title || 'Work')}</h5>
          <span class="text-[10px] text-app-muted">Page ${item.page || 1} • In Progress</span>
        </div>
      </div>
      <button class="btn-primary text-[11px] px-3 py-1">Resume</button>
    </div>
  `).join('');
}

// ────────────────────────────────────────────────────────
// EXPLORE VIEW
// ────────────────────────────────────────────────────────
function renderExploreGridView() {
  const genres = ['Fantasy', 'Sci-Fi', 'Mystery', 'Romance', 'Thriller', 'Adventure'];
  const genresBox = document.getElementById('exploreGenresGrid');
  genresBox.innerHTML = genres.map(g => `
    <div onclick="filterExploreGenre('${g}')" class="surface-card p-3 text-center cursor-pointer hover:border-app-primary">
      <span class="font-display font-semibold text-xs text-white">${g}</span>
    </div>
  `).join('');

  const grid = document.getElementById('exploreResultsGrid');
  grid.innerHTML = APP_STATE.allBooks.map(b => renderBookCard(b)).join('');
}

function filterExploreGenre(genre) {
  const grid = document.getElementById('exploreResultsGrid');
  const filtered = APP_STATE.allBooks.filter(b => b.genres && b.genres.includes(genre));
  if (!filtered.length) {
    grid.innerHTML = `<div class="col-span-2 text-center py-10 text-xs text-app-muted">No works categorized under ${genre} yet.</div>`;
    return;
  }
  grid.innerHTML = filtered.map(b => renderBookCard(b)).join('');
}

// ────────────────────────────────────────────────────────
// LIBRARY & BOOKMARKS
// ────────────────────────────────────────────────────────
async function loadLibraryContent() {
  const isAuth = !!APP_STATE.user;
  document.getElementById('libraryContent')?.classList.toggle('hidden', !isAuth);
  document.getElementById('libraryAuthGuard')?.classList.toggle('hidden', isAuth);
  if (isAuth) renderLibrarySubtab('reading');
}

function switchLibTab(tab) {
  document.querySelectorAll('.lib-subtab').forEach(b => {
    const isMatch = b.dataset.tab === tab;
    b.style.background = isMatch ? '#9270FF' : 'rgba(146, 112, 255, 0.08)';
    b.style.color = isMatch ? '#0B0B10' : '#B9A4FF';
  });
  renderLibrarySubtab(tab);
}

async function renderLibrarySubtab(tab) {
  const list = document.getElementById('libraryList');
  const empty = document.getElementById('libraryEmpty');
  list.innerHTML = `<div class="skeleton-box h-16 mb-2"></div>`;

  if (tab === 'reading') {
    const snap = await db.collection('users').doc(APP_STATE.user.uid).collection('reading_progress').orderBy('lastReadAt', 'desc').get();
    if (snap.empty) { list.innerHTML = ''; empty?.classList.remove('hidden'); return; }
    empty?.classList.add('hidden');
    const items = [];
    snap.forEach(d => items.push({ id: d.id, ...d.data() }));
    list.innerHTML = items.map(item => `
      <div onclick="openBookDetail('${escapeHtml(item.id)}')" class="surface-card p-3 flex items-center justify-between cursor-pointer">
        <div class="flex items-center gap-3 min-w-0">
          <div class="w-10 h-14 rounded-lg overflow-hidden bg-app-surface flex-shrink-0">
            ${item.coverUrl ? `<img src="${escapeHtml(item.coverUrl)}" class="w-full h-full object-cover">` : ''}
          </div>
          <div class="truncate">
            <h5 class="font-display font-semibold text-xs text-white truncate">${escapeHtml(item.title || 'Work')}</h5>
            <span class="text-[10px] text-app-muted">Page ${item.page || 1} • In Progress</span>
          </div>
        </div>
        <button class="btn-primary text-[11px] px-3 py-1">Resume</button>
      </div>
    `).join('');
  } else if (tab === 'bookmarks') {
    const snap = await db.collection('users').doc(APP_STATE.user.uid).collection('bookmarks').orderBy('createdAt', 'desc').get();
    if (snap.empty) { list.innerHTML = ''; empty?.classList.remove('hidden'); return; }
    empty?.classList.add('hidden');
    const items = [];
    snap.forEach(d => items.push({ id: d.id, ...d.data() }));
    list.innerHTML = items.map(bk => `
      <div onclick="openBookDetail('${escapeHtml(bk.id)}')" class="surface-card p-3 flex items-center justify-between cursor-pointer">
        <div class="flex items-center gap-3 min-w-0">
          <div class="w-10 h-14 rounded-lg overflow-hidden bg-app-surface flex-shrink-0">
            ${bk.coverUrl ? `<img src="${escapeHtml(bk.coverUrl)}" class="w-full h-full object-cover">` : ''}
          </div>
          <div class="truncate">
            <h5 class="font-display font-semibold text-xs text-white truncate">${escapeHtml(bk.title || 'Work')}</h5>
            <span class="text-[10px] text-app-muted">${formatLabel(bk.contentType)}</span>
          </div>
        </div>
        <button onclick="event.stopPropagation(); removeBookmarkItem('${bk.id}')" class="text-xs text-app-muted hover:text-white p-2">✕</button>
      </div>
    `).join('');
  }
}

async function removeBookmarkItem(bookId) {
  if (!APP_STATE.user) return;
  await db.collection('users').doc(APP_STATE.user.uid).collection('bookmarks').doc(bookId).delete();
  renderLibrarySubtab('bookmarks');
}

// ────────────────────────────────────────────────────────
// PROFILE VIEW
// ────────────────────────────────────────────────────────
function loadProfileContent() {
  const isAuth = !!APP_STATE.user;
  document.getElementById('profileMainContent')?.classList.toggle('hidden', !isAuth);
  document.getElementById('profileAuthGuard')?.classList.toggle('hidden', isAuth);

  if (isAuth) {
    const p = APP_STATE.profile || {};
    document.getElementById('profileNameDisplay').textContent = p.displayName || APP_STATE.user.email.split('@')[0];
    document.getElementById('profileHandleDisplay').textContent = `@${p.handle || APP_STATE.user.email.split('@')[0]}`;
    document.getElementById('profileEmailDisplay').textContent = APP_STATE.user.email;
    document.getElementById('profileBioDisplay').textContent = p.bio || 'Author & Reader on NOVELIX.';

    const img = document.getElementById('profileAvatarPhoto');
    const letter = document.getElementById('profileAvatarLetter');
    if (p.photoURL) {
      img.src = p.photoURL;
      img.classList.remove('hidden');
      letter.classList.add('hidden');
    } else {
      letter.textContent = (p.displayName || APP_STATE.user.email || 'U')[0].toUpperCase();
      img.classList.add('hidden');
      letter.classList.remove('hidden');
    }

    document.getElementById('aboutBioText').textContent = p.bio || 'No bio entered yet.';
    document.getElementById('aboutJoinedDate').textContent = p.createdAt ? new Date(p.createdAt.seconds * 1000).toLocaleDateString() : 'Active Member';
    document.getElementById('aboutCreatorStatus').textContent = p.creatorVerified ? 'Official Verified Creator' : 'Standard Reader';

    computeUserStats();
    switchProfileTab('works');
  }
}

async function computeUserStats() {
  if (!APP_STATE.user) return;
  const myWorks = APP_STATE.allBooks.filter(b => b.authorId === APP_STATE.user.uid);
  const reads = myWorks.reduce((s, b) => s + (b.viewCount || 0), 0);
  const chapters = myWorks.reduce((s, b) => s + (Array.isArray(b.languages) ? b.languages.length : 1), 0);

  document.getElementById('statPublishedCount').textContent = myWorks.length;
  document.getElementById('statChaptersCount').textContent = chapters;
  document.getElementById('statTotalViews').textContent = formatCompactNum(reads);
}

function switchProfileTab(tabId) {
  document.querySelectorAll('.prof-tab').forEach(b => {
    const isMatch = b.dataset.tab === tabId;
    b.style.background = isMatch ? '#9270FF' : 'rgba(146, 112, 255, 0.08)';
    b.style.color = isMatch ? '#0B0B10' : '#B9A4FF';
  });

  document.getElementById('profileTabContentWorks').classList.toggle('hidden', tabId !== 'works');
  document.getElementById('profileTabContentLibrary').classList.toggle('hidden', tabId !== 'library');
  document.getElementById('profileTabContentReviews').classList.toggle('hidden', tabId !== 'reviews');
  document.getElementById('profileTabContentAbout').classList.toggle('hidden', tabId !== 'about');

  if (tabId === 'works') renderProfileWorksTab();
}

function renderProfileWorksTab() {
  const list = document.getElementById('profileTabContentWorks');
  const myWorks = APP_STATE.allBooks.filter(b => b.authorId === APP_STATE.user.uid);
  if (!myWorks.length) {
    list.innerHTML = `<div class="surface-card-static p-6 text-center text-xs text-app-muted">No publications authored under this account yet.</div>`;
    return;
  }

  list.innerHTML = myWorks.map(b => `
    <div class="surface-card p-3 flex items-center justify-between">
      <div class="flex items-center gap-3 min-w-0">
        <div class="w-10 h-14 rounded-lg overflow-hidden bg-app-surface flex-shrink-0">
          ${b.coverUrl ? `<img src="${escapeHtml(b.coverUrl)}" class="w-full h-full object-cover">` : ''}
        </div>
        <div class="truncate">
          <h5 class="font-display font-semibold text-xs text-white truncate">${escapeHtml(b.title)}</h5>
          <span class="text-[10px] text-app-muted">${formatLabel(b.contentType)} • ${formatCompactNum(b.viewCount || 0)} reads</span>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button onclick="openBookDetail('${b.id}')" class="btn-secondary text-[11px] px-2.5 py-1">View</button>
        <button onclick="deleteAuthorPublication('${b.id}')" class="text-xs text-red-400 p-1 hover:text-red-300">✕</button>
      </div>
    </div>
  `).join('');
}

async function deleteAuthorPublication(id) {
  if (!confirm('Permanently delete this publication?')) return;
  try {
    await db.collection('books').doc(id).delete();
    showToast('Publication deleted');
    recalculateStorageQuota();
  } catch(e) {
    showToast(e.message);
  }
}

// ────────────────────────────────────────────────────────
// BOOK DETAIL & DUAL-ENGINE READER (PDF.JS & MANHWA)
// ────────────────────────────────────────────────────────
function openBookDetail(bookId) {
  const book = APP_STATE.allBooks.find(b => b.id === bookId);
  if (!book) return;
  APP_STATE.selectedBook = book;

  document.getElementById('detailTitle').textContent = book.title || 'Untitled';
  document.getElementById('detailAuthor').textContent = book.authorName || 'Author';
  document.getElementById('detailSynopsis').textContent = book.description || 'No synopsis provided.';
  document.getElementById('detailFormatTag').textContent = formatLabel(book.contentType);
  document.getElementById('detailReadsCount').textContent = `${formatCompactNum(book.viewCount || 0)} reads`;
  document.getElementById('detailRating').textContent = `★ ${book.avgRating ? book.avgRating.toFixed(1) : '4.8'}`;

  const coverImg = document.getElementById('detailCoverImg');
  if (book.coverUrl) { coverImg.src = book.coverUrl; coverImg.classList.remove('hidden'); }
  else coverImg.classList.add('hidden');

  const edList = document.getElementById('detailEditionsList');
  const eds = book.languages || [];
  if (!eds.length) {
    edList.innerHTML = `<p class="text-xs text-app-muted">Standard Edition</p>`;
    APP_STATE.selectedEdition = null;
  } else {
    APP_STATE.selectedEdition = eds[0];
    edList.innerHTML = eds.map((e, idx) => `
      <div onclick="selectEditionToRead(${idx})" class="surface-card p-2.5 flex items-center justify-between cursor-pointer ${idx===0 ? 'border-app-primary' : ''}">
        <span class="text-xs font-medium text-white">${escapeHtml(e.language)} Edition</span>
        <span class="text-[10px] text-app-secondary">PDF</span>
      </div>
    `).join('');
  }

  // Increment view count in Firestore
  db.collection('books').doc(bookId).update({
    viewCount: firebase.firestore.FieldValue.increment(1)
  }).catch(() => {});

  document.getElementById('bookDetailModal').classList.add('open');
}

function selectEditionToRead(idx) {
  if (!APP_STATE.selectedBook || !APP_STATE.selectedBook.languages) return;
  APP_STATE.selectedEdition = APP_STATE.selectedBook.languages[idx];
  showToast(`Selected ${APP_STATE.selectedEdition.language} Edition`);
}

function closeBookDetailModal() { document.getElementById('bookDetailModal').classList.remove('open'); }

async function toggleDetailBookmark() {
  if (!APP_STATE.user) { openAuthModal(); return; }
  const b = APP_STATE.selectedBook;
  if (!b) return;
  const ref = db.collection('users').doc(APP_STATE.user.uid).collection('bookmarks').doc(b.id);
  const doc = await ref.get();
  if (doc.exists) {
    await ref.delete();
    showToast('Removed from bookmarks');
  } else {
    await ref.set({
      id: b.id,
      title: b.title,
      coverUrl: b.coverUrl || '',
      contentType: b.contentType,
      createdAt: firebase.firestore.FieldValue.serverTimestamp()
    });
    showToast('Saved to library bookmarks');
  }
}

async function launchActiveReader() {
  const book = APP_STATE.selectedBook;
  if (!book) return;
  closeBookDetailModal();
  document.getElementById('readerModal').classList.add('open');
  document.getElementById('readerTitle').textContent = book.title;

  const edition = APP_STATE.selectedEdition || (book.languages && book.languages[0]);
  const pdfUrl = edition ? edition.fileUrl : null;

  if (pdfUrl && window.pdfjsLib) {
    document.getElementById('pdfRenderCanvas').classList.remove('hidden');
    document.getElementById('manhwaScrollContainer').classList.add('hidden');
    loadPdfReader(pdfUrl);
  } else {
    // Manhwa or text reader fallback
    document.getElementById('pdfRenderCanvas').classList.add('hidden');
    document.getElementById('manhwaScrollContainer').classList.remove('hidden');
    renderManhwaReaderFallback(book);
  }

  // Track reading progress in Firestore
  if (APP_STATE.user) {
    db.collection('users').doc(APP_STATE.user.uid).collection('reading_progress').doc(book.id).set({
      id: book.id,
      title: book.title,
      coverUrl: book.coverUrl || '',
      contentType: book.contentType,
      page: 1,
      lastReadAt: firebase.firestore.FieldValue.serverTimestamp()
    }, { merge: true });
  }
}

function closeReaderModal() { document.getElementById('readerModal').classList.remove('open'); }

async function loadPdfReader(url) {
  try {
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
    const loadingTask = pdfjsLib.getDocument(url);
    APP_STATE.pdfDocument = await loadingTask.promise;
    APP_STATE.pdfPageNumber = 1;
    renderPdfPage(APP_STATE.pdfPageNumber);
  } catch(e) {
    showToast(`PDF load error: ${e.message}`);
  }
}

async function renderPdfPage(num) {
  if (!APP_STATE.pdfDocument || APP_STATE.pdfIsRendering) return;
  APP_STATE.pdfIsRendering = true;
  const page = await APP_STATE.pdfDocument.getPage(num);
  const viewport = page.getViewport({ scale: APP_STATE.pdfZoomScale });

  const canvas = document.getElementById('pdfRenderCanvas');
  const ctx = canvas.getContext('2d');
  canvas.height = viewport.height;
  canvas.width = viewport.width;

  await page.render({ canvasContext: ctx, viewport: viewport }).promise;
  APP_STATE.pdfIsRendering = false;
  document.getElementById('readerPageIndicator').textContent = `${num} / ${APP_STATE.pdfDocument.numPages}`;
}

function changeReaderPage(delta) {
  if (!APP_STATE.pdfDocument) return;
  const newPage = APP_STATE.pdfPageNumber + delta;
  if (newPage >= 1 && newPage <= APP_STATE.pdfDocument.numPages) {
    APP_STATE.pdfPageNumber = newPage;
    renderPdfPage(newPage);
  }
}

function zoomReader(delta) {
  APP_STATE.pdfZoomScale = Math.max(0.8, Math.min(2.5, APP_STATE.pdfZoomScale + delta));
  if (APP_STATE.pdfDocument) renderPdfPage(APP_STATE.pdfPageNumber);
}

function renderManhwaReaderFallback(book) {
  const container = document.getElementById('manhwaScrollContainer');
  container.innerHTML = `
    <div class="surface-card p-6 text-center space-y-3">
      <h3 class="font-display font-bold text-base text-white">${escapeHtml(book.title)}</h3>
      <p class="text-xs text-app-muted leading-relaxed">${escapeHtml(book.description)}</p>
      <div class="py-8 text-xs text-app-secondary">End of manuscript preview.</div>
    </div>
  `;
}

// ────────────────────────────────────────────────────────
// NAVIGATION ROUTER
// ────────────────────────────────────────────────────────
function switchPage(pageId) {
  document.querySelectorAll('.app-page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => { n.style.color = '#9693A4'; });

  const targetPage = document.getElementById(`page-${pageId}`);
  if (targetPage) targetPage.classList.add('active');

  const targetNav = document.getElementById(`nav-${pageId}`);
  if (targetNav) targetNav.style.color = '#9270FF';

  APP_STATE.activePage = pageId;

  if (pageId === 'library') loadLibraryContent();
  if (pageId === 'profile') loadProfileContent();
  if (pageId === 'publish') updatePublishAccessState();
  if (pageId === 'explore') renderExploreGridView();

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ────────────────────────────────────────────────────────
// UTILITIES
// ────────────────────────────────────────────────────────
function showToast(msg) {
  const bar = document.getElementById('toastBar');
  const txt = document.getElementById('toastText');
  txt.textContent = msg;
  bar.classList.add('show');
  clearTimeout(window._toastTimer);
  window._toastTimer = setTimeout(() => bar.classList.remove('show'), 3200);
}

function setButtonLoading(id, isLoading, text) {
  const btn = document.getElementById(id);
  if (!btn) return;
  btn.disabled = isLoading;
  btn.textContent = text;
}

function showInitialHomeSkeletons() {
  const grid = document.getElementById('homeBooksGrid');
  if (grid) {
    grid.innerHTML = `
      <div class="skeleton-box aspect-[2/3]"></div>
      <div class="skeleton-box aspect-[2/3]"></div>
    `;
  }
}

function setupOnlineOfflineListeners() {
  window.addEventListener('online', () => showToast('Reconnected — cloud synced'));
  window.addEventListener('offline', () => showToast('Offline mode — reading from cache'));
}

function formatLabel(fmt) {
  const map = {
    book: 'Book', novel: 'Novel', manga: 'Manga', manhwa: 'Manhwa',
    comic: 'Comic', short_story: 'Fiction', series: 'Series', educational: 'Educational'
  };
  return map[fmt] || fmt || 'Book';
}

function formatCompactNum(n) {
  if (n >= 1000000) return (n/1000000).toFixed(1) + 'M';
  if (n >= 1000) return (n/1000).toFixed(1) + 'K';
  return String(n);
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');
}

</script>
</body>
</html>"""

with open("out/index.html", "w", encoding="utf-8") as f:
    f.write(HTML_CONTENT)
print("Regenerated out/index.html successfully")
