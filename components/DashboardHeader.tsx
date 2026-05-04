"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { Bell, History, User, Settings, LogOut, ChevronDown } from "lucide-react";
import { auth } from "@/firebase/index";
import { signOut } from "firebase/auth";
import { useAuthState } from "react-firebase-hooks/auth";

const PAGE_TITLES: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/dashboard/wallet": "Wallet",
  "/dashboard/behavioral": "Behavioral Snapshot",
  "/dashboard/simulations": "Portfolio Simulations",
  "/dashboard/co-pilot": "BQ Co-pilot",
  "/dashboard/history": "Decision History",
  "/dashboard/profile": "Profile & Settings",
};

export default function DashboardHeader() {
  const router = useRouter();
  const pathname = usePathname();
  const [user] = useAuthState(auth);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const pageTitle = PAGE_TITLES[pathname] ?? "Dashboard";

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSignOut = async () => {
    await signOut(auth);
    router.push("/login");
  };

  // Derive initials and display name from Firebase user
  const displayName = user?.displayName || user?.email?.split("@")[0] || "User";
  const initials = displayName
    .split(" ")
    .map((n: string) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between border-b border-gray-100 bg-white px-4 py-3 lg:px-6">
      {/* Page title */}
      <p className="text-sm font-medium text-gray-500">{pageTitle}</p>

      {/* Right controls */}
      <div className="flex items-center gap-3">
        {/* Bell */}
        <button className="relative flex h-9 w-9 items-center justify-center rounded-full text-gray-500 transition hover:bg-gray-100">
          <Bell className="h-5 w-5 stroke-[1.5]" />
        </button>

        {/* Avatar + Dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setDropdownOpen((prev) => !prev)}
            className="flex h-9 w-9 items-center justify-center rounded-full bg-[#10b981] text-sm font-semibold text-white transition hover:bg-[#0b9268] focus:outline-none focus:ring-2 focus:ring-[#10b981] focus:ring-offset-2"
          >
            {initials}
          </button>

          {/* Dropdown panel */}
          {dropdownOpen && (
            <div className="absolute right-0 top-11 z-50 w-52 overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-lg">
              {/* User info */}
              <div className="border-b border-gray-100 px-4 py-3">
                <p className="text-sm font-semibold text-gray-900">{displayName}</p>
                <p className="text-xs text-gray-500">Student Account</p>
              </div>

              {/* Nav links */}
              <nav className="py-1">
                <DropdownLink
                  href="/dashboard/history"
                  icon={<History className="h-4 w-4" />}
                  label="Decision History"
                  onClick={() => setDropdownOpen(false)}
                />
                <DropdownLink
                  href="/dashboard/profile"
                  icon={<User className="h-4 w-4" />}
                  label="Profile"
                  onClick={() => setDropdownOpen(false)}
                />
                <DropdownLink
                  href="/dashboard/profile?tab=settings"
                  icon={<Settings className="h-4 w-4" />}
                  label="Settings"
                  onClick={() => setDropdownOpen(false)}
                />
              </nav>

              {/* Sign out */}
              <div className="border-t border-gray-100 py-1">
                <button
                  onClick={handleSignOut}
                  className="flex w-full items-center gap-3 px-4 py-2 text-sm font-medium text-red-500 transition hover:bg-red-50"
                >
                  <LogOut className="h-4 w-4" />
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

function DropdownLink({
  href,
  icon,
  label,
  onClick,
}: {
  href: string;
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
}) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 transition hover:bg-gray-50"
    >
      <span className="text-gray-400">{icon}</span>
      {label}
    </Link>
  );
}