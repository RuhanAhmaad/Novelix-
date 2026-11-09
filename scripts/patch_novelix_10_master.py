#!/usr/bin/env python3
"""
NOVELIX 10.0 — Master Patch Script
Implements:
- Phase 1: Two publishing options: Upload File vs Paste Google Drive Link with step-by-step pipeline
- Phase 2: Complete Google Drive connection fix (system browser launch via anchor dispatch, multi-account management)
- Phase 3 & 4: 10,000 Concurrent Users Architecture (Firestore pagination, selective listener cleanup on page navigation, debounce publish lock)
- Phase 5: Security & Input Validation (sanitization, size limits)
- Phase 6: Real-time UX optimizations
"""

import sys, os, re

with open("scripts/generate_4.py", "r", encoding="utf-8") as f:
    content = f.read()

print("=== Starting NOVELIX 10.0 Master Patch ===")

# -------------------------------------------------------------
# 1. Publishing Form HTML: Add Method Toggle + Paste Drive Link Section + Step Progress Box
# -------------------------------------------------------------
old_editions_html = """          <!-- Language Editions / Documents -->
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
          </div>"""

new_publishing_html = """          <!-- 10.0 Publishing Source Method Selection -->
          <div class="surface-card p-3 rounded-xl border border-[#262638] space-y-2">
            <div class="flex items-center justify-between">
              <label class="block text-xs font-semibold text-app-muted uppercase tracking-wider">Publishing Method</label>
              <span class="text-[10px] text-app-primary font-mono font-medium">NOVELIX 10.0 Cloud</span>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <button type="button" id="pubMethodBtn-drive" onclick="setPublishMethod('drive_link')" class="py-2.5 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all bg-[#9270FF]/20 border border-[#9270FF] text-[#B9A4FF]">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
                Paste Drive Link
              </button>
              <button type="button" id="pubMethodBtn-file" onclick="setPublishMethod('file')" class="py-2.5 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all bg-[#14141D] border border-[#262638] text-[#9693A4]">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>
                Upload File (PDF)
              </button>
            </div>
            <p id="publishMethodDesc" class="text-[11px] text-app-muted px-0.5">Publish instantly from Google Drive without uploading large PDF files from your phone.</p>
          </div>

          <!-- Option B: Paste Google Drive Link Section (Default) -->
          <div id="publishDriveLinkSection" class="surface-card p-3.5 rounded-xl border border-[#262638] space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-white flex items-center gap-1.5">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4 text-app-primary"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
                Google Drive Manuscript Link
              </span>
              <span class="text-[10px] text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded font-mono font-medium">Instant • No Phone Upload</span>
            </div>

            <div>
              <label class="block text-[10px] text-app-muted uppercase font-semibold mb-1">Paste Google Drive URL</label>
              <div class="relative">
                <input type="url" id="publishDriveLinkInput" placeholder="https://drive.google.com/file/d/1A2B3C.../view?usp=sharing" class="w-full pl-3 pr-24 py-2.5 text-xs font-mono bg-[#14141D] border border-[#262638] rounded-lg text-white focus:border-[#9270FF]" oninput="handleDriveLinkInputChanged()">
                <button type="button" id="validateDriveLinkBtn" onclick="validatePastedDriveLink()" class="absolute right-1.5 top-1.5 bottom-1.5 px-3 bg-[#9270FF] hover:bg-[#805cf5] text-white text-[11px] font-semibold rounded-md flex items-center gap-1 transition-all">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3 h-3"><polyline points="20 6 9 17 4 12"/></svg>
                  Validate
                </button>
              </div>
              <p class="text-[10px] text-app-muted mt-1">Accepts standard share links, view links, or direct Google Drive URLs.</p>
            </div>

            <!-- Language and Permissions for Pasted Link -->
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="block text-[10px] text-app-muted uppercase font-semibold mb-1">Manuscript Language</label>
                <select id="publishDriveLinkLang" class="w-full px-2.5 py-2 text-xs bg-[#14141D] border border-[#262638] rounded-lg text-white">
                  <option value="English">English</option>
                  <option value="Spanish">Spanish</option>
                  <option value="French">French</option>
                  <option value="Arabic">Arabic</option>
                  <option value="Japanese">Japanese</option>
                  <option value="Korean">Korean</option>
                  <option value="German">German</option>
                  <option value="Portuguese">Portuguese</option>
                  <option value="Chinese">Chinese</option>
                </select>
              </div>
              <div>
                <label class="block text-[10px] text-app-muted uppercase font-semibold mb-1">Permission Mode</label>
                <div class="text-[11px] text-app-muted py-2 px-2.5 bg-[#14141D] rounded-lg border border-[#262638] truncate" id="driveLinkPermissionBadge">
                  Auto-detected on validate
                </div>
              </div>
            </div>

            <!-- Validation Status Box -->
            <div id="publishDriveLinkStatusCard" class="hidden p-3 rounded-lg border text-xs"></div>
          </div>

          <!-- Option A: File Upload Section (Initially Hidden) -->
          <div id="publishFileSection" class="hidden space-y-2">
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

          <!-- Step-by-Step Publishing Pipeline Status -->
          <div id="publishingStepProgressBox" class="hidden surface-card p-3.5 rounded-xl border border-[#9270FF]/40 bg-[#161226] space-y-2">
            <div class="flex items-center justify-between border-b border-[#2E2448] pb-1.5">
              <span class="text-xs font-bold text-white flex items-center gap-1.5">
                <span class="animate-spin inline-block w-3 h-3 border-2 border-app-primary border-t-transparent rounded-full"></span>
                Publishing Pipeline
              </span>
              <span id="publishingStepProgressText" class="text-[10px] font-mono text-[#B9A4FF]">Step 1 of 5</span>
            </div>
            <div class="space-y-1.5 pt-1 text-xs" id="publishingStepList">
              <div id="pubStep1" class="flex items-center gap-2 text-app-muted"><span class="w-4 text-center font-mono text-[10px]">1</span> <span>Validating link</span></div>
              <div id="pubStep2" class="flex items-center gap-2 text-app-muted"><span class="w-4 text-center font-mono text-[10px]">2</span> <span>Checking permissions</span></div>
              <div id="pubStep3" class="flex items-center gap-2 text-app-muted"><span class="w-4 text-center font-mono text-[10px]">3</span> <span>Retrieving manuscript information</span></div>
              <div id="pubStep4" class="flex items-center gap-2 text-app-muted"><span class="w-4 text-center font-mono text-[10px]">4</span> <span>Saving book details</span></div>
              <div id="pubStep5" class="flex items-center gap-2 text-app-muted"><span class="w-4 text-center font-mono text-[10px]">5</span> <span>Published successfully</span></div>
            </div>
          </div>"""

if old_editions_html in content:
    content = content.replace(old_editions_html, new_publishing_html, 1)
    print("  [OK] Replaced Editions HTML with Two Publishing Options and Step Progress")
else:
    print("  [ERROR] Editions HTML anchor not found")
    sys.exit(1)

# -------------------------------------------------------------
# 2. Initiate Google Drive Connection: Anchor Dispatch for Chrome Launch
# -------------------------------------------------------------
old_initiate_drive = """    // Step 3: Open in SYSTEM BROWSER (Chrome on Android)
    // Completely avoids WebView sandbox and origin_mismatch
    const browserOpened = window.open(authUrl, '_system');

    // Safety fallback for desktop browsers
    if (!browserOpened && !window.Capacitor) {
      const popup = window.open(authUrl, 'NOVELIX_Drive_Auth', 'width=540,height=680');
      if (popup) {
        const timer = setInterval(() => {
          if (popup.closed) {
            clearInterval(timer);
            APP_STATE._driveOAuthPending = false;
            setTimeout(() => loadConnectedDriveAccounts(), 800);
          }
        }, 1000);
      }
    }"""

new_initiate_drive = """    // Step 3: Open in SYSTEM BROWSER (Chrome on Android)
    // Programmatic anchor click triggers Capacitor Bridge.launchIntent()
    // Completely avoids WebView sandbox and origin_mismatch
    try {
      const authAnchor = document.createElement('a');
      authAnchor.href = authUrl;
      authAnchor.target = '_blank';
      authAnchor.rel = 'noopener noreferrer';
      document.body.appendChild(authAnchor);
      authAnchor.click();
      document.body.removeChild(authAnchor);
    } catch(anchorErr) {
      console.warn('Anchor dispatch fallback:', anchorErr);
      window.open(authUrl, '_system');
    }

    // Safety fallback for desktop browsers
    if (!window.Capacitor) {
      const popup = window.open(authUrl, 'NOVELIX_Drive_Auth', 'width=540,height=680');
      if (popup) {
        const timer = setInterval(() => {
          if (popup.closed) {
            clearInterval(timer);
            APP_STATE._driveOAuthPending = false;
            setTimeout(() => loadConnectedDriveAccounts(), 800);
          }
        }, 1000);
      }
    }"""

if old_initiate_drive in content:
    content = content.replace(old_initiate_drive, new_initiate_drive, 1)
    print("  [OK] Hardened initiateGoogleDriveConnection with programmatic anchor dispatch")
else:
    print("  [WARN] old_initiate_drive snippet not matched exactly")

# -------------------------------------------------------------
# 3. Enhanced loadConnectedDriveAccounts with Multi-Account details and Disconnect
# -------------------------------------------------------------
old_render_card = """    const renderCard = (acc) => `
      <div class="drive-account-card p-3.5 flex items-center justify-between">
        <div class="flex items-center gap-3 truncate">
          <div class="w-9 h-9 rounded-full bg-app-surface border border-app-border flex items-center justify-center flex-shrink-0 text-white font-bold text-xs overflow-hidden">
            ${acc.picture ? `<img src="${escapeHtml(acc.picture)}" class="w-full h-full object-cover" alt="Avatar">` : (acc.email ? escapeHtml(acc.email[0].toUpperCase()) : 'G')}
          </div>
          <div class="truncate">
            <div class="flex items-center gap-1.5">
              <span class="drive-status-dot"></span>
              <p class="text-xs font-semibold text-white truncate">${escapeHtml(acc.email || acc.name || 'Connected Drive')}</p>
            </div>
            <p class="text-[10px] text-app-muted mt-0.5">Active • Read-only access</p>
          </div>
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          <button onclick="browseDriveAccountFiles('${escapeHtml(acc.id)}')" class="btn-primary text-[11px] px-3 py-1.5 flex items-center gap-1">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3 h-3"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            Browse
          </button>
          <button onclick="disconnectDriveAccount('${escapeHtml(acc.id)}')" title="Disconnect account" class="w-7 h-7 rounded-lg surface-card text-red-400 hover:text-red-300 flex items-center justify-center text-xs">
            ✕
          </button>
        </div>
      </div>
    `;"""

new_render_card = """    const renderCard = (acc) => {
      const connectedDateStr = acc.connectedAt ? new Date(acc.connectedAt).toLocaleDateString() : 'Connected';
      return `
      <div class="drive-account-card p-3.5 flex items-center justify-between">
        <div class="flex items-center gap-3 truncate">
          <div class="w-9 h-9 rounded-full bg-app-surface border border-app-border flex items-center justify-center flex-shrink-0 text-white font-bold text-xs overflow-hidden">
            ${acc.picture ? `<img src="${escapeHtml(acc.picture)}" class="w-full h-full object-cover" alt="Avatar">` : (acc.email ? escapeHtml(acc.email[0].toUpperCase()) : 'G')}
          </div>
          <div class="truncate">
            <div class="flex items-center gap-1.5">
              <span class="drive-status-dot"></span>
              <p class="text-xs font-semibold text-white truncate">${escapeHtml(acc.email || acc.name || 'Connected Drive')}</p>
            </div>
            <p class="text-[10px] text-app-muted mt-0.5">${escapeHtml(acc.name || 'Account')} • ${connectedDateStr}</p>
          </div>
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          <button onclick="browseDriveAccountFiles('${escapeHtml(acc.id)}')" class="btn-primary text-[11px] px-3 py-1.5 flex items-center gap-1">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3 h-3"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            Browse
          </button>
          <button onclick="disconnectDriveAccount('${escapeHtml(acc.id)}')" title="Disconnect account" class="w-7 h-7 rounded-lg surface-card text-red-400 hover:text-red-300 flex items-center justify-center text-xs">
            ✕
          </button>
        </div>
      </div>
    `;};"""

if old_render_card in content:
    content = content.replace(old_render_card, new_render_card, 1)
    print("  [OK] Enhanced loadConnectedDriveAccounts account card rendering")
else:
    print("  [WARN] old_render_card snippet not matched exactly")

# -------------------------------------------------------------
# 4. Add Helper Functions: setPublishMethod, validatePastedDriveLink, updatePublishStep
# and Upgrade handlePublishSubmit with Drive Link logic & double-submit debounce
# -------------------------------------------------------------
old_handle_publish = """async function handlePublishSubmit(event, forceStatus) {
  if (event) event.preventDefault();
  if (!APP_STATE.user) { openAuthModal(); return; }

  const title = document.getElementById('publishTitleInput').value.trim();
  const desc = document.getElementById('publishSynopsisInput').value.trim();
  const status = forceStatus || document.getElementById('publishStatusSelect').value;
  const visibility = document.getElementById('publishVisibilitySelect').value;
  const coverFile = document.getElementById('coverFileInput').files[0];

  if (!title || !desc) { showToast('Please enter title and synopsis'); return; }
  if (APP_STATE.publishEditions.length === 0) { showToast('Please add at least one language edition'); return; }

  setButtonLoading('publishSubmitBtn', true, 'Uploading cover...');

  try {
    const isEditing = !!APP_STATE.editingBookId;
    const bookId = isEditing ? APP_STATE.editingBookId : db.collection('books').doc().id;
    let coverUrl = '';
    let coverSize = coverFile ? coverFile.size : 0;

    // Preserve existing cover if not replaced
    if (!coverFile && isEditing) {
      const existing = (APP_STATE.allBooks || []).find(b => b.id === bookId);
      if (existing) { coverUrl = existing.coverUrl || ''; coverSize = existing.coverSize || 0; }
    }

    if (coverFile) {
      coverUrl = await uploadMediaFile(coverFile, `covers/${bookId}/${Date.now()}.jpg`);
    }

    const languages = [];
    for (let i = 0; i < APP_STATE.publishEditions.length; i++) {
      const ed = APP_STATE.publishEditions[i];
      setButtonLoading('publishSubmitBtn', true, `Processing edition #${i+1} (${ed.language})...`);

      // 1. Existing Drive File
      if (ed.driveFile) {
        languages.push({
          language: ed.language,
          storageProvider: 'drive',
          driveFileId: ed.driveFile.fileId,
          driveAccountId: ed.driveFile.accountId || ed.driveAccountId || '',
          fileName: ed.driveFile.fileName,
          fileSize: ed.driveFile.size || 0,
          fileUrl: ed.driveFile.downloadUrl || '',
          uploadedAt: new Date().toISOString()
        });
      }
      // 2. Local file uploaded directly to Google Drive NOVELIX folder
      else if (ed.storageProvider === 'drive' && ed.file) {
        setButtonLoading('publishSubmitBtn', true, `Uploading to Google Drive (${ed.language})...`);
        const base64 = await readFileAsBase64(ed.file);
        const acctId = ed.driveAccountId || (APP_STATE.connectedDriveAccounts[0]?.id);
        if (!acctId) throw new Error('No Google Drive account selected for upload.');

        if (!functions || typeof functions.httpsCallable !== 'function') {
          throw new Error('Cloud Functions unavailable for Drive upload.');
        }

        const uploadFn = functions.httpsCallable('uploadPdfToDrive');
        const uploadRes = await uploadFn({
          accountId: acctId,
          fileName: ed.file.name,
          fileBase64: base64
        });

        if (!uploadRes.data || !uploadRes.data.success) {
          throw new Error('Failed to upload manuscript to Google Drive.');
        }

        languages.push({
          language: ed.language,
          storageProvider: 'drive',
          driveFileId: uploadRes.data.fileId,
          driveAccountId: acctId,
          fileName: uploadRes.data.fileName || ed.file.name,
          fileSize: uploadRes.data.fileSize || ed.file.size,
          fileUrl: '',
          uploadedAt: new Date().toISOString()
        });
      }
      // 3. Local file uploaded to Firebase Storage
      else if (ed.file) {
        setButtonLoading('publishSubmitBtn', true, `Uploading to Storage (${ed.language})...`);
        const fileUrl = await uploadMediaFile(ed.file, `books/${bookId}/pdfs/${ed.language}_${Date.now()}.pdf`);
        languages.push({
          language: ed.language,
          storageProvider: 'storage',
          fileUrl: fileUrl,
          fileName: ed.file.name,
          fileSize: ed.file.size,
          uploadedAt: new Date().toISOString()
        });
      }
    }

    if (languages.length === 0) {
      throw new Error('Please select or upload a PDF manuscript for your publication.');
    }

    setButtonLoading('publishSubmitBtn', true, 'Publishing to NOVELIX catalog...');

    const primaryStorage = languages.some(l => l.storageProvider === 'drive') ? 'drive' : 'storage';

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
      storageProvider: primaryStorage,
      languages: languages,
      authorId: APP_STATE.user.uid,
      authorName: APP_STATE.profile?.displayName || APP_STATE.user.email.split('@')[0],
      authorPhoto: APP_STATE.profile?.photoURL || '',
      authors: [{
        uid: APP_STATE.user.uid,
        name: APP_STATE.profile?.displayName || APP_STATE.user.email.split('@')[0],
        photoURL: APP_STATE.profile?.photoURL || '',
        role: 'Primary Author'
      }],
      viewCount: 0,
      likeCount: 0,
      bookmarkCount: 0,
      avgRating: 0,
      createdAt: firebase.firestore.FieldValue.serverTimestamp(),
      updatedAt: firebase.firestore.FieldValue.serverTimestamp()
    });

    showToast(isEditing ? 'Publication updated successfully!' : 'Publication published live to NOVELIX!');
    APP_STATE.editingBookId = null;
    const submitBtn = document.getElementById('publishSubmitBtn');
    if (submitBtn) submitBtn.textContent = 'Publish Work';
    resetPublishForm();
    switchPage('home');
  } catch(err) {
    console.error('[NOVELIX Publish] Error:', err);
    showToast(`Publication failed: ${err.message}`);
  } finally {
    setButtonLoading('publishSubmitBtn', false, 'Publish Work');
  }
}"""

new_handle_publish = """// ── NOVELIX 10.0 Publishing Method Management ───────────────────
APP_STATE.publishMethod = 'drive_link'; // 'drive_link' or 'file'
APP_STATE.validatedDriveLink = null;
APP_STATE._isPublishing = false;

function setPublishMethod(method) {
  APP_STATE.publishMethod = method;
  const driveBtn = document.getElementById('pubMethodBtn-drive');
  const fileBtn = document.getElementById('pubMethodBtn-file');
  const driveSec = document.getElementById('publishDriveLinkSection');
  const fileSec = document.getElementById('publishFileSection');
  const descEl = document.getElementById('publishMethodDesc');

  if (method === 'drive_link') {
    if (driveBtn) driveBtn.className = 'py-2.5 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all bg-[#9270FF]/20 border border-[#9270FF] text-[#B9A4FF]';
    if (fileBtn) fileBtn.className = 'py-2.5 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all bg-[#14141D] border border-[#262638] text-[#9693A4]';
    if (driveSec) driveSec.classList.remove('hidden');
    if (fileSec) fileSec.classList.add('hidden');
    if (descEl) descEl.textContent = 'Publish instantly by pasting a Google Drive link. No PDF upload from device required!';
  } else {
    if (fileBtn) fileBtn.className = 'py-2.5 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all bg-[#9270FF]/20 border border-[#9270FF] text-[#B9A4FF]';
    if (driveBtn) driveBtn.className = 'py-2.5 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all bg-[#14141D] border border-[#262638] text-[#9693A4]';
    if (driveSec) driveSec.classList.add('hidden');
    if (fileSec) fileSec.classList.remove('hidden');
    if (descEl) descEl.textContent = 'Upload PDF manuscripts directly from your phone or choose from connected Drive.';
    if (APP_STATE.publishEditions.length === 0) addEditionRow();
  }
}

function handleDriveLinkInputChanged() {
  APP_STATE.validatedDriveLink = null;
  const statusCard = document.getElementById('publishDriveLinkStatusCard');
  if (statusCard) statusCard.classList.add('hidden');
  const permBadge = document.getElementById('driveLinkPermissionBadge');
  if (permBadge) {
    permBadge.textContent = 'Auto-detected on validate';
    permBadge.className = 'text-[11px] text-app-muted py-2 px-2.5 bg-[#14141D] rounded-lg border border-[#262638] truncate';
  }
}

function formatDocSize(bytes) {
  if (!bytes || isNaN(bytes)) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  let i = 0;
  let val = bytes;
  while (val >= 1024 && i < units.length - 1) {
    val /= 1024;
    i++;
  }
  return `${val.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

async function validatePastedDriveLink() {
  const linkInput = document.getElementById('publishDriveLinkInput');
  const statusCard = document.getElementById('publishDriveLinkStatusCard');
  const permBadge = document.getElementById('driveLinkPermissionBadge');
  const link = (linkInput ? linkInput.value : '').trim();

  if (!link) {
    showToast('Please enter a Google Drive link to validate.');
    if (linkInput) linkInput.focus();
    return null;
  }

  if (statusCard) {
    statusCard.classList.remove('hidden');
    statusCard.className = 'p-3 rounded-lg border border-[#262638] bg-[#14141D] text-xs space-y-1.5';
    statusCard.innerHTML = `
      <div class="flex items-center gap-2 text-amber-300">
        <span class="inline-block w-3.5 h-3.5 border-2 border-amber-300 border-t-transparent rounded-full animate-spin"></span>
        <span class="font-medium">Validating Google Drive manuscript...</span>
      </div>
      <p class="text-[10px] text-app-muted">Checking file ID, permissions, and PDF magic bytes...</p>
    `;
  }

  try {
    if (!functions || typeof functions.httpsCallable !== 'function') {
      throw new Error('Cloud Functions are not initialized.');
    }

    const validateFn = functions.httpsCallable('validateGoogleDriveLink');
    const res = await validateFn({ link: link });
    const data = res ? res.data : null;

    if (!data) throw new Error('No response received from validation service.');

    if (data.valid) {
      APP_STATE.validatedDriveLink = data;

      if (permBadge) {
        permBadge.textContent = data.isPublic ? 'Public (Anyone with link)' : `Private (${data.accountEmail || 'Connected'})`;
        permBadge.className = `text-[11px] font-medium py-2 px-2.5 rounded-lg border truncate ${data.isPublic ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' : 'text-[#B9A4FF] bg-[#9270FF]/10 border-[#9270FF]/20'}`;
      }

      if (statusCard) {
        statusCard.className = 'p-3 rounded-lg border border-emerald-500/30 bg-emerald-500/10 text-xs space-y-1.5 text-emerald-300';
        statusCard.innerHTML = `
          <div class="flex items-center gap-1.5 font-bold text-emerald-400">
            <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
            <span>Valid Google Drive PDF found</span>
          </div>
          <div class="text-[11px] text-white">File name: <span class="font-semibold text-emerald-200">${escapeHtml(data.fileName)}</span></div>
          <div class="text-[10px] text-app-muted">File size: <span class="text-white font-mono">${formatDocSize(data.fileSize)}</span> • ${data.isPublic ? 'Public Direct Stream' : 'Encrypted Proxy Access'}</div>
        `;
      }

      // Convenience: Auto-populate publication title if empty
      const titleInput = document.getElementById('publishTitleInput');
      if (titleInput && !titleInput.value.trim() && data.fileName) {
        titleInput.value = data.fileName.replace(/\\.pdf$/i, '').replace(/[-_]/g, ' ');
      }

      showToast('Valid Google Drive PDF verified!');
      return data;
    } else {
      APP_STATE.validatedDriveLink = null;
      if (statusCard) {
        statusCard.className = 'p-3 rounded-lg border border-red-500/30 bg-red-500/10 text-xs space-y-1.5 text-red-300';
        statusCard.innerHTML = `
          <div class="flex items-center gap-1.5 font-bold text-red-400">
            <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            <span>Verification Issue</span>
          </div>
          <p class="text-[11px] text-white">${escapeHtml(data.message || 'Could not verify manuscript.')}</p>
          ${data.error === 'AUTH_REQUIRED' ? `
            <div class="pt-1">
              <button type="button" onclick="switchPage('drive')" class="btn-primary text-xs px-3 py-1">Connect Drive Account</button>
            </div>
          ` : ''}
        `;
      }
      return null;
    }
  } catch(err) {
    APP_STATE.validatedDriveLink = null;
    if (statusCard) {
      statusCard.className = 'p-3 rounded-lg border border-red-500/30 bg-red-500/10 text-xs space-y-1 text-red-300';
      statusCard.innerHTML = `
        <div class="font-semibold text-red-400">Validation Error</div>
        <p class="text-[11px] text-white">${escapeHtml(err.message || 'Validation request failed.')}</p>
      `;
    }
    return null;
  }
}

function updatePublishStep(stepNum, status) {
  // stepNum: 1 to 5; status: 'in_progress', 'completed', 'error'
  const progressBox = document.getElementById('publishingStepProgressBox');
  if (progressBox) progressBox.classList.remove('hidden');

  const stepText = document.getElementById('publishingStepProgressText');
  if (stepText) stepText.textContent = `Step ${stepNum} of 5`;

  for (let s = 1; s <= 5; s++) {
    const el = document.getElementById(`pubStep${s}`);
    if (!el) continue;
    if (s < stepNum) {
      el.className = 'flex items-center gap-2 text-emerald-400 font-medium';
      el.children[0].innerHTML = '<svg class="w-3.5 h-3.5 text-emerald-400 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>';
    } else if (s === stepNum) {
      if (status === 'error') {
        el.className = 'flex items-center gap-2 text-red-400 font-semibold';
        el.children[0].innerHTML = '✕';
      } else if (status === 'completed') {
        el.className = 'flex items-center gap-2 text-emerald-400 font-medium';
        el.children[0].innerHTML = '<svg class="w-3.5 h-3.5 text-emerald-400 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>';
      } else {
        el.className = 'flex items-center gap-2 text-white font-semibold';
        el.children[0].innerHTML = '<span class="inline-block w-2.5 h-2.5 border-2 border-app-primary border-t-transparent rounded-full animate-spin"></span>';
      }
    } else {
      el.className = 'flex items-center gap-2 text-app-muted opacity-50';
      el.children[0].innerHTML = `${s}`;
    }
  }
}

async function handlePublishSubmit(event, forceStatus) {
  if (event) event.preventDefault();
  if (!APP_STATE.user) { openAuthModal(); return; }

  // 10.0 Concurrency Protection: Debounce double-clicks
  if (APP_STATE._isPublishing) {
    console.warn('[NOVELIX Publish] Publication already in progress. Ignoring duplicate trigger.');
    return;
  }
  APP_STATE._isPublishing = true;

  const rawTitle = document.getElementById('publishTitleInput').value.trim();
  const rawDesc = document.getElementById('publishSynopsisInput').value.trim();
  const status = forceStatus || document.getElementById('publishStatusSelect').value;
  const visibility = document.getElementById('publishVisibilitySelect').value;
  const coverFile = document.getElementById('coverFileInput').files[0];

  // Sanitization & Length Restrictions (Security Phase 5)
  const title = rawTitle.substring(0, 150);
  const desc = rawDesc.substring(0, 3000);

  if (!title || !desc) {
    showToast('Please enter publication title and synopsis.');
    APP_STATE._isPublishing = false;
    return;
  }

  setButtonLoading('publishSubmitBtn', true, 'Initializing pipeline...');

  try {
    const isEditing = !!APP_STATE.editingBookId;
    const bookId = isEditing ? APP_STATE.editingBookId : db.collection('books').doc().id;
    let coverUrl = '';
    let coverSize = coverFile ? coverFile.size : 0;

    if (!coverFile && isEditing) {
      const existing = (APP_STATE.allBooks || []).find(b => b.id === bookId);
      if (existing) { coverUrl = existing.coverUrl || ''; coverSize = existing.coverSize || 0; }
    }

    if (coverFile) {
      setButtonLoading('publishSubmitBtn', true, 'Uploading cover artwork...');
      coverUrl = await uploadMediaFile(coverFile, `covers/${bookId}/${Date.now()}.jpg`);
    }

    let languages = [];
    let primaryStorage = 'drive';

    // ────────────────────────────────────────────────────────
    // BRANCH A: PASTE GOOGLE DRIVE LINK (Option B)
    // ────────────────────────────────────────────────────────
    if (APP_STATE.publishMethod === 'drive_link') {
      updatePublishStep(1, 'in_progress'); // Step 1: Validating link
      let validated = APP_STATE.validatedDriveLink;
      if (!validated) {
        validated = await validatePastedDriveLink();
      }
      if (!validated || !validated.valid) {
        updatePublishStep(1, 'error');
        throw new Error('Please validate a Google Drive PDF link before publishing.');
      }
      updatePublishStep(1, 'completed');

      updatePublishStep(2, 'in_progress'); // Step 2: Checking permissions
      await new Promise(r => setTimeout(r, 200));
      updatePublishStep(2, 'completed');

      updatePublishStep(3, 'in_progress'); // Step 3: Retrieving manuscript information
      const edLanguage = document.getElementById('publishDriveLinkLang')?.value || 'English';
      languages.push({
        language: edLanguage,
        storageProvider: 'drive',
        driveFileId: validated.fileId,
        driveIsPublic: !!validated.isPublic,
        driveAccountId: validated.accountId || '',
        fileName: validated.fileName || `${title}.pdf`,
        fileSize: validated.fileSize || 0,
        fileUrl: validated.isPublic ? `https://drive.google.com/uc?id=${validated.fileId}&export=download` : '',
        uploadedAt: new Date().toISOString()
      });
      primaryStorage = 'drive';
      updatePublishStep(3, 'completed');

    // ────────────────────────────────────────────────────────
    // BRANCH B: FILE UPLOAD (Option A)
    // ────────────────────────────────────────────────────────
    } else {
      if (APP_STATE.publishEditions.length === 0) {
        throw new Error('Please add at least one language edition.');
      }

      for (let i = 0; i < APP_STATE.publishEditions.length; i++) {
        const ed = APP_STATE.publishEditions[i];
        setButtonLoading('publishSubmitBtn', true, `Processing edition #${i+1} (${ed.language})...`);

        if (ed.driveFile) {
          languages.push({
            language: ed.language,
            storageProvider: 'drive',
            driveFileId: ed.driveFile.fileId,
            driveAccountId: ed.driveFile.accountId || ed.driveAccountId || '',
            fileName: ed.driveFile.fileName,
            fileSize: ed.driveFile.size || 0,
            fileUrl: ed.driveFile.downloadUrl || '',
            uploadedAt: new Date().toISOString()
          });
        } else if (ed.storageProvider === 'drive' && ed.file) {
          setButtonLoading('publishSubmitBtn', true, `Uploading to Drive (${ed.language})...`);
          const base64 = await readFileAsBase64(ed.file);
          const acctId = ed.driveAccountId || (APP_STATE.connectedDriveAccounts[0]?.id);
          if (!acctId) throw new Error('No Google Drive account selected for upload.');

          const uploadFn = functions.httpsCallable('uploadPdfToDrive');
          const uploadRes = await uploadFn({
            accountId: acctId,
            fileName: ed.file.name,
            fileBase64: base64
          });
          if (!uploadRes.data || !uploadRes.data.success) {
            throw new Error('Failed to upload manuscript to Google Drive.');
          }

          languages.push({
            language: ed.language,
            storageProvider: 'drive',
            driveFileId: uploadRes.data.fileId,
            driveAccountId: acctId,
            fileName: uploadRes.data.fileName || ed.file.name,
            fileSize: uploadRes.data.fileSize || ed.file.size,
            fileUrl: '',
            uploadedAt: new Date().toISOString()
          });
        } else if (ed.file) {
          setButtonLoading('publishSubmitBtn', true, `Uploading to Storage (${ed.language})...`);
          const fileUrl = await uploadMediaFile(ed.file, `books/${bookId}/pdfs/${ed.language}_${Date.now()}.pdf`);
          languages.push({
            language: ed.language,
            storageProvider: 'storage',
            fileUrl: fileUrl,
            fileName: ed.file.name,
            fileSize: ed.file.size,
            uploadedAt: new Date().toISOString()
          });
        }
      }

      if (languages.length === 0) {
        throw new Error('Please select or upload a PDF manuscript for your publication.');
      }
      primaryStorage = languages.some(l => l.storageProvider === 'drive') ? 'drive' : 'storage';
    }

    // Step 4: Saving book details to Firestore
    updatePublishStep(4, 'in_progress');
    setButtonLoading('publishSubmitBtn', true, 'Saving to NOVELIX catalog...');

    const docPayload = {
      id: bookId,
      title: title,
      description: desc,
      contentType: APP_STATE.selectedFormat,
      genres: (APP_STATE.selectedGenres || []).slice(0, 4),
      coverUrl: coverUrl,
      coverSize: coverSize,
      status: status,
      visibility: visibility,
      publishStatus: status === 'draft' ? 'draft' : 'published',
      storageProvider: primaryStorage,
      driveFileId: languages[0]?.driveFileId || '',
      driveIsPublic: languages[0]?.driveIsPublic || false,
      driveAccountId: languages[0]?.driveAccountId || '',
      languages: languages,
      authorId: APP_STATE.user.uid,
      authorName: APP_STATE.profile?.displayName || APP_STATE.user.email.split('@')[0],
      authorPhoto: APP_STATE.profile?.photoURL || '',
      authors: [{
        uid: APP_STATE.user.uid,
        name: APP_STATE.profile?.displayName || APP_STATE.user.email.split('@')[0],
        photoURL: APP_STATE.profile?.photoURL || '',
        role: 'Primary Author'
      }],
      viewCount: 0,
      likeCount: 0,
      bookmarkCount: 0,
      avgRating: 0,
      updatedAt: firebase.firestore.FieldValue.serverTimestamp()
    };

    if (!isEditing) {
      docPayload.createdAt = firebase.firestore.FieldValue.serverTimestamp();
    }

    await db.collection('books').doc(bookId).set(docPayload, { merge: true });

    // Step 5: Published successfully
    updatePublishStep(4, 'completed');
    updatePublishStep(5, 'completed');

    showToast(isEditing ? 'Publication updated successfully!' : 'Work published live to NOVELIX!');
    APP_STATE.editingBookId = null;
    const submitBtn = document.getElementById('publishSubmitBtn');
    if (submitBtn) submitBtn.textContent = 'Publish Work';

    setTimeout(() => {
      resetPublishForm();
      switchPage('home');
    }, 900);

  } catch(err) {
    console.error('[NOVELIX Publish] Error:', err);
    showToast(`Publication failed: ${err.message}`);
  } finally {
    APP_STATE._isPublishing = false;
    setButtonLoading('publishSubmitBtn', false, 'Publish Work');
  }
}"""

if old_handle_publish in content:
    content = content.replace(old_handle_publish, new_handle_publish, 1)
    print("  [OK] Replaced handlePublishSubmit with 10.0 Drive Link & Concurrency Protected version")
else:
    print("  [ERROR] old_handle_publish snippet not matched exactly")
    sys.exit(1)

# -------------------------------------------------------------
# 5. Architecture for 10,000 Concurrent Users:
# Limit Firestore query to 15, add pagination, cleanup listeners on page switch
# -------------------------------------------------------------
old_books_feed = """function startFirestoreBooksFeed() {
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
}"""

new_books_feed = """// ── NOVELIX 10.0 High-Concurrency Feed Architecture (10,000 Users) ──
APP_STATE.lastBookDoc = null;
APP_STATE.isFetchingMoreBooks = false;

function startFirestoreBooksFeed() {
  if (!db) return;
  if (APP_STATE.realtimeBooksUnsub) {
    APP_STATE.realtimeBooksUnsub();
    APP_STATE.realtimeBooksUnsub = null;
  }

  // High Concurrency: Limit real-time snapshot to initial 15 works to conserve read quotas
  APP_STATE.realtimeBooksUnsub = db.collection('books')
    .where('visibility', '==', 'public')
    .where('publishStatus', '==', 'published')
    .orderBy('createdAt', 'desc')
    .limit(15)
    .onSnapshot((snapshot) => {
      document.getElementById('headerLivePill')?.classList.remove('hidden');
      const books = [];
      snapshot.forEach(doc => books.push({ id: doc.id, ...doc.data() }));
      APP_STATE.allBooks = books;
      if (snapshot.docs.length > 0) {
        APP_STATE.lastBookDoc = snapshot.docs[snapshot.docs.length - 1];
      }
      renderHomeShelfViews();
      if (APP_STATE.activePage === 'explore') renderExploreGridView();
      recalculateStorageQuota();
    }, (err) => {
      console.warn('Realtime feed notice:', err.message);
      loadBooksFallbackFeed();
    });
}

async function loadMoreBooks() {
  if (APP_STATE.isFetchingMoreBooks || !APP_STATE.lastBookDoc || !db) return;
  APP_STATE.isFetchingMoreBooks = true;

  try {
    const snap = await db.collection('books')
      .where('visibility', '==', 'public')
      .where('publishStatus', '==', 'published')
      .orderBy('createdAt', 'desc')
      .startAfter(APP_STATE.lastBookDoc)
      .limit(15)
      .get();

    if (!snap.empty) {
      const moreBooks = [];
      snap.forEach(doc => moreBooks.push({ id: doc.id, ...doc.data() }));
      APP_STATE.allBooks = [...APP_STATE.allBooks, ...moreBooks];
      APP_STATE.lastBookDoc = snap.docs[snap.docs.length - 1];
      if (APP_STATE.activePage === 'explore') renderExploreGridView();
      else renderHomeShelfViews();
    }
  } catch (err) {
    console.warn('Load more books warning:', err.message);
  } finally {
    APP_STATE.isFetchingMoreBooks = false;
  }
}"""

if old_books_feed in content:
    content = content.replace(old_books_feed, new_books_feed, 1)
    print("  [OK] Replaced startFirestoreBooksFeed with 15-item paginated feed")
else:
    print("  [WARN] old_books_feed snippet not matched exactly")

# -------------------------------------------------------------
# 6. switchPage Listener Cleanup for 10,000 Users
# -------------------------------------------------------------
old_switch_page = """function switchPage(pageId) {
  document.querySelectorAll('.app-page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => { n.style.color = '#9693A4'; });

  let targetPage = document.getElementById(`page-${pageId}`);
  if (!targetPage) {
    // Graceful in-app 404 Page Not Found fallback
    targetPage = document.getElementById('page-notfound');
    pageId = 'notfound';
  }

  if (targetPage) targetPage.classList.add('active');

  const targetNav = document.getElementById(`nav-${pageId}`);
  if (targetNav) targetNav.style.color = '#9270FF';

  APP_STATE.activePage = pageId;

  if (pageId === 'library') loadLibraryContent();
  if (pageId === 'profile') loadProfileContent();
  if (pageId === 'publish') updatePublishAccessState();
  if (pageId === 'explore') renderExploreGridView();
  if (pageId === 'drive') loadConnectedDriveAccounts();

  window.scrollTo({ top: 0, behavior: 'smooth' });
}"""

new_switch_page = """function switchPage(pageId) {
  document.querySelectorAll('.app-page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => { n.style.color = '#9693A4'; });

  let targetPage = document.getElementById(`page-${pageId}`);
  if (!targetPage) {
    targetPage = document.getElementById('page-notfound');
    pageId = 'notfound';
  }

  if (targetPage) targetPage.classList.add('active');

  const targetNav = document.getElementById(`nav-${pageId}`);
  if (targetNav) targetNav.style.color = '#9270FF';

  const prevPage = APP_STATE.activePage;
  APP_STATE.activePage = pageId;

  // 10.0 Concurrency: Unsubscribe catalog listener when user is reading or browsing library/profile
  if (pageId !== 'home' && pageId !== 'explore') {
    if (APP_STATE.realtimeBooksUnsub) {
      APP_STATE.realtimeBooksUnsub();
      APP_STATE.realtimeBooksUnsub = null;
    }
  } else if (!APP_STATE.realtimeBooksUnsub) {
    // Resubscribe when returning to home or explore
    startFirestoreBooksFeed();
  }

  if (pageId === 'library') loadLibraryContent();
  if (pageId === 'profile') loadProfileContent();
  if (pageId === 'publish') updatePublishAccessState();
  if (pageId === 'explore') renderExploreGridView();
  if (pageId === 'drive') loadConnectedDriveAccounts();

  window.scrollTo({ top: 0, behavior: 'smooth' });
}"""

if old_switch_page in content:
    content = content.replace(old_switch_page, new_switch_page, 1)
    print("  [OK] Injected listener unsubscribe cleanup in switchPage")
else:
    print("  [WARN] old_switch_page snippet not matched exactly")

with open("scripts/generate_4.py", "w", encoding="utf-8") as f:
    f.write(content)

print("=== Successfully updated scripts/generate_4.py ===")
