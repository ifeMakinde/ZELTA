"use client";

import { initializeApp, getApps, getApp, type FirebaseApp } from "firebase/app";
import { getAuth, type Auth } from "firebase/auth";

let _app: FirebaseApp | null = null;
let _auth: Auth | null = null;

function getFirebaseConfig() {
  const apiKey = process.env.NEXT_PUBLIC_FIREBASE_APIKEY;
  const authDomain = process.env.NEXT_PUBLIC_FIREBASE_AUTHDOMAIN;
  const projectId = process.env.NEXT_PUBLIC_FIREBASE_PROJECTID;
  const storageBucket = process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET;
  const messagingSenderId = process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID;
  const appId = process.env.NEXT_PUBLIC_FIREBASE_APP_ID;
  const measurementId = process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID;

  if (!apiKey || !authDomain || !projectId || !storageBucket || !messagingSenderId || !appId) {
    console.warn("[Firebase] Missing required env vars — Firebase will not initialize.");
    return null;
  }

  return { apiKey, authDomain, projectId, storageBucket, messagingSenderId, appId, measurementId };
}

/**
 * Returns the Firebase Auth singleton. Safe to call multiple times.
 * Returns null during SSR or if env vars are missing.
 */
export function getFirebaseAuth(): Auth | null {
  if (typeof window === "undefined") return null;
  if (_auth) return _auth;

  const config = getFirebaseConfig();
  if (!config) return null;

  try {
    _app = getApps().length ? getApp() : initializeApp(config);
    _auth = getAuth(_app);
    return _auth;
  } catch (e) {
    console.error("[Firebase] Initialization error:", e);
    return null;
  }
}

/**
 * Exported `auth` proxy — compatible with:
 * - useAuthState(auth)
 * - signOut(auth)
 * - onAuthStateChanged(auth, ...)
 *
 * Lazily calls getFirebaseAuth() on first access.
 */
export const auth: Auth = new Proxy({} as Auth, {
  get(_target, prop: string | symbol) {
    const instance = getFirebaseAuth();
    if (!instance) {
      if (prop === "currentUser") return null;
      // Return a no-op for function calls during SSR
      return () => {};
    }
    const value = (instance as unknown as Record<string | symbol, unknown>)[prop];
    return typeof value === "function" ? (value as Function).bind(instance) : value;
  },
});