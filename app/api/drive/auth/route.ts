import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/utils/supabase/server';

export async function GET(request: NextRequest) {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const clientId = process.env.GOOGLE_CLIENT_ID;
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || request.nextUrl.origin;
  const redirectUri = `${siteUrl}/api/drive/callback`;

  const accountName = request.nextUrl.searchParams.get('accountName') || 'Personal Drive';
  const state = Buffer.from(JSON.stringify({ userId: user.id, accountName })).toString('base64');

  if (!clientId || clientId.includes('your_google_client_id')) {
    // Return mock connect URL or configuration message if credentials not yet configured
    const returnUrl = new URL('/publish', request.url);
    returnUrl.searchParams.set('drive_notice', 'google_credentials_needed');
    return NextResponse.redirect(returnUrl);
  }

  const scope = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/userinfo.email',
  ].join(' ');

  const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
    new URLSearchParams({
      client_id: clientId,
      redirect_uri: redirectUri,
      response_type: 'code',
      scope: scope,
      access_type: 'offline',
      prompt: 'consent',
      state: state,
    }).toString();

  return NextResponse.redirect(authUrl);
}
