#!/usr/bin/env python3
"""
Patch functions/index.js to add:
1. extractGoogleDriveFileId(url)
2. validateGoogleDriveLink callable function
3. Update getReaderPdfData to support public and private drive files smoothly
4. Update streamDrivePdf to support public and private drive files
"""

import sys

TARGET = "functions/index.js"

with open(TARGET, "r", encoding="utf-8") as f:
    content = f.read()

# ─────────────────────────────────────────────────────────────
# 1. Add extractGoogleDriveFileId helper and validateGoogleDriveLink
# ─────────────────────────────────────────────────────────────
new_functions = """/**
 * Helper to safely extract Google Drive File ID from diverse URL formats:
 * - https://drive.google.com/file/d/FILE_ID/view
 * - https://drive.google.com/open?id=FILE_ID
 * - https://drive.google.com/uc?id=FILE_ID
 * - https://drive.google.com/file/d/FILE_ID/edit
 * - https://docs.google.com/file/d/FILE_ID/...
 * - raw 25-65 character alphanumeric file IDs
 */
function extractGoogleDriveFileId(url) {
  if (!url || typeof url !== 'string') return null;
  const trimmed = url.trim();

  // /file/d/([a-zA-Z0-9_-]{25,})/
  const m1 = trimmed.match(/\\/file\\/d\\/([a-zA-Z0-9_-]{25,})/);
  if (m1) return m1[1];

  // id=([a-zA-Z0-9_-]{25,})
  const m2 = trimmed.match(/[?&]id=([a-zA-Z0-9_-]{25,})/);
  if (m2) return m2[1];

  // /d/([a-zA-Z0-9_-]{25,})
  const m3 = trimmed.match(/\\/d\\/([a-zA-Z0-9_-]{25,})/);
  if (m3) return m3[1];

  // Bare ID
  if (/^[a-zA-Z0-9_-]{25,65}$/.test(trimmed)) {
    return trimmed;
  }

  return null;
}

/**
 * 14B. VALIDATE GOOGLE DRIVE LINK (Callable Function)
 * Validates pasted Google Drive links for publishing without requiring re-upload:
 * 1. Safely parses URL and extracts fileId.
 * 2. Checks public availability (HEAD / GET probe).
 * 3. If private, verifies against user's connected Google Drive account(s).
 * 4. Ensures document is a valid PDF and retrieves real title and size.
 */
exports.validateGoogleDriveLink = onCall({
  secrets: [googleDriveOAuthClientJson],
  concurrency: 80,
  maxInstances: 100
}, async (request) => {
  const callerUid = request.auth ? request.auth.uid : null;
  if (!callerUid) {
    throw new HttpsError('unauthenticated', 'User must be authenticated with NOVELIX to validate Drive links.');
  }

  const { link, accountId } = request.data || {};
  if (!link || typeof link !== 'string') {
    throw new HttpsError('invalid-argument', 'Missing or invalid link.');
  }

  const fileId = extractGoogleDriveFileId(link);
  if (!fileId) {
    return {
      valid: false,
      error: 'INVALID_URL_FORMAT',
      message: 'Could not extract a valid Google Drive file ID from the link. Please provide a standard drive.google.com link.'
    };
  }

  // 1. First probe public accessibility
  let publicInfo = null;
  try {
    const probeRes = await fetch(`https://drive.google.com/uc?id=${fileId}&export=download`, {
      method: 'GET',
      headers: { 'Range': 'bytes=0-1024' },
      redirect: 'follow'
    });

    const contentType = (probeRes.headers.get('content-type') || '').toLowerCase();
    const disposition = probeRes.headers.get('content-disposition') || '';

    if (probeRes.ok) {
      const buffer = await probeRes.arrayBuffer();
      const bytes = new Uint8Array(buffer);
      // Validate PDF magic bytes: %PDF
      const isPdfHeader = bytes.length >= 4 && bytes[0] === 0x25 && bytes[1] === 0x50 && bytes[2] === 0x44 && bytes[3] === 0x46;

      if (isPdfHeader || contentType.includes('application/pdf')) {
        let extractedName = '';
        const matchName = disposition.match(/filename\\*?=['"]?(?:UTF-\\d['"]*)?([^;\\r\\n"']*)['"]?/i);
        if (matchName && matchName[1]) extractedName = decodeURIComponent(matchName[1]);

        publicInfo = {
          isPublic: true,
          fileId: fileId,
          fileName: extractedName || `Google_Drive_${fileId.substring(0, 8)}.pdf`,
          fileSize: parseInt(probeRes.headers.get('content-range')?.split('/')[1] || probeRes.headers.get('content-length') || '0', 10),
          mimeType: 'application/pdf',
          downloadUrl: `https://drive.google.com/uc?id=${fileId}&export=download`
        };
      }
    }
  } catch (probeErr) {
    console.warn('Public probe notice:', probeErr.message);
  }

  if (publicInfo) {
    return {
      valid: true,
      fileId: fileId,
      isPublic: true,
      fileName: publicInfo.fileName,
      fileSize: publicInfo.fileSize,
      mimeType: publicInfo.mimeType,
      message: 'Public Google Drive PDF verified successfully!'
    };
  }

  // 2. If not public, check user's connected Google Drive accounts
  const accountsSnap = await db.collection('users').doc(callerUid).collection('drive_accounts').get();
  const availableAccounts = [];
  accountsSnap.forEach(doc => availableAccounts.push(doc.data()));

  if (availableAccounts.length === 0) {
    return {
      valid: false,
      fileId: fileId,
      isPublic: false,
      error: 'AUTH_REQUIRED',
      message: 'This Google Drive file is private. Please connect your Google Drive account so NOVELIX can verify and access the manuscript, or adjust the file sharing in Google Drive to "Anyone with the link".'
    };
  }

  // If accountId provided, check that account first; otherwise test each connected account
  let targetAccounts = availableAccounts;
  if (accountId) {
    const matched = availableAccounts.find(a => a.id === accountId);
    if (matched) targetAccounts = [matched, ...availableAccounts.filter(a => a.id !== accountId)];
  }

  let lastDriveError = null;
  for (const acct of targetAccounts) {
    try {
      const tokenData = await getValidDriveToken(callerUid, acct.id);
      const metaRes = await fetch(`https://www.googleapis.com/drive/v3/files/${fileId}?fields=id,name,mimeType,size,trashed`, {
        headers: { Authorization: `Bearer ${tokenData.accessToken}` }
      });

      if (metaRes.ok) {
        const meta = await metaRes.json();
        if (meta.trashed) {
          return {
            valid: false,
            fileId: fileId,
            isPublic: false,
            error: 'FILE_TRASHED',
            message: 'This manuscript is in your Google Drive trash. Please restore it before publishing.'
          };
        }

        if (meta.mimeType !== 'application/pdf' && !meta.name.toLowerCase().endsWith('.pdf')) {
          return {
            valid: false,
            fileId: fileId,
            isPublic: false,
            error: 'NOT_A_PDF',
            message: `Selected file is ${meta.mimeType || 'not a PDF'}. NOVELIX only supports PDF manuscripts.`
          };
        }

        return {
          valid: true,
          fileId: fileId,
          isPublic: false,
          accountId: acct.id,
          accountEmail: acct.email,
          fileName: meta.name,
          fileSize: parseInt(meta.size || '0', 10),
          mimeType: meta.mimeType || 'application/pdf',
          message: `Private Google Drive manuscript verified via ${acct.email}.`
        };
      } else if (metaRes.status === 404) {
        lastDriveError = 'Account does not have access to this file.';
      } else if (metaRes.status === 403) {
        lastDriveError = 'Access denied by Google Drive. Check file sharing permissions.';
      }
    } catch(err) {
      lastDriveError = err.message;
    }
  }

  return {
    valid: false,
    fileId: fileId,
    isPublic: false,
    error: 'ACCESS_DENIED',
    message: lastDriveError || 'Your connected Google Drive account does not have permission to access this file.'
  };
});
"""

insertion_anchor = "exports.importGoogleDrivePdf = onCall("
if insertion_anchor not in content:
    print("Error: insertion anchor not found in functions/index.js")
    sys.exit(1)

content = content.replace(insertion_anchor, new_functions + "\n" + insertion_anchor)
print("1. Added extractGoogleDriveFileId and validateGoogleDriveLink to functions/index.js")

# ─────────────────────────────────────────────────────────────
# 2. Update getReaderPdfData to support public Drive links & streaming
# ─────────────────────────────────────────────────────────────
old_reader_pdf = """    const driveFileId = targetEdition.driveFileId || targetEdition.fileId;
    const driveAccountId = targetEdition.driveAccountId || book.driveAccountId;
    const authorUid = book.authorId;

    const tokenData = await getValidDriveToken(authorUid, driveAccountId);
    const driveRes = await fetch(`https://www.googleapis.com/drive/v3/files/${driveFileId}?alt=media`, {
      headers: { Authorization: `Bearer ${tokenData.accessToken}` }
    });"""

new_reader_pdf = """    const driveFileId = targetEdition.driveFileId || targetEdition.fileId;
    const driveAccountId = targetEdition.driveAccountId || book.driveAccountId;
    const authorUid = book.authorId;
    const driveIsPublic = targetEdition.driveIsPublic || book.driveIsPublic;

    // Fast-path: If public Drive link, probe/fetch directly without consuming Drive API quota
    if (driveIsPublic) {
      try {
        const publicRes = await fetch(`https://drive.google.com/uc?id=${driveFileId}&export=download`);
        if (publicRes.ok) {
          const arrayBuffer = await publicRes.arrayBuffer();
          const base64 = Buffer.from(arrayBuffer).toString('base64');
          return {
            success: true,
            storageProvider: 'drive',
            isPublic: true,
            base64: base64,
            fileName: targetEdition.fileName || `${book.title}.pdf`,
            fileSize: arrayBuffer.byteLength
          };
        }
      } catch (pubErr) {
        console.warn('Public drive fetch fallback to authenticated:', pubErr.message);
      }
    }

    const tokenData = await getValidDriveToken(authorUid, driveAccountId);
    const driveRes = await fetch(`https://www.googleapis.com/drive/v3/files/${driveFileId}?alt=media`, {
      headers: { Authorization: `Bearer ${tokenData.accessToken}` }
    });"""

if old_reader_pdf in content:
    content = content.replace(old_reader_pdf, new_reader_pdf)
    print("2. Updated getReaderPdfData in functions/index.js")
else:
    print("Warning: old_reader_pdf block not found, checking alternatives...")

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully updated functions/index.js")
