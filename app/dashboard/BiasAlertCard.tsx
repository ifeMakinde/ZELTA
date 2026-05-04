import { Brain } from "lucide-react";

interface BiasCardProps {
  bias_explanation?: string;
  bias_confidence?: string;
  active_bias?: string;
  loading?: boolean;
  error?: string | null;
}

export default function BiasAlertCard({
  bias_explanation,
  active_bias,
  loading = false,
  error = null,
}: BiasCardProps) {
  // Loading skeleton
  if (loading) {
    return (
      <div className="flex gap-4 p-5 bg-gray-100 rounded-xl">
        <div className="w-6 h-6 bg-gray-300 rounded-full animate-pulse shrink-0" />
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-gray-300 rounded animate-pulse w-32" />
          <div className="h-6 bg-gray-300 rounded animate-pulse w-40" />
          <div className="h-4 bg-gray-300 rounded animate-pulse" />
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex gap-4 p-5 bg-white rounded-xl border border-red-200">
        <Brain color="red" />
        <p className="text-red-600 text-sm">
          Failed to load bias data: {error}
        </p>
      </div>
    );
  }

  // No data state
  if (!bias_explanation) {
    return (
      <div className="flex gap-4 p-5 bg-orange-50 rounded-xl">
        <Brain color="orange" />
        <div>
          <p className="font-semibold text-sm">Analyzing bias...</p>
          <p className="text-sm text-gray-500 mt-1">
            Data will appear here shortly
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-4 p-5 bg-orange-50 rounded-xl">
      <Brain color="orange" />

      <div>
        <p className="font-semibold text-sm">Active Bias Detected</p>

        <h2 className="text-xl font-bold text-orange-500 uppercase">
          {active_bias}
        </h2>

        <p className="text-sm text-gray-600 mt-1">{bias_explanation}</p>
      </div>
    </div>
  );
}
