import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/utils/supabase/server';
import { decryptToken } from '@/utils/crypto';

export async function GET(
  request: NextRequest,
  { params }: { params: { fileId: string } }
) {
  const fileId = params.fileId;
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();

  // Find book file record
  const { data: bookFile, error: fileError } = await supabase
    .from('book_files')
    .select('*, books(id, title, status, visibility, created_by, allow_download)')
    .eq('drive_file_id', fileId)
    .maybeSingle();

  // If found in database, enforce visibility rules
  if (bookFile && bookFile.books) {
    const book = bookFile.books;
    const isPublic = book.visibility === 'public' && book.status === 'published';
    const isOwner = user && book.created_by === user.id;

    if (!isPublic && !isOwner) {
      return NextResponse.json({ error: 'Access denied to this publication' }, { status: 403 });
    }
  }

  // Find drive account associated with the file
  let driveAccount = null;
  if (bookFile?.drive_account_id) {
    const { data: acc } = await supabase
      .from('google_drive_accounts')
      .select('*')
      .eq('id', bookFile.drive_account_id)
      .maybeSingle();
    driveAccount = acc;
  }

  // If not found by drive_account_id, look for primary drive account of author or requester
  if (!driveAccount && user) {
    const { data: acc } = await supabase
      .from('google_drive_accounts')
      .select('*')
      .eq('user_id', user.id)
      .order('is_primary', { ascending: false })
      .limit(1)
      .maybeSingle();
    driveAccount = acc;
  }

  if (!driveAccount) {
    // If no Google Drive token is configured for this specific file, check if it's a direct url or public sample
    return NextResponse.json(
      { error: 'Google Drive authorization credentials for this document were not found.' },
      { status: 404 }
    );
  }

  try {
    const refreshToken = decryptToken(driveAccount.encrypted_refresh_token);
    const clientId = process.env.GOOGLE_CLIENT_ID;
    const clientSecret = process.env.GOOGLE_CLIENT_SECRET;

    if (!clientId || !clientSecret || clientId.includes('your_google_client_id')) {
      return NextResponse.json(
        { error: 'Google Drive client credentials not set on server.' },
        { status: 500 }
      );
    }

    const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        client_id: clientId,
        client_secret: clientSecret,
        refresh_token: refreshToken,
        grant_type: 'refresh_token',
      }),
    });

    const tokenData = await tokenRes.json();
    if (!tokenRes.ok || !tokenData.access_token) {
      return NextResponse.json({ error: 'Failed to authenticate with Google Drive' }, { status: 502 });
    }

    // Stream the file directly from Google Drive API
    const driveStreamRes = await fetch(
      `https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`,
      {
        headers: { Authorization: `Bearer ${tokenData.access_token}` },
      }
    );

    if (!driveStreamRes.ok) {
      return NextResponse.json({ error: 'Failed to retrieve file content from Drive' }, { status: driveStreamRes.status });
    }

    const headers = new Headers();
    headers.set('Content-Type', 'application/pdf');
    headers.set('Content-Disposition', `inline; filename="${bookFile?.file_name || 'document.pdf'}"`);
    headers.set('Cache-Control', 'public, max-age=3600');

    return new NextResponse(driveStreamRes.body as any, {
      status: 200,
      headers,
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message || 'Error streaming PDF' }, { status: 500 });
  }
}
