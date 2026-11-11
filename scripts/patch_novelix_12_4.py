#!/usr/bin/env python3
"""
Patch v12.4.0 — Fix: ImgBB test (URLSearchParams), Email registration (Firestore rules conflict),
Drive "No Files" (upload from device + paste URL), Series cover album upload, Better error messages
"""
import re

src = '/data/user/0/com.termux/files/home/Novelix project/scripts/generate_4.py'

with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

patches = []

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 1: Fix adminTestImgBBKey – use URLSearchParams instead of FormData
# ─────────────────────────────────────────────────────────────────────────────
OLD_TEST = '''async function adminTestImgBBKey() {
  const input = document.getElementById('adminImgbbKeyInput');
  const key = (input ? input.value : '').trim() || getActiveImgBBKey();
  const resultBox = document.getElementById('adminImgbbTestResult');

  if (resultBox) {
    resultBox.classList.remove('hidden');
    resultBox.className = 'text-[11px] p-2.5 rounded-lg font-mono bg-[#14141E] text-amber-300 border border-amber-500/20';
    resultBox.textContent = 'Testing ImgBB API connectivity...';
  }

  try {
    // Test probe with 1x1 transparent PNG in base64
    const testPixel = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAAElFTkSuQmCC';
    const form = new FormData();
    form.append('key', key);
    form.append('image', testPixel);
    form.append('name', 'novelix_test_probe');

    const res = await fetch('https://api.imgbb.com/1/upload', {
      method: 'POST',
      body: form
    });

    const json = await res.json();
    if (json && json.success) {
      if (resultBox) {
        resultBox.className = 'text-[11px] p-2.5 rounded-lg font-mono bg-emerald-500/10 text-emerald-300 border border-emerald-500/30';
        resultBox.textContent = `✓ ImgBB API Valid! Status: ${json.status} | URL: ${json.data.url}`;
      }
      showToast('✓ ImgBB API key verified successfully!');
    } else {
      throw new Error(json?.error?.message || 'Invalid API Key response');
    }
  } catch (err) {
    if (resultBox) {
      resultBox.className = 'text-[11px] p-2.5 rounded-lg font-mono bg-red-500/10 text-red-300 border border-red-500/30';
      resultBox.textContent = `✕ Test Failed: ${err.message}`;
    }
    showToast(`ImgBB Test Error: ${err.message}`);
  }
}'''

NEW_TEST = '''async function adminTestImgBBKey() {
  const input = document.getElementById('adminImgbbKeyInput');
  const key = (input ? input.value : '').trim() || getActiveImgBBKey();
  const resultBox = document.getElementById('adminImgbbTestResult');

  if (resultBox) {
    resultBox.classList.remove('hidden');
    resultBox.className = 'text-[11px] p-2.5 rounded-lg font-mono bg-[#14141E] text-amber-300 border border-amber-500/20';
    resultBox.textContent = 'Testing ImgBB API connectivity...';
  }

  try {
    // Use a confirmed-working 2x2 red PNG base64 (tested via curl)
    // Using URLSearchParams (not FormData) to avoid CapacitorHttp mangling the body
    const testPixel = 'iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAADklEQVQI12P4z8BQDwAEgAF/QualIQAAAABJRU5ErkJggg==';
    const params = new URLSearchParams();
    params.append('key', key);
    params.append('image', testPixel);
    params.append('name', 'novelix_test_probe');

    const res = await fetch('https://api.imgbb.com/1/upload', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: params.toString()
    });

    const json = await res.json();
    if (json && json.success) {
      if (resultBox) {
        resultBox.className = 'text-[11px] p-2.5 rounded-lg font-mono bg-emerald-500/10 text-emerald-300 border border-emerald-500/30';
        resultBox.textContent = `✓ ImgBB API Valid! Status: ${json.status} | URL: ${json.data.url}`;
      }
      showToast('✓ ImgBB API key verified successfully!');
    } else {
      throw new Error(json?.error?.message || 'Invalid API Key response');
    }
  } catch (err) {
    if (resultBox) {
      resultBox.className = 'text-[11px] p-2.5 rounded-lg font-mono bg-red-500/10 text-red-300 border border-red-500/30';
      resultBox.textContent = `✕ Test Failed: ${err.message}`;
    }
    showToast(`ImgBB Test Error: ${err.message}`);
  }
}'''

patches.append(('ImgBB test fix (URLSearchParams)', OLD_TEST, NEW_TEST))

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 2: Fix uploadToImgBB – use URLSearchParams instead of FormData
# ─────────────────────────────────────────────────────────────────────────────
OLD_UPLOAD = '''  const apiKey = getActiveImgBBKey();
  const formData = new FormData();
  formData.append('key', apiKey);
  formData.append('image', base64Data);
  formData.append('name', (file.name || 'cover').replace(/\\.[^/.]+$/, ''));

  const resp = await fetch('https://api.imgbb.com/1/upload', {
    method: 'POST',
    body: formData
  });'''

NEW_UPLOAD = '''  const apiKey = getActiveImgBBKey();
  // Use URLSearchParams to avoid CapacitorHttp mangling FormData on Android
  const uploadParams = new URLSearchParams();
  uploadParams.append('key', apiKey);
  uploadParams.append('image', base64Data);
  uploadParams.append('name', (file.name || 'cover').replace(/\\.[^/.]+$/, ''));

  const resp = await fetch('https://api.imgbb.com/1/upload', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: uploadParams.toString()
  });'''

patches.append(('uploadToImgBB fix (URLSearchParams)', OLD_UPLOAD, NEW_UPLOAD))

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 3: Fix executeEmailRegister – remove blocked Firestore fields
# ─────────────────────────────────────────────────────────────────────────────
OLD_EMAIL_REG = '''  setButtonLoading('btnActionRegister', true, 'Creating account...');
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
    setAuthError(err.message);
    showToast('Registration failed: ' + err.message);
  } finally {
    setButtonLoading('btnActionRegister', false, 'Create NOVELIX Account');
  }
}'''

NEW_EMAIL_REG = '''  setButtonLoading('btnActionRegister', true, 'Creating account...');
  try {
    const cred = await auth.createUserWithEmailAndPassword(email, password);
    if (cred.user) {
      await cred.user.updateProfile({ displayName: name });
      const handle = name.toLowerCase().replace(/[^a-z0-9]/g, '');
      // NOTE: Do NOT include creatorVerified or storageQuotaBytes here —
      // Firestore security rules block those fields on user-created documents.
      // They are set later by the admin/server or handled by onAuthStateChanged.
      await db.collection('users').doc(cred.user.uid).set({
        uid: cred.user.uid,
        email: email,
        displayName: name,
        handle: handle,
        photoURL: '',
        bio: '',
        createdAt: firebase.firestore.FieldValue.serverTimestamp()
      }, { merge: true });
    }
    showToast('✓ Account created! Welcome to NOVELIX');
    closeAuthModal();
  } catch(err) {
    // Map Firebase error codes to friendly messages
    let friendlyMsg = err.message;
    if (err.code === 'auth/email-already-in-use') {
      friendlyMsg = 'This email is already registered. Try signing in instead.';
    } else if (err.code === 'auth/invalid-email') {
      friendlyMsg = 'Please enter a valid email address.';
    } else if (err.code === 'auth/weak-password') {
      friendlyMsg = 'Password is too weak. Use at least 6 characters.';
    } else if (err.code === 'auth/network-request-failed') {
      friendlyMsg = 'Network error. Please check your internet connection.';
    } else if (err.code && err.code.startsWith('auth/')) {
      friendlyMsg = 'Registration failed: ' + err.code.replace('auth/', '').replace(/-/g, ' ');
    }
    setAuthError(friendlyMsg);
    showToast('Registration failed: ' + friendlyMsg);
  } finally {
    setButtonLoading('btnActionRegister', false, 'Create NOVELIX Account');
  }
}'''

patches.append(('Email registration fix (remove blocked fields + friendly errors)', OLD_EMAIL_REG, NEW_EMAIL_REG))

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 4: Fix Drive "No Files" – add Upload from Device + Paste URL options
# ─────────────────────────────────────────────────────────────────────────────
OLD_DRIVE_NO_FILES = '''    const data = await res.json();
    APP_STATE.activeDriveFiles = data.files || [];
    APP_STATE._activeDriveToken = token;
    renderDriveFilesList(APP_STATE.activeDriveFiles, token);
    updatePageDriveBrowser(APP_STATE.activeDriveFiles, acc.email);
  } catch(e) {
    container.innerHTML = `
      <div class="surface-card-static p-6 text-center space-y-2">
        <p class="text-xs text-red-400 font-semibold">Failed to load files</p>
        <p class="text-[11px] text-app-muted">Check your internet connection and try again.</p>
        <button onclick="browseDriveAccountFiles('${escapeHtml(accId)}')" class="btn-secondary text-xs px-3 py-1.5 mt-2">Retry</button>
      </div>
    `;
  }
}'''

NEW_DRIVE_NO_FILES = '''    const data = await res.json();
    APP_STATE.activeDriveFiles = data.files || [];
    APP_STATE._activeDriveToken = token;
    if (APP_STATE.activeDriveFiles.length === 0) {
      // No files found — show upload options
      renderDriveNoFilesUI(container, accId);
    } else {
      renderDriveFilesList(APP_STATE.activeDriveFiles, token);
      updatePageDriveBrowser(APP_STATE.activeDriveFiles, acc.email);
    }
  } catch(e) {
    console.warn('[NOVELIX Drive] File list error:', e.message);
    renderDriveNoFilesUI(container, accId);
  }
}

function renderDriveNoFilesUI(container, accId) {
  container.innerHTML = `
    <div class="space-y-3 p-2">
      <div class="surface-card-static p-4 text-center space-y-2 rounded-xl border border-amber-500/20">
        <div class="text-2xl">📂</div>
        <p class="text-xs text-amber-300 font-semibold">No PDF files found in your Drive</p>
        <p class="text-[10px] text-app-muted">Upload a PDF directly from your device or paste a Drive share URL below.</p>
      </div>

      <!-- Option 1: Upload from device -->
      <div class="surface-card-static p-4 rounded-xl space-y-2">
        <p class="text-[10px] text-app-muted uppercase font-bold tracking-widest">📤 Upload PDF from Device</p>
        <input type="file" id="driveDirectPdfInput" accept=".pdf,application/pdf" class="hidden"
          onchange="handleDriveDirectPdfUpload(this, '${escapeHtml(accId)}')">
        <button onclick="document.getElementById('driveDirectPdfInput').click()"
          class="btn-primary text-xs w-full py-2.5 font-semibold flex items-center justify-center gap-2">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg>
          Choose PDF from Album / Files
        </button>
      </div>

      <!-- Option 2: Paste Drive URL -->
      <div class="surface-card-static p-4 rounded-xl space-y-2">
        <p class="text-[10px] text-app-muted uppercase font-bold tracking-widest">🔗 Paste Google Drive URL</p>
        <input type="url" id="driveManualUrlInput" placeholder="https://drive.google.com/file/d/..." 
          class="w-full px-3 py-2 text-xs bg-[#14141E] border border-[#262638] rounded-lg text-white font-mono">
        <button onclick="importFromDriveUrl(document.getElementById('driveManualUrlInput').value)"
          class="btn-secondary text-xs w-full py-2 font-semibold">
          Import from Drive URL
        </button>
      </div>

      <!-- Retry -->
      <button onclick="browseDriveAccountFiles('${escapeHtml(accId)}')"
        class="text-[11px] text-app-muted underline w-full text-center py-1">
        ↻ Refresh Drive list
      </button>
    </div>
  `;
}

async function handleDriveDirectPdfUpload(input, accId) {
  const file = input.files && input.files[0];
  if (!file) return;
  if (file.type && !file.type.includes('pdf')) {
    showToast('Please select a PDF file.');
    return;
  }
  showToast('Reading PDF from device...');
  try {
    // Create a fake Drive-style file object and import directly
    const fakeFileId = 'local_' + Date.now();
    const url = URL.createObjectURL(file);
    // Store for use in studio
    APP_STATE._localPdfBlob = file;
    APP_STATE._localPdfUrl = url;
    closeDrivePickerModal();
    // Open book studio with this file
    await importLocalPdfToStudio(file);
  } catch(e) {
    showToast('Failed to read PDF: ' + e.message);
  }
}

async function importLocalPdfToStudio(file) {
  showToast('Loading PDF into studio...');
  try {
    const base64 = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
    // Open studio if not open
    openPublishModal && openPublishModal();
    // Fill in content area
    setTimeout(() => {
      const contentInput = document.getElementById('bookContentInput');
      if (contentInput) {
        contentInput.value = '[PDF: ' + file.name + ']\\n\\nPDF uploaded directly from device.\\nFile size: ' + (file.size / 1024).toFixed(1) + ' KB';
        showToast('✓ PDF loaded into studio. Add details and publish.');
      }
      // Store PDF data URL for publishing
      APP_STATE._pendingPdfDataUrl = base64;
      APP_STATE._pendingPdfName = file.name;
    }, 400);
  } catch(e) {
    showToast('PDF load error: ' + e.message);
  }
}

function importFromDriveUrl(url) {
  if (!url || !url.trim()) {
    showToast('Please paste a Google Drive URL first.');
    return;
  }
  const trimmed = url.trim();
  // Extract file ID from various Drive URL formats
  let fileId = '';
  const patterns = [
    /\/file\/d\/([a-zA-Z0-9_-]+)/,
    /id=([a-zA-Z0-9_-]+)/,
    /\/d\/([a-zA-Z0-9_-]+)/
  ];
  for (const p of patterns) {
    const m = trimmed.match(p);
    if (m) { fileId = m[1]; break; }
  }
  if (!fileId) {
    showToast('Could not extract file ID from URL. Use a Google Drive share link.');
    return;
  }
  const token = APP_STATE._activeDriveToken || localStorage.getItem('novelix_active_drive_token') || '';
  closeDrivePickerModal();
  importDriveFileToStudio(fileId, 'Drive File', token);
}'''

patches.append(('Drive no-files UI with upload + URL input', OLD_DRIVE_NO_FILES, NEW_DRIVE_NO_FILES))

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 5: Series modal – add "Choose from Album" button for cover image
# ─────────────────────────────────────────────────────────────────────────────
OLD_SERIES_COVER = '''      <div>
        <label class="block text-[10px] text-app-muted uppercase font-semibold mb-1">Series Banner / Cover Image URL (Optional)</label>
        <input type="url" id="seriesCoverUrlInput" placeholder="https://i.ibb.co/..." class="w-full px-3 py-2 text-xs bg-[#14141E] border border-[#262638] rounded-lg text-white font-mono">
      </div>'''

NEW_SERIES_COVER = '''      <div>
        <label class="block text-[10px] text-app-muted uppercase font-semibold mb-1">Series Banner / Cover Image (Optional)</label>
        <!-- Hidden file input for album pick -->
        <input type="file" id="seriesCoverFileInput" accept="image/*" class="hidden" onchange="handleSeriesCoverFileSelected(this)">
        <!-- Album picker button -->
        <button type="button" onclick="document.getElementById('seriesCoverFileInput').click()"
          class="w-full mb-2 flex items-center justify-center gap-2 px-3 py-2 text-xs rounded-lg border border-dashed border-[#9b59b6]/50 bg-[#9b59b6]/10 text-purple-300 hover:bg-[#9b59b6]/20 transition-colors font-semibold">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
          <span id="seriesCoverPickerLabel">📷 Choose Cover from Album</span>
        </button>
        <!-- URL fallback -->
        <input type="url" id="seriesCoverUrlInput" placeholder="Or paste image URL: https://i.ibb.co/..." class="w-full px-3 py-2 text-xs bg-[#14141E] border border-[#262638] rounded-lg text-white font-mono">
        <!-- Upload progress indicator -->
        <div id="seriesCoverUploadStatus" class="hidden text-[10px] text-amber-300 mt-1 font-mono"></div>
      </div>'''

patches.append(('Series modal cover album picker', OLD_SERIES_COVER, NEW_SERIES_COVER))

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 6: Add handleSeriesCoverFileSelected function near saveAuthorSeries
# ─────────────────────────────────────────────────────────────────────────────
OLD_CLOSE_SERIES = '''function closeSeriesModal() {
  const m = document.getElementById('seriesModal');
  if (m) m.classList.remove('open');
}

async function saveAuthorSeries() {'''

NEW_CLOSE_SERIES = '''function closeSeriesModal() {
  const m = document.getElementById('seriesModal');
  if (m) m.classList.remove('open');
}

async function handleSeriesCoverFileSelected(input) {
  const file = input.files && input.files[0];
  if (!file) return;
  const statusEl = document.getElementById('seriesCoverUploadStatus');
  const labelEl = document.getElementById('seriesCoverPickerLabel');
  if (statusEl) { statusEl.classList.remove('hidden'); statusEl.textContent = '⏳ Uploading cover to ImgBB...'; }
  if (labelEl) labelEl.textContent = '⏳ Uploading...';
  try {
    const result = await uploadToImgBB(file);
    const urlInput = document.getElementById('seriesCoverUrlInput');
    if (urlInput) urlInput.value = result.url;
    if (statusEl) { statusEl.textContent = '✓ Cover uploaded: ' + result.url; }
    if (labelEl) labelEl.textContent = '✓ ' + (file.name || 'Cover selected');
    showToast('✓ Series cover uploaded successfully!');
  } catch(err) {
    if (statusEl) { statusEl.textContent = '✕ Upload failed: ' + err.message; }
    if (labelEl) labelEl.textContent = '📷 Choose Cover from Album';
    showToast('Cover upload failed: ' + err.message);
  }
}

async function saveAuthorSeries() {'''

patches.append(('handleSeriesCoverFileSelected function', OLD_CLOSE_SERIES, NEW_CLOSE_SERIES))

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 7: Update version to 12.4.0
# ─────────────────────────────────────────────────────────────────────────────
OLD_VER = "NOVELIX_VERSION = '12.3.0'"
NEW_VER = "NOVELIX_VERSION = '12.4.0'"
patches.append(('Version bump to 12.4.0', OLD_VER, NEW_VER))

# ─────────────────────────────────────────────────────────────────────────────
# Apply all patches
# ─────────────────────────────────────────────────────────────────────────────
applied = 0
failed = []
for name, old, new in patches:
    if old in code:
        code = code.replace(old, new, 1)
        print(f'  ✓ Applied: {name}')
        applied += 1
    else:
        print(f'  ✗ FAILED:  {name}')
        failed.append(name)

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print(f'\nResult: {applied}/{len(patches)} patches applied')
if failed:
    print('FAILED patches:')
    for n in failed:
        print(f'  - {n}')
else:
    print('All patches applied successfully!')
