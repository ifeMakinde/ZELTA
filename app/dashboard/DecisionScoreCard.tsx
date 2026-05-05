import { ArrowDownRight } from "lucide-react";

interface DecisionScoreCardProps {
  confidence_gap?: number;
  bias_confidence?: string;
  rational_pct?: number;
  behavioral_pct?: number;
  loading?: boolean;
  error?: string | null;
}

export default function DecisionScoreCard({
  confidence_gap,
  bias_confidence,
  rational_pct,
  behavioral_pct,
  loading = false,
  error = null,
}: DecisionScoreCardProps) {
  // Loading skeleton
  if (loading) {
    return (
      <div className="p-5 rounded-xl space-y-5">
        <div className="flex justify-between">
          <div className="h-4 bg-gray-200 rounded animate-pulse w-40" />
          <div className="w-5 h-5 bg-gray-200 rounded animate-pulse" />
        </div>
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded animate-pulse" />
          <div className="h-2 bg-gray-200 rounded animate-pulse" />
        </div>
        <div className="h-6 bg-gray-200 rounded animate-pulse" />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="p-5 rounded-xl bg-white border border-red-200">
        <p className="text-red-600 text-sm">
          Failed to load decision data: {error}
        </p>
      </div>
    );
  }

  // No data state
  if (confidence_gap === undefined || confidence_gap === null) {
    return (
      <div className="p-5 rounded-xl space-y-5 bg-gray-50">
        <div className="flex justify-between">
          <p className="font-bold uppercase text-sm">
            Decision Confidence Score
          </p>
          <ArrowDownRight />
        </div>
        <p className="text-gray-400 text-sm">Loading confidence analysis...</p>
      </div>
    );
  }

  return (
    <div className=" p-5 rounded-xl space-y-5">
      <div className="flex justify-between">
        <p className="font-bold uppercase text-sm">Decision Confidence Score</p>
        <ArrowDownRight />
      </div>

      <Bar label="Rational" value={Math.round((rational_pct ?? 0) * 100)} color="green" />
      <Bar label="Impulse" value={Math.round((behavioral_pct ?? 0) * 100)} color="orange" />

      <div className="bg-green-50 text-[#444] p-3 rounded-lg text-sm">
        <strong>Confidence Gap: {Math.round((confidence_gap ?? 0) * 100)}%</strong> –{" "}
        {`${bias_confidence} urgency `}
      </div>
    </div>
  );
}

function Bar({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: "green" | "orange";
}) {
  return (
    <div>
      <div className="flex justify-between text-sm">
        <span>{label}</span>
        <span>{value}%</span>
      </div>

      <div className="w-full bg-gray-100 h-2 rounded-full">
        <div
          className={`h-2 rounded-full bg-${color}-500`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}