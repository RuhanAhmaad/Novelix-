#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "  NOVELIX — Android APK Build & Sync Tool"
echo "=========================================================="

echo "[1/3] Building Web Platform..."
pnpm build

echo "[2/3] Synchronizing Web Assets with Native Android Shell..."
pnpm cap sync android

echo "[3/3] Android Project Synchronized!"
echo ""
echo "Native Android project location: ./android"
echo ""
echo "Choose how you would like to generate the final .apk file:"
echo ""
echo "METHOD A: GitHub Actions (Recommended - Cloud Build)"
echo "  1. Push code to your GitHub repository:"
echo "     git add ."
echo "     git commit -m 'Configure Android APK build'"
echo "     git push origin main"
echo "  2. Go to your repo -> 'Actions' tab -> 'Build NOVELIX Android APK'"
echo "  3. Click 'Run workflow'. In ~3 minutes, download your APK from the Artifacts section!"
echo ""
echo "METHOD B: Android Studio"
echo "  Run: pnpm cap open android"
echo "  Then click: Build -> Build Bundle(s) / APK(s) -> Build APK(s)"
echo ""
echo "METHOD C: Local Gradle (if Java 17 and Android SDK are installed)"
echo "  cd android && ./gradlew assembleDebug"
echo "  APK Output: ./android/app/build/outputs/apk/debug/app-debug.apk"
echo "=========================================================="
