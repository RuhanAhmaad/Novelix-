/**
 * NOVELIX 2.2 — Cloud Functions for Firebase
 * High-performance, serverless backend operations
 */

const { onDocumentCreated, onDocumentWritten, onDocumentUpdated } = require('firebase-functions/v2/firestore');
const { onCall, HttpsError } = require('firebase-functions/v2/https');
const { beforeUserCreated } = require('firebase-functions/v2/identity');
const admin = require('firebase-admin');

if (!admin.apps.length) {
  admin.initializeApp();
}

const db = admin.firestore();
const auth = admin.auth();

/**
 * 1. SET ADMIN CLAIM (Callable Function)
 * Securely assign admin custom claim. Only verified admins or initial secret can call this.
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
 * 3. NEW CHAPTER NOTIFICATION TRIGGER
 * Send FCM push notification and in-app notifications to all followers when an author publishes a chapter.
 */
exports.onChapterPublished = onDocumentWritten('books/{bookId}/chapters/{chapterId}', async (event) => {
  const before = event.data.before ? event.data.before.data() : null;
  const after = event.data.after ? event.data.after.data() : null;

  // Only trigger on newly published chapter
  if (!after || !after.isPublished) return;
  if (before && before.isPublished) return;

  const bookId = event.params.bookId;
  const bookDoc = await db.collection('books').doc(bookId).get();
  if (!bookDoc.exists) return;

  const book = bookDoc.data();
  const authorId = book.authorId;
  const bookTitle = book.title || 'Untitled';
  const chapterNum = after.chapterNumber || after.chapterNum || 1;

  // Retrieve author followers
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

  // Send FCM Push notification to topic for this book/author
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
 * Notify author when a user follows them.
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
