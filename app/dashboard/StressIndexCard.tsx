"use client";
import { StressLevel } from "@/types/zelta";
import { TrendingDown } from "lucide-react";

interface StressIndexCardProps {
  stress_index?: number;
  stress_level?: StressLevel;
  stress_label?: string;
  crowd_yes?: number;
  market_probability?: number;
  loading?: boolean;
  error?: string | null;
}

export default function StressIndexCard({
  stress_index,
  stress_level,
  stress_label,
  crowd_yes,
  market_probability,
  loading = false,
  error = null,
}: StressIndexCardProps) {
  // Loading skeleton
  if (loading) {
    return (
      <div className="bg-white p-5 rounded-xl space-y-5 shadow-sm">
        <div className="flex justify-between items-center">
          <p className="font-bold uppercase text-sm">Student Stress Index</p>
          <span className="p-2 bg-gray-200 rounded-lg animate-pulse w-10 h-10" />
        </div>
        <div className="h-8 bg-gray-200 rounded animate-pulse" />
        <div className="h-6 bg-gray-200 rounded w-32 animate-pulse" />
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded animate-pulse" />
          <div className="h-2 bg-gray-200 rounded animate-pulse" />
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-white p-5 rounded-xl shadow-sm border border-red-200">
        <p className="text-red-600 text-sm">{error}</p>
      </div>
    );
  }

  // No data state
  if (stress_index === undefined || stress_index === null) {
    return (
      <div className="bg-white p-5 rounded-xl space-y-5 shadow-sm">
        <div className="flex justify-between items-center">
          <p className="font-bold uppercase text-sm">Student Stress Index</p>
          <span className="p-2 bg-green-100 rounded-lg">
            <TrendingDown color="green" />
          </span>
        </div>
        <p className="text-gray-400 text-sm">Loading data...</p>
      </div>
    );
  }

  // Determine stress colour based on level
  const stressColor =
    stress_level === "CRISIS"
      ? "text-red-500"
      : stress_level === "MODERATE"
      ? "text-yellow-500"
      : "text-green-500";

  const badgeBg =
    stress_level === "CRISIS"
      ? "bg-red-50 text-red-600"
      : stress_level === "MODERATE"
      ? "bg-yellow-50 text-yellow-600"
      : "bg-green-50 text-green-600";

  const barColor =
    stress_level === "CRISIS"
      ? "#ef4444"
      : stress_level === "MODERATE"
      ? "#eab308"
      : "#22c55e";

  // crowd_yes and market_probability are decimal fractions (0–1) from API
  const crowdPct = Math.round((crowd_yes ?? 0) * 100);
  const modelPct = Math.round((market_probability ?? 0) * 100);

  return (
    <div className="bg-white p-5 rounded-xl space-y-4 shadow-sm">
      <div className="flex justify-between items-center">
        <p className="font-bold uppercase text-sm">Student Stress Index</p>
        <span className="p-2 bg-green-100 rounded-lg">
          <TrendingDown color="green" />
        </span>
      </div>

      <h2 className={`text-3xl font-bold ${stressColor}`}>
        {stress_index}<span className="text-lg font-normal text-gray-400">/100</span>
      </h2>

      <span className={`inline-block px-3 py-1 rounded-lg text-sm font-medium ${badgeBg}`}>
        {stress_level ?? "UNKNOWN"}
      </span>

      {/* Progress bar */}
      <div className="space-y-1">
        <div className="flex justify-between text-sm text-gray-500">
          <span>Bayse Primary Signal</span>
          <span>{stress_index}%</span>
        </div>
        <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
          <div
            className="h-2 rounded-full transition-all duration-500"
            style={{ width: `${Math.min(stress_index, 100)}%`, backgroundColor: barColor }}
          />
        </div>
      </div>

      {stress_label && (
        <p className="text-sm text-gray-500">{stress_label}</p>
      )}

      <div className="flex gap-3">
        <MiniStat title="Bayse Crowd" value={`${crowdPct}%`} color="orange" />
        <MiniStat title="Zelta Model" value={`${modelPct}%`} color="green" />
      </div>
    </div>
  );
}

function MiniStat({
  title,
  value,
  color,
}: {
  title: string;
  value: string;
  color: "green" | "orange";
}) {
  const textColor = color === "green" ? "text-green-500" : "text-orange-500";
  return (
    <div className="flex-1 p-3 bg-gray-50 rounded-lg">
      <p className="text-xs text-gray-500">{title}</p>
      <p className={`font-semibold ${textColor}`}>{value}</p>
    </div>
  );
}