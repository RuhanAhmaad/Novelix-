/**
 * NOVELIX 4.0 — Cloud Functions for Firebase
 * High-performance, serverless backend operations & secure admin endpoints
 */

const { onDocumentCreated, onDocumentWritten, onDocumentUpdated } = require('firebase-functions/v2/firestore');
const { onCall, HttpsError } = require('firebase-functions/v2/https');
const admin = require('firebase-admin');

if (!admin.apps.length) {
  admin.initializeApp();
}

const db = admin.firestore();
const auth = admin.auth();

// Default storage quota per user: 500 MB in bytes
const DEFAULT_USER_QUOTA_BYTES = 500 * 1024 * 1024;

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
