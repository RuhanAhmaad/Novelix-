# NOVELIX 5.0 — Google Drive Publishing Integration Report

## 1. Executive Summary

NOVELIX 5.0 introduces an end-to-end author publishing workflow that allows authors to publish books using either **Google Drive** or **Firebase Storage** as the manuscript storage provider. The architecture guarantees zero exposure of private OAuth refresh tokens or client secrets, provides multi-account Google Drive support, enables direct upload into a dedicated `NOVELIX` folder in the author's Google Drive, and validates all file metadata before committing publications to Firestore.

---

## 2. Key Requirements & Architecture

### A. Author Publishing Flow
1. Author inputs book details: title, synopsis, format (Book, Comic, Manga, Textbook), and up to 4 genres.
2. Author uploads high-resolution cover image (stored in Firebase Storage `covers/{bookId}/...` or ImgBB fallback).
3. Author configures language editions (English, Spanish, French, Arabic, Japanese, Korean, German, Portuguese, Chinese).
4. For each edition, the author selects the Storage Provider:
   - **Google Drive**: Can choose which connected account to use, select an existing PDF via Drive file picker, OR upload a new PDF from device directly to the author's Google Drive in a `NOVELIX` folder.
   - **Device Storage**: Uploads the PDF file directly to Firebase Storage (`books/{bookId}/pdfs/...`).
5. Real-time progress displays step-by-step progress (`Uploading cover...`, `Processing edition...`, `Publishing to NOVELIX catalog...`).
6. Success is rendered only after backend confirmation and Firestore document creation.

### B. Cloud Functions Endpoints Added/Upgraded
In `functions/index.js`:
- `uploadPdfToDrive` (Callable Function):
  - Authenticates the caller.
  - Retrieves valid access token via `getValidDriveToken(callerUid, accountId)` (refreshes if needed).
  - Checks if a `NOVELIX` folder exists in the author's Google Drive root; if not, creates it.
  - Performs multipart upload directly to the `NOVELIX` folder.
  - Returns `fileId`, `fileName`, `fileSize`, `folderId`.
- `importGoogleDrivePdf` (Callable Function):
  - Imports an existing file reference or creates a cloud copy for caching.
- `getReaderPdfData` (Callable Function):
  - Securely streams/serves Drive PDFs to authenticated readers through server-side proxy without making author's Drive files public.
- `streamDrivePdf` (HTTP Endpoint):
  - Streams PDF bytes directly with `Content-Type: application/pdf` and private cache control.

---

## 3. Firestore Document Schema (`books/{bookId}`)

```typescript
interface NovelixBookDocument {
  id: string;
  title: string;
  description: string;
  contentType: 'book' | 'comic' | 'manga' | 'textbook';
  genres: string[];
  coverUrl: string;
  coverSize: number;
  status: 'ongoing' | 'completed' | 'draft';
  visibility: 'public' | 'unlisted';
  publishStatus: 'published' | 'draft';
  storageProvider: 'drive' | 'storage';
  languages: Array<{
    language: string;
    storageProvider: 'drive' | 'storage';
    fileUrl?: string;           // Firebase Storage URL if stored in Firebase
    driveFileId?: string;       // Google Drive file ID if stored in Drive
    driveAccountId?: string;    // Connected Drive account reference
    fileName: string;
    fileSize: number;
    uploadedAt: string;
  }>;
  authorId: string;
  authorName: string;
  authorPhoto: string;
  authors: Array<{
    uid: string;
    name: string;
    photoURL: string;
    role: string;
  }>;
  viewCount: number;
  likeCount: number;
  bookmarkCount: number;
  avgRating: number;
  createdAt: FirebaseFirestore.Timestamp;
  updatedAt: FirebaseFirestore.Timestamp;
}
```

---

## 4. Multi-Account Google Drive Management

Authors can connect multiple Google Drive accounts in NOVELIX:
1. Each connected account is stored under `users/{uid}/drive_accounts/{accountId}` with metadata (email, displayName, photoURL).
2. Confidential refresh tokens are encrypted using AES-256-CBC and stored in a protected server-only collection `users/{uid}/drive_secure_tokens/{accountId}`.
3. In the publishing dashboard, each edition row features a dropdown allowing the author to select which specific Drive account to use for the publication.
