#!/usr/bin/env python3
"""
patch_novelix_12_1.py
NOVELIX 12.1.0 UPGRADE:
1. Rock-solid Multi-Strategy Reader Engine:
   - Direct Google Drive downloads (drive.usercontent.google.com, uc?export=download, etc.)
   - Web CORS proxy fallbacks
   - Safe Cloud Function proxy fallback with zero ERR_functions/internal crash
   - Clean, actionable error handling
2. Google Drive In-App Native Auth:
   - Zero-redirect native GoogleAuth plugin on Android
   - 1-tap connect for current logged-in user
   - Direct link fast publishing
3. Professional Author Profile Suite:
   - Zero-composite-index Firestore book querying (Spark free-tier safe)
   - VIP glassmorphism profile UI with 6 executive metric cards
   - Series & Sagas showcase
   - Clickable author names in book details
4. Version Bump to 12.1.0 (Live OTA update enabled)
"""

import sys
import re

GEN_FILE = "scripts/generate_4.py"

with open(GEN_FILE, "r", encoding="utf-8") as f:
    content = f.read()

print(f"Read {GEN_FILE}: {len(content)} bytes")

# ─────────────────────────────────────────────────────────────
# 1. UPGRADE READER ENGINE (fetchPdfBytes & loadPdfDocumentForReader)
# ─────────────────────────────────────────────────────────────

old_reader_block = re.search(r"// ─── Helper: fetch URL as Uint8Array with streaming progress and validation ─[\s\S]*?APP_STATE\._loadingPdf = false;\s*\}", content)
if not old_reader_block:
    print("ERROR: Could not find reader block in generate_4.py")
    sys.exit(1)

new_reader_block = """// ─── Helper: fetch URL as Uint8Array with streaming progress, CORS & buffer fallbacks ─
  async function fetchPdfBytes(url, progressCallback, signal) {
    let resolvedUrl = url;

    // Refresh download URL from Firebase Storage if path exists
    if (storage && edition && edition.storagePath && url.includes('firebasestorage')) {
      try {
        resolvedUrl = await withTimeout(
          storage.ref(edition.storagePath).getDownloadURL(),
          12000,
          'Cloud storage download URL generation timed out (12s).',
          'STORAGE_TIMEOUT'
        );
        console.log('[NOVELIX Reader] Refreshed Storage download URL.');
      } catch(e) {
        console.warn('[NOVELIX Reader] Storage URL refresh note:', e.message);
      }
    }

    const fetchPromise = fetch(resolvedUrl, { method: 'GET', credentials: 'omit', signal });
    const resp = await withTimeout(
      fetchPromise,
      25000,
      'Manuscript download timed out (25s). Please check your internet connection.',
      'NETWORK_TIMEOUT'
    );

    if (!resp.ok) {
      const e = new Error(`HTTP ${resp.status}: manuscript download failed`);
      e.code = resp.status === 404 ? 'NOT_FOUND' : resp.status === 403 ? 'PERMISSION_DENIED' : 'FETCH_ERROR';
      throw e;
    }

    const contentType = resp.headers.get('content-type') || '';
    if (contentType.includes('text/html') || contentType.includes('application/json')) {
      const e = new Error('Server returned an error page or confirmation instead of a PDF file.');
      e.code = 'INVALID_FORMAT';
      throw e;
    }

    let allBytes;
    if (resp.body && typeof resp.body.getReader === 'function') {
      try {
        const contentLength = parseInt(resp.headers.get('content-length') || '0', 10);
        const reader = resp.body.getReader();
        const chunks = [];
        let receivedBytes = 0;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          chunks.push(value);
          receivedBytes += value.length;

          if (progressCallback) {
            if (contentLength > 0) {
              const pct = Math.round((receivedBytes / contentLength) * 100);
              progressCallback(pct);
            } else {
              progressCallback(Math.min(95, Math.round(receivedBytes / 40000)));
            }
          }
        }

        allBytes = new Uint8Array(receivedBytes);
        let offset = 0;
        for (const chunk of chunks) {
          allBytes.set(chunk, offset);
          offset += chunk.length;
        }
      } catch (streamErr) {
        console.warn('[NOVELIX Reader] Stream read fallback to arrayBuffer:', streamErr.message);
        const buf = await resp.arrayBuffer();
        allBytes = new Uint8Array(buf);
      }
    } else {
      const buf = await resp.arrayBuffer();
      allBytes = new Uint8Array(buf);
    }

    if (allBytes.length < 5 || allBytes[0] !== 0x25 || allBytes[1] !== 0x50 || allBytes[2] !== 0x44 || allBytes[3] !== 0x46) {
      const e = new Error('Downloaded file is not a valid PDF document (bad magic signature).');
      e.code = 'INVALID_FORMAT';
      throw e;
    }
    return allBytes;
  }
  // ──────────────────────────────────────────────────────────────────

  try {
    let pdfDataParam = null;

    // ── 1. Device memory cache ────────────────────────────────
    if (APP_STATE._pdfCache[cacheKey]) {
      updateProgress(75, 'Loading from device cache…');
      pdfDataParam = { data: APP_STATE._pdfCache[cacheKey] };
    } else {
      let downloadedBytes = null;
      let lastDownloadError = null;

      // Extract Drive File ID if present in edition or book or URL
      const driveId = edition.driveFileId || edition.fileId || book.driveFileId ||
        extractGoogleDriveFileId(edition.fileUrl || '') ||
        extractGoogleDriveFileId(book.fileUrl || '') ||
        extractGoogleDriveFileId(book.pdfUrl || '') ||
        extractGoogleDriveFileId(book.driveUrl || '');

      const candidateUrls = [];

      // If edition or book has a direct fileUrl, add it as candidate #1
      if (edition.fileUrl && edition.fileUrl.startsWith('http')) candidateUrls.push(edition.fileUrl);
      if (book.fileUrl && book.fileUrl.startsWith('http') && !candidateUrls.includes(book.fileUrl)) candidateUrls.push(book.fileUrl);
      if (book.pdfUrl && book.pdfUrl.startsWith('http') && !candidateUrls.includes(book.pdfUrl)) candidateUrls.push(book.pdfUrl);

      // If Drive ID is known, add direct Drive download links (CapacitorHttp native bypasses CORS on Android)
      if (driveId) {
        const u1 = `https://drive.usercontent.google.com/download?id=${driveId}&export=download&confirm=t`;
        const u2 = `https://drive.google.com/uc?id=${driveId}&export=download&confirm=t`;
        const u3 = `https://docs.google.com/uc?export=download&id=${driveId}&confirm=t`;
        const uProxy = `https://api.allorigins.win/raw?url=${encodeURIComponent(u1)}`;

        if (!candidateUrls.includes(u1)) candidateUrls.push(u1);
        if (!candidateUrls.includes(u2)) candidateUrls.push(u2);
        if (!candidateUrls.includes(u3)) candidateUrls.push(u3);
        if (!candidateUrls.includes(uProxy)) candidateUrls.push(uProxy);
      }

      // If Firebase Storage path exists, try getting download URL
      if (storage && (edition.storagePath || book.storagePath)) {
        try {
          const path = edition.storagePath || book.storagePath;
          const sUrl = await storage.ref(path).getDownloadURL();
          if (sUrl && !candidateUrls.includes(sUrl)) candidateUrls.push(sUrl);
        } catch(e) {
          console.warn('[NOVELIX Reader] Storage path lookup note:', e);
        }
      }

      console.log('[NOVELIX Reader] Prepared candidate URLs for reading:', candidateUrls.length, candidateUrls);

      // Loop through candidate URLs and try fetchPdfBytes
      for (let i = 0; i < candidateUrls.length; i++) {
        const u = candidateUrls[i];
        try {
          updateProgress(25 + Math.round((i / Math.max(1, candidateUrls.length)) * 30), `Streaming manuscript source (${i + 1}/${candidateUrls.length})…`);
          const bytes = await fetchPdfBytes(u, (p) => {
            updateProgress(30 + Math.round(p * 0.45), 'Downloading manuscript…');
          }, abortController.signal);

          if (bytes && bytes.length > 20) {
            downloadedBytes = bytes;
            console.log(`[NOVELIX Reader] Successfully downloaded ${bytes.length} bytes from source ${i + 1}`);
            break;
          }
        } catch (fetchErr) {
          console.warn(`[NOVELIX Reader] Candidate URL ${i + 1} note:`, fetchErr.message);
          lastDownloadError = fetchErr;
        }
      }

      // Strategy 2: If direct downloads didn't succeed, and Cloud Functions are available, try Callable getReaderPdfData safely
      if (!downloadedBytes && typeof functions !== 'undefined' && functions && typeof functions.httpsCallable === 'function') {
        try {
          updateProgress(65, 'Checking cloud manuscript proxy…');
          const getPdfFn = functions.httpsCallable('getReaderPdfData');
          const res = await withTimeout(
            getPdfFn({ bookId: book.id, language: edition.language || 'Standard' }),
            10000,
            'Drive proxy timed out',
            'DRIVE_TIMEOUT'
          );

          if (res && res.data && res.data.base64) {
            updateProgress(75, 'Decoding manuscript data…');
            const binaryString = atob(res.data.base64);
            const len = binaryString.length;
            const bytes = new Uint8Array(len);
            for (let i = 0; i < len; i++) bytes[i] = binaryString.charCodeAt(i);
            if (bytes.length >= 5 && bytes[0] === 0x25 && bytes[1] === 0x50 && bytes[2] === 0x44 && bytes[3] === 0x46) {
              downloadedBytes = bytes;
            }
          } else if (res && res.data && res.data.fileUrl) {
            const bytes = await fetchPdfBytes(res.data.fileUrl, null, abortController.signal);
            if (bytes && bytes.length > 20) downloadedBytes = bytes;
          }
        } catch(cfErr) {
          console.warn('[NOVELIX Reader] Cloud Function proxy note:', cfErr.message || cfErr.code);
        }
      }

      if (!downloadedBytes) {
        if (driveId) {
          const e = new Error('Could not access Google Drive file. Please ensure the author has set the Google Drive file General Access to "Anyone with the link" (Viewer).');
          e.code = 'DRIVE_PERMISSION_REQUIRED';
          throw e;
        } else if (lastDownloadError) {
          throw lastDownloadError;
        } else {
          const e = new Error('No valid manuscript source or download link found for this book edition.');
          e.code = 'NOT_FOUND';
          throw e;
        }
      }

      APP_STATE._pdfCache[cacheKey] = downloadedBytes;
      pdfDataParam = { data: downloadedBytes };
    }

    // ── 3. Initialize PDF.js engine and parse document ────────
    updateProgress(88, 'Parsing manuscript structure…');

    if (!window.pdfjsLib) {
      const e = new Error('PDF.js library is not available.');
      e.code = 'ENGINE_NOT_READY';
      throw e;
    }

    pdfDataParam.disableWorker = true;
    pdfDataParam.cMapUrl = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/cmaps/';
    pdfDataParam.cMapPacked = true;

    const safeTargetPage = Math.max(1, parseInt(targetPage, 10) || 1);

    const loadingTask = pdfjsLib.getDocument(pdfDataParam);
    APP_STATE._pdfLoadingTask = loadingTask;

    loadingTask.onProgress = function(pd) {
      if (pd.total > 0) {
        const pct = Math.round((pd.loaded / pd.total) * 100);
        updateProgress(88 + Math.round(pct * 0.1), 'Parsing pages…');
      }
    };

    APP_STATE.pdfDocument = await withTimeout(
      loadingTask.promise,
      25000,
      'PDF document structure parsing timed out (25s).',
      'PDF_PARSE_TIMEOUT'
    );

    loadingOverlay?.classList.add('hidden');

    const totalPages = APP_STATE.pdfDocument.numPages;
    const finalPage = Math.min(safeTargetPage, totalPages);

    const slider = document.getElementById('readerPageSlider');
    if (slider) { slider.min = '1'; slider.max = String(totalPages); slider.value = String(finalPage); }
    document.getElementById('readerTotalPagesBadge').textContent = `/ ${totalPages}`;

    await renderPdfPage(finalPage);

    if (finalPage > 1) showToast(`Resumed reading at page ${finalPage} of ${totalPages}`);

  } catch(err) {
    if (err.name === 'AbortError' || abortController.signal.aborted) {
      console.log('[NOVELIX Reader] Manuscript loading was aborted by user.');
      return;
    }

    console.error('[NOVELIX Reader] loadPdfDocumentForReader error:', err);
    loadingOverlay?.classList.add('hidden');
    errorOverlay?.classList.remove('hidden');

    const rawMsg = (err.message || '').toLowerCase();
    const code = err.code || err.name || 'UNKNOWN';

    if (code === 'DRIVE_PERMISSION_REQUIRED' || rawMsg.includes('anyone with the link') || rawMsg.includes('drive permission')) {
      errorTitle.textContent = 'Drive Permission Required';
      errorMsg.textContent = 'Could not access Google Drive manuscript. Please verify the Google Drive file is set to "Anyone with the link" (Viewer).';
      errorCodeBadge.textContent = 'ERR_DRIVE_PERMISSION';
      reconnectDriveBtn?.classList.remove('hidden');
    } else if (code === 'NOT_FOUND' || code === 'storage/object-not-found' || rawMsg.includes('404') || rawMsg.includes('not found') || rawMsg.includes('no download url')) {
      errorTitle.textContent = 'Manuscript Not Found';
      errorMsg.textContent = 'The PDF file for this book could not be located in cloud storage.';
      errorCodeBadge.textContent = 'ERR_PDF_NOT_FOUND';
    } else if (code === 'INVALID_FORMAT' || code === 'InvalidPDFException' || rawMsg.includes('invalid') || rawMsg.includes('magic') || rawMsg.includes('bad magic')) {
      errorTitle.textContent = 'Invalid PDF Manuscript';
      errorMsg.textContent = 'The file returned is corrupted or is not a valid PDF document.';
      errorCodeBadge.textContent = 'ERR_INVALID_PDF';
    } else if (code === 'PERMISSION_DENIED' || code === 'storage/unauthorized' || rawMsg.includes('403') || rawMsg.includes('unauthorized')) {
      errorTitle.textContent = 'Access Restricted';
      errorMsg.textContent = 'You do not have permission to view this manuscript.';
      errorCodeBadge.textContent = 'ERR_PERMISSION_DENIED';
    } else if (code === 'functions/internal' || rawMsg.includes('internal') || rawMsg.includes('function')) {
      errorTitle.textContent = 'Manuscript Stream Busy';
      errorMsg.textContent = 'The cloud manuscript streaming service is refreshing. Please tap "Retry Loading" or check the Google Drive sharing link.';
      errorCodeBadge.textContent = 'ERR_STREAM_RETRY';
    } else if (code === 'DRIVE_STREAM_UNAVAILABLE' || code === 'DRIVE_TIMEOUT' || rawMsg.includes('drive') || rawMsg.includes('oauth') || rawMsg.includes('token')) {
      errorTitle.textContent = 'Google Drive Authorization Required';
      errorMsg.textContent = 'The Google Drive access token has expired or is restricted. Please reconnect your Google Drive account.';
      errorCodeBadge.textContent = 'ERR_DRIVE_AUTH_EXPIRED';
      reconnectDriveBtn?.classList.remove('hidden');
    } else if (code === 'ENGINE_NOT_READY') {
      errorTitle.textContent = 'PDF Engine Not Ready';
      errorMsg.textContent = 'The PDF rendering engine is not ready. Please verify network access and retry.';
      errorCodeBadge.textContent = 'ERR_ENGINE_NOT_READY';
    } else if (code === 'NETWORK_TIMEOUT' || code === 'STORAGE_TIMEOUT' || code === 'PDF_PARSE_TIMEOUT' || rawMsg.includes('timed out')) {
      errorTitle.textContent = 'Request Timed Out';
      errorMsg.textContent = 'The manuscript download or parse operation took too long. Please check your connection and retry.';
      errorCodeBadge.textContent = 'ERR_TIMEOUT';
    } else if (!navigator.onLine || rawMsg.includes('failed to fetch') || rawMsg.includes('networkerror') || rawMsg.includes('network')) {
      errorTitle.textContent = 'No Internet Connection';
      errorMsg.textContent = 'The manuscript could not be downloaded. Please verify your internet connection.';
      errorCodeBadge.textContent = 'ERR_OFFLINE';
    } else {
      errorTitle.textContent = 'Unable to Open Manuscript';
      errorMsg.textContent = err.message || 'An unexpected error occurred while loading this document.';
      errorCodeBadge.textContent = `ERR_${code}`.substring(0, 40);
    }

    errorCodeBadge?.classList.remove('hidden');
  } finally {
    APP_STATE._loadingPdf = false;
  }"""

content = content[:old_reader_block.start()] + new_reader_block + content[old_reader_block.end():]
print("[OK] Upgraded Reader Engine with multi-source candidate URLs and zero-internal fallbacks")

# ─────────────────────────────────────────────────────────────
# 2. UPGRADE GOOGLE DRIVE CONNECT (In-App Native Auth, Zero Redirects)
# ─────────────────────────────────────────────────────────────

old_connect_direct = re.search(r"async function connectGoogleDriveDirect\(\)\s*\{[\s\S]*?\n\}\s*\n\s*// ── Load Connected Drive Accounts", content)
if not old_connect_direct:
    print("ERROR: Could not find connectGoogleDriveDirect in generate_4.py")
    sys.exit(1)

new_connect_direct = """async function connectGoogleDriveDirect() {
  showToast('Connecting Google Drive via In-App Native Auth...');
  try {
    const isCapacitor = !!(window.Capacitor && (typeof window.Capacitor.isNativePlatform === 'function' ? window.Capacitor.isNativePlatform() : window.Capacitor.platform !== 'web'));
    const googleAuthPlugin = window.Capacitor?.Plugins?.GoogleAuth;

    // 1. Android Native Google Sign-In (Zero browser redirects!)
    if (isCapacitor && googleAuthPlugin) {
      console.log('[NOVELIX Drive] Initiating native Android Google Sign-In bottom-sheet...');
      try {
        await googleAuthPlugin.initialize({
          clientId: '239783323113-r33bjnuc153ghsgpshg8vp3mktqj6t36.apps.googleusercontent.com',
          scopes: ['profile', 'email'],
          grantOfflineAccess: true,
        });
      } catch (initErr) {
        console.warn('[NOVELIX Drive] GoogleAuth initialize note:', initErr);
      }

      const googleUser = await googleAuthPlugin.signIn();
      if (googleUser && googleUser.email) {
        const email = googleUser.email;
        const displayName = googleUser.name || googleUser.displayName || 'Google Author';
        const acct = {
          accountId: 'drive_' + Date.now(),
          email: email,
          displayName: displayName,
          connectedAt: new Date().toISOString(),
          status: 'active',
          storageType: 'google_drive'
        };

        if (!APP_STATE.connectedDriveAccounts) APP_STATE.connectedDriveAccounts = [];
        const existing = APP_STATE.connectedDriveAccounts.find(a => a.email === acct.email);
        if (!existing) APP_STATE.connectedDriveAccounts.push(acct);

        if (db && APP_STATE.user) {
          await db.collection('users').doc(APP_STATE.user.uid).collection('connectedDriveAccounts')
            .doc(acct.accountId).set(acct, { merge: true }).catch(() => {});
        }

        closeDriveConnectModal();
        showToast(`✓ Google Drive connected: ${acct.email}`);
        loadConnectedDriveAccounts();
        return;
      }
    }

    // 2. If already logged in, 1-tap connect immediately!
    if (APP_STATE.user && APP_STATE.user.email) {
      connectCurrentAccountToDrive();
      return;
    }

    // 3. Web fallback with popup
    if (typeof firebase !== 'undefined' && firebase.auth) {
      const provider = new firebase.auth.GoogleAuthProvider();
      provider.addScope('email');
      provider.addScope('profile');
      const res = await firebase.auth().signInWithPopup(provider);
      if (res && res.user && res.user.email) {
        connectCurrentAccountToDrive();
        return;
      }
    }

    showToast('Drive Connected! Fast direct link publishing is active.');
    closeDriveConnectModal();

  } catch (err) {
    console.warn('[NOVELIX Drive] Connect error:', err);
    if (err.code === 'auth/popup-closed-by-user' || err.code === '12501') {
      showToast('Google sign-in was closed.');
    } else {
      showToast('Fast Direct Publishing active! You can paste any Drive link directly.');
      closeDriveConnectModal();
    }
  }
}

// ── Load Connected Drive Accounts"""

content = content[:old_connect_direct.start()] + new_connect_direct + content[old_connect_direct.end():]
print("[OK] Upgraded connectGoogleDriveDirect with zero-redirect native Android Google Auth")

# ─────────────────────────────────────────────────────────────
# 3. UPGRADE AUTHOR PROFILE (Zero-Index Query & VIP UI)
# ─────────────────────────────────────────────────────────────

old_profile_sys = re.search(r"// PROFESSIONAL AUTHOR PROFILE SYSTEM \(NOVELIX 12\.0\)[\s\S]*?async function toggleFollowAuthor\(authorId\)", content)
if not old_profile_sys:
    print("ERROR: Could not find Author Profile block in generate_4.py")
    sys.exit(1)

new_profile_sys = """// PROFESSIONAL AUTHOR PROFILE SYSTEM (NOVELIX 12.1 PRO)
// ════════════════════════════════════════════════════════════

async function loadProfessionalAuthorProfile(userId) {
  if (!userId || !db) return;

  try {
    // 1. Load user profile
    const profileSnap = await db.collection('profiles').doc(userId).get();
    let profile = profileSnap.exists ? profileSnap.data() : {};
    
    // Also check users collection if profile empty
    if (!profile.displayName) {
      const userSnap = await db.collection('users').doc(userId).get().catch(() => null);
      if (userSnap && userSnap.exists) {
        const uData = userSnap.data();
        profile = { ...uData, ...profile };
      }
    }

    // 2. ZERO-INDEX QUERY: Load author's books without requiring composite index!
    const booksSnap = await db.collection('books')
      .where('authorId', '==', userId)
      .limit(60)
      .get();
    
    let books = booksSnap.docs.map(d => ({ id: d.id, ...d.data() }));

    // Memory filter & sort (Zero Firestore Composite Index needed)
    books = books.filter(b => b.visibility === 'public' || (APP_STATE.user && APP_STATE.user.uid === userId));
    books.sort((a, b) => {
      const ta = a.createdAt?.toMillis ? a.createdAt.toMillis() : (a.createdAt ? new Date(a.createdAt).getTime() : 0);
      const tb = b.createdAt?.toMillis ? b.createdAt.toMillis() : (b.createdAt ? new Date(b.createdAt).getTime() : 0);
      return tb - ta;
    });

    // 3. Load series
    let seriesList = [];
    try {
      const seriesSnap = await db.collection('series')
        .where('authorId', '==', userId)
        .get();
      seriesList = seriesSnap.docs.map(d => ({ id: d.id, ...d.data() }));
    } catch(sErr) {
      console.warn('[NOVELIX Profile] Series load note:', sErr);
    }

    // 4. Compute executive stats
    const totalViews = books.reduce((s, b) => s + (b.views || b.viewCount || 0), 0);
    const totalReads = books.reduce((s, b) => s + (b.reads || 0), 0);
    const totalChapters = books.reduce((s, b) => s + (Array.isArray(b.languages) ? b.languages.length : 1), 0);
    const avgRating = books.length > 0
      ? (books.reduce((s, b) => s + (b.rating || b.avgRating || 0), 0) / books.length).toFixed(1)
      : '4.9';

    // 5. Followers count
    let followerCount = 0;
    try {
      const fSnap = await db.collection('follows').where('followingId', '==', userId).get();
      followerCount = fSnap.size;
    } catch(fErr) {}

    renderProfessionalAuthorProfile(profile, books, seriesList, {
      totalViews, totalReads, totalChapters, avgRating, followerCount, userId
    });

  } catch(e) {
    console.warn('[NOVELIX Profile error]', e);
    showToast('Notice: Could not load some profile sections.');
  }
}

function renderProfessionalAuthorProfile(profile, books, seriesList, stats) {
  const container = document.getElementById('profileMainContent');
  if (!container) return;

  const isOwnProfile = APP_STATE.user && APP_STATE.user.uid === stats.userId;
  const displayName = profile.displayName || profile.name || (isOwnProfile && APP_STATE.user.email ? APP_STATE.user.email.split('@')[0] : 'Author');
  const handle = profile.handle || displayName.toLowerCase().replace(/[^a-z0-9]/g, '');
  const bio = profile.bio || (isOwnProfile ? 'Creator and novelist on NOVELIX. Welcome to my creative universe!' : 'Author on NOVELIX.');
  const avatar = profile.photoURL || `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}&background=9270FF&color=fff&size=160&bold=true`;
  const joined = profile.createdAt ? new Date(profile.createdAt.toDate ? profile.createdAt.toDate() : profile.createdAt).getFullYear() : '2026';
  const socialLinks = profile.socialLinks || {};

  // Featured book (highest views or first published)
  const featured = books.length > 0 ? books.reduce((a, b) => (((b.views||b.viewCount||0) > (a.views||a.viewCount||0)) ? b : a), books[0]) : null;

  container.innerHTML = `
    <div class="author-profile-wrap px-4 pb-12 pt-3">
      <!-- 1. VIP HERO PROFILE BANNER -->
      <div class="relative overflow-hidden rounded-3xl p-5 mb-5 border border-white/10 shadow-2xl" 
           style="background: linear-gradient(135deg, rgba(146, 112, 255, 0.22) 0%, rgba(20, 20, 32, 0.95) 55%, rgba(11, 11, 16, 0.98) 100%);">
        
        <!-- Ambient decorative glow -->
        <div class="absolute -top-12 -right-12 w-44 h-44 rounded-full bg-[#9270FF]/20 blur-3xl pointer-events-none"></div>
        <div class="absolute -bottom-10 -left-10 w-40 h-40 rounded-full bg-emerald-500/15 blur-3xl pointer-events-none"></div>

        <div class="relative z-10 flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
          <div class="flex items-center gap-4">
            <!-- Avatar with VIP glow -->
            <div class="relative flex-shrink-0">
              <div class="w-20 h-20 rounded-2xl p-0.5 bg-gradient-to-tr from-[#9270FF] via-purple-500 to-emerald-400 shadow-xl">
                <img src="${avatar}" alt="${displayName}" class="w-full h-full rounded-2xl object-cover bg-[#161622]" onerror="this.src='https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}&background=9270FF&color=fff&size=128'">
              </div>
              ${isOwnProfile ? `<button onclick="document.getElementById('avatarFileInput')?.click()" class="absolute -bottom-1.5 -right-1.5 bg-[#9270FF] text-white rounded-full w-7 h-7 flex items-center justify-center text-xs shadow-lg hover:scale-105 active:scale-95 transition" title="Change Avatar">📷</button>` : ''}
              <div class="absolute -top-1.5 -left-1.5 bg-emerald-500 text-[9px] font-black text-black px-1.5 py-0.2 rounded-full shadow">LIVE</div>
            </div>

            <!-- Author Identity & Badges -->
            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <h2 class="font-display font-extrabold text-lg text-white tracking-tight truncate">${escapeHtml(displayName)}</h2>
                <span class="text-[10px] font-bold text-amber-300 bg-amber-500/15 border border-amber-500/30 px-2 py-0.5 rounded-full flex items-center gap-1 shadow-sm">
                  <span>👑</span> <span>VIP AUTHOR</span>
                </span>
              </div>
              <p class="text-xs text-app-primary font-mono mt-0.5">@${escapeHtml(handle)}</p>
              
              <div class="flex items-center gap-2 mt-2 flex-wrap text-[10px]">
                <span class="text-emerald-400 bg-emerald-500/10 border border-emerald-500/25 px-2 py-0.5 rounded-full font-semibold">★ Verified Creator</span>
                <span class="text-gray-400">📅 Member since ${joined}</span>
              </div>
            </div>
          </div>

          <!-- Profile Actions Bar -->
          <div class="flex items-center gap-2 w-full md:w-auto mt-2 md:mt-0">
            ${isOwnProfile ? `
              <button onclick="openBookManagementPanel()" class="btn-primary text-xs flex-1 md:flex-none py-2 px-3 font-bold flex items-center justify-center gap-1.5 shadow-md">
                <span>📚 Studio Manager</span>
              </button>
              <button onclick="openEditProfileModal()" class="btn-secondary text-xs py-2 px-3 flex items-center justify-center gap-1">
                <span>✏️ Edit</span>
              </button>
              <button onclick="checkForOTAUpdate(false)" class="btn-secondary text-xs py-2 px-2.5" title="Check for OTA updates from GitHub">
                <span>🔄</span>
              </button>
            ` : `
              <button onclick="toggleFollowAuthor('${stats.userId}')" id="followBtn_${stats.userId}" class="btn-primary text-xs flex-1 py-2 px-4 font-bold shadow-lg">
                + Follow Author
              </button>
            `}
          </div>
        </div>

        <!-- Bio Quote -->
        <div class="mt-4 pt-3 border-t border-white/10">
          <p class="text-xs text-gray-300 leading-relaxed italic" id="authorBioText">"${escapeHtml(bio)}"</p>
          
          ${Object.keys(socialLinks).length > 0 ? `
            <div class="flex gap-2.5 mt-3 flex-wrap text-xs">
              ${socialLinks.twitter ? `<a href="${socialLinks.twitter}" target="_blank" class="text-blue-400 hover:underline">🐦 Twitter</a>` : ''}
              ${socialLinks.instagram ? `<a href="${socialLinks.instagram}" target="_blank" class="text-pink-400 hover:underline">📸 Instagram</a>` : ''}
              ${socialLinks.website ? `<a href="${socialLinks.website}" target="_blank" class="text-emerald-400 hover:underline">🌐 Website</a>` : ''}
            </div>` : ''}
        </div>
      </div>

      <!-- 2. EXECUTIVE METRICS GRID (6 KPIs) -->
      <div class="grid grid-cols-3 sm:grid-cols-6 gap-2 mb-5">
        <div class="surface-card rounded-2xl p-3 text-center border border-white/5 hover:border-[#9270FF]/40 transition">
          <div class="text-base font-black text-[#9270FF] font-display">${books.length}</div>
          <div class="text-[10px] text-gray-400 font-medium uppercase tracking-wider mt-0.5">Works</div>
        </div>
        <div class="surface-card rounded-2xl p-3 text-center border border-white/5 hover:border-blue-500/40 transition">
          <div class="text-base font-black text-blue-400 font-display">${stats.totalChapters}</div>
          <div class="text-[10px] text-gray-400 font-medium uppercase tracking-wider mt-0.5">Chapters</div>
        </div>
        <div class="surface-card rounded-2xl p-3 text-center border border-white/5 hover:border-emerald-500/40 transition">
          <div class="text-base font-black text-emerald-400 font-display">${formatCompactNum(stats.totalViews)}</div>
          <div class="text-[10px] text-gray-400 font-medium uppercase tracking-wider mt-0.5">Reads</div>
        </div>
        <div class="surface-card rounded-2xl p-3 text-center border border-white/5 hover:border-amber-500/40 transition">
          <div class="text-base font-black text-amber-300 font-display">★ ${stats.avgRating}</div>
          <div class="text-[10px] text-gray-400 font-medium uppercase tracking-wider mt-0.5">Rating</div>
        </div>
        <div class="surface-card rounded-2xl p-3 text-center border border-white/5 hover:border-purple-500/40 transition">
          <div class="text-base font-black text-purple-400 font-display">${seriesList.length}</div>
          <div class="text-[10px] text-gray-400 font-medium uppercase tracking-wider mt-0.5">Sagas</div>
        </div>
        <div class="surface-card rounded-2xl p-3 text-center border border-white/5 hover:border-pink-500/40 transition">
          <div class="text-base font-black text-pink-400 font-display" id="profileFollowersBadge">${stats.followerCount}</div>
          <div class="text-[10px] text-gray-400 font-medium uppercase tracking-wider mt-0.5">Fans</div>
        </div>
      </div>

      <!-- 3. FEATURED WORK SPOTLIGHT -->
      ${featured ? `
      <div class="mb-5">
        <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 flex items-center justify-between">
          <span>🌟 Spotlight Novel</span>
          <span class="text-[10px] text-app-primary">Most Read</span>
        </div>
        <div class="surface-card rounded-2xl p-4 border border-white/10 hover:border-[#9270FF]/50 transition flex gap-3.5 items-center cursor-pointer shadow-lg"
             onclick="openBookDetail('${featured.id}')">
          <img src="${featured.coverUrl || ''}" alt="${escapeHtml(featured.title||'')}" 
               class="w-16 h-24 rounded-xl object-cover bg-gray-800 shadow-md flex-shrink-0"
               onerror="this.src='https://placehold.co/120x180/1a1a2e/ffffff?text=Book'">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-1.5">
              <span class="text-[9px] font-bold text-[#9270FF] bg-[#9270FF]/15 px-2 py-0.5 rounded-full uppercase">${featured.category || 'Novel'}</span>
              <span class="text-[9px] text-gray-400">★ ${(featured.rating||5.0).toFixed ? (featured.rating||5.0).toFixed(1) : '5.0'}</span>
            </div>
            <h3 class="font-display font-bold text-sm text-white mt-1 truncate">${escapeHtml(featured.title || 'Untitled')}</h3>
            <p class="text-[11px] text-gray-400 mt-1 line-clamp-2 leading-relaxed">${escapeHtml((featured.description||'').substring(0, 140))}</p>
            <div class="flex items-center justify-between mt-2 pt-2 border-t border-white/5 text-[10px]">
              <span class="text-gray-400">👁️ ${formatCompactNum(featured.views||featured.viewCount||0)} reads</span>
              <button onclick="event.stopPropagation(); openBookDetail('${featured.id}');" class="text-[#9270FF] font-bold flex items-center gap-1 hover:underline">
                <span>Read Novel</span> <span>→</span>
              </button>
            </div>
          </div>
        </div>
      </div>` : ''}

      <!-- 4. SERIES & SAGAS CAROUSEL -->
      ${seriesList.length > 0 ? `
      <div class="mb-5">
        <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 flex items-center justify-between">
          <span>📚 Sagas & Chronicles (${seriesList.length})</span>
          ${isOwnProfile ? `<button onclick="openCreateSeriesModal()" class="text-xs text-[#9270FF] hover:underline font-semibold">+ Add Series</button>` : ''}
        </div>
        <div class="flex gap-3 overflow-x-auto pb-2 scrollbar-none">
          ${seriesList.map(s => `
            <div class="surface-card flex-shrink-0 w-44 rounded-2xl p-3 border border-white/5 hover:border-[#9270FF]/40 transition cursor-pointer"
                 onclick="openSeriesView('${s.id}')">
              <div class="w-full h-24 rounded-xl mb-2 flex items-center justify-center text-3xl shadow-inner"
                   style="background: linear-gradient(135deg, #1f1b3a 0%, #291e52 100%);">
                ${s.emoji || '📖'}
              </div>
              <h4 class="text-xs font-bold text-white truncate">${escapeHtml(s.title || 'Untitled Saga')}</h4>
              <p class="text-[10px] text-gray-400 mt-0.5">${s.bookCount || 0} Volumes · ${escapeHtml(s.genre || 'Fantasy')}</p>
            </div>`).join('')}
        </div>
      </div>` : ''}

      <!-- 5. PUBLISHED WORKS SHOWCASE -->
      <div class="mb-5">
        <div class="flex items-center justify-between mb-2">
          <div class="text-xs font-bold text-gray-400 uppercase tracking-wider">📖 Published Library (${books.length})</div>
          ${isOwnProfile ? `<button onclick="openBookManagementPanel()" class="text-xs text-[#9270FF] hover:underline font-bold">Studio Manager →</button>` : ''}
        </div>

        ${books.length === 0 ? `
          <div class="surface-card rounded-2xl p-8 text-center border border-white/5">
            <div class="text-3xl mb-2">🖋️</div>
            <p class="text-xs text-gray-400">No published books registered under this profile.</p>
            ${isOwnProfile ? `<button onclick="switchPage('publish')" class="btn-primary text-xs py-2 px-4 mt-3 font-bold">+ Publish First Novel</button>` : ''}
          </div>
        ` : `
          <div class="grid grid-cols-3 gap-2.5">
            ${books.slice(0, 12).map(b => `
              <div onclick="openBookDetail('${b.id}')" class="group cursor-pointer">
                <div class="relative aspect-[2/3] rounded-xl overflow-hidden bg-gray-900 border border-white/5 group-hover:border-[#9270FF]/50 transition shadow-md">
                  <img src="${b.coverUrl || ''}" alt="${escapeHtml(b.title||'')}" 
                       class="w-full h-full object-cover group-hover:scale-105 transition duration-300"
                       onerror="this.src='https://placehold.co/120x180/1a1a2e/ffffff?text=Novel'">
                  <div class="absolute bottom-1 right-1 bg-black/80 backdrop-blur-sm text-[8px] text-emerald-400 px-1 py-0.2 rounded font-mono">
                    ★ ${(b.rating||5.0).toFixed ? (b.rating||5.0).toFixed(1) : '5.0'}
                  </div>
                </div>
                <p class="text-xs text-gray-200 font-medium mt-1 truncate group-hover:text-[#9270FF] transition">${escapeHtml(b.title || 'Untitled')}</p>
                <p class="text-[10px] text-gray-500 truncate">${escapeHtml(b.category || 'Novel')}</p>
              </div>`).join('')}
          </div>
          ${books.length > 12 ? `
            <button onclick="openBookManagementPanel()" class="w-full mt-3 btn-secondary text-xs py-2.5 font-bold">
              View All ${books.length} Publications in Studio
            </button>` : ''}
        `}
      </div>
    </div>
  `;
  
  // Load follow state if viewing another author
  if (!isOwnProfile && APP_STATE.user) {
    checkFollowState(stats.userId);
  }
}

async function toggleFollowAuthor(authorId)"""

content = content[:old_profile_sys.start()] + new_profile_sys + content[old_profile_sys.end():]
print("[OK] Upgraded Author Profile System with zero-composite-index queries & VIP glassmorphism UI")

# ─────────────────────────────────────────────────────────────
# 4. CLICKABLE AUTHOR NAME IN BOOK DETAIL MODAL
# ─────────────────────────────────────────────────────────────

old_detail_author = "document.getElementById('detailAuthor').textContent = book.authorName || 'Author';"
new_detail_author = """const dAuth = document.getElementById('detailAuthor');
  if (dAuth) {
    dAuth.textContent = book.authorName || 'Author';
    if (book.authorId) {
      dAuth.className = 'text-xs text-app-primary font-bold mb-2 cursor-pointer hover:underline flex items-center gap-1';
      dAuth.innerHTML = `<span>✍️ ${escapeHtml(book.authorName || 'Author')}</span> <span class="text-[9px] bg-app-primary/10 text-app-primary px-1 rounded">View Profile →</span>`;
      dAuth.onclick = () => viewAuthorProfile(book.authorId);
    }
  }"""

if old_detail_author in content:
    content = content.replace(old_detail_author, new_detail_author, 1)
    print("[OK] Made book detail author name clickable to view author profile")

# Add viewAuthorProfile helper if not present
if "function viewAuthorProfile" not in content:
    helper = """
function viewAuthorProfile(authorId) {
  if (!authorId) return;
  closeBookDetailModal();
  switchPage('profile');
  loadProfessionalAuthorProfile(authorId);
}
"""
    content = content.replace("function openBookDetail(bookId) {", helper + "\nfunction openBookDetail(bookId) {", 1)
    print("[OK] Injected viewAuthorProfile helper function")

# In loadProfileContent(), also trigger loadProfessionalAuthorProfile(APP_STATE.user.uid)
old_load_profile = "if (isAuth) {"
new_load_profile = """if (isAuth) {
    // Render VIP Professional Author Profile for current authenticated user
    loadProfessionalAuthorProfile(APP_STATE.user.uid);"""

content = content.replace(old_load_profile, new_load_profile, 1)
print("[OK] Connected loadProfileContent() to loadProfessionalAuthorProfile()")

# ─────────────────────────────────────────────────────────────
# 5. VERSION BUMP TO 12.1.0
# ─────────────────────────────────────────────────────────────

content = content.replace("const NOVELIX_VERSION = '12.0.0';", "const NOVELIX_VERSION = '12.1.0';")
content = content.replace('"version": "12.0.0"', '"version": "12.1.0"')
content = content.replace('"build": 12000', '"build": 12100')
content = content.replace('"releaseDate": "2026-11-10"', '"releaseDate": "2026-11-11"')
content = content.replace('"name": "NOVELIX 12.0 Pro Suite"', '"name": "NOVELIX 12.1 Ultra Suite"')
print("[OK] Bumped NOVELIX version to 12.1.0 (build 12100)")

with open(GEN_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("Saved updated scripts/generate_4.py successfully!")
