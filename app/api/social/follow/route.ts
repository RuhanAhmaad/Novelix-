import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/utils/supabase/server';

export async function POST(request: NextRequest) {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Please log in to follow authors' }, { status: 401 });
  }

  const { authorId } = await request.json();
  if (!authorId) {
    return NextResponse.json({ error: 'Author ID required' }, { status: 400 });
  }

  if (authorId === user.id) {
    return NextResponse.json({ error: 'You cannot follow yourself' }, { status: 400 });
  }

  // Check if already following
  const { data: existing } = await supabase
    .from('follows')
    .select('id')
    .eq('follower_id', user.id)
    .eq('following_id', authorId)
    .maybeSingle();

  if (existing) {
    // Unfollow
    await supabase.from('follows').delete().eq('id', existing.id);
    return NextResponse.json({ following: false });
  } else {
    // Follow
    await supabase.from('follows').insert({ follower_id: user.id, following_id: authorId });

    // Send notification to author
    await supabase.from('notifications').insert({
      recipient_id: authorId,
      sender_id: user.id,
      type: 'new_follower',
      title: 'New Follower!',
      message: 'Someone started following your profile and updates.',
      link: `/author/${user.id}`,
    });

    return NextResponse.json({ following: true });
  }
}
