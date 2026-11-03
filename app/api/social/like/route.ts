import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/utils/supabase/server';

export async function POST(request: NextRequest) {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Please log in to like this book' }, { status: 401 });
  }

  const { bookId } = await request.json();
  if (!bookId) {
    return NextResponse.json({ error: 'Book ID required' }, { status: 400 });
  }

  // Check if liked
  const { data: existing } = await supabase
    .from('likes')
    .select('id')
    .eq('user_id', user.id)
    .eq('book_id', bookId)
    .maybeSingle();

  if (existing) {
    // Unlike
    await supabase.from('likes').delete().eq('id', existing.id);
    return NextResponse.json({ liked: false });
  } else {
    // Like
    await supabase.from('likes').insert({ user_id: user.id, book_id: bookId });
    return NextResponse.json({ liked: true });
  }
}
