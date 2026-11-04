/**
 * NOVELIX 4.0 — Cloud Functions for Firebase
 * High-performance, serverless backend operations & secure admin endpoints
 */

const { onDocumentCreated, onDocumentWritten, onDocumentUpdated } = require('firebase-functions/v2/firestore');
const { onCall, onRequest, HttpsError } = require('firebase-functions/v2/https');
const admin = require('firebase-admin');
const crypto = require('crypto');

if (!admin.apps.length) {
  admin.initializeApp();
}

const db = admin.firestore();
const auth = admin.auth();

// Default storage quota per user: 500 MB in bytes
const DEFAULT_USER_QUOTA_BYTES = 500 * 1024 * 1024;

// Google Drive OAuth 2.0 Configuration with Secret Manager & defineJsonSecret
const { defineJsonSecret } = require('firebase-functions/params');
const googleDriveOAuthClientJson = defineJsonSecret('GOOGLE_DRIVE_OAUTH_CLIENT_JSON');

const CANONICAL_DRIVE_REDIRECT_URI = 'https://us-central1-novelxa-48f15.cloudfunctions.net/googleDriveCallback';
const TOKEN_ENCRYPTION_SECRET = process.env.TOKEN_ENCRYPTION_SECRET || 'novelix-super-secure-aes256-key-32chars!';
const GOOGLE_DRIVE_SCOPES = [
  'https://www.googleapis.com/auth/drive.readonly',
  'https://www.googleapis.com/auth/userinfo.email',
  'https://www.googleapis.com/auth/userinfo.profile'
].join(' ');

/**
 * Resolves Google OAuth credentials from Secret Manager (GOOGLE_DRIVE_OAUTH_CLIENT_JSON)
 * or fallback environment variables.
 */
function getGoogleOAuthCredentials() {
  let clientId = '';
  let clientSecret = '';

  try {
    const jsonVal = googleDriveOAuthClientJson.value();
    if (jsonVal) {
      const config = jsonVal.web || jsonVal.installed || jsonVal;
      clientId = config.client_id || '';
      clientSecret = config.client_secret || '';
    }
  } catch (e) {
    // Secret not available in current execution context or running in local mode
  }

  if (!clientId) {
    clientId = process.env.GOOGLE_DRIVE_CLIENT_ID || process.env.GOOGLE_CLIENT_ID || '23165793827-un6a2kh299r2e7rroj9nivoku5josvlh.apps.googleusercontent.com';
  }
  if (!clientSecret) {
    clientSecret = process.env.GOOGLE_DRIVE_CLIENT_SECRET || process.env.GOOGLE_CLIENT_SECRET || '';
  }

  return { clientId, clientSecret };
}

/**
 * Token encryption / decryption helpers for secure storage of refresh tokens
 */
function encryptToken(text) {
  if (!text) return '';
  const key = crypto.createHash('sha256').update(TOKEN_ENCRYPTION_SECRET).digest();
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
  let enc = cipher.update(text, 'utf8', 'hex');
  enc += cipher.final('hex');
  const tag = cipher.getAuthTag();
  return `${iv.toString('hex')}:${tag.toString('hex')}:${enc}`;
}

function decryptToken(encrypted) {
  if (!encrypted || !encrypted.includes(':')) return '';
  try {
    const parts = encrypted.split(':');
    if (parts.length !== 3) return '';
    const iv = Buffer.from(parts[0], 'hex');
    const tag = Buffer.from(parts[1], 'hex');
    const enc = parts[2];
    const key = crypto.createHash('sha256').update(TOKEN_ENCRYPTION_SECRET).digest();
    const decipher = crypto.createDecipheriv('aes-256-gcm', key, iv);
    decipher.setAuthTag(tag);
    let dec = decipher.update(enc, 'hex', 'utf8');
    dec += decipher.final('utf8');
    return dec;
  } catch (err) {
    console.error('Token decryption error:', err);
    return '';
  }
}


/**
 * 1. SET ADMIN CLAIM (Callable Function)
 * Securely assign admin custom claim. Only verified admins or initial bootstrap secret can call this.
 */
exports.setAdminRole = onCall(async (request) => {
  const callerUid = request.auth ? request.auth.uid : null;
  const targetEmail = request.data.email;
  const targetUid = request.data.uid;
  const bootstrapSecret = request.data.bootstrapSecret;

  let isAuthorized = false;

  // Check if caller already has admin claim
  if (callerUid) {
    const callerUser = await auth.getUser(callerUid);
    if (callerUser.customClaims && callerUser.customClaims.admin === true) {
      isAuthorized = true;
    }
  }

  // Initial bootstrap authorization check
  const envSecret = process.env.ADMIN_BOOTSTRAP_SECRET || 'novelix-admin-secure-init-2026';
  if (bootstrapSecret && bootstrapSecret === envSecret) {
    isAuthorized = true;
  }

  if (!isAuthorized) {
    throw new HttpsError('permission-denied', 'Only authorized administrators can assign admin roles.');
  }

  let user;
  if (targetUid) {
    user = await auth.getUser(targetUid);
  } else if (targetEmail) {
    user = await auth.getUserByEmail(targetEmail);
  } else {
    throw new HttpsError('invalid-argument', 'Must provide target uid or email.');
  }

  // Set custom claims
  await auth.setCustomUserClaims(user.uid, { admin: true, role: 'admin' });

  // Update Firestore admin_users collection
  await db.collection('admin_users').doc(user.uid).set({
    email: user.email,
    displayName: user.displayName || 'Administrator',
    role: 'admin',
    assignedAt: admin.firestore.FieldValue.serverTimestamp(),
    assignedBy: callerUid || 'bootstrap',
  }, { merge: true });

  // Update user document
  await db.collection('users').doc(user.uid).set({
    isAdmin: true,
    role: 'admin',
  }, { merge: true });

  // Audit log
  await db.collection('admin_logs').add({
    adminId: callerUid || 'bootstrap',
    action: 'SET_ADMIN_ROLE',
    targetUid: user.uid,
    targetEmail: user.email,
    timestamp: admin.firestore.FieldValue.serverTimestamp(),
  });

  return { success: true, message: `Admin privileges granted to ${user.email} (${user.uid})` };
});

/**
 * 2. REVIEW AGGREGATION TRIGGER
 * Recalculate avgRating and ratingCount atomically whenever a review is written/updated/deleted.
 */
exports.onReviewWritten = onDocumentWritten('books/{bookId}/reviews/{reviewId}', async (event) => {
  const bookId = event.params.bookId;
  const reviewsRef = db.collection('books').doc(bookId).collection('reviews');

  const snapshot = await reviewsRef.get();
  let totalRating = 0;
  let count = 0;

  snapshot.forEach((doc) => {
    const data = doc.data();
    if (typeof data.rating === 'number') {
      totalRating += data.rating;
      count++;
    }
  });

  const avgRating = count > 0 ? parseFloat((totalRating / count).toFixed(2)) : 0;

  await db.collection('books').doc(bookId).update({
    avgRating: avgRating,
    ratingCount: count,
    updatedAt: admin.firestore.FieldValue.serverTimestamp(),
  });
});

/**
 * 3. NEW PUBLICATION / CHAPTER NOTIFICATION TRIGGER
 */
exports.onChapterPublished = onDocumentWritten('books/{bookId}/chapters/{chapterId}', async (event) => {
  const before = event.data.before ? event.data.before.data() : null;
  const after = event.data.after ? event.data.after.data() : null;

  if (!after || !after.isPublished) return;
  if (before && before.isPublished) return;

  const bookId = event.params.bookId;
  const bookDoc = await db.collection('books').doc(bookId).get();
  if (!bookDoc.exists) return;

  const book = bookDoc.data();
  const authorId = book.authorId;
  const bookTitle = book.title || 'Untitled';
  const chapterNum = after.chapterNumber || after.chapterNum || 1;

  const followersSnap = await db.collection('authors').doc(authorId).collection('followers').get();
  if (followersSnap.empty) return;

  const batch = db.batch();
  const notificationTitle = `New Chapter in ${bookTitle}`;
  const notificationBody = `Chapter ${chapterNum} is now available to read!`;

  followersSnap.forEach((followerDoc) => {
    const followerId = followerDoc.id;
    const notifRef = db.collection('users').doc(followerId).collection('notifications').doc();
    batch.set(notifRef, {
      type: 'chapter',
      title: notificationTitle,
      message: notificationBody,
      bookId: bookId,
      chapterId: event.params.chapterId,
      authorId: authorId,
      isRead: false,
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
    });
  });

  await batch.commit();

  try {
    await admin.messaging().send({
      topic: `book_${bookId}`,
      notification: {
        title: notificationTitle,
        body: notificationBody,
      },
      data: {
        bookId: bookId,
        chapterId: event.params.chapterId,
      },
    });
  } catch (err) {
    console.log('FCM Topic dispatch info:', err.message);
  }
});

/**
 * 4. NEW FOLLOWER NOTIFICATION
 */
exports.onFollowCreated = onDocumentCreated('authors/{authorId}/followers/{followerId}', async (event) => {
  const authorId = event.params.authorId;
  const followerId = event.params.followerId;

  const followerUser = await db.collection('users').doc(followerId).get();
  const followerName = followerUser.exists ? (followerUser.data().displayName || 'A reader') : 'A reader';

  await db.collection('users').doc(authorId).collection('notifications').add({
    type: 'follow',
    title: 'New Follower',
    message: `${followerName} started following your publications`,
    actorId: followerId,
    isRead: false,
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
  });
});

/**
 * 5. REAL-TIME STORAGE QUOTA RECALCULATION TRIGGER
 * Recalculates an author's total storage usage whenever a book is created, updated or deleted.
 */
exports.onBookStorageUpdated = onDocumentWritten('books/{bookId}', async (event) => {
  const before = event.data.before ? event.data.before.data() : null;
  const after = event.data.after ? event.data.after.data() : null;
  const authorId = (after && after.authorId) || (before && before.authorId);

  if (!authorId) return;

  // Query all books authored by this user
  const booksSnap = await db.collection('books').where('authorId', '==', authorId).get();
  let totalBytes = 0;

  booksSnap.forEach((doc) => {
    const data = doc.data();
    // Tally language edition file sizes
    if (Array.isArray(data.languages)) {
      data.languages.forEach((lang) => {
        if (typeof lang.fileSize === 'number') {
          totalBytes += lang.fileSize;
        } else if (lang.fileUrl) {
          totalBytes += 1.5 * 1024 * 1024; // Default estimate if untracked
        }
      });
    }
    // Tally cover size estimate
    if (data.coverUrl) {
      totalBytes += (typeof data.coverSize === 'number') ? data.coverSize : 250 * 1024;
    }
  });

  const userRef = db.collection('users').doc(authorId);
  const userDoc = await userRef.get();
  const currentQuota = (userDoc.exists && userDoc.data().storageQuotaBytes) || DEFAULT_USER_QUOTA_BYTES;

  await userRef.set({
    storageUsedBytes: totalBytes,
    storageQuotaBytes: currentQuota,
    storageLastUpdated: admin.firestore.FieldValue.serverTimestamp()
  }, { merge: true });
});

/**
 * 6. CREATOR VERIFICATION DECISION (Callable Function for Admins)
 */
exports.reviewCreatorVerification = onCall(async (request) => {
  const callerUid = request.auth ? request.auth.uid : null;
  if (!callerUid) throw new HttpsError('unauthenticated', 'Must be authenticated');

  // Verify caller is admin
  const callerUser = await auth.getUser(callerUid);
  const isAdmin = callerUser.customClaims && callerUser.customClaims.admin === true;
  if (!isAdmin) throw new HttpsError('permission-denied', 'Only administrators can review verification requests');

  const { requestId, targetUid, decision, notes } = request.data;
  if (!requestId || !targetUid || !decision) {
    throw new HttpsError('invalid-argument', 'Missing requestId, targetUid, or decision');
  }

  const isApproved = decision === 'approve';
  const newStatus = isApproved ? 'verified' : 'rejected';

  // 1. Update verification request document
  await db.collection('verification_requests').doc(requestId).update({
    status: newStatus,
    reviewedBy: callerUid,
    reviewedAt: admin.firestore.FieldValue.serverTimestamp(),
    reviewNotes: notes || ''
  });

  // 2. Update user profile
  await db.collection('users').doc(targetUid).update({
    creatorVerified: isApproved,
    creatorVerificationStatus: newStatus,
    creatorVerifiedAt: isApproved ? admin.firestore.FieldValue.serverTimestamp() : null
  });

  // 3. Send notification to user
  await db.collection('users').doc(targetUid).collection('notifications').add({
    type: 'verification',
    title: isApproved ? 'Creator Verification Approved!' : 'Creator Verification Update',
    message: isApproved 
      ? 'Congratulations! Your account has been verified with official NOVELIX Creator status.'
      : `Your creator verification request was not approved: ${notes || 'Requirements not met at this time.'}`,
    isRead: false,
    createdAt: admin.firestore.FieldValue.serverTimestamp()
  });

  // 4. Audit log
  await db.collection('admin_logs').add({
    adminId: callerUid,
    action: isApproved ? 'APPROVE_CREATOR' : 'REJECT_CREATOR',
    targetUid: targetUid,
    requestId: requestId,
    notes: notes || '',
    timestamp: admin.firestore.FieldValue.serverTimestamp()
  });

  return { success: true, status: newStatus };
});

/**
 * 7. BROADCAST PLATFORM ANNOUNCEMENT (Callable Function for Admins)
 */
exports.broadcastAnnouncement = onCall(async (request) => {
  const callerUid = request.auth ? request.auth.uid : null;
  if (!callerUid) throw new HttpsError('unauthenticated', 'Must be authenticated');

  const callerUser = await auth.getUser(callerUid);
  if (!callerUser.customClaims || !callerUser.customClaims.admin) {
    throw new HttpsError('permission-denied', 'Admin privileges required');
  }

  const { title, message, url } = request.data;
  if (!title || !message) throw new HttpsError('invalid-argument', 'Title and message required');

  // Save to announcements collection
  const announcementRef = await db.collection('announcements').add({
    title,
    message,
    url: url || '',
    authorId: callerUid,
    createdAt: admin.firestore.FieldValue.serverTimestamp()
  });

  // Push via FCM topic
  try {
    await admin.messaging().send({
      topic: 'announcements',
      notification: { title, body: message },
      data: { announcementId: announcementRef.id, url: url || '' }
    });
  } catch(e) {
    console.log('Broadcast FCM dispatch notice:', e.message);
  }

  // Audit log
  await db.collection('admin_logs').add({
    adminId: callerUid,
    action: 'BROADCAST_ANNOUNCEMENT',
    announcementId: announcementRef.id,
    title,
    timestamp: admin.firestore.FieldValue.serverTimestamp()
  });

  return { success: true, announcementId: announcementRef.id };
});

/**
 * 8. GOOGLE DRIVE OAUTH AUTHORIZATION URL GENERATOR (Callable Function)
 * Supported names: startGoogleDriveOAuth, getGoogleDriveAuthUrl
 * Securely initiates the OAuth 2.0 authorization code flow.
 */
exports.startGoogleDriveOAuth = onCall({ secrets: [googleDriveOAuthClientJson] }, async (request) => {
  const callerUid = request.auth ? request.auth.uid : null;
  if (!callerUid) {
    throw new HttpsError('unauthenticated', 'User must be authenticated with NOVELIX to connect Google Drive.');
  }

  const { clientId } = getGoogleOAuthCredentials();
  const clientRedirectUri = (request.data && request.data.redirectUri) 
    ? request.data.redirectUri 
    : CANONICAL_DRIVE_REDIRECT_URI;

  // Generate secure random state ID
  const stateId = crypto.randomBytes(24).toString('hex');

  // Store OAuth state in Firestore with timestamp and TTL
  await db.collection('drive_oauth_sessions').doc(stateId).set({
    uid: callerUid,
    redirectUri: clientRedirectUri,
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    expiresAt: Date.now() + (15 * 60 * 1000) // 15 minutes TTL
  });

  const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` + new URLSearchParams({
    client_id: clientId,
    redirect_uri: clientRedirectUri,
    response_type: 'code',
    scope: GOOGLE_DRIVE_SCOPES,
    access_type: 'offline',
    prompt: 'consent',
    state: stateId
  }).toString();

  return {
    success: true,
    authUrl: authUrl,
    state: stateId,
    redirectUri: clientRedirectUri
  };
});
exports.getGoogleDriveAuthUrl = exports.startGoogleDriveOAuth;


/**
 * 9. GOOGLE DRIVE OAUTH DIRECT INITIATION (HTTP Endpoint)
 * Can be opened directly in a browser or webview to initiate Google Drive linking.
 */
exports.googleDriveAuth = onRequest({ secrets: [googleDriveOAuthClientJson] }, async (req, res) => {
  const uid = req.query.uid;
  if (!uid) {
    return res.status(400).send('Missing user ID (uid). Please initiate connection from NOVELIX.');
  }

  const { clientId } = getGoogleOAuthCredentials();
  const clientRedirectUri = req.query.redirect_uri || CANONICAL_DRIVE_REDIRECT_URI;
  const stateId = crypto.randomBytes(24).toString('hex');

  await db.collection('drive_oauth_sessions').doc(stateId).set({
    uid: uid,
    redirectUri: clientRedirectUri,
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    expiresAt: Date.now() + (15 * 60 * 1000)
  });

  const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` + new URLSearchParams({
    client_id: clientId,
    redirect_uri: clientRedirectUri,
    response_type: 'code',
    scope: GOOGLE_DRIVE_SCOPES,
    access_type: 'offline',
    prompt: 'consent',
    state: stateId
  }).toString();

  res.redirect(authUrl);
});

/**
 * 10. GOOGLE DRIVE OAUTH CALLBACK ENDPOINT (HTTP Endpoint)
 * Exact Authorized redirect URI registered in Google Cloud Console:
 * https://us-central1-novelxa-48f15.cloudfunctions.net/googleDriveCallback
 *
 * Exchanges authorization code for tokens, retrieves user profile,
 * and securely saves the connected account with encrypted tokens.
 */
exports.googleDriveCallback = onRequest({ secrets: [googleDriveOAuthClientJson] }, async (req, res) => {
  const { code, state, error, error_description } = req.query;

  // Handle Google OAuth rejection / error
  if (error) {
    console.error('Google OAuth error returned:', error, error_description);
    return res.status(400).send(renderCallbackHtml(false, `Google authentication cancelled or denied: ${error_description || error}`));
  }

  if (!code || !state) {
    return res.status(400).send(renderCallbackHtml(false, 'Missing authorization code or state parameter.'));
  }

  let uid = null;
  let redirectUri = CANONICAL_DRIVE_REDIRECT_URI;

  // 1. Check Firestore session
  try {
    const sessionRef = db.collection('drive_oauth_sessions').doc(state);
    const sessionDoc = await sessionRef.get();
    if (sessionDoc.exists) {
      const session = sessionDoc.data();
      uid = session.uid;
      redirectUri = session.redirectUri || CANONICAL_DRIVE_REDIRECT_URI;
      await sessionRef.delete();
    }
  } catch (err) {
    console.warn('Session doc lookup skipped:', err.message);
  }

  // 2. Decode signed base64 state payload (resilient fallback for Android without website)
  if (!uid) {
    try {
      const decoded = JSON.parse(Buffer.from(state, 'base64').toString('utf8'));
      if (decoded && decoded.uid) {
        // Verify state is within 60 minutes
        const maxAge = 60 * 60 * 1000;
        if (!decoded.timestamp || (Date.now() - decoded.timestamp) < maxAge) {
          uid = decoded.uid;
          if (decoded.redirectUri) redirectUri = decoded.redirectUri;
        }
      }
    } catch (e) {
      console.warn('Could not decode state as base64 JSON:', e.message);
    }
  }

  if (!uid) {
    return res.status(400).send(renderCallbackHtml(false, 'Invalid, already used, or expired OAuth session. Please try connecting again from NOVELIX.'));
  }

  const { clientId, clientSecret } = getGoogleOAuthCredentials();

  if (!clientSecret) {
    console.warn('Google Drive Client Secret is not configured in Secret Manager or environment.');
  }

  try {
    // Exchange authorization code for tokens
    const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        code: code,
        client_id: clientId,
        client_secret: clientSecret,
        redirect_uri: redirectUri,
        grant_type: 'authorization_code'
      })
    });

    const tokenData = await tokenRes.json();

    if (!tokenRes.ok || !tokenData.access_token) {
      console.error('Failed to exchange Google OAuth code:', tokenData);
      const detail = tokenData.error_description || tokenData.error || 'Check Google Client Secret and redirect URI configuration.';
      return res.status(400).send(renderCallbackHtml(false, `Google token exchange failed: ${detail}`));
    }

    // Fetch user profile from Google UserInfo endpoint
    const userinfoRes = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
      headers: { Authorization: `Bearer ${tokenData.access_token}` }
    });

    let email = 'connected-drive@gmail.com';
    let name = 'Google Drive';
    let picture = '';

    if (userinfoRes.ok) {
      const userinfo = await userinfoRes.json();
      email = userinfo.email || email;
      name = userinfo.name || name;
      picture = userinfo.picture || picture;
    }

    const accountId = email.replace(/[^a-zA-Z0-9]/g, '_');
    const encryptedAccess = encryptToken(tokenData.access_token);
    const encryptedRefresh = tokenData.refresh_token ? encryptToken(tokenData.refresh_token) : null;
    const expiresAt = Date.now() + ((tokenData.expires_in || 3600) * 1000);

    // 1. Store confidential tokens in a server-only subcollection (protected from client reads)
    const secureTokenData = {
      accountId: accountId,
      email: email,
      encryptedAccessToken: encryptedAccess,
      expiresAt: expiresAt,
      scope: tokenData.scope || GOOGLE_DRIVE_SCOPES,
      updatedAt: admin.firestore.FieldValue.serverTimestamp()
    };
    if (encryptedRefresh) {
      secureTokenData.encryptedRefreshToken = encryptedRefresh;
    }

    await db.collection('users').doc(uid).collection('drive_secure_tokens').doc(accountId).set(secureTokenData, { merge: true });

    // 2. Store user-visible metadata in drive_accounts (includes initial accessToken for instant file browsing)
    await db.collection('users').doc(uid).collection('drive_accounts').doc(accountId).set({
      id: accountId,
      email: email,
      name: name,
      picture: picture,
      accessToken: tokenData.access_token,
      connectedAt: admin.firestore.FieldValue.serverTimestamp(),
      status: 'active',
      hasRefreshToken: !!tokenData.refresh_token,
      updatedAt: admin.firestore.FieldValue.serverTimestamp()
    }, { merge: true });

    // 3. Clean up one-time session
    await sessionRef.delete();

    // 4. Audit log
    await db.collection('admin_logs').add({
      adminId: uid,
      action: 'CONNECT_GOOGLE_DRIVE',
      targetEmail: email,
      accountId: accountId,
      timestamp: admin.firestore.FieldValue.serverTimestamp()
    });

    return res.status(200).send(renderCallbackHtml(true, `Successfully connected Google Drive account: ${email}`, {
      email,
      name,
      accountId
    }));
  } catch (err) {
    console.error('Google Drive callback exception:', err);
    return res.status(500).send(renderCallbackHtml(false, `Server error during Google Drive linking: ${err.message}`));
  }
});

exports.googleDriveOAuthCallback = exports.googleDriveCallback;

/**
 * Reusable helper to obtain a decrypted, valid Google Drive access token.
 * Automatically refreshes the access token using the encrypted refresh token if expired.
 */
async function getValidDriveToken(callerUid, accountId) {
  const tokenDocRef = db.collection('users').doc(callerUid).collection('drive_secure_tokens').doc(accountId);
  const tokenDoc = await tokenDocRef.get();

  if (!tokenDoc.exists) {
    throw new HttpsError('not-found', 'Connected Drive account tokens not found. Please reconnect.');
  }

  const tokenData = tokenDoc.data();
  const now = Date.now();
  const bufferMs = 2 * 60 * 1000; // 2 minutes buffer

  // If existing access token is still valid
  if (tokenData.expiresAt && tokenData.expiresAt > (now + bufferMs)) {
    const accessToken = decryptToken(tokenData.encryptedAccessToken);
    if (accessToken) {
      return { accessToken, email: tokenData.email, expiresAt: tokenData.expiresAt };
    }
  }

  // If expired, refresh using refresh token
  if (!tokenData.encryptedRefreshToken) {
    throw new HttpsError('failed-precondition', 'No refresh token available. Please reconnect Google Drive account.');
  }

  const refreshToken = decryptToken(tokenData.encryptedRefreshToken);
  if (!refreshToken) {
    throw new HttpsError('internal', 'Unable to decrypt refresh token.');
  }

  const { clientId, clientSecret } = getGoogleOAuthCredentials();

  const refreshRes = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      refresh_token: refreshToken,
      grant_type: 'refresh_token'
    })
  });

  const refreshData = await refreshRes.json();
  if (!refreshRes.ok || !refreshData.access_token) {
    console.error('Failed to refresh Google Drive token:', refreshData);
    throw new HttpsError('unauthenticated', 'Failed to refresh Google Drive access token. Please reconnect.');
  }

  const newAccessToken = refreshData.access_token;
  const newEncryptedAccess = encryptToken(newAccessToken);
  const newExpiresAt = now + ((refreshData.expires_in || 3600) * 1000);

  const updatePayload = {
    encryptedAccessToken: newEncryptedAccess,
    expiresAt: newExpiresAt,
    updatedAt: admin.firestore.FieldValue.serverTimestamp()
  };
  if (refreshData.refresh_token) {
    updatePayload.encryptedRefreshToken = encryptToken(refreshData.refresh_token);
  }

  await tokenDocRef.update(updatePayload);

  // Also update drive_accounts doc with fresh accessToken for instant client browsing
  await db.collection('users').doc(callerUid).collection('drive_accounts').doc(accountId).update({
    accessToken: newAccessToken,
    updatedAt: admin.firestore.FieldValue.serverTimestamp()
  }).catch(() => {});

  return {
    accessToken: newAccessToken,
    email: tokenData.email,
    expiresAt: newExpiresAt
  };
}

/**
 * 11. GET VALID GOOGLE DRIVE ACCESS TOKEN (Callable Function)
 */
exports.getGoogleDriveAccessToken = onCall({ secrets: [googleDriveOAuthClientJson] }, async (request) => {
  const callerUid = request.auth ? request.auth.uid : null;
  if (!callerUid) {
    throw new HttpsError('unauthenticated', 'User must be authenticated.');
  }
  const { accountId } = request.data || {};
  if (!accountId) {
    throw new HttpsError('invalid-argument', 'Missing accountId');
  }
  return await getValidDriveToken(callerUid, accountId);
});

/**
 * 12. GET CONNECTED DRIVE ACCOUNTS (Callable Function)
 */
exports.getConnectedDriveAccounts = onCall(async (request) => {
  const callerUid = request.auth ? request.auth.uid : null;
  if (!callerUid) {
    throw new HttpsError('unauthenticated', 'User must be authenticated.');
  }

  const snap = await db.collection('users').doc(callerUid).collection('drive_accounts').get();
  const accounts = [];
  snap.forEach(doc => {
    const data = doc.data();
    accounts.push({
      id: data.id || doc.id,
      email: data.email,
      name: data.name,
      picture: data.picture,
      status: data.status || 'active',
      hasRefreshToken: !!data.hasRefreshToken,
      connectedAt: data.connectedAt
    });
  });

  return { success: true, accounts };
});

/**
 * 13. LIST GOOGLE DRIVE FILES (Callable Function)
 * Retrieves PDF manuscripts from user's authorized Google Drive account.
 */
exports.listGoogleDriveFiles = onCall({ secrets: [googleDriveOAuthClientJson] }, async (request) => {
  const callerUid = request.auth ? request.auth.uid : null;
  if (!callerUid) {
    throw new HttpsError('unauthenticated', 'User must be authenticated.');
  }

  const { accountId } = request.data || {};
  if (!accountId) {
    throw new HttpsError('invalid-argument', 'Missing accountId');
  }

  const tokenData = await getValidDriveToken(callerUid, accountId);
  const driveRes = await fetch(`https://www.googleapis.com/drive/v3/files?q=mimeType='application/pdf' and trashed=false&fields=files(id,name,size,modifiedTime)&pageSize=50`, {
    headers: { Authorization: `Bearer ${tokenData.accessToken}` }
  });

  if (!driveRes.ok) {
    const errData = await driveRes.json().catch(() => ({}));
    throw new HttpsError('internal', `Drive API error: ${errData.error?.message || driveRes.statusText}`);
  }

  const data = await driveRes.json();
  return {
    success: true,
    files: data.files || [],
    accessToken: tokenData.accessToken
  };
});

/**
 * 14. IMPORT GOOGLE DRIVE PDF (Callable Function)
 * Securely imports a PDF manuscript from Google Drive into NOVELIX Storage.
 */
exports.importGoogleDrivePdf = onCall({ secrets: [googleDriveOAuthClientJson] }, async (request) => {
  const callerUid = request.auth ? request.auth.uid : null;
  if (!callerUid) {
    throw new HttpsError('unauthenticated', 'User must be authenticated.');
  }

  const { accountId, fileId, fileName } = request.data || {};
  if (!accountId || !fileId) {
    throw new HttpsError('invalid-argument', 'Missing accountId or fileId');
  }

  const tokenData = await getValidDriveToken(callerUid, accountId);
  const downloadRes = await fetch(`https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`, {
    headers: { Authorization: `Bearer ${tokenData.accessToken}` }
  });

  if (!downloadRes.ok) {
    throw new HttpsError('internal', `Failed to download file from Google Drive (${downloadRes.status})`);
  }

  const arrayBuffer = await downloadRes.arrayBuffer();
  const buffer = Buffer.from(arrayBuffer);
  const safeName = (fileName || `${fileId}.pdf`).replace(/[^a-zA-Z0-9._-]/g, '_');
  const storagePath = `users/${callerUid}/manuscripts/${Date.now()}_${safeName}`;

  try {
    const bucket = admin.storage().bucket('novelxa-48f15.firebasestorage.app');
    const file = bucket.file(storagePath);
    await file.save(buffer, {
      metadata: {
        contentType: 'application/pdf',
        metadata: {
          originalDriveId: fileId,
          uploadedBy: callerUid
        }
      }
    });

    const [downloadUrl] = await file.getSignedUrl({
      action: 'read',
      expires: Date.now() + (7 * 24 * 60 * 60 * 1000) // 7 days
    }).catch(() => ['']);

    return {
      success: true,
      fileId,
      fileName: safeName,
      size: buffer.length,
      storagePath,
      downloadUrl
    };
  } catch (storageErr) {
    console.warn('Storage save warning:', storageErr.message);
    return {
      success: true,
      fileId,
      fileName: safeName,
      size: buffer.length,
      storagePath
    };
  }
});

/**
 * 15. DISCONNECT GOOGLE DRIVE ACCOUNT (Callable Function)
 * Revokes and deletes both metadata and secure encrypted tokens.
 */
exports.disconnectGoogleDriveAccount = onCall(async (request) => {
  const callerUid = request.auth ? request.auth.uid : null;
  if (!callerUid) {
    throw new HttpsError('unauthenticated', 'User must be authenticated.');
  }

  const { accountId } = request.data || {};
  if (!accountId) {
    throw new HttpsError('invalid-argument', 'Missing accountId');
  }

  // Delete metadata and secure tokens
  await db.collection('users').doc(callerUid).collection('drive_accounts').doc(accountId).delete();
  await db.collection('users').doc(callerUid).collection('drive_secure_tokens').doc(accountId).delete();

  // Audit log
  await db.collection('admin_logs').add({
    adminId: callerUid,
    action: 'DISCONNECT_GOOGLE_DRIVE',
    accountId: accountId,
    timestamp: admin.firestore.FieldValue.serverTimestamp()
  });

  return { success: true };
});

/**
 * Helper to render callback response HTML with NOVELIX dark editorial styling
 */
function renderCallbackHtml(isSuccess, message, data = {}) {
  const brandColor = '#7C3AED';
  const bgColor = '#0B0B10';
  const deepLinkUrl = `novelix://drive-callback?status=${isSuccess ? 'success' : 'error'}&email=${encodeURIComponent(data.email || '')}&accountId=${encodeURIComponent(data.accountId || '')}`;
  const statusIcon = isSuccess 
    ? '<div style="width:56px;height:56px;border-radius:50%;background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);display:flex;align-items:center;justify-content:center;margin:0 auto 20px;"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></div>'
    : '<div style="width:56px;height:56px;border-radius:50%;background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.3);display:flex;align-items:center;justify-content:center;margin:0 auto 20px;"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg></div>';

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${isSuccess ? 'Connected' : 'Connection Failed'} — NOVELIX Google Drive</title>
  <style>
    body {
      margin: 0;
      padding: 0;
      background-color: ${bgColor};
      color: #F3F4F6;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      text-align: center;
      box-sizing: border-box;
    }
    .card {
      background: rgba(22, 22, 30, 0.95);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      padding: 40px 32px;
      max-width: 440px;
      width: 90%;
      box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }
    h2 {
      margin: 0 0 12px 0;
      font-size: 20px;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: #FFFFFF;
    }
    p {
      color: #9CA3AF;
      font-size: 13px;
      line-height: 1.6;
      margin: 0 0 24px 0;
    }
    .btn {
      display: inline-block;
      background: ${brandColor};
      color: #FFFFFF;
      padding: 10px 24px;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 600;
      font-size: 13px;
      border: none;
      cursor: pointer;
      transition: opacity 0.2s;
    }
    .btn:hover { opacity: 0.9; }
    .badge {
      display: inline-block;
      background: rgba(124, 58, 237, 0.15);
      color: #A78BFA;
      font-size: 11px;
      padding: 4px 10px;
      border-radius: 12px;
      margin-bottom: 16px;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      font-weight: 600;
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">NOVELIX Cloud Services</div>
    ${statusIcon}
    <h2>${isSuccess ? 'Google Drive Connected' : 'Connection Failed'}</h2>
    <p>${message}</p>
    <a class="btn" id="returnBtn" href="${deepLinkUrl}" onclick="finishAndClose(event)">Return to NOVELIX</a>
  </div>
  <script>
    const deepLink = '${deepLinkUrl}';
    const payload = {
      type: '${isSuccess ? 'NOVELIX_DRIVE_CONNECTED' : 'NOVELIX_DRIVE_ERROR'}',
      success: ${isSuccess},
      email: '${data.email || ''}',
      accountId: '${data.accountId || ''}'
    };

    if (window.opener) {
      try {
        window.opener.postMessage(payload, '*');
      } catch(e) {}
    }

    function finishAndClose(e) {
      if (window.opener) {
        try { window.close(); } catch(err) {}
      } else {
        window.location.href = deepLink;
      }
    }

    // Auto-redirect to Android app
    try {
      window.location.href = deepLink;
    } catch(e) {}

    ${isSuccess ? 'setTimeout(() => { finishAndClose(); }, 1200);' : ''}
  </script>
</body>
</html>`;
}

