import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.novelix.app',
  appName: 'NOVELIX',
  webDir: 'out',
  server: {
    androidScheme: 'https',
    cleartext: true,
  },
  android: {
    allowMixedContent: true,
    backgroundColor: '#0B0B10',
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 1000,
      launchAutoHide: true,
      backgroundColor: '#0B0B10',
      androidSplashResourceName: 'splash',
      showSpinner: false,
    },
    Keyboard: {
      resize: 'body',
      resizeOnFullScreen: true,
    },
    GoogleAuth: {
      scopes: ['profile', 'email'],
      serverClientId: '239783323113-r33bjnuc153ghsgpshg8vp3mktqj6t36.apps.googleusercontent.com',
      forceCodeForRefreshToken: false,
    },
    CapacitorHttp: {
      enabled: true,
    },
  },
};

export default config;
