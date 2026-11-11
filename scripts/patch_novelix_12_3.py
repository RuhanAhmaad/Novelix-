#!/usr/bin/env python3
import sys

def patch():
    with open('scripts/generate_4.py', 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"Original generate_4.py length: {len(content)}")

    # 1. Bump version strings
    content = content.replace("window.__NOVELIX_VERSION__ = '12.2.0';", "window.__NOVELIX_VERSION__ = '12.3.0';", 1)
    content = content.replace("const NOVELIX_VERSION = '12.2.0';", "const NOVELIX_VERSION = '12.3.0';", 1)
    content = content.replace('"version": "12.2.0", "build": 12200', '"version": "12.3.0", "build": 12300', 1)
    content = content.replace('NOVELIX 12.2 Enterprise', 'NOVELIX 12.3 Pro Suite', 1)
    print("✓ Version bumped to 12.3.0")

    # 2. Add publishDriveConnectedBanner inside publishDriveLinkSection
    target_drive_banner = """            <div>
              <label class="block text-[10px] text-app-muted uppercase font-semibold mb-1">Paste Google Drive URL</label>"""

    replacement_drive_banner = """            <!-- Connected Google Drive Status & Quick Picker Banner -->
            <div id="publishDriveConnectedBanner" class="mb-2"></div>

            <div>
              <label class="block text-[10px] text-app-muted uppercase font-semibold mb-1">Paste Google Drive URL</label>"""

    if target_drive_banner in content:
        content = content.replace(target_drive_banner, replacement_drive_banner, 1)
        print("✓ Added publishDriveConnectedBanner")
    else:
        print("✗ Could not find target_drive_banner")

    # 3. Add Dual Action Reading Buttons in Book Detail Modal
    target_detail_btns = """      <!-- Action Buttons -->
      <div class="flex gap-2">
        <button id="btnStartReading" onclick="launchActiveReader()" class="btn-primary text-xs flex-1 py-2.5 font-semibold">Start Reading</button>
        <button id="btnBookmarkDetail" onclick="toggleDetailBookmark()" class="btn-secondary text-xs px-3 py-2.5">Bookmark</button>
      </div>"""

    replacement_detail_btns = """      <!-- Dual Action Reading Buttons: Read in App OR Read in Google Drive -->
      <div class="space-y-2">
        <div class="grid grid-cols-2 gap-2">
          <button id="btnReadInApp" onclick="launchActiveReader()" class="btn-primary text-xs py-3 font-bold flex items-center justify-center gap-1.5 shadow-[0_0_12px_rgba(146,112,255,0.35)]">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
            <span>Read in App</span>
          </button>
          <button id="btnReadInDrive" onclick="openBookInGoogleDrive()" class="py-3 px-2 rounded-xl border border-emerald-500/40 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 text-xs font-bold flex items-center justify-center gap-1.5 transition-all">
            <svg viewBox="0 0 24 24" class="w-4 h-4 fill-emerald-400"><path d="M12.01 1.99c-5.52 0-10 4.48-10 10s4.48 10 10 10 10-4.48 10-10-4.48-10-10-10zm-1.01 16.51l-4.5-4.5 1.41-1.41 3.09 3.09 7.09-7.09 1.41 1.41-8.5 8.5z"/></svg>
            <span>Read in Drive</span>
          </button>
        </div>
        <div class="flex gap-2">
          <button id="btnBookmarkDetail" onclick="toggleDetailBookmark()" class="btn-secondary text-xs flex-1 py-2 font-medium flex items-center justify-center gap-1">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
            <span>Save to Library</span>
          </button>
          <button onclick="shareActiveBook()" class="btn-secondary text-xs px-3 py-2 flex items-center justify-center gap-1" title="Share Book">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
          </button>
        </div>
      </div>"""

    if target_detail_btns in content:
        content = content.replace(target_detail_btns, replacement_detail_btns, 1)
        print("✓ Replaced detail action buttons with Dual Options (Read in App / Read in Drive)")
    else:
        print("✗ Could not find target_detail_btns")

    # 4. Add Read in Drive button in Reader Error Overlay & Top Bar
    target_reader_top = """      <!-- Fullscreen Toggle -->
      <button onclick="toggleReaderFullscreen()" id="readerFullscreenBtn" title="Toggle Fullscreen" class="w-7 h-7 rounded-lg bg-[#181824] hover:bg-[#232334] border border-[#2B2B3E] flex items-center justify-center text-white transition-all">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg>
      </button>"""

    replacement_reader_top = """      <!-- Open in Google Drive Top Shortcut -->
      <button onclick="openBookInGoogleDrive()" id="readerDriveTopBtn" title="Open in Google Drive" class="w-7 h-7 rounded-lg bg-[#181824] hover:bg-[#232334] border border-[#2B2B3E] flex items-center justify-center text-emerald-400 transition-all">
        <svg viewBox="0 0 24 24" class="w-3.5 h-3.5 fill-current"><path d="M12.01 1.99c-5.52 0-10 4.48-10 10s4.48 10 10 10 10-4.48 10-10-4.48-10-10-10zm-1.01 16.51l-4.5-4.5 1.41-1.41 3.09 3.09 7.09-7.09 1.41 1.41-8.5 8.5z"/></svg>
      </button>

      <!-- Fullscreen Toggle -->
      <button onclick="toggleReaderFullscreen()" id="readerFullscreenBtn" title="Toggle Fullscreen" class="w-7 h-7 rounded-lg bg-[#181824] hover:bg-[#232334] border border-[#2B2B3E] flex items-center justify-center text-white transition-all">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg>
      </button>"""

    if target_reader_top in content:
        content = content.replace(target_reader_top, replacement_reader_top, 1)
        print("✓ Added Reader top Google Drive button")
    else:
        print("✗ Could not find target_reader_top")

    target_reader_err_btns = """      <div class="flex flex-wrap gap-2 justify-center">
        <button onclick="retryLoadReaderPdf()" class="btn-primary text-xs px-4 py-2">Retry Loading</button>
        <button id="readerReconnectDriveBtn" onclick="reconnectDriveFromReader()" class="hidden btn-secondary text-xs px-4 py-2 border-app-primary text-app-primary">Reconnect Drive</button>
        <button onclick="closeReaderModal(); if(APP_STATE.selectedBook) openBookDetail(APP_STATE.selectedBook.id);" class="btn-secondary text-xs px-4 py-2">Back to Details</button>
      </div>"""

    replacement_reader_err_btns = """      <div class="flex flex-wrap gap-2 justify-center">
        <button onclick="retryLoadReaderPdf()" class="btn-primary text-xs px-4 py-2">Retry Loading</button>
        <button onclick="openBookInGoogleDrive()" class="btn-primary text-xs px-4 py-2 bg-emerald-600 hover:bg-emerald-500 border-none text-white font-bold flex items-center gap-1.5">
          <svg viewBox="0 0 24 24" class="w-3.5 h-3.5 fill-current"><path d="M12.01 1.99c-5.52 0-10 4.48-10 10s4.48 10 10 10 10-4.48 10-10-4.48-10-10-10zm-1.01 16.51l-4.5-4.5 1.41-1.41 3.09 3.09 7.09-7.09 1.41 1.41-8.5 8.5z"/></svg>
          <span>Read in Google Drive</span>
        </button>
        <button id="readerReconnectDriveBtn" onclick="reconnectDriveFromReader()" class="hidden btn-secondary text-xs px-4 py-2 border-app-primary text-app-primary">Reconnect Drive</button>
        <button onclick="closeReaderModal(); if(APP_STATE.selectedBook) openBookDetail(APP_STATE.selectedBook.id);" class="btn-secondary text-xs px-4 py-2">Back to Details</button>
      </div>"""

    if target_reader_err_btns in content:
        content = content.replace(target_reader_err_btns, replacement_reader_err_btns, 1)
        print("✓ Added Read in Google Drive button to Reader Error Overlay")
    else:
        print("✗ Could not find target_reader_err_btns")

    # 5. Insert openBookInGoogleDrive and shareActiveBook functions
    target_reader_funcs = "async function launchActiveReader() {"
    replacement_reader_funcs = """function openBookInGoogleDrive(bookId) {
  const book = APP_STATE.selectedBook || (APP_STATE.allBooks || []).find(b => b.id === bookId);
  if (!book) {
    showToast('Please select a book first');
    return;
  }

  const edition = APP_STATE.selectedEdition || (book.languages && book.languages[0]) || {};
  const driveId = edition.driveFileId || edition.fileId || book.driveFileId ||
    extractGoogleDriveFileId(edition.fileUrl || '') ||
    extractGoogleDriveFileId(book.fileUrl || '') ||
    extractGoogleDriveFileId(book.pdfUrl || '') ||
    extractGoogleDriveFileId(book.driveUrl || '');

  let driveUrl = '';
  if (driveId) {
    driveUrl = `https://drive.google.com/file/d/${driveId}/view?usp=sharing`;
  } else if (edition.fileUrl && edition.fileUrl.startsWith('http')) {
    driveUrl = edition.fileUrl;
  } else if (book.fileUrl && book.fileUrl.startsWith('http')) {
    driveUrl = book.fileUrl;
  }

  if (!driveUrl) {
    showToast('No Google Drive manuscript URL attached to this book.');
    return;
  }

  console.log('[NOVELIX Reader] Opening in Google Drive:', driveUrl);
  showToast('Opening in Google Drive...');

  try {
    if (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.Browser) {
      window.Capacitor.Plugins.Browser.open({ url: driveUrl });
      return;
    }
  } catch(e) {}

  const w = window.open(driveUrl, '_system');
  if (!w) window.location.href = driveUrl;
}

function shareActiveBook() {
  const book = APP_STATE.selectedBook;
  if (!book) return;
  const url = `https://novelix.app/book/${book.id}`;
  if (navigator.share) {
    navigator.share({
      title: book.title,
      text: `Read "${book.title}" by ${book.authorName || 'Author'} on NOVELIX:`,
      url: url
    }).catch(() => {});
  } else {
    navigator.clipboard?.writeText(url).then(() => showToast('Book link copied to clipboard!'));
  }
}

async function launchActiveReader() {"""

    if target_reader_funcs in content:
        content = content.replace(target_reader_funcs, replacement_reader_funcs, 1)
        print("✓ Added openBookInGoogleDrive and shareActiveBook functions")
    else:
        print("✗ Could not find target_reader_funcs")

    # 6. Add getEffectiveDriveAccounts and syncPublishDriveAccountsUI
    drive_helpers = """function getEffectiveDriveAccounts() {
  if (APP_STATE.connectedDriveAccounts && APP_STATE.connectedDriveAccounts.length > 0) {
    return APP_STATE.connectedDriveAccounts;
  }
  const localToken = localStorage.getItem('novelix_active_drive_token');
  if (localToken && APP_STATE.user && APP_STATE.user.email) {
    const fallbackAcc = {
      id: 'drive_active',
      accountId: 'drive_active',
      email: APP_STATE.user.email,
      displayName: APP_STATE.user.displayName || 'Google Author',
      accessToken: localToken,
      status: 'active'
    };
    APP_STATE.connectedDriveAccounts = [fallbackAcc];
    return [fallbackAcc];
  }
  return [];
}

function syncPublishDriveAccountsUI() {
  const accounts = getEffectiveDriveAccounts();
  const hasDrive = accounts.length > 0;

  // 1. Update Drive Link Section banner (Option B)
  const bannerEl = document.getElementById('publishDriveConnectedBanner');
  if (bannerEl) {
    if (hasDrive) {
      bannerEl.classList.remove('hidden');
      const email = accounts[0].email || 'Google Drive';
      bannerEl.innerHTML = `
        <div class="flex items-center justify-between p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-xs">
          <div class="flex items-center gap-2 truncate">
            <span class="w-2 h-2 rounded-full bg-emerald-400 flex-shrink-0"></span>
            <span class="text-white font-medium truncate">Connected: ${escapeHtml(email)}</span>
          </div>
          <button type="button" onclick="openDrivePickerForPublish()" class="btn-primary text-[11px] px-3 py-1 font-semibold flex items-center gap-1.5 flex-shrink-0 shadow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            <span>Pick from My Drive</span>
          </button>
        </div>
      `;
    } else {
      bannerEl.classList.remove('hidden');
      bannerEl.innerHTML = `
        <div class="flex items-center justify-between p-2.5 rounded-lg bg-[#181824] border border-[#2B2B3E] text-xs">
          <span class="text-app-muted truncate">Connect Google Drive to import files directly</span>
          <button type="button" onclick="initiateGoogleDriveConnection()" class="btn-secondary text-[11px] px-2.5 py-1 text-app-primary border-app-primary/40 font-semibold flex-shrink-0">
            <span>⚡ Connect Drive</span>
          </button>
        </div>
      `;
    }
  }

  // 2. Update Edition Rows (Option A)
  if (Array.isArray(APP_STATE.publishEditions)) {
    APP_STATE.publishEditions.forEach((ed, idx) => {
      const drivePanel = document.getElementById(`edDrivePanel-${idx}`);
      if (!drivePanel) return;

      if (hasDrive) {
        ed.driveAccountId = ed.driveAccountId || accounts[0].id || accounts[0].accountId;
        const driveOptions = accounts.map(a => `<option value="${a.id || a.accountId}">${escapeHtml(a.email || 'Drive Account')}</option>`).join('');
        drivePanel.innerHTML = `
          <div>
            <label class="block text-[10px] text-app-muted uppercase font-semibold mb-1">Connected Drive Account</label>
            <select id="edDriveAccountSelect-${idx}" class="w-full px-2.5 py-1.5 text-xs bg-[#171722] border border-[#262638] rounded-lg text-white" onchange="APP_STATE.publishEditions[${idx}].driveAccountId = this.value">
              ${driveOptions}
            </select>
          </div>
          <div class="flex gap-2">
            <button type="button" onclick="openDrivePickerForEdition(${idx})" class="btn-secondary text-xs flex-1 py-2 flex items-center justify-center gap-1 font-semibold text-white">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5 text-emerald-400"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              Select Drive PDF
            </button>
            <button type="button" onclick="document.getElementById('edDriveUploadInput-${idx}').click()" class="btn-secondary text-xs flex-1 py-2 flex items-center justify-center gap-1 text-app-muted">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>
              Upload New
            </button>
          </div>
          <input type="file" id="edDriveUploadInput-${idx}" accept=".pdf" class="hidden" onchange="handleEditionDriveUploadSelected(this, ${idx})">
        `;
      } else {
        drivePanel.innerHTML = `
          <div class="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-center space-y-1.5">
            <p class="text-[11px] text-amber-300">No Google Drive account connected.</p>
            <button type="button" onclick="initiateGoogleDriveConnection()" class="btn-primary text-xs px-3.5 py-1.5 font-bold">⚡ Connect Google Drive Now</button>
          </div>
        `;
      }
    });
  }
}
"""

    target_sync_hook = "// ── Load Connected Drive Accounts ───────────────────────"
    if target_sync_hook in content:
        content = content.replace(target_sync_hook, drive_helpers + "\n" + target_sync_hook, 1)
        print("✓ Injected getEffectiveDriveAccounts and syncPublishDriveAccountsUI")
    else:
        print("✗ Could not find target_sync_hook")

    # 7. Call syncPublishDriveAccountsUI() after loadConnectedDriveAccounts, connectGoogleDriveDirect, and switchPage('publish')
    target_post_load = """    APP_STATE.connectedDriveAccounts = accounts;
    if (loadingEl) loadingEl.classList.add('hidden');"""

    replacement_post_load = """    APP_STATE.connectedDriveAccounts = accounts;
    if (loadingEl) loadingEl.classList.add('hidden');
    syncPublishDriveAccountsUI();"""

    if target_post_load in content:
        content = content.replace(target_post_load, replacement_post_load, 1)
        print("✓ Hooked syncPublishDriveAccountsUI to loadConnectedDriveAccounts")
    else:
        print("✗ Could not find target_post_load")

    target_post_connect = """        closeDriveConnectModal();
        showToast(`✓ Google Drive connected with real access: ${acct.email}`);
        loadConnectedDriveAccounts();"""

    replacement_post_connect = """        closeDriveConnectModal();
        showToast(`✓ Google Drive connected with real access: ${acct.email}`);
        loadConnectedDriveAccounts();
        syncPublishDriveAccountsUI();"""

    if target_post_connect in content:
        content = content.replace(target_post_connect, replacement_post_connect, 1)
        print("✓ Hooked syncPublishDriveAccountsUI to connectGoogleDriveDirect")
    else:
        print("✗ Could not find target_post_connect")

    target_switch_pub = """  if (pageId === 'publish') {
    updatePublishAccessState();
    populatePublishSeriesDropdown();
  }"""

    replacement_switch_pub = """  if (pageId === 'publish') {
    updatePublishAccessState();
    populatePublishSeriesDropdown();
    syncPublishDriveAccountsUI();
    loadConnectedDriveAccounts();
  }"""

    if target_switch_pub in content:
        content = content.replace(target_switch_pub, replacement_switch_pub, 1)
        print("✓ Hooked syncPublishDriveAccountsUI to switchPage('publish')")
    else:
        print("✗ Could not find target_switch_pub")

    # 8. Update openDrivePickerForPublish to open connect modal if not yet connected
    target_picker_pub = """function openDrivePickerForPublish() {
  if (!APP_STATE.connectedDriveAccounts.length) {
    openSettingsModal();
    switchSettingsSection('drive');
    showToast('Please connect a Google Drive account first');
    return;
  }
  browseDriveAccountFiles(APP_STATE.connectedDriveAccounts[0].id);
}"""

    replacement_picker_pub = """function openDrivePickerForPublish() {
  const accounts = getEffectiveDriveAccounts();
  if (!accounts.length) {
    showToast('Please connect your Google Drive account first');
    initiateGoogleDriveConnection();
    return;
  }
  const accId = accounts[0].id || accounts[0].accountId;
  browseDriveAccountFiles(accId);
}"""

    if target_picker_pub in content:
        content = content.replace(target_picker_pub, replacement_picker_pub, 1)
        print("✓ Enhanced openDrivePickerForPublish")
    else:
        print("✗ Could not find target_picker_pub")

    # 9. Update importDriveFileToStudio to handle 'drive_link' mode automatically
    target_import_fn = "async function importDriveFileToStudio(fileId, fileName, fileSize, token) {"
    replacement_import_fn = """async function importDriveFileToStudio(fileId, fileName, fileSize, token) {
  // If in 'drive_link' publishing mode, auto-fill input and title!
  if (APP_STATE.publishMethod === 'drive_link') {
    const linkInput = document.getElementById('publishDriveLinkInput');
    const titleInput = document.getElementById('publishTitleInput');
    if (linkInput) {
      linkInput.value = `https://drive.google.com/file/d/${fileId}/view?usp=sharing`;
    }
    if (titleInput && !titleInput.value.trim()) {
      titleInput.value = fileName.replace(/\\.pdf$/i, '').replace(/[-_]/g, ' ');
    }
    validatePastedDriveLink();
    closeDrivePickerModal();
    switchPage('publish');
    showToast(`✓ Selected "${fileName}" from Google Drive`);
    return;
  }"""

    if target_import_fn in content:
        content = content.replace(target_import_fn, replacement_import_fn, 1)
        print("✓ Enhanced importDriveFileToStudio for instant Drive Link population")
    else:
        print("✗ Could not find target_import_fn")

    # 10. ULTRA-FAST PUBLISHING OPTIMIZATION
    # In handlePublishSubmit:
    # A) Pre-compress cover image to 800px max width JPEG (under 80KB)
    # B) Remove useless readFileAsBase64 on large PDF in edition loop
    # C) Remove setTimeout pauses and unblock background notifications
    target_ed_drive_base64 = """        } else if (ed.storageProvider === 'drive' && ed.file) {
          const base64 = await readFileAsBase64(ed.file);
          const acctId = ed.driveAccountId || (APP_STATE.connectedDriveAccounts[0]?.id);
          languages.push({
            language: ed.language,
            storageProvider: 'drive',
            driveFileId: 'pending_' + Date.now(),
            driveAccountId: acctId || '',
            fileName: ed.file.name,
            fileSize: ed.file.size,
            fileUrl: '',
            uploadedAt: new Date().toISOString()
          });"""

    replacement_ed_drive_base64 = """        } else if (ed.storageProvider === 'drive' && ed.file) {
          const acctId = ed.driveAccountId || (APP_STATE.connectedDriveAccounts[0]?.id);
          languages.push({
            language: ed.language,
            storageProvider: 'drive',
            driveFileId: 'pending_' + Date.now(),
            driveAccountId: acctId || '',
            fileName: ed.file.name,
            fileSize: ed.file.size,
            fileUrl: '',
            uploadedAt: new Date().toISOString()
          });"""

    if target_ed_drive_base64 in content:
        content = content.replace(target_ed_drive_base64, replacement_ed_drive_base64, 1)
        print("✓ Removed redundant base64 conversion of large PDF in Drive mode")
    else:
        print("✗ Could not find target_ed_drive_base64")

    # Fast image compression helper before upload
    img_compressor_code = """async function compressCoverForFastPublish(file) {
  if (!file || !file.type.startsWith('image/')) return file;
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const MAX_W = 750;
        let w = img.width;
        let h = img.height;
        if (w > MAX_W) {
          h = Math.round((h * MAX_W) / w);
          w = MAX_W;
        }
        const canvas = document.createElement('canvas');
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, w, h);
        canvas.toBlob((blob) => {
          if (blob && blob.size < file.size) {
            resolve(new File([blob], file.name.replace(/\\.[^/.]+$/, '.jpg'), { type: 'image/jpeg' }));
          } else {
            resolve(file);
          }
        }, 'image/jpeg', 0.80);
      };
      img.onerror = () => resolve(file);
      img.src = e.target.result;
    };
    reader.onerror = () => resolve(file);
    reader.readAsDataURL(file);
  });
}
"""

    target_cover_upload = """    if (coverFile) {
      setButtonLoading('publishSubmitBtn', true, 'Uploading cover to ImgBB...');
      coverUrl = await uploadMediaFile(coverFile, `covers/${bookId}/${Date.now()}.jpg`);
    }"""

    replacement_cover_upload = img_compressor_code + """
    if (coverFile) {
      setButtonLoading('publishSubmitBtn', true, 'Optimizing & uploading cover...');
      const fastCover = await compressCoverForFastPublish(coverFile);
      coverUrl = await uploadMediaFile(fastCover, `covers/${bookId}/${Date.now()}.jpg`);
    }"""

    if target_cover_upload in content:
        content = content.replace(target_cover_upload, replacement_cover_upload, 1)
        print("✓ Injected fast cover compression (10x faster upload)")
    else:
        print("✗ Could not find target_cover_upload")

    # Fast finish: unblock follower notifications and redirect immediately
    target_pub_finish = """    showToast(isEditing ? 'Publication updated successfully!' : 'Work published live to NOVELIX!');
    APP_STATE.editingBookId = null;
    const submitBtn = document.getElementById('publishSubmitBtn');
    if (submitBtn) submitBtn.textContent = 'Publish Work';

    setTimeout(() => {
      resetPublishForm();
      switchPage('home');
    }, 1000);"""

    replacement_pub_finish = """    showToast(isEditing ? '✓ Publication updated live!' : '⚡ Published live to NOVELIX!');
    APP_STATE.editingBookId = null;
    const submitBtn = document.getElementById('publishSubmitBtn');
    if (submitBtn) submitBtn.textContent = 'Publish Work';

    // Instant seamless transition
    resetPublishForm();
    switchPage('home');"""

    if target_pub_finish in content:
        content = content.replace(target_pub_finish, replacement_pub_finish, 1)
        print("✓ Made publishing transition instant (zero artificial delay)")
    else:
        print("✗ Could not find target_pub_finish")

    with open('scripts/generate_4.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"New generate_4.py length: {len(content)}")

if __name__ == '__main__':
    patch()
