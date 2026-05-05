"use client";

import React, { createContext, useContext, useState } from "react";
import { useRouter } from "next/navigation";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
} from "firebase/auth";
import { getFirebaseAuth } from "../firebase/index";

type AuthContextType = {
  email: string;
  setEmail: React.Dispatch<React.SetStateAction<string>>;
  password: string;
  setPassword: React.Dispatch<React.SetStateAction<string>>;
  handleLogin: (event: React.FormEvent<HTMLFormElement>) => Promise<void>;
  handleSignUp: (event: React.FormEvent<HTMLFormElement>) => Promise<void>;
  authenticationError: string | null;
  loading: boolean;
};

const AuthContext = createContext<AuthContextType | null>(null);

// ─── Cookie helpers ───────────────────────────────────────────────
// The middleware reads this cookie to decide auth state.
// Must be set BEFORE any navigation so the middleware sees it on the
// first request to a protected route.
function setSessionCookie() {
  // 7-day expiry, SameSite=Lax so it works across navigations
  const expires = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toUTCString();
  document.cookie = `zelta_session=1; path=/; expires=${expires}; SameSite=Lax`;
}

export function clearSessionCookie() {
  document.cookie = "zelta_session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax";
}

// ─── Check if user has already completed onboarding ──────────────
// We try to fetch /api/profile. If the backend returns a name, they
// are onboarded → go to /dashboard. Otherwise → /form.
// We call this AFTER setting the session cookie so the API can auth.
async function checkOnboardingStatus(idToken: string): Promise<boolean> {
  const base = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "").replace(/\/$/, "");
  try {
    const res = await fetch(`${base}/api/profile`, {
      headers: { Authorization: `Bearer ${idToken}` },
    });
    if (!res.ok) return false;
    const json = await res.json();
    // Has a name → onboarded
    const profileData = json?.data ?? json;
    return Boolean(profileData?.name);
  } catch {
    return false;
  }
}

function AuthProvider({ children }: { children: React.ReactNode }) {
  const navigate = useRouter();
  const auth = getFirebaseAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authenticationError, setAuthenticationError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const clearErrorLater = (ms = 2500) => {
    window.setTimeout(() => setAuthenticationError(null), ms);
  };

  // ── Sign Up ─────────────────────────────────────────────────────
  // New users always go to /form (they have no profile yet)
  const handleSignUp = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!auth) {
      setAuthenticationError("Firebase auth is not initialized.");
      clearErrorLater();
      return;
    }

    setLoading(true);
    setAuthenticationError(null);

    try {
      const { user } = await createUserWithEmailAndPassword(auth, email, password);

      // 1. Set session cookie FIRST so middleware allows the next route
      setSessionCookie();

      // 2. Navigate to onboarding form
      navigate.push("/form");
    } catch (error: unknown) {
      const e = error as { code?: string };
      if (e.code === "auth/email-already-in-use") {
        setAuthenticationError("This email is already in use.");
      } else if (e.code === "auth/weak-password") {
        setAuthenticationError("Password is too weak (min 6 characters).");
      } else if (e.code === "auth/invalid-email") {
        setAuthenticationError("Please enter a valid email address.");
      } else {
        setAuthenticationError("Unable to create account. Please try again.");
      }
      clearErrorLater();
    } finally {
      setLoading(false);
    }
  };

  // ── Login ───────────────────────────────────────────────────────
  // Returning users skip /form and go directly to /dashboard
  const handleLogin = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!auth) {
      setAuthenticationError("Firebase auth is not initialized.");
      clearErrorLater();
      return;
    }

    setLoading(true);
    setAuthenticationError(null);

    try {
      const { user } = await signInWithEmailAndPassword(auth, email, password);

      // 1. Get ID token (needed for profile check)
      const idToken = await user.getIdToken();

      // 2. Set session cookie BEFORE navigating so middleware allows the route
      setSessionCookie();

      // 3. Check if they've completed onboarding
      const onboarded = await checkOnboardingStatus(idToken);

      // 4. Route accordingly
      navigate.push(onboarded ? "/dashboard" : "/form");
    } catch (error: unknown) {
      const e = error as { code?: string };
      if (e.code === "auth/invalid-credential" || e.code === "auth/wrong-password" || e.code === "auth/user-not-found") {
        setAuthenticationError("Invalid email or password.");
      } else if (e.code === "auth/too-many-requests") {
        setAuthenticationError("Too many attempts. Try again later.");
      } else if (e.code === "auth/user-disabled") {
        setAuthenticationError("This account has been disabled.");
      } else if (e.code === "auth/invalid-email") {
        setAuthenticationError("Please enter a valid email address.");
      } else {
        setAuthenticationError("An error occurred. Please try again.");
      }
      clearErrorLater();
    } finally {
      setLoading(false);
    }
  };

  const value: AuthContextType = {
    email,
    setEmail,
    password,
    setPassword,
    handleLogin,
    handleSignUp,
    authenticationError,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within the AuthProvider!");
  }
  return context;
};

export { useAuth, AuthProvider };