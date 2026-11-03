import { createBrowserClient } from '@supabase/ssr';

export function createClient() {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://gzwpfvhmjweeydiwdsga.supabase.co';
  const supabaseKey =
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ||
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
    'sb_publishable_APwu-OfPQmtnj-f-pwxfZw_OxiwM8A1';

  return createBrowserClient(supabaseUrl, supabaseKey);
}
