import { NextRequest, NextResponse } from "next/server";

/**
 * Routes that require authentication.
 * Any path starting with these prefixes will be protected.
 */
const PROTECTED_PREFIXES = ["/dashboard", "/form"];

/**
 * Routes that authenticated users should NOT access
 * (redirect them to the dashboard instead).
 */
const AUTH_ONLY_ROUTES = ["/login", "/sign-up"];

/**
 * The cookie name Firebase Auth sets when a user is signed in.
 * Firebase stores the current user in IndexedDB on the client,
 * but it also sets a cookie we can check server-side as a lightweight
 * signal — we validate fully on the client and in API calls via Bearer token.
 *
 * Firebase sets a cookie named after the project:
 *   firebase:authUser:<API_KEY>:[DEFAULT]
 * Since we can't read that from middleware without the API key at build time,
 * we use a simpler approach: check for any cookie that starts with "firebase:"
 * or fall back to a custom session indicator cookie we set on login.
 *
 * The real security is enforced server-side via Firebase Admin + Bearer token
 * in every API call. This middleware only handles UX redirects.
 */
function isAuthenticated(request: NextRequest): boolean {
  // Check for Firebase auth cookies — Firebase sets cookies with the format:
  // firebase:authUser:<apiKey>:[DEFAULT]
  // We also check for a simpler custom auth signal cookie.
  const cookies = request.cookies;

  for (const [name] of cookies) {
    if (name.startsWith("firebase:authUser:")) {
      return true;
    }
  }

  // Also check our own lightweight session marker (set after successful login)
  const sessionCookie = cookies.get("zelta_session");
  if (sessionCookie?.value === "1") {
    return true;
  }

  return false;
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const isProtected = PROTECTED_PREFIXES.some((prefix) =>
    pathname.startsWith(prefix)
  );

  const isAuthRoute = AUTH_ONLY_ROUTES.some(
    (route) => pathname === route || pathname.startsWith(route + "/")
  );

  // Unauthenticated user trying to access a protected route → send to /login
  if (isProtected && !isAuthenticated(request)) {
    const loginUrl = new URL("/login", request.url);
    // Preserve the original destination so we can redirect back after login
    loginUrl.searchParams.set("from", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Authenticated user trying to access login/sign-up → send to dashboard
  if (isAuthRoute && isAuthenticated(request)) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  /*
   * Match all routes EXCEPT:
   * - Next.js internals (_next/static, _next/image)
   * - Public static files (favicon, images, etc.)
   * - API routes (handled by the backend)
   */
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|public/|api/).*)",
  ],
};