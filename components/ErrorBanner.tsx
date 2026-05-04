"use client";

import { AlertCircle, X } from "lucide-react";
import { useState, useEffect } from "react";

interface ErrorBannerProps {
  error: string | null;
  onRetry?: () => void;
  onDismiss?: () => void;
  autoHideDuration?: number; // ms, 0 = never auto-hide
}

export default function ErrorBanner({
  error,
  onRetry,
  onDismiss,
  autoHideDuration = 8000,
}: ErrorBannerProps) {
  const [visible, setVisible] = useState(!!error);

  useEffect(() => {
    setVisible(!!error);

    if (error && autoHideDuration > 0) {
      const timer = setTimeout(() => {
        setVisible(false);
        onDismiss?.();
      }, autoHideDuration);
      return () => clearTimeout(timer);
    }
  }, [error, autoHideDuration, onDismiss]);

  if (!visible || !error) return null;

  return (
    <div className="fixed top-4 left-4 right-4 lg:max-w-120 lg:right-4 lg:left-[80%] z-50 animate-in fade-in slide-in-from-top-2">
      <div className="flex gap-3 p-4 rounded-lg bg-white border border-red-300 shadow-lg">
        <div className="shrink-0 mt-0.5">
          <AlertCircle className="w-5 h-5 text-red-600" />
        </div>

        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-red-800 line-clamp-2">
            Failed to load dashboard data
          </p>
          <p className="text-xs text-red-600 mt-1 line-clamp-1">{error}</p>
          <div className="flex gap-2 mt-3">
            {onRetry && (
              <button
                onClick={() => {
                  onRetry();
                  setVisible(false);
                }}
                className="text-xs font-medium px-3 py-1.5 rounded bg-red-600 hover:bg-red-700 text-white transition-colors"
              >
                Retry
              </button>
            )}
            <button
              onClick={() => {
                setVisible(false);
                onDismiss?.();
              }}
              className="text-xs font-medium px-3 py-1.5 text-red-600 hover:bg-red-100 rounded transition-colors"
            >
              Dismiss
            </button>
          </div>
        </div>

        <button
          onClick={() => {
            setVisible(false);
            onDismiss?.();
          }}
          className="shrink-0 text-red-600 hover:text-red-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
