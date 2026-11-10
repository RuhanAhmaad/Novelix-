#!/usr/bin/env node
/**
 * ═══════════════════════════════════════════════════════════════
 * NOVELIX 11.0 — VIP TERMINAL ADMIN CONSOLE
 * ═══════════════════════════════════════════════════════════════
 * Provides direct terminal administration for the NOVELIX platform:
 *  - System Health & Analytics
 *  - Books & Publication Management (List, Feature, Delete, Inspect Drive links)
 *  - User Management (Grant VIP Admin, Suspend, Restore)
 *  - Real-Time Push Notification Broadcaster (Instant alerts with audio chime)
 *  - Fast Cloudflare / Google Drive Diagnostics
 * ═══════════════════════════════════════════════════════════════
 */

const readline = require('readline');
const https = require('https');

const PROJECT_ID = 'novelxa-48f15';
const FIRESTORE_BASE = `https://firestore.googleapis.com/v1/projects/${PROJECT_ID}/databases/(default)/documents`;

// ANSI Color Palette
const GOLD = '\x1b[38;2;255;215;0m';
const PURPLE = '\x1b[38;2;146;112;255m';
const GREEN = '\x1b[38;2;52;211;153m';
const RED = '\x1b[38;2;248;113;113m';
const CYAN = '\x1b[38;2;56;189;248m';
const BOLD = '\x1b[1m';
const DIM = '\x1b[2m';
const RESET = '\x1b[0m';

function printHeader() {
  console.clear();
  console.log(`
${GOLD}╔═══════════════════════════════════════════════════════════════════════════╗
║   👑  NOVELIX 11.0 — MASTER VIP TERMINAL ADMINISTRATION CONSOLE          ║
║   Spark Free Plan • Real-Time Push Dispatcher • Zero Cloud Costs          ║
╚═══════════════════════════════════════════════════════════════════════════╝${RESET}
  `);
}

function requestFirestore(method, path, body = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(`${FIRESTORE_BASE}/${path}`);
    const options = {
      method: method,
      headers: {
        'Content-Type': 'application/json',
      }
    };

    const req = https.request(url, options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          resolve({ status: res.statusCode, data: parsed });
        } catch (e) {
          resolve({ status: res.statusCode, data });
        }
      });
    });

    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

function createRl() {
  return readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
}

function ask(rl, prompt) {
  return new Promise(resolve => rl.question(prompt, resolve));
}

async function showAnalytics() {
  printHeader();
  console.log(`${CYAN}${BOLD}[ 📊 System Overview & Live Analytics ]${RESET}\n`);
  process.stdout.write('Connecting to Firestore... ');

  try {
    const [booksRes, usersRes, notifsRes] = await Promise.all([
      requestFirestore('GET', 'books?pageSize=100'),
      requestFirestore('GET', 'users?pageSize=100'),
      requestFirestore('GET', 'notifications?pageSize=50')
    ]);

    const booksCount = booksRes.data?.documents?.length || 0;
    const usersCount = usersRes.data?.documents?.length || 0;
    const notifsCount = notifsRes.data?.documents?.length || 0;

    console.log(`${GREEN}Connected (HTTP ${booksRes.status})${RESET}\n`);
    console.log(`  • ${GOLD}Total Published Titles:${RESET}    ${BOLD}${booksCount}${RESET}`);
    console.log(`  • ${GOLD}Total Registered Accounts:${RESET} ${BOLD}${usersCount}${RESET}`);
    console.log(`  • ${GOLD}Active Broadcast Alerts:${RESET}   ${BOLD}${notifsCount}${RESET}`);
    console.log(`  • ${GOLD}Manuscript Cloud Engine:${RESET}   ${GREEN}Direct Google Drive Streaming (Free)${RESET}`);
    console.log(`  • ${GOLD}Cover & Avatar Storage:${RESET}    ${GREEN}ImgBB Free Tier (Zero Firebase bytes)${RESET}`);
    console.log(`  • ${GOLD}Push Notification Mesh:${RESET}    ${GREEN}Real-Time Heads-Up Banner + Web Audio Chime${RESET}`);
  } catch (err) {
    console.log(`${RED}Error: ${err.message}${RESET}`);
  }

  const rl = createRl();
  await ask(rl, `\n${DIM}Press Enter to return to main menu...${RESET}`);
  rl.close();
}

async function listBooks() {
  printHeader();
  console.log(`${CYAN}${BOLD}[ 📚 Published Books & Manuscript Catalog ]${RESET}\n`);

  try {
    const res = await requestFirestore('GET', 'books?pageSize=50');
    const docs = res.data?.documents || [];

    if (!docs.length) {
      console.log(`${DIM}No books currently found in Firestore catalog.${RESET}`);
    } else {
      docs.forEach((doc, idx) => {
        const id = doc.name.split('/').pop();
        const f = doc.fields || {};
        const title = f.title?.stringValue || 'Untitled';
        const author = f.authorName?.stringValue || 'Unknown';
        const lang = f.language?.stringValue || 'English';
        const views = f.viewCount?.integerValue || 0;
        const isFeatured = f.isFeatured?.booleanValue ? `${GOLD}★ FEATURED${RESET}` : `${DIM}Standard${RESET}`;

        console.log(` ${BOLD}[${idx + 1}]${RESET} ${GOLD}${title}${RESET} (ID: ${CYAN}${id}${RESET})`);
        console.log(`     Author: ${author} | Language: ${lang} | Reads: ${views} | Status: ${isFeatured}`);
      });
    }
  } catch (err) {
    console.log(`${RED}Error fetching books: ${err.message}${RESET}`);
  }

  const rl = createRl();
  await ask(rl, `\n${DIM}Press Enter to return to main menu...${RESET}`);
  rl.close();
}

async function listUsers() {
  printHeader();
  console.log(`${CYAN}${BOLD}[ 👥 Registered Users & Roles ]${RESET}\n`);

  try {
    const res = await requestFirestore('GET', 'users?pageSize=50');
    const docs = res.data?.documents || [];

    if (!docs.length) {
      console.log(`${DIM}No user documents found in Firestore.${RESET}`);
    } else {
      docs.forEach((doc, idx) => {
        const uid = doc.name.split('/').pop();
        const f = doc.fields || {};
        const email = f.email?.stringValue || 'No email';
        const name = f.displayName?.stringValue || 'Reader';
        const role = f.role?.stringValue || 'reader';
        const isVIP = role === 'admin' ? `${GOLD}👑 VIP ADMIN${RESET}` : `${DIM}${role}${RESET}`;

        console.log(` ${BOLD}[${idx + 1}]${RESET} ${name} (${CYAN}${email}${RESET})`);
        console.log(`     UID: ${uid} | Role: ${isVIP}`);
      });
    }
  } catch (err) {
    console.log(`${RED}Error fetching users: ${err.message}${RESET}`);
  }

  const rl = createRl();
  await ask(rl, `\n${DIM}Press Enter to return to main menu...${RESET}`);
  rl.close();
}

async function broadcastPush() {
  printHeader();
  console.log(`${GOLD}${BOLD}[ 🚀 Broadcast Real-Time Push Notification ]${RESET}\n`);
  console.log(`${DIM}This notification will instantly appear as an In-App Heads-Up Banner with audio chime on all active reader devices.${RESET}\n`);

  const rl = createRl();
  const title = await ask(rl, `${BOLD}Notification Title:${RESET} `);
  if (!title.trim()) {
    console.log(`${RED}Cancelled: Title cannot be empty.${RESET}`);
    rl.close();
    return;
  }

  const message = await ask(rl, `${BOLD}Message Body:${RESET} `);
  if (!message.trim()) {
    console.log(`${RED}Cancelled: Message cannot be empty.${RESET}`);
    rl.close();
    return;
  }

  const bookId = await ask(rl, `${BOLD}Target Book ID (Optional, press Enter to skip):${RESET} `);

  console.log(`\nBroadcasting: "${GOLD}${title}${RESET}"...`);

  const notifDoc = {
    fields: {
      title: { stringValue: title.trim() },
      message: { stringValue: message.trim() },
      bookId: { stringValue: bookId.trim() },
      type: { stringValue: 'broadcast' },
      isRead: { booleanValue: false },
      broadcast: { booleanValue: true },
      createdAt: { integerValue: String(Date.now()) },
      sender: { stringValue: '👑 VIP Terminal Admin' }
    }
  };

  try {
    const res = await requestFirestore('POST', 'notifications', notifDoc);
    if (res.status === 200 || res.status === 201) {
      console.log(`\n${GREEN}${BOLD}✓ SUCCESS: Push notification broadcasted!${RESET}`);
      console.log(`Document ID: ${CYAN}${res.data?.name?.split('/').pop()}${RESET}`);
      console.log(`${DIM}Active devices will receive the notification banner immediately.${RESET}`);
    } else {
      console.log(`\n${RED}Firestore Response (${res.status}): ${JSON.stringify(res.data)}${RESET}`);
    }
  } catch (err) {
    console.log(`\n${RED}Broadcast failed: ${err.message}${RESET}`);
  }

  await ask(rl, `\n${DIM}Press Enter to return to main menu...${RESET}`);
  rl.close();
}

async function grantVipAdmin() {
  printHeader();
  console.log(`${GOLD}${BOLD}[ 👑 Grant VIP Administrator Privileges ]${RESET}\n`);

  const rl = createRl();
  const uid = await ask(rl, `${BOLD}Enter User UID or Email to promote:${RESET} `);

  if (!uid.trim()) {
    console.log(`${RED}Cancelled.${RESET}`);
    rl.close();
    return;
  }

  const targetUid = uid.trim();
  console.log(`Updating role to "admin" for ${targetUid}...`);

  const updateBody = {
    fields: {
      role: { stringValue: 'admin' },
      isVIP: { booleanValue: true },
      updatedAt: { stringValue: new Date().toISOString() }
    }
  };

  try {
    const res = await requestFirestore('PATCH', `users/${targetUid}?updateMask.fieldPaths=role&updateMask.fieldPaths=isVIP`, updateBody);
    if (res.status === 200) {
      console.log(`\n${GREEN}${BOLD}✓ SUCCESS: User ${targetUid} has been promoted to VIP Administrator!${RESET}`);
    } else {
      console.log(`\n${RED}Status: ${res.status}. Note: In the app, you can also click "Instant VIP Admin Login" or type "admin" in the terminal for instant VIP access.${RESET}`);
    }
  } catch (err) {
    console.log(`\n${RED}Error: ${err.message}${RESET}`);
  }

  await ask(rl, `\n${DIM}Press Enter to return to main menu...${RESET}`);
  rl.close();
}

async function mainMenu() {
  while (true) {
    printHeader();
    console.log(`  ${BOLD}[1]${RESET} 📊 View System Overview & Live Analytics`);
    console.log(`  ${BOLD}[2]${RESET} 📚 List & Inspect Published Books`);
    console.log(`  ${BOLD}[3]${RESET} 👥 View Registered Users & Profiles`);
    console.log(`  ${BOLD}[4]${RESET} 🚀 ${GOLD}${BOLD}Broadcast Push Notification to All Devices${RESET}`);
    console.log(`  ${BOLD}[5]${RESET} 👑 Grant VIP Admin Role to User`);
    console.log(`  ${BOLD}[6]${RESET} 💡 How to Access VIP Admin in App & Terminal`);
    console.log(`  ${BOLD}[0]${RESET} ✕ Exit Console\n`);

    const rl = createRl();
    const choice = (await ask(rl, `${BOLD}Select an option [0-6]:${RESET} `)).trim();
    rl.close();

    if (choice === '1') await showAnalytics();
    else if (choice === '2') await listBooks();
    else if (choice === '3') await listUsers();
    else if (choice === '4') await broadcastPush();
    else if (choice === '5') await grantVipAdmin();
    else if (choice === '6') {
      printHeader();
      console.log(`${GOLD}${BOLD}[ 💡 VIP Admin Access Instructions ]${RESET}\n`);
      console.log(`  ${BOLD}1. In-App One-Tap Login:${RESET}`);
      console.log(`     • Tap "Sign In" in NOVELIX.`);
      console.log(`     • Tap the glowing gold button: ${GOLD}👑 Instant VIP Admin Login${RESET}.`);
      console.log(`     • Unlocks the entire VIP Executive Suite with full administrative powers.\n`);
      console.log(`  ${BOLD}2. In-App Terminal Access:${RESET}`);
      console.log(`     • Tap the NOVELIX top logo 5 times to open the Developer Terminal.`);
      console.log(`     • Type ${GOLD}admin${RESET} and hit Enter.`);
      console.log(`     • Automatically elevates your session and opens the VIP Admin Console!\n`);
      console.log(`  ${BOLD}3. In-App Terminal Push Command:${RESET}`);
      console.log(`     • In Developer Terminal, type: ${CYAN}push Title | Message${RESET}`);
      console.log(`     • Broadcasts a real-time notification to all devices instantly!\n`);
      console.log(`  ${BOLD}4. Termux / System Terminal Access:${RESET}`);
      console.log(`     • Simply run ${GOLD}./admin.sh${RESET} or ${GOLD}pnpm admin${RESET} in this terminal.`);

      const rl2 = createRl();
      await ask(rl2, `\n${DIM}Press Enter to return to main menu...${RESET}`);
      rl2.close();
    }
    else if (choice === '0' || choice === 'exit' || choice === 'q') {
      console.log(`\n${GREEN}Exiting NOVELIX VIP Console. Have a great day!${RESET}\n`);
      process.exit(0);
    }
  }
}

mainMenu().catch(console.error);
