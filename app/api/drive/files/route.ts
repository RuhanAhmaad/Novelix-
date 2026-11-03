import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/utils/supabase/server';
import { decryptToken } from '@/utils/crypto';

// Helper to get a valid Google Drive Access Token
async function getDriveAccessToken(userId: string, accountId?: string) {
  const supabase = createClient();

  let query = supabase
    .from('google_drive_accounts')
    .select('*')
    .eq('user_id', userId);

  if (accountId) {
    query = query.eq('id', accountId);
  } else {
    query = query.order('is_primary', { ascending: false }).limit(1);
  }

  const { data: accounts } = await query;
  if (!accounts || accounts.length === 0) {
    throw new Error('No connected Google Drive account found.');
  }

  const account = accounts[0];
  const refreshToken = decryptToken(account.encrypted_refresh_token);

  const clientId = process.env.GOOGLE_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET;

  if (!clientId || !clientSecret || clientId.includes('your_google_client_id')) {
    throw new Error('Google OAuth credentials not configured on the server.');
  }

  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      refresh_token: refreshToken,
      grant_type: 'refresh_token',
    }),
  });

  const data = await res.json();
  if (!res.ok || !data.access_token) {
    throw new Error(data.error_description || 'Failed to refresh Google Drive access token');
  }

  return { accessToken: data.access_token, account };
}

// GET: List PDF files from connected Google Drive
export async function GET(request: NextRequest) {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const accountId = request.nextUrl.searchParams.get('accountId') || undefined;

  try {
    const { accessToken, account } = await getDriveAccessToken(user.id, accountId);

    const driveRes = await fetch(
      "https://www.googleapis.com/drive/v3/files?q=mimeType='application/pdf'+and+trashed=false&fields=files(id,name,size,mimeType,createdTime,modifiedTime)&pageSize=30",
      {
        headers: { Authorization: `Bearer ${accessToken}` },
      }
    );

    const driveData = await driveRes.json();

    if (!driveRes.ok) {
      return NextResponse.json({ error: driveData.error?.message || 'Failed to fetch Drive files' }, { status: 500 });
    }

    return NextResponse.json({
      account: { id: account.id, name: account.account_name, email: account.email },
      files: driveData.files || [],
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 400 });
  }
}

// POST: Upload a PDF file to Google Drive
export async function POST(request: NextRequest) {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const formData = await request.formData();
    const file = formData.get('file') as File | null;
    const accountId = (formData.get('accountId') as string) || undefined;

    if (!file) {
      return NextResponse.json({ error: 'No PDF file provided' }, { status: 400 });
    }

    const { accessToken, account } = await getDriveAccessToken(user.id, accountId);

    const metadata = {
      name: file.name,
      mimeType: 'application/pdf',
      description: 'Uploaded via NOVELIX Publishing Studio',
    };

    const boundary = '-------314159265358979323846';
    const delimiter = `\r\n--${boundary}\r\n`;
    const closeDelimiter = `\r\n--${boundary}--`;

    const fileBuffer = await file.arrayBuffer();
    const metadataString = JSON.stringify(metadata);

    const multipartRequestBody = Buffer.concat([
      Buffer.from(
        `${delimiter}Content-Type: application/json; charset=UTF-8\r\n\r\n${metadataString}`
      ),
      Buffer.from(
        `${delimiter}Content-Type: application/pdf\r\n\r\n`
      ),
      Buffer.from(fileBuffer),
      Buffer.from(closeDelimiter),
    ]);

    const uploadRes = await fetch(
      'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,size,mimeType',
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': `multipart/related; boundary=${boundary}`,
        },
        body: multipartRequestBody,
      }
    );

    const uploadData = await uploadRes.json();

    if (!uploadRes.ok) {
      return NextResponse.json({ error: uploadData.error?.message || 'Drive upload failed' }, { status: 500 });
    }

    return NextResponse.json({
      success: true,
      fileId: uploadData.id,
      fileName: uploadData.name,
      fileSize: uploadData.size,
      accountId: account.id,
      accountEmail: account.email,
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 400 });
  }
}
