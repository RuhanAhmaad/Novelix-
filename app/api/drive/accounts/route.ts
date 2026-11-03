import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/utils/supabase/server';

// GET: List all connected Google Drive accounts for the logged-in user
export async function GET() {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { data: accounts, error } = await supabase
    .from('google_drive_accounts')
    .select('id, account_name, email, is_primary, created_at, updated_at')
    .eq('user_id', user.id)
    .order('is_primary', { ascending: false })
    .order('created_at', { ascending: false });

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ accounts: accounts || [] });
}

// DELETE: Disconnect a Google Drive account
export async function DELETE(request: NextRequest) {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { accountId } = await request.json();
  if (!accountId) {
    return NextResponse.json({ error: 'Account ID required' }, { status: 400 });
  }

  const { error } = await supabase
    .from('google_drive_accounts')
    .delete()
    .eq('id', accountId)
    .eq('user_id', user.id);

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ success: true });
}

// PATCH: Set preferred/primary Google Drive account
export async function PATCH(request: NextRequest) {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { accountId, action } = await request.json();

  if (action === 'set_primary') {
    // Unset current primary accounts
    await supabase
      .from('google_drive_accounts')
      .update({ is_primary: false })
      .eq('user_id', user.id);

    // Set new primary
    const { error } = await supabase
      .from('google_drive_accounts')
      .update({ is_primary: true })
      .eq('id', accountId)
      .eq('user_id', user.id);

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }
  }

  return NextResponse.json({ success: true });
}
