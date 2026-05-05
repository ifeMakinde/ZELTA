"use client";
import { StressLevel } from "@/types/zelta";
import { TrendingDown } from "lucide-react";

interface StressIndexCardProps {
  stress_index?: number;
  stress_level?: StressLevel;
  stress_label?: string;
  crowd_yes?: number;       // 0-1 decimal from IntelligenceData
  market_probability?: number; // 0-1 decimal
  bayse_primary?: number;   // 0-1 decimal
  loading?: boolean;
  error?: string | null;
}

function safeNum(v: number | undefined | null): number {
  const n = Number(v);
  return isNaN(n) ? 0 : n;
}

function pct(v: number | undefined | null): number {
  return Math.round(safeNum(v) * 100);
}

export default function StressIndexCard({
  stress_index,
  stress_level,
  stress_label,
  crowd_yes,
  market_probability,
  bayse_primary,
  loading = false,
  error = null,
}: StressIndexCardProps) {
  if (loading) {
    return (
      <div className="bg-white p-5 rounded-xl space-y-4 shadow-sm animate-pulse">
        <div className="flex justify-between">
          <div className="h-4 bg-gray-200 rounded w-40" />
          <div className="h-9 w-9 bg-gray-200 rounded-lg" />
        </div>
        <div className="h-8 bg-gray-200 rounded w-24" />
        <div className="h-6 bg-gray-200 rounded w-16" />
        <div className="h-2 bg-gray-200 rounded-full w-full" />
        <div className="flex gap-3">
          <div className="flex-1 h-14 bg-gray-200 rounded-lg" />
          <div className="flex-1 h-14 bg-gray-200 rounded-lg" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white p-5 rounded-xl shadow-sm border border-red-200">
        <p className="text-red-600 text-sm">{error}</p>
      </div>
    );
  }

  if (stress_index === undefined || stress_index === null) {
    return (
      <div className="bg-white p-5 rounded-xl space-y-4 shadow-sm">
        <div className="flex justify-between">
          <p className="font-bold uppercase text-sm">Student Stress Index</p>
          <span className="p-2 bg-green-100 rounded-lg"><TrendingDown color="green" /></span>
        </div>
        <p className="text-gray-400 text-sm">Loading stress data...</p>
      </div>
    );
  }

  // stress_index from /api/intelligence is 0-1 → multiply by 100
  const stressDisplay = Math.round(safeNum(stress_index));

  // bayse_primary is 0-1
  const bayseSignalPct = pct(bayse_primary);

  // crowd_yes is 0-1 (crowd_yes_price from Bayse); fall back to bayse_primary
  const crowdDisplay = crowd_yes !== undefined ? pct(crowd_yes) : bayseSignalPct;

  // market_probability is 0-1; fall back to inverse of crowd
  const modelDisplay = market_probability !== undefined
    ? pct(market_probability)
    : Math.max(0, 100 - crowdDisplay);

  return (
    <div className="bg-white p-5 rounded-xl space-y-4 shadow-sm">
      <div className="flex justify-between items-center">
        <p className="font-bold uppercase text-sm">Student Stress Index</p>
        <span className="p-2 bg-green-100 rounded-lg">
          <TrendingDown color="green" />
        </span>
      </div>

      <h2 className="text-3xl font-bold text-green-500">{stressDisplay}/100</h2>

      {stress_level && (
        <span className="inline-block bg-green-50 text-green-600 px-3 py-1 rounded-lg text-sm font-medium">
          {stress_level}
        </span>
      )}

      <div className="p-2">
        <div className="flex justify-between text-sm mb-1">
          <span>Bayse Primary Signal</span>
          <span>{bayseSignalPct}%</span>
        </div>
        <progress
          value={stressDisplay}
          max={100}
          className="w-full h-2 rounded-full"
        />
      </div>

      {stress_label && (
        <p className="text-sm text-gray-500">{stress_label}</p>
      )}

      <div className="flex gap-3">
        <MiniStat title="Bayse Crowd" value={`${crowdDisplay}%`} color="orange" />
        <MiniStat title="Zelta Model" value={`${modelDisplay}%`} color="green" />
      </div>
    </div>
  );
}

function MiniStat({ title, value, color }: { title: string; value: string; color: "green" | "orange" }) {
  return (
    <div className="flex-1 p-3 bg-gray-50 rounded-lg">
      <p className="text-sm">{title}</p>
      <p className={`font-semibold text-${color}-500`}>{value}</p>
    </div>
  );
}