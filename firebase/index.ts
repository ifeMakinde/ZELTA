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
    return null;
  }

  return { apiKey, authDomain, projectId, storageBucket, messagingSenderId, appId, measurementId };
}

export function getFirebaseAuth(): Auth | null {
  if (typeof window === "undefined") return null;
  if (_auth) return _auth;

  const config = getFirebaseConfig();
  if (!config) return null;

  _app = getApps().length ? getApp() : initializeApp(config);
  _auth = getAuth(_app);
  return _auth;
}

// Eagerly-typed auth singleton — safe for useAuthState and signOut.
// Components that need the raw Auth instance should call getFirebaseAuth().
// This proxy is exported as `auth` for backward compatibility with
// react-firebase-hooks/auth (useAuthState(auth)).
function createAuthProxy(): Auth {
  return new Proxy({} as Auth, {
    get(_target, prop) {
      const instance = getFirebaseAuth();
      if (!instance) {
        // Return safe defaults for the most common hook properties
        if (prop === "currentUser") return null;
        return undefined;
      }
      const value = (instance as any)[prop];
      return typeof value === "function" ? value.bind(instance) : value;
    },
  });
}

export const auth: Auth = createAuthProxy();