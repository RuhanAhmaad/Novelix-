import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.novelix.app',
  appName: 'NOVELIX',
  webDir: 'out',
  // 👇 This URL will be automatically updated by GitHub Actions
  // to point to your live Vercel deployment during the APK build.
  // For local testing, replace this with your Vercel URL or localhost:3000.
  server: {
    url: 'https://novelix.vercel.app',
    androidScheme: 'https',
    cleartext: false,
    hostname: 'novelix.app',
  },
  android: {
    allowMixedContent: false,
    backgroundColor: '#070709',
    webContentsDebuggingEnabled: false, // Set to true for dev debugging
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      launchAutoHide: true,
      backgroundColor: '#070709',
      androidSplashResourceName: 'splash',
      showSpinner: false,
    },
    Keyboard: {
      resize: 'body',
      resizeOnFullScreen: true,
    },
  },
};

export default config;
