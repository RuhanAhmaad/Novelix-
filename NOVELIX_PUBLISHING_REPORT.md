# NOVELIX 7.0 — Publishing System Report

**Generated:** 2026-11-07  
**Module:** Author Publishing, Multi-Edition Management & Editing  
**Database:** Cloud Firestore (`books` collection)

---

## 1. Supported Creative Formats

Authors can publish across seven supported content types:
- **Books:** Single or multi-volume standard manuscripts.
- **Novels:** Light novels, serialized web novels, and prose.
- **Series:** Episodic or multi-part narrative releases.
- **Chapters:** Individual serialized chapter releases.
- **Manhwa:** Vertical scrolling Korean webtoons.
- **Manga:** Japanese-style right-to-left formatted works.
- **Comics:** Western comic books and graphic novels.

---

## 2. Multi-Language Editions & Volumes

Each publication contains a normalized `languages` array supporting unlimited editions and volumes:
```json
{
  "language": "English",
  "storageProvider": "storage",
  "fileUrl": "https://firebasestorage.googleapis.com/...",
  "storagePath": "books/{bookId}/pdfs/English_1730971200000.pdf",
  "fileName": "volume_1.pdf",
  "fileSize": 3481920,
  "uploadedAt": "2026-11-07T09:45:00.000Z"
}
```

Authors can attach manuscripts through:
1. **Firebase Storage Upload:** Direct multipart upload via `storage.ref().put()`.
2. **Google Drive Integration:** Direct selection from authorized Google Drive accounts via backend callable or folder upload.

---

## 3. Publication Editing & Unpublishing Workflow

NOVELIX 7.0 introduces full author publication lifecycle management:
1. **Edit Publication (`openEditPublication(bookId)`):**
   - Pre-populates title, synopsis, content type, genres, status, and visibility.
   - Preserves existing editions and cover images.
   - Sets `APP_STATE.editingBookId` to execute an `update()` instead of creating a duplicate document.
2. **Draft Saving:**
   - Authors can save unfinished works with `publishStatus: 'draft'`, keeping them private.
3. **Unpublishing:**
   - Setting visibility to `unlisted` or status to `draft` instantly removes the work from public Home and Explore feeds while preserving author access in Profile.
4. **Permanent Deletion:**
   - Authors can delete their publications directly from the Profile Works tab with confirmation.
