"use client";

import React from "react";
import { AlertCircle, Inbox, Loader2, RefreshCcw } from "lucide-react";

interface StateProps {
  text?: string;
  className?: string;
}

export function LoadingState({ text = "Loading data...", className = "" }: StateProps) {
  return (
    <div className={`w-full rounded-2xl border border-gray-100 bg-white p-6 shadow-sm ${className}`}>
      <div className="flex items-center gap-3 mb-6">
        <Loader2 className="h-5 w-5 animate-spin text-blue-500" />
        <p className="text-sm font-medium text-gray-600 italic">{text}</p>
      </div>
      
      {/* Skeleton Rows */}
      <div className="space-y-4">
        <div className="h-4 w-full animate-pulse rounded-md bg-gray-100" />
        <div className="h-4 w-5/6 animate-pulse rounded-md bg-gray-100" />
        <div className="h-4 w-4/6 animate-pulse rounded-md bg-gray-100" />
      </div>
    </div>
  );
}

export function ErrorState({ 
  error, 
  onRetry 
}: { 
  error: string; 
  onRetry?: () => void 
}) {
  return (
    <div className="w-full rounded-2xl border border-red-100 bg-red-50/50 p-6 flex flex-col items-center text-center">
      <div className="mb-3 rounded-full bg-red-100 p-2">
        <AlertCircle className="h-6 w-6 text-red-600" />
      </div>
      <h3 className="font-semibold text-red-900">Analysis Failed</h3>
      <p className="mt-1 text-sm text-red-600/80 max-w-xs">{error}</p>
      
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-red-700 active:scale-95"
        >
          <RefreshCcw className="h-4 w-4" />
          Try Again
        </button>
      )}
    </div>
  );
}

export function EmptyState({ text = "No behavioral data found.", icon: Icon = Inbox }: StateProps & { icon?: any }) {
  return (
    <div className="w-full rounded-2xl border border-dashed border-gray-200 bg-gray-50/30 p-10 flex flex-col items-center text-center">
      <Icon className="h-10 w-10 text-gray-300 mb-3" />
      <p className="text-sm font-medium text-gray-500">{text}</p>
      <p className="text-xs text-gray-400 mt-1">Check back later after more activities.</p>
    </div>
  );
}