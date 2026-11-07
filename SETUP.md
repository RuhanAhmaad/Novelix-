# 📱 NOVELIX — APK Build Guide

## How to Get Your APK in 3 Steps

---

## STEP 1 — Push to GitHub

Run these commands in your project folder:

```bash
git init
git add .
git commit -m "NOVELIX v1.0 — Full Platform + Android APK"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/novelix.git
git push -u origin main
```

> Replace `YOUR_USERNAME` with your GitHub username.
> Create the repo at **github.com/new** (name it `novelix`, set to Public or Private).

---

## STEP 2 — Add GitHub Secrets (for Vercel auto-deploy)

Go to your GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**

Add these secrets:

| Secret Name | Value |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | `https://gzwpfvhmjweeydiwdsga.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | `sb_publishable_APwu-OfPQmtnj-f-pwxfZw_OxiwM8A1` |
| `NEXT_PUBLIC_IMGBB_API_KEY` | *(migrated to Firebase Storage)* |
| `VERCEL_TOKEN` | *(see below)* |
| `VERCEL_ORG_ID` | *(see below)* |
| `VERCEL_PROJECT_ID` | *(see below)* |

### Getting Vercel Credentials

1. Go to [vercel.com](https://vercel.com) → Sign up/Login
2. Create a new project → Import your GitHub repo
3. Set environment variables (same as the table above)
4. Deploy once manually from the Vercel dashboard
5. Then get credentials:
   - **VERCEL_TOKEN**: [vercel.com/account/tokens](https://vercel.com/account/tokens) → Create Token
   - **VERCEL_ORG_ID**: `vercel env pull .env.vercel.local` or from Team Settings
   - **VERCEL_PROJECT_ID**: Found in your project's Settings → General

---

## STEP 3 — Download APK

After pushing to GitHub:

1. Go to your repo on GitHub
2. Click the **Actions** tab
3. Click **"🚀 Build NOVELIX Android APK"** workflow
4. Wait ~5-10 minutes for it to complete ✅
5. Scroll to **Artifacts** at the bottom
6. Download **NOVELIX-Debug-APK**
7. Transfer to your Android device
8. Install (enable Unknown Sources first in Settings → Security)

---

## Quick Build (No Vercel Setup)

If you just want an APK without deploying first, push to GitHub and the workflow will still build — but the APK will point to `https://novelix.vercel.app` as placeholder. You must deploy to Vercel separately.

---

## What the APK Does

The NOVELIX APK is a **native Android WebView wrapper** that loads your live deployed web app. This means:

- ✅ **ALL features work** — Supabase auth, Google OAuth, PDF reading, Drive sync
- ✅ **Looks and feels native** — splash screen, app icon, full screen
- ✅ **Deep links work** — `novelix://` URLs open the app
- ✅ **Always up to date** — push web updates without releasing new APK
- ✅ **Notifications** — POST_NOTIFICATIONS permission ready

---

## File Structure

```
android/
├── app/
│   ├── src/main/
│   │   ├── AndroidManifest.xml     ← permissions, deep links
│   │   └── res/xml/
│   │       ├── network_security_config.xml  ← HTTPS domains
│   │       └── file_paths.xml
│   ├── build.gradle                ← app build config
│   └── proguard-rules.pro          ← release optimization
├── build.gradle                    ← project build config
└── gradlew                         ← build tool

.github/workflows/
└── build-apk.yml                   ← GitHub Actions pipeline

capacitor.config.ts                 ← Capacitor + server URL
vercel.json                         ← Vercel deployment config
```

---

## Troubleshooting

### Build fails: `ANDROID_SDK_ROOT not found`
- The GitHub Actions workflow sets this up automatically via `android-actions/setup-android`

### App shows blank screen
- Check that your Vercel URL is live and accessible
- Look at the `capacitor.config.ts` — the `server.url` must be your deployed URL

### Google Login doesn't work in APK
- Add `com.novelix.app` as an OAuth authorized redirect URI in Supabase dashboard
- Add your Supabase URL's callback to Google Cloud Console OAuth settings

### APK installs but can't access internet
- Check `network_security_config.xml` — make sure your deployment domain is listed
