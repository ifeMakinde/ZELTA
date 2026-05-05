import { NextRequest, NextResponse } from "next/server";

const PROTECTED_PREFIXES = ["/dashboard"];
const AUTH_ONLY_ROUTES = ["/login", "/sign-up"];

/**
 * 🔐 Simple cookie-based auth check
 */
function isAuthenticated(request: NextRequest): boolean {
  const sessionCookie = request.cookies.get("zelta_session");
  return sessionCookie?.value === "1";
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const authenticated = isAuthenticated(request);

  const isProtected = PROTECTED_PREFIXES.some((prefix) =>
    pathname.startsWith(prefix)
  );

  const isAuthRoute = AUTH_ONLY_ROUTES.some(
    (route) => pathname === route || pathname.startsWith(route + "/")
  );

  /**
   * 🚫 BLOCK unauthenticated access to protected routes
   */
  if (isProtected && !authenticated) {
    const loginUrl = new URL("/login", request.url);

    // Preserve where user wanted to go
    loginUrl.searchParams.set("from", pathname);

    return NextResponse.redirect(loginUrl);
  }

  /**
   * 🚫 Prevent logged-in users from seeing login/signup again
   */
  if (isAuthRoute && authenticated) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  /**
   * ✅ Allow request
   */
  const response = NextResponse.next();

  /**
   * 🧠 Prevent caching issues (VERY IMPORTANT)
   * Avoid stale auth state in Next.js edge
   */
  response.headers.set("Cache-Control", "no-store");

  return response;
}

export const config = {
  matcher: [
    /*
     * Match everything except:
     * - Next internals
     * - static files
     * - API routes
     */
    "/((?!_next/static|_next/image|favicon.ico|public|api).*)",
  ],
};