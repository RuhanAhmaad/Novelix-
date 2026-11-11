#!/usr/bin/env python3
"""
Patch for NOVELIX 12.0:
1. Fix missing closing </div> on #driveConnectModal (Root cause of blank screen!)
2. Fix Firestore compound query requiring missing composite index
"""

GEN_FILE = "scripts/generate_4.py"

with open(GEN_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# ── 1. Fix the unclosed driveConnectModal ──
old_drive_modal_end = """        <span>Connect via Google Auth</span>
      </button>
    </div>
  </div>
</div>


<!-- Immediate Early Startup Guard: Prevents accidental modal flashing before scripts load -->"""

new_drive_modal_end = """        <span>Connect via Google Auth</span>
      </button>
    </div>
  </div>
  </div>
</div>


<!-- Immediate Early Startup Guard: Prevents accidental modal flashing before scripts load -->"""

if old_drive_modal_end in content:
    content = content.replace(old_drive_modal_end, new_drive_modal_end, 1)
    print("✓ Added missing </div> to close #driveConnectModal")
else:
    print("WARNING: old_drive_modal_end not found")

# ── 2. Fix Firestore real-time query to avoid requiring composite index ──
old_feed_query = """  // High Concurrency: Limit real-time snapshot to initial 15 works to conserve read quotas
  APP_STATE.realtimeBooksUnsub = db.collection('books')
    .where('visibility', '==', 'public')
    .where('publishStatus', '==', 'published')
    .orderBy('createdAt', 'desc')
    .limit(15)
    .onSnapshot((snapshot) => {
      document.getElementById('headerLivePill')?.classList.remove('hidden');
      const books = [];
      snapshot.forEach(doc => books.push({ id: doc.id, ...doc.data() }));
      APP_STATE.allBooks = books;
      if (snapshot.docs.length > 0) {
        APP_STATE.lastBookDoc = snapshot.docs[snapshot.docs.length - 1];
      }
      renderHomeShelfViews();
      if (APP_STATE.activePage === 'explore') renderExploreGridView();
      recalculateStorageQuota();
    }, (err) => {
      console.warn('Realtime feed notice:', err.message);
      loadBooksFallbackFeed();
    });"""

new_feed_query = """  // Zero-Index High Concurrency Real-Time Query: works without manual composite indexes
  APP_STATE.realtimeBooksUnsub = db.collection('books')
    .where('visibility', '==', 'public')
    .limit(30)
    .onSnapshot((snapshot) => {
      document.getElementById('headerLivePill')?.classList.remove('hidden');
      const books = [];
      snapshot.forEach(doc => {
        const d = doc.data();
        if (d.publishStatus !== 'draft' && d.status !== 'draft') {
          books.push({ id: doc.id, ...d });
        }
      });
      // In-memory sort by newest first (no composite index needed)
      books.sort((a, b) => {
        const ta = a.createdAt?.toDate ? a.createdAt.toDate().getTime() : (a.createdAt || 0);
        const tb = b.createdAt?.toDate ? b.createdAt.toDate().getTime() : (b.createdAt || 0);
        return tb - ta;
      });
      APP_STATE.allBooks = books;
      if (snapshot.docs.length > 0) {
        APP_STATE.lastBookDoc = snapshot.docs[snapshot.docs.length - 1];
      }
      renderHomeShelfViews();
      if (APP_STATE.activePage === 'explore') renderExploreGridView();
      recalculateStorageQuota();
    }, (err) => {
      console.warn('Realtime feed notice:', err.message);
      loadBooksFallbackFeed();
    });"""

if old_feed_query in content:
    content = content.replace(old_feed_query, new_feed_query, 1)
    print("✓ Updated startFirestoreBooksFeed to zero-index query")
else:
    print("WARNING: old_feed_query not found")

# Update fallback query as well
old_fallback = """async function loadBooksFallbackFeed() {
  try {
    const snap = await db.collection('books').where('publishStatus', '==', 'published').limit(30).get();
    const books = [];
    snap.forEach(doc => books.push({ id: doc.id, ...doc.data() }));
    APP_STATE.allBooks = books;
    renderHomeShelfViews();
  } catch(e) {
    document.getElementById('homeEmptyState')?.classList.remove('hidden');
  }
}"""

new_fallback = """async function loadBooksFallbackFeed() {
  try {
    const snap = await db.collection('books').where('visibility', '==', 'public').limit(30).get();
    const books = [];
    snap.forEach(doc => {
      const d = doc.data();
      if (d.publishStatus !== 'draft' && d.status !== 'draft') {
        books.push({ id: doc.id, ...d });
      }
    });
    books.sort((a, b) => {
      const ta = a.createdAt?.toDate ? a.createdAt.toDate().getTime() : (a.createdAt || 0);
      const tb = b.createdAt?.toDate ? b.createdAt.toDate().getTime() : (b.createdAt || 0);
      return tb - ta;
    });
    APP_STATE.allBooks = books;
    renderHomeShelfViews();
  } catch(e) {
    document.getElementById('homeEmptyState')?.classList.remove('hidden');
  }
}"""

if old_fallback in content:
    content = content.replace(old_fallback, new_fallback, 1)
    print("✓ Updated loadBooksFallbackFeed to zero-index query")
else:
    print("WARNING: old_fallback not found")

with open(GEN_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print(f"generate_4.py written successfully ({len(content):,} chars)")
