import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/utils/supabase/server';
import { encryptToken } from '@/utils/crypto';

export async function GET(request: NextRequest) {
  const url = request.nextUrl;
  const code = url.searchParams.get('code');
  const stateRaw = url.searchParams.get('state');

  if (!code || !stateRaw) {
    return NextResponse.redirect(new URL('/publish?error=drive_auth_failed', request.url));
  }

  let state: { userId: string; accountName: string };
  try {
    state = JSON.parse(Buffer.from(stateRaw, 'base64').toString('utf8'));
  } catch {
    return NextResponse.redirect(new URL('/publish?error=invalid_state', request.url));
  }

  const clientId = process.env.GOOGLE_CLIENT_ID!;
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET!;
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || url.origin;
  const redirectUri = `${siteUrl}/api/drive/callback`;

  try {
    // Exchange code for tokens
    const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        code,
        client_id: clientId,
        client_secret: clientSecret,
        redirect_uri: redirectUri,
        grant_type: 'authorization_code',
      }),
    });

    const tokenData = await tokenRes.json();

    if (!tokenRes.ok || !tokenData.access_token) {
      console.error('Failed to exchange Google OAuth code:', tokenData);
      return NextResponse.redirect(new URL('/publish?error=token_exchange_failed', request.url));
    }

    // Get user email from Google UserInfo
    const userinfoRes = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
      headers: { Authorization: `Bearer ${tokenData.access_token}` },
    });
    const userinfo = await userinfoRes.json();
    const email = userinfo.email || 'connected-account@gmail.com';

    // Encrypt the refresh token
    const refreshToken = tokenData.refresh_token || tokenData.access_token;
    const encryptedRefreshToken = encryptToken(refreshToken);

    const supabase = createClient();

    // Check if user has any existing accounts (if not, make this primary)
    const { data: existing } = await supabase
      .from('google_drive_accounts')
      .select('id')
      .eq('user_id', state.userId);

    const isPrimary = !existing || existing.length === 0;

    // Insert or update the account
    await supabase.from('google_drive_accounts').insert({
      user_id: state.userId,
      account_name: state.accountName || 'Google Drive',
      email: email,
      encrypted_refresh_token: encryptedRefreshToken,
      is_primary: isPrimary,
    });

    return NextResponse.redirect(new URL('/publish?drive_connected=true', request.url));
  } catch (error) {
    console.error('Google Drive Callback Exception:', error);
    return NextResponse.redirect(new URL('/publish?error=drive_exception', request.url));
  }
}
