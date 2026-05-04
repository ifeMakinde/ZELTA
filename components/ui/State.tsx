"use client";

export function LoadingState({ text = "Loading..." }: { text?: string }) {
  return (
    <div className="w-full rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="h-4 w-4 animate-pulse rounded-full bg-gray-300" />
        <p className="text-sm text-gray-500">{text}</p>
      </div>
      <div className="mt-4 h-3 w-full animate-pulse rounded-full bg-gray-100" />
      <div className="mt-3 h-3 w-5/6 animate-pulse rounded-full bg-gray-100" />
      <div className="mt-3 h-3 w-4/6 animate-pulse rounded-full bg-gray-100" />
    </div>
  );
}

export function ErrorState({ error }: { error: string }) {
  return (
    <div className="w-full rounded-2xl border border-red-200 bg-red-50 p-5">
      <p className="font-semibold text-red-600">Something went wrong</p>
      <p className="mt-1 text-sm text-red-500">{error}</p>
    </div>
  );
}

export function EmptyState({ text = "No data available" }: { text?: string }) {
  return (
    <div className="w-full rounded-2xl border border-gray-100 bg-white p-5">
      <p className="text-sm text-gray-400">{text}</p>
    </div>
  );
}