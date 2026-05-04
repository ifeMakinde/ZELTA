import { auth } from "@/firebase/index";
import { onAuthStateChanged, type User } from "firebase/auth";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

interface ApiResponse<T> {
  success: boolean;
  data: T;
}

// Waits for Firebase to finish rehydrating auth state.
// auth.currentUser is null on cold load even when the user IS logged in —
// this resolves once Firebase confirms the session (or confirms no user).
function waitForAuthUser(): Promise<User> {
  return new Promise((resolve, reject) => {
    // If Firebase already has the user ready, no need to wait
    if (auth.currentUser) {
      resolve(auth.currentUser);
      return;
    }

    // Otherwise wait for the first auth state emission
    const unsubscribe = onAuthStateChanged(
      auth,
      (user) => {
        unsubscribe(); // stop listening after first emission
        if (user) {
          resolve(user);
        } else {
          reject(new Error("Not authenticated"));
        }
      },
      (error) => {
        unsubscribe();
        reject(error);
      },
    );
  });
}

export async function apiFetch<T>(path: string): Promise<T> {
  const user = await waitForAuthUser(); // waits for Firebase — never races
  const token = await user.getIdToken();

  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body?.message ?? `Request failed: ${res.status}`);
  }

  const json: ApiResponse<T> = await res.json();
  return json.data;
}
