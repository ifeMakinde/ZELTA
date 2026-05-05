"use client";

import { initializeApp, getApps, getApp, type FirebaseApp } from "firebase/app";
import { getAuth, type Auth } from "firebase/auth";

let app: FirebaseApp | null = null;
let auth: Auth | null = null;

function getFirebaseConfig() {
  const apiKey = process.env.NEXT_PUBLIC_FIREBASE_APIKEY;
  const authDomain = process.env.NEXT_PUBLIC_FIREBASE_AUTHDOMAIN;
  const projectId = process.env.NEXT_PUBLIC_FIREBASE_PROJECTID;
  const storageBucket = process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET;
  const messagingSenderId = process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID;
  const appId = process.env.NEXT_PUBLIC_FIREBASE_APP_ID;
  const measurementId = process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID;

  if (
    !apiKey ||
    !authDomain ||
    !projectId ||
    !storageBucket ||
    !messagingSenderId ||
    !appId
  ) {
    return null;
  }

  return {
    apiKey,
    authDomain,
    projectId,
    storageBucket,
    messagingSenderId,
    appId,
    measurementId,
  };
}

export function getFirebaseAuth() {
  if (typeof window === "undefined") return null;

  if (auth) return auth;

  const config = getFirebaseConfig();
  if (!config) return null;

  app = getApps().length ? getApp() : initializeApp(config);
  auth = getAuth(app);

  return auth;
}