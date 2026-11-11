#!/usr/bin/env python3
"""
Final touches for NOVELIX 11.0:
1. Save seriesId and seriesOrder into docPayload in handlePublishSubmit
2. Display series on book detail modal
3. Call populatePublishSeriesDropdown when entering publish page
"""

GEN_FILE = "scripts/generate_4.py"

with open(GEN_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update docPayload in handlePublishSubmit
doc_payload_old = """    const docPayload = {
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
      storageProvider: primaryStorage,"""

doc_payload_new = """    const selSeriesId = document.getElementById('publishSeriesSelect')?.value || '';
    const selSeriesOrder = (document.getElementById('publishSeriesOrderInput')?.value || '').trim();

    const docPayload = {
      id: bookId,
      title: title,
      description: desc,
      contentType: APP_STATE.selectedFormat,
      genres: (APP_STATE.selectedGenres || []).slice(0, 4),
      coverUrl: coverUrl,
      coverSize: coverSize,
      seriesId: selSeriesId,
      seriesOrder: selSeriesOrder,
      status: status,
      visibility: visibility,
      publishStatus: status === 'draft' ? 'draft' : 'published',
      storageProvider: primaryStorage,"""

if doc_payload_old in content:
    content = content.replace(doc_payload_old, doc_payload_new, 1)
    print("✓ Added seriesId and seriesOrder to docPayload")
else:
    print("WARNING: doc_payload_old not found")

# Increment series count when book is published
series_union_code = """    // Step 6: Creating publication record
    updatePublishStep(6, 'in_progress');
    await db.collection('books').doc(bookId).set(docPayload, { merge: true });
    updatePublishStep(6, 'completed');

    if (selSeriesId && db) {
      db.collection('series').doc(selSeriesId).update({
        bookCount: firebase.firestore.FieldValue.increment(1),
        books: firebase.firestore.FieldValue.arrayUnion({
          bookId: bookId,
          title: title,
          order: selSeriesOrder || 'Book',
          coverUrl: coverUrl
        })
      }).catch(err => console.warn('Series update notice:', err));
    }"""

old_step6 = """    // Step 6: Creating publication record
    updatePublishStep(6, 'in_progress');
    await db.collection('books').doc(bookId).set(docPayload, { merge: true });
    updatePublishStep(6, 'completed');"""

if old_step6 in content:
    content = content.replace(old_step6, series_union_code, 1)
    print("✓ Added series union update to Step 6")
else:
    print("WARNING: old_step6 not found")

# 2. Display series on book detail modal
old_detail_fmt = """  document.getElementById('detailFormatTag').textContent = formatLabel(book.contentType);"""
new_detail_fmt = """  const seriesLabel = book.seriesOrder ? `📚 ${book.seriesOrder}` : (book.seriesId ? '📚 In Series' : '');
  document.getElementById('detailFormatTag').textContent = seriesLabel ? `${formatLabel(book.contentType)} · ${seriesLabel}` : formatLabel(book.contentType);"""

if old_detail_fmt in content:
    content = content.replace(old_detail_fmt, new_detail_fmt, 1)
    print("✓ Updated detailFormatTag to display series information")
else:
    print("WARNING: old_detail_fmt not found")

# 3. Call populatePublishSeriesDropdown when entering publish page
old_switch_pub = """  if (pageId === 'publish') updatePublishAccessState();"""
new_switch_pub = """  if (pageId === 'publish') {
    updatePublishAccessState();
    populatePublishSeriesDropdown();
  }"""

if old_switch_pub in content:
    content = content.replace(old_switch_pub, new_switch_pub, 1)
    print("✓ Added populatePublishSeriesDropdown call to switchPage('publish')")
else:
    print("WARNING: old_switch_pub not found")

with open(GEN_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("Saved generate_4.py successfully")
