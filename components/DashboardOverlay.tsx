"use client";

import { Loader2 } from "lucide-react";

interface DashboardOverlayProps {
  show: boolean;
  message?: string;
}

export default function DashboardOverlay({
  show,
  message = "Loading dashboard...",
}: DashboardOverlayProps) {
  if (!show) return null;

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/5 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-3 bg-white/95 px-6 py-4 rounded-lg shadow-lg">
        <Loader2 className="w-6 h-6 text-green-500 animate-spin" />
        <p className="text-sm font-medium text-gray-700">{message}</p>
      </div>
    </div>
  );
}
