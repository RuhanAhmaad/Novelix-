/**
 * NOVELIX 11.0 — Cloudflare Worker Backend (Free Tier: 100k requests/day)
 * Provides:
 * 1. Google Drive OAuth Initiation (/oauth/auth-url)
 * 2. Google Drive OAuth Callback & Token Exchange (/oauth/callback)
 * 3. Drive Link Validation & Metadata Inspection (/drive/validate)
 * 4. Drive Manuscript Streaming Proxy (/drive/stream)
 * 5. Push Notifications Dispatch (/fcm/notify)
 */

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
  'Access-Control-Max-Age': '86400',
};

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...CORS_HEADERS,
    },
  });
}

function errorResponse(code, message, status = 400, details = null) {
  return jsonResponse({
    success: false,
    error: {
      code,
      message,
      details,
      timestamp: new Date().toISOString()
    }
  }, status);
}

// Simple AES-GCM token encryption for secure storage
async function encryptToken(text, secret) {
  const enc = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    enc.encode(secret.padEnd(32, '0').slice(0, 32)),
    { name: 'AES-GCM' },
    false,
    ['encrypt']
  );
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const encrypted = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    keyMaterial,
    enc.encode(text)
  );
  const combined = new Uint8Array(iv.length + encrypted.byteLength);
  combined.set(iv);
  combined.set(new Uint8Array(encrypted), iv.length);
  return btoa(String.fromCharCode(...combined));
}

export default {
  async fetch(request, env, ctx) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS_HEADERS });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    try {
      // 1. Health check
      if (path === '/' || path === '/health') {
        return jsonResponse({
          service: 'NOVELIX Cloudflare Backend',
          version: '11.0.0',
          tier: 'Cloudflare Workers Free',
          status: 'online',
          endpoints: [
            '/oauth/auth-url',
            '/oauth/callback',
            '/drive/validate',
            '/drive/stream',
            '/fcm/notify'
          ]
        });
      }

      // 2. OAuth Initiation
      if (path === '/oauth/auth-url') {
        const uid = url.searchParams.get('uid');
        if (!uid) {
          return errorResponse('MISSING_UID', 'User UID is required to start authorization.');
        }

        const clientId = env.GOOGLE_DRIVE_CLIENT_ID || '23165793827-un6a2kh299r2e7rroj9nivoku5josvlh.apps.googleusercontent.com';
        const redirectUri = env.CANONICAL_REDIRECT_URI || `${url.origin}/oauth/callback`;
        const state = btoa(JSON.stringify({ uid, ts: Date.now() }));

        const scopes = [
          'https://www.googleapis.com/auth/drive.readonly',
          'https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile'
        ].join(' ');

        const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
          new URLSearchParams({
            client_id: clientId,
            redirect_uri: redirectUri,
            response_type: 'code',
            scope: scopes,
            access_type: 'offline',
            prompt: 'consent',
            state: state
          }).toString();

        return jsonResponse({
          success: true,
          authUrl: googleAuthUrl,
          redirectUri
        });
      }

      // 3. OAuth Callback
      if (path === '/oauth/callback') {
        const code = url.searchParams.get('code');
        const stateRaw = url.searchParams.get('state');
        const errParam = url.searchParams.get('error');

        const deepLinkBase = env.APP_DEEP_LINK || 'novelix://drive-callback';

        if (errParam || !code) {
          const errRedirect = `${deepLinkBase}?error=${encodeURIComponent(errParam || 'missing_code')}`;
          return Response.redirect(errRedirect, 302);
        }

        let stateObj = {};
        try {
          stateObj = JSON.parse(atob(stateRaw));
        } catch (_) {}

        const clientId = env.GOOGLE_DRIVE_CLIENT_ID || '23165793827-un6a2kh299r2e7rroj9nivoku5josvlh.apps.googleusercontent.com';
        const clientSecret = env.GOOGLE_DRIVE_CLIENT_SECRET;
        if (!clientSecret) {
          const errRedirect = `${deepLinkBase}?error=${encodeURIComponent('missing_client_secret')}`;
          return Response.redirect(errRedirect, 302);
        }
        const redirectUri = env.CANONICAL_REDIRECT_URI || `${url.origin}/oauth/callback`;

        // Exchange code for tokens
        const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({
            code,
            client_id: clientId,
            client_secret: clientSecret,
            redirect_uri: redirectUri,
            grant_type: 'authorization_code'
          })
        });

        const tokenData = await tokenRes.json();
        if (!tokenRes.ok || !tokenData.access_token) {
          const errRedirect = `${deepLinkBase}?error=token_exchange_failed`;
          return Response.redirect(errRedirect, 302);
        }

        // Fetch User profile info
        let userEmail = 'drive-user@novelix.app';
        let userName = 'Google Drive User';
        let userPhoto = '';
        try {
          const userRes = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
            headers: { Authorization: `Bearer ${tokenData.access_token}` }
          });
          if (userRes.ok) {
            const userData = await userRes.json();
            userEmail = userData.email || userEmail;
            userName = userData.name || userName;
            userPhoto = userData.picture || '';
          }
        } catch (_) {}

        const encSecret = env.TOKEN_ENCRYPTION_SECRET || 'novelix-super-secure-aes256-key-32chars!';
        const encryptedRefreshToken = tokenData.refresh_token
          ? await encryptToken(tokenData.refresh_token, encSecret)
          : '';

        // Deep link redirect back to Android App
        const appCallbackUrl = `${deepLinkBase}?` + new URLSearchParams({
          success: 'true',
          email: userEmail,
          name: userName,
          photo: userPhoto,
          accessToken: tokenData.access_token,
          expiresIn: String(tokenData.expires_in || 3600),
          hasRefreshToken: String(!!tokenData.refresh_token),
          encRefreshToken: encryptedRefreshToken,
          uid: stateObj.uid || ''
        }).toString();

        return new Response(`<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>NOVELIX — Drive Authorization Connected</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { background: #0B0B10; color: #FFF; font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; text-align: center; }
    .card { background: #161622; padding: 2rem; border-radius: 1rem; border: 1px solid #28283C; max-width: 90%; }
    .btn { display: inline-block; background: #9270FF; color: white; padding: 0.75rem 1.5rem; border-radius: 0.5rem; text-decoration: none; font-weight: bold; margin-top: 1rem; }
  </style>
</head>
<body>
  <div class="card">
    <h2>Google Drive Connected!</h2>
    <p>Account: <b>${userEmail}</b></p>
    <p>Returning to NOVELIX...</p>
    <a href="${appCallbackUrl}" class="btn">Open NOVELIX App</a>
  </div>
  <script>
    window.location.href = "${appCallbackUrl}";
    setTimeout(function() { window.close(); }, 3000);
  </script>
</body>
</html>`, {
          headers: { 'Content-Type': 'text/html; charset=utf-8' }
        });
      }

      // 4. Drive Link Validation
      if (path === '/drive/validate') {
        const body = await request.json().catch(() => ({}));
        const fileId = body.fileId;
        const accessToken = body.accessToken;

        if (!fileId) {
          return errorResponse('INVALID_ARGUMENT', 'Google Drive file ID is required.', 400);
        }

        // 4a. Check if public
        try {
          const publicRes = await fetch(`https://drive.google.com/uc?id=${fileId}&export=download`, {
            method: 'GET',
            headers: { 'Range': 'bytes=0-1024' }
          });

          if (publicRes.ok) {
            const buf = await publicRes.arrayBuffer();
            const bytes = new Uint8Array(buf);
            const isPdf = bytes.length >= 4 && bytes[0] === 0x25 && bytes[1] === 0x50 && bytes[2] === 0x44 && bytes[3] === 0x46;
            const cType = (publicRes.headers.get('content-type') || '').toLowerCase();

            if (isPdf || cType.includes('application/pdf')) {
              const dispo = publicRes.headers.get('content-disposition') || '';
              const matchName = dispo.match(/filename\*?=['"]?(?:UTF-\d['"]*)?([^;\r\n"']*)['"]?/i);
              const fileName = matchName && matchName[1] ? decodeURIComponent(matchName[1]) : `Google_Drive_${fileId.slice(0, 8)}.pdf`;
              const fileSize = parseInt(publicRes.headers.get('content-range')?.split('/')[1] || publicRes.headers.get('content-length') || '0', 10);

              return jsonResponse({
                success: true,
                valid: true,
                isPublic: true,
                fileId,
                fileName,
                fileSize,
                mimeType: 'application/pdf',
                downloadUrl: `https://drive.google.com/uc?id=${fileId}&export=download`
              });
            }
          }
        } catch (_) {}

        // 4b. Authenticated inspection with token if provided
        if (accessToken) {
          const metaRes = await fetch(`https://www.googleapis.com/drive/v3/files/${fileId}?fields=id,name,mimeType,size,trashed`, {
            headers: { Authorization: `Bearer ${accessToken}` }
          });

          if (metaRes.ok) {
            const meta = await metaRes.json();
            if (meta.trashed) {
              return errorResponse('FILE_TRASHED', 'This manuscript is in your Google Drive trash.', 400);
            }
            if (meta.mimeType !== 'application/pdf' && !meta.name.toLowerCase().endsWith('.pdf')) {
              return errorResponse('UNSUPPORTED_TYPE', `File is ${meta.mimeType || 'not a PDF'}. NOVELIX requires PDF format.`, 400);
            }
            return jsonResponse({
              success: true,
              valid: true,
              isPublic: false,
              fileId: meta.id,
              fileName: meta.name,
              fileSize: parseInt(meta.size || '0', 10),
              mimeType: 'application/pdf'
            });
          } else if (metaRes.status === 404) {
            return errorResponse('FILE_NOT_FOUND', 'File not found on Google Drive.', 404);
          } else if (metaRes.status === 403) {
            return errorResponse('PERMISSION_DENIED', 'Permission denied. Ensure your Google account has view access to this file.', 403);
          }
        }

        return errorResponse('PERMISSION_DENIED', 'This Google Drive file is private. Please set sharing to "Anyone with the link can view" or connect your Google Drive account.', 403);
      }

      // 5. Drive Streaming Proxy
      if (path === '/drive/stream') {
        const fileId = url.searchParams.get('fileId');
        const token = url.searchParams.get('token');

        if (!fileId) {
          return new Response('File ID required', { status: 400 });
        }

        let driveFetchUrl = `https://drive.google.com/uc?id=${fileId}&export=download`;
        const headers = {};
        if (token) {
          driveFetchUrl = `https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`;
          headers['Authorization'] = `Bearer ${token}`;
        }

        const driveRes = await fetch(driveFetchUrl, { headers });
        return new Response(driveRes.body, {
          status: driveRes.status,
          headers: {
            'Content-Type': 'application/pdf',
            'Content-Disposition': `inline; filename="manuscript_${fileId}.pdf"`,
            ...CORS_HEADERS
          }
        });
      }

      return errorResponse('NOT_FOUND', 'Endpoint not found', 404);
    } catch (err) {
      return errorResponse('SERVER_ERROR', err.message || 'Internal server error', 500);
    }
  }
};
