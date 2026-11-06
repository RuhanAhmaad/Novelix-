# NOVELIX 7.0 — PDF Integration Report

**Generated:** 2026-11-06  
**Commit:** `072ea3e`

---

## PDF Library

**Library:** PDF.js 3.11.174 (Mozilla)  
**Loading:** CDN `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js`  
**Worker mode:** `disableWorker: true` — single-thread rendering in Capacitor Android WebView  
**CMap:** Loaded from CDN for international character support

> **Why PDF.js over native plugin?**  
> NOVELIX is a Capacitor web app. The in-app reader uses a `<canvas>` element to render PDFs via PDF.js directly in the WebView. This avoids launching an external viewer and gives full control over the reading UI (zoom, themes, page turns, bookmarks). PDF.js is the same engine used by Firefox and Google Chrome.

---

## Storage Integration Map

```
Book Published → Firestore: books/{bookId}
  └── languages[]: Array of editions
        ├── storageProvider: "storage" | "drive" | "external"
        ├── fileUrl:         Firebase Storage download URL (may expire)
        ├── storagePath:     Firebase Storage internal path (used to regenerate URL)
        ├── driveFileId:     Google Drive file ID
        ├── driveAccountId:  Author's linked Drive account ID
        └── language:        "English" | "Urdu" | "Arabic" | ...
```

---

## PDF Loading Flow (All Providers)

### A. Firebase Storage

```
openBookDetail(bookId)
  → edition.storageProvider === 'storage'
  → loadPdfDocumentForReader(book, edition, page)
    → fetch(edition.fileUrl) with credentials:'omit'
    → [if 403/404] storage.ref(edition.storagePath).getDownloadURL() [URL refresh]
    → fetch(freshUrl) → Uint8Array
    → validate %PDF- magic bytes
    → pdfjsLib.getDocument({ data: bytes, disableWorker: true })
    → renderPdfPage(page)
```

### B. Google Drive (via Cloud Function proxy)

```
openBookDetail(bookId)
  → edition.storageProvider === 'drive'
  → loadPdfDocumentForReader(book, edition, page)
    → functions.httpsCallable('getReaderPdfData')({ bookId, language })
      [Server: auth check → author's refreshed Drive token → fetch file → base64]
    → atob(res.data.base64) → Uint8Array
    → validate %PDF- magic bytes
    → pdfjsLib.getDocument({ data: bytes, disableWorker: true })
    → renderPdfPage(page)
```

### C. External HTTPS PDF URL

```
openBookDetail(bookId)
  → edition.fileUrl = 'https://example.com/book.pdf'
  → edition.storageProvider === 'storage' (no driveFileId)
  → fetch(edition.fileUrl) with credentials:'omit'
  → content-type check (reject HTML error pages)
  → Uint8Array → %PDF- validation
  → pdfjsLib.getDocument({ data: bytes, disableWorker: true })
```

---

## Firestore Metadata Fields (Per Edition)

| Field | Type | Description |
|-------|------|-------------|
| `language` | String | Edition language label (e.g., "English", "Urdu") |
| `storageProvider` | String | "storage", "drive", or "external" |
| `fileUrl` | String | Download URL (Firebase Storage token URL or HTTPS) |
| `storagePath` | String | Firebase Storage path (`books/{id}/pdfs/…`) for URL refresh |
| `driveFileId` | String | Google Drive file ID |
| `driveAccountId` | String | Author's linked Drive account reference |
| `fileName` | String | Original filename |
| `fileSize` | Number | Bytes |
| `uploadedAt` | String | ISO 8601 timestamp |

**Root-level book fields (legacy / single-edition fallback):**

| Field | Type | Description |
|-------|------|-------------|
| `fileUrl` | String | Synthesized into edition on `openBookDetail()` |
| `driveFileId` | String | Synthesized into edition on `openBookDetail()` |
| `storageProvider` | String | Root-level fallback |
| `publishStatus` | String | "published" or "draft" |
| `visibility` | String | "public" or "private" |

---

## Reading Progress Schema (Firestore)

```
users/{uid}/reading_progress/{bookId}
  bookId:                 "abc123"      ← matches document ID
  id:                     "abc123"      ← redundant but explicit
  title:                  "My Novel"
  authorName:             "Jane Doe"
  coverUrl:               "https://…"
  contentType:            "book"
  page:                   47            ← last read page
  totalPages:             312
  percent:                15
  selectedEditionLanguage: "English"    ← which edition was being read
  bookmarks:              [12, 47, 89]  ← bookmarked page numbers
  lastReadAt:             Timestamp
```

---

## Security Notes

- Google Drive OAuth tokens are **never exposed to the frontend**. The Cloud Function `getReaderPdfData` uses the author's encrypted refresh token from Firestore to obtain a fresh access token server-side, fetches the PDF binary, and returns it as Base64 to the caller.
- Firebase Storage security rules are respected. Anonymous users can only read books with `visibility: public`.
- The `getReaderPdfData` callable verifies: (1) book exists in Firestore, (2) book is published and public OR caller is the author.
- No PDF bytes are written to device storage — they are held in memory (`APP_STATE._pdfCache`) and cleared on app restart.
