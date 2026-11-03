import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/utils/supabase/server';

// GET: Retrieve reading progress for a user and book (with optional language)
export async function GET(request: NextRequest) {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const bookId = request.nextUrl.searchParams.get('bookId');
  const languageCode = request.nextUrl.searchParams.get('language') || 'en';

  if (!bookId) {
    return NextResponse.json({ error: 'Book ID required' }, { status: 400 });
  }

  const { data: progress } = await supabase
    .from('reading_progress')
    .select('*')
    .eq('user_id', user.id)
    .eq('book_id', bookId)
    .eq('language_code', languageCode)
    .maybeSingle();

  return NextResponse.json({ progress: progress || { current_page: 1, total_pages: 1 } });
}

// POST: Save or update reading progress
export async function POST(request: NextRequest) {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const body = await request.json();
  const { bookId, languageCode = 'en', currentPage, totalPages } = body;

  if (!bookId || !currentPage) {
    return NextResponse.json({ error: 'Missing parameters' }, { status: 400 });
  }

  const completionPercentage = totalPages > 0 ? (currentPage / totalPages) * 100 : 0;

  const { data, error } = await supabase
    .from('reading_progress')
    .upsert(
      {
        user_id: user.id,
        book_id: bookId,
        language_code: languageCode,
        current_page: currentPage,
        total_pages: totalPages || 1,
        completion_percentage: Math.min(100, Math.max(0, completionPercentage)),
        last_read_at: new Date().toISOString(),
      },
      { onConflict: 'user_id,book_id,language_code' }
    )
    .select()
    .single();

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  // Update user daily streak if needed
  await supabase
    .from('profiles')
    .update({ last_read_at: new Date().toISOString() })
    .eq('id', user.id);

  return NextResponse.json({ success: true, progress: data });
}
