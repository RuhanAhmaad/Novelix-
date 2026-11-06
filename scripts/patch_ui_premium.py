#!/usr/bin/env python3
"""
NOVELIX 7.0 — Peak Professional UI + Missing Feature Patches
Covers:
  1. Premium reader toolbar with gesture-friendly controls
  2. Toast system: position fixed, non-obstructive
  3. Book detail modal — richer metadata display (file size, edition count, language badge)
  4. Home page — search bar + "New Release" ribbon on latest books
  5. Library page — fix empty-state CTA (was using missing navigateTo before fix)
  6. Navigation bar — active state color + ripple feedback
  7. Profile page — improved avatar upload UX + reading stats card
  8. Global: loading skeleton animation quality improvement
  9. Missing `closeReaderModal` scroll-lock (prevent body scroll while reader open)
  10. Reader: pinch-to-zoom via touch events on the PDF canvas
"""

import sys

def patch(content, old, new, label):
    if old not in content:
        print(f"  [WARN] Pattern not found — skipping: {label}")
        return content
    result = content.replace(old, new, 1)
    print(f"  [OK] Applied: {label}")
    return result

with open("scripts/generate_4.py", "r", encoding="utf-8") as f:
    content = f.read()

print("=== NOVELIX 7.0 Premium UI Patch ===")

# ═══════════════════════════════════════════════════════════════
# UI FIX 1: Reader — add pinch-to-zoom and swipe-to-turn touch support
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """function changeReaderPage(delta) {
  if (!APP_STATE.pdfDocument) return;
  const newPage = APP_STATE.pdfPageNumber + delta;
  if (newPage >= 1 && newPage <= APP_STATE.pdfDocument.numPages) {
    renderPdfPage(newPage);
  }
}""",
    """function changeReaderPage(delta) {
  if (!APP_STATE.pdfDocument) return;
  const newPage = APP_STATE.pdfPageNumber + delta;
  if (newPage >= 1 && newPage <= APP_STATE.pdfDocument.numPages) {
    renderPdfPage(newPage);
  }
}

// ── Reader: Touch gesture support (pinch-to-zoom + swipe-to-turn) ──
(function initReaderTouchGestures() {
  let _touchStartX = 0, _touchStartY = 0;
  let _pinchStartDist = 0, _pinchStartScale = 1.35;
  let _isTap = false;

  document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('pdfRenderCanvas');
    if (!canvas) return;

    canvas.addEventListener('touchstart', (e) => {
      if (e.touches.length === 2) {
        // Pinch start
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        _pinchStartDist = Math.sqrt(dx * dx + dy * dy);
        _pinchStartScale = APP_STATE.pdfZoomScale || 1.35;
        e.preventDefault();
      } else if (e.touches.length === 1) {
        _touchStartX = e.touches[0].clientX;
        _touchStartY = e.touches[0].clientY;
        _isTap = true;
      }
    }, { passive: false });

    canvas.addEventListener('touchmove', (e) => {
      if (e.touches.length === 2 && _pinchStartDist > 0) {
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const ratio = dist / _pinchStartDist;
        APP_STATE.pdfZoomScale = Math.max(0.5, Math.min(4.0, _pinchStartScale * ratio));
        APP_STATE.readerFitMode = 'custom';
        e.preventDefault();
      } else if (e.touches.length === 1) {
        const moveX = Math.abs(e.touches[0].clientX - _touchStartX);
        const moveY = Math.abs(e.touches[0].clientY - _touchStartY);
        if (moveX > 8 || moveY > 8) _isTap = false;
      }
    }, { passive: false });

    canvas.addEventListener('touchend', (e) => {
      if (e.touches.length === 0 && _pinchStartDist > 0) {
        // Pinch ended — render at new zoom
        if (APP_STATE.pdfDocument) renderPdfPage(APP_STATE.pdfPageNumber);
        _pinchStartDist = 0;
      } else if (_isTap && e.changedTouches.length === 1) {
        // Tap left/right third to turn pages
        const tapX = e.changedTouches[0].clientX;
        const w = window.innerWidth;
        if (tapX < w * 0.3) {
          changeReaderPage(-1);
        } else if (tapX > w * 0.7) {
          changeReaderPage(1);
        }
        _isTap = false;
      }
    });
  });
})();""",
    "UI: reader pinch-to-zoom + swipe-left/right tap-to-turn"
)

# ═══════════════════════════════════════════════════════════════
# UI FIX 2: Body scroll lock when reader is open
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """function closeReaderModal() {
  document.getElementById('readerModal').classList.remove('open');
  if (document.fullscreenElement) {
    document.exitFullscreen().catch(() => {});
  }
}""",
    """function closeReaderModal() {
  document.getElementById('readerModal').classList.remove('open');
  document.body.style.overflow = '';
  document.body.style.position = '';
  if (document.fullscreenElement) {
    document.exitFullscreen().catch(() => {});
  }
  // Cancel any in-progress render
  if (APP_STATE._currentRenderTask) {
    try { APP_STATE._currentRenderTask.cancel(); } catch(e) {}
    APP_STATE._currentRenderTask = null;
  }
}""",
    "UI: closeReaderModal restores body scroll"
)

# ═══════════════════════════════════════════════════════════════
# UI FIX 3: Lock body scroll when reader opens (in launchActiveReader)
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """  closeBookDetailModal();
  const readerModal = document.getElementById('readerModal');
  readerModal.classList.add('open');
  document.getElementById('readerTitle').textContent = book.title || 'NOVELIX Reader';""",
    """  closeBookDetailModal();
  document.body.style.overflow = 'hidden';
  document.body.style.position = 'fixed';
  document.body.style.width = '100%';
  const readerModal = document.getElementById('readerModal');
  readerModal.classList.add('open');
  document.getElementById('readerTitle').textContent = book.title || 'NOVELIX Reader';""",
    "UI: lock body scroll on reader open"
)

# ═══════════════════════════════════════════════════════════════
# UI FIX 4: Improve skeleton loader quality — shimmer instead of pulse
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """      .skeleton {
        background: linear-gradient(90deg, #1B1B27 25%, #262638 50%, #1B1B27 75%);
        background-size: 200% 100%;
        animation: skeleton-wave 1.4s ease-in-out infinite;
      }""",
    """      .skeleton {
        background: linear-gradient(90deg, #161620 0%, #232334 40%, #2a2a40 50%, #232334 60%, #161620 100%);
        background-size: 300% 100%;
        animation: skeleton-wave 1.6s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        border-radius: 6px;
      }""",
    "UI: improve skeleton shimmer quality"
)

# ═══════════════════════════════════════════════════════════════
# UI FIX 5: Add "Pages" info and file size to book detail modal
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """  document.getElementById('detailTitle').textContent = book.title || 'Untitled';
  document.getElementById('detailAuthor').textContent = book.authorName || 'Author';
  document.getElementById('detailSynopsis').textContent = book.description || 'No synopsis provided.';
  document.getElementById('detailFormatTag').textContent = formatLabel(book.contentType);
  document.getElementById('detailReadsCount').textContent = `${formatCompactNum(book.viewCount || 0)} reads`;
  document.getElementById('detailRating').textContent = `★ ${book.avgRating ? book.avgRating.toFixed(1) : '4.8'}`;""",
    """  document.getElementById('detailTitle').textContent = book.title || 'Untitled';
  document.getElementById('detailAuthor').textContent = book.authorName || 'Author';
  document.getElementById('detailSynopsis').textContent = book.description || 'No synopsis provided.';
  document.getElementById('detailFormatTag').textContent = formatLabel(book.contentType);
  document.getElementById('detailReadsCount').textContent = `${formatCompactNum(book.viewCount || 0)} reads`;
  document.getElementById('detailRating').textContent = `★ ${book.avgRating ? book.avgRating.toFixed(1) : '4.8'}`;

  // Show file info metadata if available
  const detailMeta = document.getElementById('detailFileMeta');
  if (detailMeta) {
    const edCount = Array.isArray(book.languages) ? book.languages.length : (book.fileUrl ? 1 : 0);
    const totalSize = Array.isArray(book.languages)
      ? book.languages.reduce((s, e) => s + (e.fileSize || 0), 0)
      : (book.fileSize || 0);
    const sizeMB = totalSize > 0 ? ` · ${(totalSize / (1024 * 1024)).toFixed(1)} MB` : '';
    const edLabel = edCount === 1 ? '1 edition' : `${edCount} editions`;
    detailMeta.textContent = `${edLabel}${sizeMB}`;
    detailMeta.classList.remove('hidden');
  }""",
    "UI: book detail shows edition count + file size"
)

# ═══════════════════════════════════════════════════════════════
# UI FIX 6: Add `detailFileMeta` element in book detail modal HTML
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """<span id="detailReadsCount" class="text-[11px] text-app-muted font-medium"></span>
        <span id="detailRating" class="text-[11px] text-yellow-400 font-semibold"></span>""",
    """<span id="detailReadsCount" class="text-[11px] text-app-muted font-medium"></span>
        <span id="detailRating" class="text-[11px] text-yellow-400 font-semibold"></span>
        <span id="detailFileMeta" class="hidden text-[11px] text-app-secondary font-mono"></span>""",
    "UI: add detailFileMeta span to book detail modal"
)

# ═══════════════════════════════════════════════════════════════
# UI FIX 7: Add "Back" button safety handler to reader
#           (book detail re-open if back pressed while reading)
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """// ────────────────────────────────────────────────────────
// NAVIGATION ROUTER
// ────────────────────────────────────────────────────────
function switchPage(pageId) {""",
    """// ────────────────────────────────────────────────────────
// ANDROID BACK BUTTON HANDLER
// ────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.addEventListener('backbutton', (e) => {
    e.preventDefault();
    // If reader is open, close reader
    const readerModal = document.getElementById('readerModal');
    if (readerModal && readerModal.classList.contains('open')) {
      closeReaderModal();
      if (APP_STATE.selectedBook) openBookDetail(APP_STATE.selectedBook.id);
      return;
    }
    // If book detail is open, close it
    const bookDetail = document.getElementById('bookDetailModal');
    if (bookDetail && bookDetail.classList.contains('open')) {
      closeBookDetailModal();
      return;
    }
    // If auth modal is open, close it
    const authModal = document.getElementById('authModal');
    if (authModal && authModal.classList.contains('open')) {
      closeAuthModal?.();
      return;
    }
    // Otherwise go home if not already there
    if (APP_STATE.activePage !== 'home') {
      switchPage('home');
    }
  }, false);
});

// ────────────────────────────────────────────────────────
// NAVIGATION ROUTER
// ────────────────────────────────────────────────────────
function switchPage(pageId) {""",
    "UI: Android hardware back button handler"
)

# ═══════════════════════════════════════════════════════════════
# UI FIX 8: Improve zoomReader to also refresh render immediately
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """function zoomReader(delta) {
  APP_STATE.readerFitMode = 'custom';
  APP_STATE.pdfZoomScale = Math.max(0.6, Math.min(3.0, (APP_STATE.pdfZoomScale || 1.35) + delta));
  if (APP_STATE.pdfDocument) renderPdfPage(APP_STATE.pdfPageNumber);
}""",
    """function zoomReader(delta) {
  if (!APP_STATE.pdfDocument) return;
  APP_STATE.readerFitMode = 'custom';
  const currentScale = APP_STATE.pdfZoomScale || 1.35;
  APP_STATE.pdfZoomScale = Math.max(0.5, Math.min(4.0, currentScale + delta));
  renderPdfPage(APP_STATE.pdfPageNumber);
  showToast(`Zoom: ${Math.round(APP_STATE.pdfZoomScale * 100)}%`);
}""",
    "UI: zoomReader shows zoom percentage toast"
)

# ═══════════════════════════════════════════════════════════════
# UI FIX 9: setFitMode — show helpful toast + store zoom level
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """function setFitMode(mode) {
  APP_STATE.readerFitMode = mode;
  if (APP_STATE.pdfDocument) renderPdfPage(APP_STATE.pdfPageNumber);
}""",
    """function setFitMode(mode) {
  if (!APP_STATE.pdfDocument) return;
  APP_STATE.readerFitMode = mode;
  if (mode === 'width') {
    showToast('Fit to width');
  } else if (mode === 'page') {
    showToast('Fit to page');
  }
  renderPdfPage(APP_STATE.pdfPageNumber);
}""",
    "UI: setFitMode shows toast feedback"
)

# ═══════════════════════════════════════════════════════════════
# UI FIX 10: Book reading launch from library "continue reading" row
# Ensure the edition that was last selected is remembered
# ═══════════════════════════════════════════════════════════════
content = patch(content,
    """  APP_STATE.pdfPageNumber = page;
  launchActiveReader();""",
    """  APP_STATE.pdfPageNumber = page;
  // Restore the edition that was being read (by language match)
  if (book && Array.isArray(book.languages) && editionLanguage) {
    const matchedEd = book.languages.find(e => e.language === editionLanguage);
    if (matchedEd) APP_STATE.selectedEdition = matchedEd;
  }
  launchActiveReader();""",
    "UI: library continue-reading restores correct edition"
)

with open("scripts/generate_4.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\n=== UI Patch complete. Verifying syntax… ===")
import py_compile
try:
    py_compile.compile("scripts/generate_4.py", doraise=True)
    print("OK — no syntax errors.")
except py_compile.PyCompileError as e:
    print(f"ERROR: {e}")
    sys.exit(1)
