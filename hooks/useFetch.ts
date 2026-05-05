"use client";

import { getFirebaseAuth } from "@/firebase/index";
import { onAuthStateChanged, type User } from "firebase/auth";

interface ApiResponse<T> {
  success: boolean;
  data: T;
}

function getBaseUrl() {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!base) {
    throw new Error("Missing NEXT_PUBLIC_API_BASE_URL environment variable");
  }
  return base.replace(/\/$/, "");
}

function waitForAuthUser(): Promise<User> {
  const auth = getFirebaseAuth();

  if (!auth) {
    return Promise.reject(new Error("Firebase auth is not initialized"));
  }

  if (auth.currentUser) {
    return Promise.resolve(auth.currentUser);
  }

  return new Promise<User>((resolve, reject) => {
    const unsubscribe = onAuthStateChanged(
      auth,
      (user) => {
        unsubscribe();
        if (user) {
          resolve(user);
        } else {
          reject(new Error("Not authenticated"));
        }
      },
      (error) => {
        unsubscribe();
        reject(error);
      }
    );
  });
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const baseUrl = getBaseUrl();
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = `${baseUrl}${normalizedPath}`;

  const user = await waitForAuthUser();
  const token = await user.getIdToken();

  const headers = new Headers(options.headers);
  headers.set("Authorization", `Bearer ${token}`);

  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(url, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let errorMessage = `Request failed: ${res.status}`;

    try {
      const contentType = res.headers.get("content-type") || "";
      if (contentType.includes("application/json")) {
        const errorBody = await res.json();
        errorMessage = errorBody?.message || errorBody?.error || errorMessage;
      } else {
        const textError = await res.text();
        console.error("[API Raw Error]", textError);
      }
    } catch {
      console.error("[API Error] Could not parse error response body");
    }

    throw new Error(errorMessage);
  }

  const contentType = res.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    const json = await res.json();
    return json && typeof json === "object" && "data" in json
      ? (json as ApiResponse<T>).data
      : (json as T);
  }

  return (await res.text()) as unknown as T;
}