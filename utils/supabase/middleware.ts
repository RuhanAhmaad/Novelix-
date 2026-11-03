import { createServerClient } from '@supabase/ssr';
import { NextResponse, type NextRequest } from 'next/server';

export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({
    request,
  });

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://gzwpfvhmjweeydiwdsga.supabase.co';
  const supabaseKey =
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ||
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
    'sb_publishable_APwu-OfPQmtnj-f-pwxfZw_OxiwM8A1';

  const supabase = createServerClient(supabaseUrl, supabaseKey, {
    cookies: {
      getAll() {
        return request.cookies.getAll();
      },
      setAll(cookiesToSet: Array<{ name: string; value: string; options?: any }>) {
        cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
        supabaseResponse = NextResponse.next({
          request,
        });
        cookiesToSet.forEach(({ name, value, options }) =>
          supabaseResponse.cookies.set(name, value, options)
        );
      },
    },
  });

  // IMPORTANT: Avoid calling getUser within routes that don't need it if performance is critical,
  // but to secure protected paths, we verify the user.
  const path = request.nextUrl.pathname;
  const protectedRoutes = ['/publish', '/library', '/settings', '/dashboard', '/admin'];
  const isProtected = protectedRoutes.some((route) => path === route || path.startsWith(`${route}/`));

  const {
    data: { user },
  } = await supabase.auth.getUser();

  // If unauthenticated and accessing a protected route, redirect to login
  if (!user && isProtected) {
    const url = request.nextUrl.clone();
    url.pathname = '/auth/login';
    url.searchParams.set('redirectTo', path);
    return NextResponse.redirect(url);
  }

  // If user is accessing /admin, verify admin privileges
  if (user && path.startsWith('/admin')) {
    // Check profiles table or user_roles table
    const { data: profile } = await supabase
      .from('profiles')
      .select('is_admin')
      .eq('id', user.id)
      .single();

    if (!profile?.is_admin) {
      // Check user_roles table as fallback
      const { data: userRole } = await supabase
        .from('user_roles')
        .select('role')
        .eq('user_id', user.id)
        .eq('role', 'admin')
        .maybeSingle();

      if (!userRole) {
        const url = request.nextUrl.clone();
        url.pathname = '/';
        url.searchParams.set('error', 'unauthorized_admin');
        return NextResponse.redirect(url);
      }
    }
  }

  // If already logged in and trying to go to login/register, redirect to dashboard or home
  if (user && (path === '/auth/login' || path === '/auth/register')) {
    const url = request.nextUrl.clone();
    url.pathname = '/';
    return NextResponse.redirect(url);
  }

  return supabaseResponse;
}
