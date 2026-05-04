"use client";

import { useTransition } from "react";
import { useRouter, usePathname } from "next/navigation";
import FullPageLoader from "@/components/FullPageLoader";

export default function PageTransitionLoader() {
  const router = useRouter();
  const pathname = usePathname();
  const [isPending, startTransition] = useTransition();

  // Wrap router.push to use transitions
  const navigateTo = (url: string) => {
    startTransition(() => {
      router.push(url);
    });
  };

  // Store navigateTo in window for global access if needed
  if (typeof window !== "undefined") {
    (window as any).__navigateTo = navigateTo;
  }

  // Determine loading message based on current route
  const getMessage = () => {
    if (pathname.includes("dashboard")) return "Loading dashboard...";
    if (pathname.includes("auth") || pathname.includes("login")) return "Signing in...";
    if (pathname.includes("sign-up")) return "Creating account...";
    return "Loading...";
  };

  return <FullPageLoader show={isPending} message={getMessage()} />;
}

