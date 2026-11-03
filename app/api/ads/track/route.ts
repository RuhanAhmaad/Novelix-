import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/utils/supabase/server';

export async function POST(request: NextRequest) {
  try {
    const { adId, eventType } = await request.json();

    if (!adId || !['impression', 'click'].includes(eventType)) {
      return NextResponse.json({ error: 'Invalid ad tracking payload' }, { status: 400 });
    }

    const supabase = createClient();
    const { data: { user } } = await supabase.auth.getUser();

    // Log the anonymous or authenticated event
    await supabase.from('ad_events').insert({
      ad_id: adId,
      event_type: eventType,
      user_id: user?.id || null,
    });

    // Update aggregate counter on the ad
    if (eventType === 'impression') {
      await supabase.rpc('increment_ad_impressions', { target_ad_id: adId });
    } else if (eventType === 'click') {
      await supabase.rpc('increment_ad_clicks', { target_ad_id: adId });
    }

    return NextResponse.json({ success: true });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
