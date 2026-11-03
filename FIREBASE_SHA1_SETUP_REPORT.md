# NOVELIX — Firebase SHA-1 & SHA-256 Certificate Fingerprint Report

**Generated Date:** 2026-11-03  
**Application Name:** NOVELIX  
**Package Name:** `com.novelix.app`  
**Firebase Project:** `novelxa-48f15`  
**Build System:** Capacitor 8.6 + Android Gradle Plugin 8.13 (Groovy DSL)  

---

## 1. Verified Certificate Fingerprints

The certificate fingerprints were extracted using the official Android/Java keystore toolchain (`keytool` / Gradle signing report):

### **Variant: `debug`**
- **Keystore File:** `android/app/debug.keystore`
- **Alias:** `androiddebugkey`
- **Owner / Issuer:** `CN=Android Debug, O=Android, C=US`
- **Validity:** Valid until **Sat Mar 21 2054** (10,000 days)
- **Signature Algorithm:** `SHA384withRSA`
- **Key Algorithm:** `2048-bit RSA`

| Metric | Complete Fingerprint Value |
|---|---|
| **SHA-1** | `8A:FA:EA:99:07:A6:1B:C4:04:F0:3A:B0:43:7F:9D:86:B4:74:7F:B3` |
| **SHA-256** | `7C:7C:92:17:8F:85:6E:CC:E8:6A:8E:F4:B0:BE:2D:8F:84:B2:82:FB:F9:1F:C1:25:D4:8A:14:47:9A:B7:91:78` |

### **Variant: `release`**
- **Status:** Currently configured in `android/app/build.gradle` to use `signingConfig signingConfigs.debug` for testing APK generation.
- **Release SHA-1:** `8A:FA:EA:99:07:A6:1B:C4:04:F0:3A:B0:43:7F:9D:86:B4:74:7F:B3`
- **Production Note:** When preparing for Google Play Store production release, create a dedicated production release key (`release.jks`) or opt-in to Google Play App Signing (which provides its own Google Play SHA-1).

---

## 2. Project Architecture & Gradle Configuration

- **Framework:** Capacitor Android (`@capacitor/android` v8.6.0) with Next.js web build output (`out/`).
- **Gradle Build Script:** Groovy DSL (`android/app/build.gradle`, `android/build.gradle`, `android/variables.gradle`).
- **Signing Configuration Status:**
  `android/app/build.gradle` explicitly binds `signingConfigs.debug` to `file('debug.keystore')`. This ensures identical fingerprints across local machines (Windows, macOS, Linux) and automated GitHub Actions CI builds.
- **Google Services Plugin:**
  Applied via `com.google.gms.google-services` plugin and `com.google.gms:google-services:4.4.4` dependency.
- **Firebase BoM:**
  Native Firebase BoM `33.9.0` included in `android/app/build.gradle`.

---

## 3. Step-by-Step Instructions: Adding the SHA-1 to Firebase Console

To enable Google Sign-In and Android App Verification with Firebase:

1. Open your browser and navigate to the [Firebase Console](https://console.firebase.google.com/).
2. Select your project: **`novelxa-48f15`**.
3. In the top-left sidebar, click the **Gear icon (⚙️)** next to *Project Overview* and select **Project settings**.
4. In the **General** tab, scroll down to the **Your apps** section.
5. Select the Android application **`com.novelix.app`** (App ID: `1:239783323113:android:72ab9f84efe4b4957f5778`).
6. Under **SHA certificate fingerprints**, click the **Add fingerprint** button.
7. Paste the **SHA-1** fingerprint:
   ```
   8A:FA:EA:99:07:A6:1B:C4:04:F0:3A:B0:43:7F:9D:86:B4:74:7F:B3
   ```
8. Click **Save**.
9. *(Recommended)* Click **Add fingerprint** again and also paste the **SHA-256** fingerprint:
   ```
   7C:7C:92:17:8F:85:6E:CC:E8:6A:8E:F4:B0:BE:2D:8F:84:B2:82:FB:F9:1F:C1:25:D4:8A:14:47:9A:B7:91:78
   ```
10. Click **Save**.

---

## 4. Google Services Configuration Update

After registering the fingerprint in Firebase:

1. In the same **Your apps** section in Firebase Console, click the **Download google-services.json** button.
2. Verify the contents:
   - `package_name` must be `com.novelix.app`.
   - `oauth_client` array will now contain a newly generated OAuth client linked to your SHA-1.
3. Place/replace the file in your project at:
   ```
   android/app/google-services.json
   ```

---

## 5. Google Authentication Verification Checklist

| Component | Status | Details |
|---|---|---|
| **Package Name** | ✅ Verified | `com.novelix.app` |
| **Android Keystore** | ✅ Created & Configured | `android/app/debug.keystore` |
| **SHA-1 Fingerprint** | ✅ Generated | `8A:FA:EA:99:07:A6:1B:C4:04:F0:3A:B0:43:7F:9D:86:B4:74:7F:B3` |
| **SHA-256 Fingerprint** | ✅ Generated | `7C:7C:92:17:8F:85:6E:CC:E8:6A:8E:F4:B0:BE:2D:8F:84:B2:82:FB:F9:1F:C1:25:D4:8A:14:47:9A:B7:91:78` |
| **Firebase Auth SDK** | ✅ Configured | `firebase-auth-compat` in `out/index.html` & Firebase native BoM |
| **Google Sign-In Provider** | ⚙️ Action Required | Enable "Google" in Firebase Console -> Authentication -> Sign-in method |
| **OAuth Consent Screen** | ⚙️ Action Required | Configure support email in Google Cloud Console / Firebase Authentication settings |
| **Updated google-services.json** | ⚙️ Action Required | Download after saving SHA-1 in Firebase Console and replace in `android/app/` |
