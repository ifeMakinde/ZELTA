"use client";

import { auth } from "@/firebase/index";
import { onAuthStateChanged, type User } from "firebase/auth";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

interface ApiResponse<T> {
  success: boolean;
  data: T;
}

/**
 * Waits for Firebase to finish rehydrating auth state.
 */
function waitForAuthUser(): Promise<User> {
  return new Promise((resolve, reject) => {
    if (auth.currentUser) {
      resolve(auth.currentUser);
      return;
    }

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

/**
 * Robust fetch wrapper with auth, URL sanitization, and detailed error reporting.
 */
export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const user = await waitForAuthUser();
  const token = await user.getIdToken();

  if (!BASE_URL) {
    throw new Error("Missing NEXT_PUBLIC_API_BASE_URL environment variable");
  }

  // 1. Sanitizing URL: Strips trailing slash from Base and ensures leading slash on Path.
  // This prevents the "https://api.com//endpoint" double-slash bug.
  const normalizedBase = BASE_URL.replace(/\/$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = `${normalizedBase}${normalizedPath}`;

  const headers = {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json",
    ...(options?.headers ?? {}),
  } as Record<string, string>;

  const res = await fetch(url, {
    ...options,
    headers,
  });

  // 2. Enhanced Error Handling
  if (!res.ok) {
    let errorMessage = `Request failed: ${res.status}`;
    
    try {
      // Check if the response is JSON before parsing to avoid "Unexpected token < in JSON"
      const contentType = res.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        const errorBody = await res.json();
        errorMessage = errorBody?.message || errorBody?.error || errorMessage;
        console.error(`[API 500/Error Context]:`, errorBody);
      } else {
        // If it's a 500 error returning HTML/Text (common in server crashes)
        const textError = await res.text();
        console.error(`[API Raw Error]:`, textError);
      }
    } catch (e) {
      console.error("[API Error] Could not parse error response body.");
    }

    throw new Error(errorMessage);
  }

  // 3. Flexible Data Extraction
  const json = await res.json();
  
  // Checks for your standard { success: true, data: T } wrapper,
  // but falls back to returning the whole object if the wrapper is missing.
  return json && typeof json === 'object' && 'data' in json 
    ? (json as ApiResponse<T>).data 
    : (json as T);
}