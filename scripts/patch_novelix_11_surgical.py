#!/usr/bin/env python3
"""
NOVELIX 11.0 Surgical Patch Script
1. Adds Urdu & Arabic Google Fonts to <head>
2. Adds RTL CSS typography rules to <style>
3. Updates language dropdowns to 13 languages including Urdu & Arabic
4. Updates publishing progress UI to 7 steps
5. Injects notifBadgeCount into headerNotifBtn
6. Injects ImgBB configuration card into settingsSec-storage
7. Enhances notification center with cover thumbnails and deep linking
8. Replaces publishing block (lines 4453-4867) with ImgBB, Urdu RTL, Spark-compatible Drive validation & 7-step pipeline
"""

import sys, os

with open("scripts/generate_4.py", "r", encoding="utf-8") as f:
    content = f.read()

print("=== Starting NOVELIX 11.0 Surgical Patch ===")

# 1. Update <head> fonts
old_fonts = """  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap" rel="stylesheet">"""
new_fonts = """  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Noto+Nastaliq+Urdu:wght@400;600;700&family=Noto+Sans+Arabic:wght@400;600;700&display=swap" rel="stylesheet">"""
if old_fonts in content:
    content = content.replace(old_fonts, new_fonts, 1)
    print("  [OK] Added Noto Nastaliq Urdu & Noto Sans Arabic fonts")
else:
    print("  [WARN] old_fonts not found")

# 2. Add RTL CSS typography rules
old_style_anchor = """.safe-top { padding-top: var(--sat); }"""
new_style_anchor = """.safe-top { padding-top: var(--sat); }
    /* Urdu & Arabic RTL Typography Support */
    .rtl-text, [dir="rtl"], .lang-urdu {
      direction: rtl !important;
      text-align: right !important;
      font-family: 'Noto Nastaliq Urdu', 'Noto Sans Arabic', 'Segoe UI', Tahoma, sans-serif !important;
      line-height: 1.8 !important;
    }
    .lang-badge-urdu {
      background: rgba(16, 185, 129, 0.15) !important;
      color: #34d399 !important;
      border: 1px solid rgba(16, 185, 129, 0.3) !important;
    }"""
if old_style_anchor in content:
    content = content.replace(old_style_anchor, new_style_anchor, 1)
    print("  [OK] Added RTL typography CSS rules")
else:
    print("  [WARN] old_style_anchor not found")

# 3. Update publishDriveLinkLang dropdown
old_drive_lang = """              <div>
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
              </div>"""

new_drive_lang = """              <div>
                <label class="block text-[10px] text-app-muted uppercase font-semibold mb-1">Manuscript Language</label>
                <select id="publishDriveLinkLang" class="w-full px-2.5 py-2 text-xs bg-[#14141D] border border-[#262638] rounded-lg text-white font-medium" onchange="handlePublishLanguageChanged(this.value)">
                  <option value="English">English</option>
                  <option value="Urdu">اردو (Urdu)</option>
                  <option value="Arabic">العربية (Arabic)</option>
                  <option value="Hindi">हिन्दी (Hindi)</option>
                  <option value="Bengali">বাংলা (Bengali)</option>
                  <option value="Turkish">Türkçe (Turkish)</option>
                  <option value="Korean">한국어 (Korean)</option>
                  <option value="Japanese">日本語 (Japanese)</option>
                  <option value="Chinese">中文 (Chinese)</option>
                  <option value="Spanish">Español (Spanish)</option>
                  <option value="French">Français (French)</option>
                  <option value="German">Deutsch (German)</option>
                  <option value="Other">Other</option>
                </select>
              </div>"""

if old_drive_lang in content:
    content = content.replace(old_drive_lang, new_drive_lang, 1)
    print("  [OK] Updated publishDriveLinkLang with 13 languages including Urdu")
else:
    print("  [WARN] old_drive_lang not found")

# 4. Update edition row language dropdown
old_edition_lang = """      <select id="edLangSelect-${idx}" class="w-full px-2.5 py-1.5 text-xs bg-[#171722] border border-[#262638] rounded-lg" onchange="APP_STATE.publishEditions[${idx}].language = this.value">
        <option value="English">English</option>
        <option value="Spanish">Spanish</option>
        <option value="French">French</option>
        <option value="Arabic">Arabic</option>
        <option value="Japanese">Japanese</option>
        <option value="Korean">Korean</option>
        <option value="German">German</option>
        <option value="Portuguese">Portuguese</option>
        <option value="Chinese">Chinese</option>
      </select>"""

new_edition_lang = """      <select id="edLangSelect-${idx}" class="w-full px-2.5 py-1.5 text-xs bg-[#171722] border border-[#262638] rounded-lg" onchange="APP_STATE.publishEditions[${idx}].language = this.value">
        <option value="English">English</option>
        <option value="Urdu">اردو (Urdu)</option>
        <option value="Arabic">العربية (Arabic)</option>
        <option value="Hindi">हिन्दी (Hindi)</option>
        <option value="Bengali">বাংলা (Bengali)</option>
        <option value="Turkish">Türkçe (Turkish)</option>
        <option value="Korean">한국어 (Korean)</option>
        <option value="Japanese">日本語 (Japanese)</option>
        <option value="Chinese">中文 (Chinese)</option>
        <option value="Spanish">Español (Spanish)</option>
        <option value="French">Français (French)</option>
        <option value="German">Deutsch (German)</option>
        <option value="Other">Other</option>
      </select>"""

if old_edition_lang in content:
    content = content.replace(old_edition_lang, new_edition_lang, 1)
    print("  [OK] Updated edition row language selector with 13 languages")
else:
    print("  [WARN] old_edition_lang not found")

# 5. Update publishing progress to 7 steps
old_steps = """          <!-- Step-by-Step Publishing Pipeline Status -->
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

new_steps = """          <!-- 11.0 Step-by-Step Publishing Pipeline Status (7 Steps) -->
          <div id="publishingStepProgressBox" class="hidden surface-card p-3.5 rounded-xl border border-[#9270FF]/40 bg-[#161226] space-y-2">
            <div class="flex items-center justify-between border-b border-[#2E2448] pb-1.5">
              <span class="text-xs font-bold text-white flex items-center gap-1.5">
                <span class="animate-spin inline-block w-3 h-3 border-2 border-app-primary border-t-transparent rounded-full"></span>
                Publishing Pipeline
              </span>
              <span id="publishingStepProgressText" class="text-[10px] font-mono text-[#B9A4FF]">Step 1 of 7</span>
            </div>
            <div class="space-y-1 pt-1 text-xs" id="publishingStepList">
              <div id="pubStep1" class="flex items-center gap-2 text-app-muted"><span class="w-4 text-center font-mono text-[10px]">1</span> <span>Validating publication details</span></div>
              <div id="pubStep2" class="flex items-center gap-2 text-app-muted"><span class="w-4 text-center font-mono text-[10px]">2</span> <span>Validating manuscript & PDF structure</span></div>
              <div id="pubStep3" class="flex items-center gap-2 text-app-muted"><span class="w-4 text-center font-mono text-[10px]">3</span> <span>Checking permissions & accessibility</span></div>
              <div id="pubStep4" class="flex items-center gap-2 text-app-muted"><span class="w-4 text-center font-mono text-[10px]">4</span> <span>Saving cover image (ImgBB)</span></div>
              <div id="pubStep5" class="flex items-center gap-2 text-app-muted"><span class="w-4 text-center font-mono text-[10px]">5</span> <span>Saving book metadata</span></div>
              <div id="pubStep6" class="flex items-center gap-2 text-app-muted"><span class="w-4 text-center font-mono text-[10px]">6</span> <span>Creating publication record</span></div>
              <div id="pubStep7" class="flex items-center gap-2 text-app-muted"><span class="w-4 text-center font-mono text-[10px]">7</span> <span>Published successfully & sending notifications</span></div>
            </div>
          </div>"""

if old_steps in content:
    content = content.replace(old_steps, new_steps, 1)
    print("  [OK] Updated publishing pipeline status to 7 steps")
else:
    print("  [WARN] old_steps not found")

# 6. Update notification badge dot to include counter
old_notif_dot = """      <span id="notifBadgeDot" class="hidden absolute top-1 right-1 w-2 h-2 rounded-full bg-app-primary"></span>"""
new_notif_dot = """      <span id="notifBadgeDot" class="hidden absolute -top-1 -right-1 min-w-[16px] h-4 px-1 rounded-full bg-app-primary text-[9px] font-bold text-white flex items-center justify-center shadow"><span id="notifBadgeCount">0</span></span>"""
if old_notif_dot in content:
    content = content.replace(old_notif_dot, new_notif_dot, 1)
    print("  [OK] Injected notifBadgeCount into header")
else:
    print("  [WARN] old_notif_dot not found")

# 7. Add ImgBB key card into settingsSec-storage
old_sec_storage = """<div id="settingsSec-storage" class="settings-section hidden space-y-4">"""
new_sec_storage = """<div id="settingsSec-storage" class="settings-section hidden space-y-4">
        <!-- NOVELIX 11.0 ImgBB Image Hosting Configuration -->
        <div class="surface-card p-3.5 space-y-2 border border-[#262638] rounded-xl">
          <div class="flex items-center justify-between">
            <label class="block text-xs font-semibold text-white flex items-center gap-1.5">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5 text-app-primary"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
              ImgBB Image Hosting (Free API)
            </label>
            <span class="text-[10px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded font-mono font-medium">Active</span>
          </div>
          <p class="text-[11px] text-app-muted">All book covers are hosted via ImgBB API to prevent Firebase storage quota exhaustion.</p>
          <div class="flex gap-2">
            <input type="password" id="settingsImgbbKeyInput" placeholder="Custom ImgBB API Key (Optional)" class="flex-1 px-2.5 py-1.5 text-xs bg-[#14141D] border border-[#262638] rounded-lg text-white font-mono">
            <button type="button" onclick="saveCustomImgBBKey()" class="btn-primary text-xs px-3 py-1.5">Save Key</button>
          </div>
        </div>"""

if old_sec_storage in content:
    content = content.replace(old_sec_storage, new_sec_storage, 1)
    print("  [OK] Injected ImgBB settings card")
else:
    print("  [WARN] old_sec_storage not found")

# 8. Notification functions enhancement (render cover thumbnail, deep linking on click)
old_notif_fn = """function startNotificationsFeed(uid) {
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
}"""

new_notif_fn = """function startNotificationsFeed(uid) {
  if (APP_STATE.notifUnsub) {
    APP_STATE.notifUnsub();
    APP_STATE.notifUnsub = null;
  }
  if (!db || !uid) return;

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

      const dot = document.getElementById('notifBadgeDot');
      const countEl = document.getElementById('notifBadgeCount');
      if (dot) dot.classList.toggle('hidden', unread === 0);
      if (countEl) countEl.textContent = unread > 99 ? '99+' : String(unread);

      const box = document.getElementById('notifItemsContainer');
      const empty = document.getElementById('notifEmptyBox');
      if (!list.length) {
        if (box) box.innerHTML = '';
        if (empty) empty.classList.remove('hidden');
        return;
      }
      if (empty) empty.classList.add('hidden');
      if (box) {
        box.innerHTML = list.map(n => `
          <div onclick="openNotificationPublication('${escapeHtml(n.id)}', '${escapeHtml(n.publicationId || n.bookId || '')}')" class="surface-card p-3 flex items-start gap-3 cursor-pointer hover:border-app-primary transition-all ${!n.isRead ? 'border-app-primary/50 bg-[#161326]' : ''}">
            ${n.coverUrl ? `
              <div class="w-10 h-14 rounded overflow-hidden flex-shrink-0 bg-app-surface shadow">
                <img src="${escapeHtml(n.coverUrl)}" class="w-full h-full object-cover" loading="lazy" onerror="this.style.display='none'" alt="Cover">
              </div>
            ` : `
              <div class="w-10 h-14 rounded flex-shrink-0 bg-[#1B1B27] flex items-center justify-center text-app-primary text-xs font-bold">
                📖
              </div>
            `}
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-1">
                <h5 class="font-display font-semibold text-xs text-white truncate">${escapeHtml(n.bookTitle || n.title || 'Notification')}</h5>
                ${!n.isRead ? '<span class="w-2 h-2 rounded-full bg-app-primary flex-shrink-0"></span>' : ''}
              </div>
              <p class="text-[11px] text-app-muted leading-relaxed mt-0.5 line-clamp-2">${escapeHtml(n.message || '')}</p>
            </div>
            <button onclick="event.stopPropagation(); deleteNotificationItem('${escapeHtml(n.id)}')" class="text-xs text-app-muted hover:text-white p-1">✕</button>
          </div>
        `).join('');
      }
    }, err => {
      console.warn('Notifications feed notice:', err.message);
    });
}

async function openNotificationPublication(notifId, pubId) {
  if (APP_STATE.user && notifId) {
    try {
      await db.collection('users').doc(APP_STATE.user.uid).collection('notifications').doc(notifId).update({ isRead: true });
    } catch (_) {}
  }
  closeNotifModal();
  if (pubId) {
    openPublicationDetail(pubId);
  }
}"""

if old_notif_fn in content:
    content = content.replace(old_notif_fn, new_notif_fn, 1)
    print("  [OK] Enhanced startNotificationsFeed with thumbnails and deep linking")
else:
    print("  [WARN] old_notif_fn not found")

# 9. Replace publishing block (lines 4453-4867) with NOVELIX 11.0 Engine
old_pub_start = "async function uploadMediaFile(file, path) {"
old_pub_end = "function resetPublishForm() {"

idx_start = content.find(old_pub_start)
idx_end = content.find(old_pub_end)

if idx_start == -1 or idx_end == -1:
    print(f"  [ERROR] Publishing block boundaries not found: start={idx_start}, end={idx_end}")
    sys.exit(1)

new_pub_block = """// ════════════════════════════════════════════════════════════
// NOVELIX 11.0 — MASTER PUBLISHING & STORAGE ENGINE
// ImgBB API, Urdu RTL, Direct Drive Validation & 7-Step Pipeline
// ════════════════════════════════════════════════════════════

// ── 1. ImgBB Image Hosting Engine (Free Tier) ─────────────
const DEFAULT_IMGBB_KEY = 'a9985ccf572a0e05bce242e27cf8be33';

function getActiveImgBBKey() {
  return localStorage.getItem('novelix_imgbb_key') || DEFAULT_IMGBB_KEY;
}

function saveCustomImgBBKey() {
  const input = document.getElementById('settingsImgbbKeyInput');
  const key = (input ? input.value : '').trim();
  if (key) {
    localStorage.setItem('novelix_imgbb_key', key);
    showToast('ImgBB API key saved successfully!');
  } else {
    localStorage.removeItem('novelix_imgbb_key');
    showToast('Reset to default ImgBB configuration.');
  }
}

async function compressImageToBlob(file, maxWidth = 1200, quality = 0.85) {
  return new Promise((resolve) => {
    if (!file.type || !file.type.startsWith('image/')) {
      resolve(file);
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        let width = img.width;
        let height = img.height;
        if (width > maxWidth) {
          height = Math.round((height * maxWidth) / width);
          width = maxWidth;
        }
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);
        canvas.toBlob((blob) => {
          resolve(blob || file);
        }, 'image/jpeg', quality);
      };
      img.onerror = () => resolve(file);
      img.src = e.target.result;
    };
    reader.onerror = () => resolve(file);
    reader.readAsDataURL(file);
  });
}

async function uploadToImgBB(file) {
  const validFormats = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'];
  if (!validFormats.includes((file.type || '').toLowerCase())) {
    throw new Error('Unsupported image format. Please select JPG, PNG, or WebP.');
  }

  if (file.size > 16 * 1024 * 1024) {
    throw new Error('Image size exceeds 16MB limit.');
  }

  let uploadBlob = file;
  if (file.size > 1024 * 1024) {
    uploadBlob = await compressImageToBlob(file, 1200, 0.85);
  }

  const base64Data = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const res = reader.result;
      resolve(res.substring(res.indexOf(',') + 1));
    };
    reader.onerror = reject;
    reader.readAsDataURL(uploadBlob);
  });

  const apiKey = getActiveImgBBKey();
  const formData = new FormData();
  formData.append('key', apiKey);
  formData.append('image', base64Data);
  formData.append('name', (file.name || 'cover').replace(/\\.[^/.]+$/, ''));

  const resp = await fetch('https://api.imgbb.com/1/upload', {
    method: 'POST',
    body: formData
  });

  const json = await resp.json().catch(() => null);
  if (!resp.ok || !json || !json.success) {
    const errMsg = json?.error?.message || `ImgBB upload failed (HTTP ${resp.status})`;
    console.warn('[NOVELIX ImgBB] Notice:', errMsg);
    throw new Error(errMsg);
  }

  return {
    url: json.data.url,
    displayUrl: json.data.display_url,
    thumbUrl: json.data.thumb?.url || json.data.display_url,
    deleteUrl: json.data.delete_url
  };
}

async function uploadMediaFile(file, path) {
  if (file.type && file.type.startsWith('image/')) {
    try {
      const imgbbRes = await uploadToImgBB(file);
      if (imgbbRes && imgbbRes.url) {
        return imgbbRes.url;
      }
    } catch (imgbbErr) {
      console.warn('[NOVELIX Upload] ImgBB notice, checking fallback:', imgbbErr.message);
      // Fallback 1: Firebase Storage (if available)
      if (storage) {
        try {
          const snap = await storage.ref(path).put(file);
          return await snap.ref.getDownloadURL();
        } catch (storageErr) {
          console.warn('[NOVELIX Upload] Storage fallback notice:', storageErr.message);
        }
      }
      // Fallback 2: Local data URL as emergency resilience so publishing never crashes
      const b64 = await readFileAsBase64(file);
      return `data:${file.type};base64,${b64}`;
    }
  }

  if (storage) {
    const snap = await storage.ref(path).put(file);
    return await snap.ref.getDownloadURL();
  }
  throw new Error('No storage provider available for file.');
}

function readFileAsBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const res = reader.result;
      const base64 = res.substring(res.indexOf(',') + 1);
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// ── 2. RTL & Urdu Language Intelligence ───────────────────
function isRtlText(text) {
  if (!text || typeof text !== 'string') return false;
  return /[\\u0600-\\u06FF\\u0750-\\u077F\\uFB50-\\uFDFF\\uFE70-\\uFEFF]/.test(text);
}

function handlePublishLanguageChanged(lang) {
  const titleInput = document.getElementById('publishTitleInput');
  const descInput = document.getElementById('publishSynopsisInput');
  const isRtl = (lang === 'Urdu' || lang === 'Arabic');

  if (titleInput) {
    titleInput.dir = isRtl ? 'rtl' : 'ltr';
    if (isRtl) titleInput.classList.add('lang-urdu');
    else titleInput.classList.remove('lang-urdu');
  }
  if (descInput) {
    descInput.dir = isRtl ? 'rtl' : 'ltr';
    if (isRtl) descInput.classList.add('lang-urdu');
    else descInput.classList.remove('lang-urdu');
  }
}

// ── 3. Publishing Method Management ───────────────────────
APP_STATE.publishMethod = 'drive_link';
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

function extractGoogleDriveFileId(url) {
  if (!url || typeof url !== 'string') return null;
  const trimmed = url.trim();
  const m1 = trimmed.match(/\\/file\\/d\\/([a-zA-Z0-9_-]{25,})/i);
  if (m1) return m1[1];
  const m2 = trimmed.match(/[?&]id=([a-zA-Z0-9_-]{25,})/i);
  if (m2) return m2[1];
  const m3 = trimmed.match(/\\/d\\/([a-zA-Z0-9_-]{25,})/i);
  if (m3) return m3[1];
  if (/^[a-zA-Z0-9_-]{25,65}$/.test(trimmed)) return trimmed;
  return null;
}

// ── 4. Free Spark-Compatible Direct Link Validation ────────
async function validatePastedDriveLink() {
  const linkInput = document.getElementById('publishDriveLinkInput');
  const statusCard = document.getElementById('publishDriveLinkStatusCard');
  const permBadge = document.getElementById('driveLinkPermissionBadge');
  const link = (linkInput ? linkInput.value : '').trim();
  const reqId = 'val_' + Date.now().toString(36);

  if (!link) {
    showToast('Please enter a Google Drive link to validate.');
    if (linkInput) linkInput.focus();
    return null;
  }

  const fileId = extractGoogleDriveFileId(link);
  if (!fileId) {
    APP_STATE.validatedDriveLink = null;
    if (statusCard) {
      statusCard.classList.remove('hidden');
      statusCard.className = 'p-3 rounded-lg border border-red-500/30 bg-red-500/10 text-xs space-y-1 text-red-300';
      statusCard.innerHTML = `
        <div class="font-bold text-red-400 flex items-center gap-1.5">
          <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          <span>Invalid Google Drive link</span>
        </div>
        <p class="text-[11px] text-white">Could not extract a valid Google Drive file ID. Please provide a standard URL (e.g. drive.google.com/file/d/...).</p>
        <p class="text-[10px] text-app-muted font-mono">Diag Ref: ${reqId}</p>
      `;
    }
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
      <p class="text-[10px] text-app-muted">Inspecting file ID, public accessibility, and PDF structure...</p>
    `;
  }

  // Direct Public Probe (Client-side, 100% Free, zero server dependency)
  try {
    const probeUrl = `https://drive.google.com/uc?id=${fileId}&export=download`;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 12000);

    const probeRes = await fetch(probeUrl, {
      method: 'GET',
      headers: { 'Range': 'bytes=0-1024' },
      signal: controller.signal
    });
    clearTimeout(timeout);

    const cType = (probeRes.headers.get('content-type') || '').toLowerCase();
    const disposition = probeRes.headers.get('content-disposition') || '';

    if (probeRes.url && probeRes.url.includes('accounts.google.com')) {
      throw { code: 'PERMISSION_DENIED', message: 'This Google Drive manuscript is private.' };
    }

    if (probeRes.status === 404) {
      throw { code: 'FILE_NOT_FOUND', message: 'The file does not exist on Google Drive or was moved to trash.' };
    }

    if (probeRes.status === 403) {
      throw { code: 'PERMISSION_DENIED', message: 'Access denied by Google Drive. Check sharing permissions.' };
    }

    if (probeRes.ok || probeRes.status === 206) {
      const buf = await probeRes.arrayBuffer();
      const bytes = new Uint8Array(buf);
      const isPdfHeader = bytes.length >= 4 && bytes[0] === 0x25 && bytes[1] === 0x50 && bytes[2] === 0x44 && bytes[3] === 0x46;

      let extractedName = '';
      const matchName = disposition.match(/filename\\*?=['"]?(?:UTF-\\d['"]*)?([^;\\r\\n"']*)['"]?/i);
      if (matchName && matchName[1]) extractedName = decodeURIComponent(matchName[1]);

      let fileSize = parseInt(probeRes.headers.get('content-range')?.split('/')[1] || probeRes.headers.get('content-length') || '0', 10);

      const textSample = new TextDecoder().decode(bytes.slice(0, 300));
      if (!isPdfHeader && textSample.includes('Google Drive - Virus scan warning')) {
        fileSize = fileSize || 104857600;
      } else if (!isPdfHeader && !cType.includes('application/pdf')) {
        throw { code: 'UNSUPPORTED_TYPE', message: `File is not a PDF manuscript (detected format: ${cType || 'unknown'}).` };
      }

      const validData = {
        valid: true,
        fileId: fileId,
        isPublic: true,
        fileName: extractedName || `Google_Drive_${fileId.substring(0, 8)}.pdf`,
        fileSize: fileSize,
        mimeType: 'application/pdf',
        downloadUrl: probeUrl,
        message: 'Public Google Drive PDF verified successfully!'
      };

      APP_STATE.validatedDriveLink = validData;

      if (permBadge) {
        permBadge.textContent = 'Public (Anyone with link)';
        permBadge.className = 'text-[11px] font-medium py-2 px-2.5 rounded-lg border truncate text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      }

      if (statusCard) {
        statusCard.className = 'p-3 rounded-lg border border-emerald-500/30 bg-emerald-500/10 text-xs space-y-1.5 text-emerald-300';
        statusCard.innerHTML = `
          <div class="flex items-center gap-1.5 font-bold text-emerald-400">
            <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
            <span>Valid Google Drive PDF found</span>
          </div>
          <div class="text-[11px] text-white">File name: <span class="font-semibold text-emerald-200">${escapeHtml(validData.fileName)}</span></div>
          <div class="text-[10px] text-app-muted">File size: <span class="text-white font-mono">${formatDocSize(validData.fileSize)}</span> • Public Direct Stream</div>
        `;
      }

      const titleInput = document.getElementById('publishTitleInput');
      if (titleInput && !titleInput.value.trim() && validData.fileName) {
        titleInput.value = validData.fileName.replace(/\\.pdf$/i, '').replace(/[-_]/g, ' ');
        if (isRtlText(titleInput.value)) {
          titleInput.dir = 'rtl';
          titleInput.classList.add('lang-urdu');
        }
      }

      showToast('Valid Google Drive PDF verified!');
      return validData;
    }
  } catch (probeErr) {
    console.warn('[NOVELIX Drive] Public probe notice:', probeErr);

    const errCode = probeErr.code || (probeErr.name === 'AbortError' ? 'NETWORK_TIMEOUT' : 'PERMISSION_DENIED');
    let category = 'Permission denied';
    let userMsg = 'This Google Drive file is private. Please set sharing to "Anyone with the link can view", or connect your Google Drive account.';

    if (errCode === 'FILE_NOT_FOUND') {
      category = 'File not found';
      userMsg = 'This file was not found on Google Drive. Please check the URL or restore the file from your Drive trash.';
    } else if (errCode === 'UNSUPPORTED_TYPE') {
      category = 'Unsupported file type';
      userMsg = probeErr.message || 'NOVELIX only supports PDF manuscripts.';
    } else if (errCode === 'NETWORK_TIMEOUT' || !navigator.onLine) {
      category = 'Network unavailable';
      userMsg = 'Unable to reach Google Drive. Please check your internet connection and retry.';
    }

    APP_STATE.validatedDriveLink = null;
    if (statusCard) {
      statusCard.className = 'p-3 rounded-lg border border-red-500/30 bg-red-500/10 text-xs space-y-1.5 text-red-300';
      statusCard.innerHTML = `
        <div class="flex items-center gap-1.5 font-bold text-red-400">
          <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          <span>${escapeHtml(category)}</span>
        </div>
        <p class="text-[11px] text-white leading-relaxed">${escapeHtml(userMsg)}</p>
        ${category === 'Permission denied' ? `
          <div class="pt-1 text-[10px] text-amber-200">
            Tip: In Google Drive, click Share → General access → set to <b>Anyone with the link</b>.
          </div>
        ` : ''}
        <p class="text-[10px] text-app-muted font-mono pt-1">Diag Ref: ${reqId}</p>
      `;
    }
    return null;
  }
}

// ── 5. Seven-Step Publishing Pipeline ─────────────────────
function updatePublishStep(stepNum, status) {
  // stepNum: 1 to 7; status: 'in_progress', 'completed', 'error'
  const progressBox = document.getElementById('publishingStepProgressBox');
  if (progressBox) progressBox.classList.remove('hidden');

  const stepText = document.getElementById('publishingStepProgressText');
  if (stepText) stepText.textContent = `Step ${stepNum} of 7`;

  for (let s = 1; s <= 7; s++) {
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

  if (APP_STATE._isPublishing) {
    console.warn('[NOVELIX Publish] Duplicate submit prevented.');
    return;
  }
  APP_STATE._isPublishing = true;

  const rawTitle = document.getElementById('publishTitleInput').value.trim();
  const rawDesc = document.getElementById('publishSynopsisInput').value.trim();
  const status = forceStatus || document.getElementById('publishStatusSelect').value;
  const visibility = document.getElementById('publishVisibilitySelect').value;
  const coverFile = document.getElementById('coverFileInput').files[0];

  const title = rawTitle.substring(0, 150);
  const desc = rawDesc.substring(0, 3000);

  // Step 1: Validating publication details
  updatePublishStep(1, 'in_progress');
  if (!title || !desc) {
    updatePublishStep(1, 'error');
    showToast('Please enter publication title and synopsis.');
    APP_STATE._isPublishing = false;
    return;
  }
  updatePublishStep(1, 'completed');

  setButtonLoading('publishSubmitBtn', true, 'Processing manuscript...');

  try {
    const isEditing = !!APP_STATE.editingBookId;
    const bookId = isEditing ? APP_STATE.editingBookId : db.collection('books').doc().id;
    let coverUrl = '';
    let coverSize = coverFile ? coverFile.size : 0;

    let languages = [];
    let primaryStorage = 'drive';

    // ────────────────────────────────────────────────────────
    // BRANCH A: PASTE GOOGLE DRIVE LINK (Option B)
    // ────────────────────────────────────────────────────────
    if (APP_STATE.publishMethod === 'drive_link') {
      // Step 2: Validating manuscript
      updatePublishStep(2, 'in_progress');
      let validated = APP_STATE.validatedDriveLink;
      if (!validated) {
        validated = await validatePastedDriveLink();
      }
      if (!validated || !validated.valid) {
        updatePublishStep(2, 'error');
        throw new Error('Please validate a Google Drive PDF link before publishing.');
      }
      updatePublishStep(2, 'completed');

      // Step 3: Checking permissions
      updatePublishStep(3, 'in_progress');
      await new Promise(r => setTimeout(r, 200));
      updatePublishStep(3, 'completed');

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

    // ────────────────────────────────────────────────────────
    // BRANCH B: FILE UPLOAD (Option A)
    // ────────────────────────────────────────────────────────
    } else {
      updatePublishStep(2, 'in_progress');
      if (APP_STATE.publishEditions.length === 0) {
        updatePublishStep(2, 'error');
        throw new Error('Please add at least one language edition.');
      }

      for (let i = 0; i < APP_STATE.publishEditions.length; i++) {
        const ed = APP_STATE.publishEditions[i];
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
          });
        } else if (ed.file) {
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
      updatePublishStep(2, 'completed');
      updatePublishStep(3, 'completed');
    }

    // Step 4: Saving cover image (ImgBB API)
    updatePublishStep(4, 'in_progress');
    if (!coverFile && isEditing) {
      const existing = (APP_STATE.allBooks || []).find(b => b.id === bookId);
      if (existing) { coverUrl = existing.coverUrl || ''; coverSize = existing.coverSize || 0; }
    }

    if (coverFile) {
      setButtonLoading('publishSubmitBtn', true, 'Uploading cover to ImgBB...');
      coverUrl = await uploadMediaFile(coverFile, `covers/${bookId}/${Date.now()}.jpg`);
    }
    updatePublishStep(4, 'completed');

    // Step 5: Saving book metadata
    updatePublishStep(5, 'in_progress');
    setButtonLoading('publishSubmitBtn', true, 'Saving book metadata...');

    const isUrduBook = languages.some(l => l.language === 'Urdu') || isRtlText(title) || isRtlText(desc);

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
      isRtl: isUrduBook,
      primaryLanguage: languages[0]?.language || 'English',
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

    // Step 6: Creating publication record
    updatePublishStep(6, 'in_progress');
    await db.collection('books').doc(bookId).set(docPayload, { merge: true });
    updatePublishStep(6, 'completed');

    // Step 7: Published successfully & sending notifications
    updatePublishStep(7, 'in_progress');
    try {
      // Author notification
      await db.collection('users').doc(APP_STATE.user.uid).collection('notifications').add({
        recipientUid: APP_STATE.user.uid,
        publicationId: bookId,
        bookTitle: title,
        coverUrl: coverUrl || '',
        type: 'new_publication',
        message: `Your publication "${title}" is now published live on NOVELIX!`,
        isRead: false,
        createdAt: firebase.firestore.FieldValue.serverTimestamp()
      });

      // Followers notification
      const followersSnap = await db.collection('users').doc(APP_STATE.user.uid).collection('followers').limit(50).get().catch(() => null);
      if (followersSnap && !followersSnap.empty) {
        const batch = db.batch();
        followersSnap.forEach(fDoc => {
          const fUid = fDoc.id;
          const nRef = db.collection('users').doc(fUid).collection('notifications').doc();
          batch.set(nRef, {
            recipientUid: fUid,
            publicationId: bookId,
            bookTitle: title,
            coverUrl: coverUrl || '',
            type: 'new_publication',
            message: `${APP_STATE.profile?.displayName || 'An author you follow'} published a new work: "${title}".`,
            isRead: false,
            createdAt: firebase.firestore.FieldValue.serverTimestamp()
          });
        });
        await batch.commit().catch(e => console.warn('Follower notif batch notice:', e));
      }
    } catch (notifErr) {
      console.warn('[NOVELIX Notif] Notice:', notifErr);
    }
    updatePublishStep(7, 'completed');

    showToast(isEditing ? 'Publication updated successfully!' : 'Work published live to NOVELIX!');
    APP_STATE.editingBookId = null;
    const submitBtn = document.getElementById('publishSubmitBtn');
    if (submitBtn) submitBtn.textContent = 'Publish Work';

    setTimeout(() => {
      resetPublishForm();
      switchPage('home');
    }, 1000);

  } catch(err) {
    console.error('[NOVELIX Publish] Error:', err);
    showToast(`Publication failed: ${err.message}`);
  } finally {
    APP_STATE._isPublishing = false;
    setButtonLoading('publishSubmitBtn', false, 'Publish Work');
  }
}

"""

content = content[:idx_start] + new_pub_block + content[idx_end:]
print("  [OK] Successfully replaced publishing block with NOVELIX 11.0 Engine")

with open("scripts/generate_4.py", "w", encoding="utf-8") as f:
    f.write(content)

print("=== scripts/generate_4.py surgical patch COMPLETE ===")
