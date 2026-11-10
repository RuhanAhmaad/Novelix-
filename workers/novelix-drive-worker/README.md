# NOVELIX 11.0 — Free Cloudflare Worker (Drive OAuth & Verification)

This Cloudflare Worker provides a 100% free backend solution (100,000 requests/day, zero billing required) for:
- Google Drive OAuth 2.0 Web Client initiation
- Google OAuth 2.0 authorization code exchange
- Private Google Drive manuscript metadata verification
- Secure streaming of private PDFs
- Free-tier FCM push notification delivery

## Quick Free Deployment (2 minutes)

1. **Install Wrangler (if not installed):**
   ```bash
   npm install -g wrangler
   ```

2. **Authenticate with your free Cloudflare account:**
   ```bash
   wrangler login
   ```

3. **Set your Google Client Secret:**
   ```bash
   wrangler secret put GOOGLE_DRIVE_CLIENT_SECRET
   # Enter your OAuth 2.0 Client Secret when prompted
   ```

4. **Deploy:**
   ```bash
   wrangler deploy
   ```

5. **Update Google Cloud Console:**
   Add your deployed worker callback URL (e.g., `https://novelix-drive-worker.<subdomain>.workers.dev/oauth/callback`) to:
   - Google Cloud Console -> APIs & Services -> Credentials -> OAuth 2.0 Client IDs -> Authorized redirect URIs.
