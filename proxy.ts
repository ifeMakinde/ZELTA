import { NextRequest, NextResponse } from "next/server";

// Routes that require auth
const PROTECTED_PREFIXES = ["/dashboard", "/form"];

// Routes only for unauthenticated users
const AUTH_ONLY_ROUTES = ["/login", "/sign-up"];

function isAuthenticated(request: NextRequest): boolean {
  return request.cookies.get("zelta_session")?.value === "1";
}

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const authenticated = isAuthenticated(request);

  const isProtected = PROTECTED_PREFIXES.some((p) => pathname.startsWith(p));
  const isAuthRoute = AUTH_ONLY_ROUTES.some(
    (r) => pathname === r || pathname.startsWith(r + "/")
  );

  // Block unauthenticated access to protected routes
  if (isProtected && !authenticated) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("from", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Prevent authenticated users from seeing login/signup
  if (isAuthRoute && authenticated) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  const response = NextResponse.next();
  response.headers.set("Cache-Control", "no-store");
  return response;
}

export const proxyConfig = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|public|api).*)",
  ],
};