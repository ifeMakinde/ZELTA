"use client";

import { useTransition } from "react";
import { useRouter } from "next/navigation";

/**
 * Hook for handling navigation with automatic loading UI
 * Usage in login/auth pages:
 *
 * const { navigate, isPending } = useNavigateWithLoader();
 *
 * const handleLogin = async (credentials) => {
 *   const result = await authenticate(credentials);
 *   if (result.success) {
 *     navigate(`/dashboard?username=${result.user.name}`);
 *   }
 * };
 *
 * // The FullPageLoader will automatically show during navigation
 */
export function useNavigateWithLoader() {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  const navigate = (url: string) => {
    startTransition(() => {
      router.push(url);
    });
  };

  return { navigate, isPending };
}
