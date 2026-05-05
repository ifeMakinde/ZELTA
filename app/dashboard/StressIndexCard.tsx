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
      <div className="bg-white p-5 rounded-xl shadow-sm border border-red-200 ">
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

  return (
    <div className="bg-white p-5 rounded-xl space-y-5 shadow-sm">
      <div className="flex justify-between items-center">
        <p className="font-bold uppercase text-sm">Student Stress Index</p>

        <span className="p-2 bg-green-100 rounded-lg">
          <TrendingDown color="green" />
        </span>
      </div>

      <h2 className="text-3xl font-bold text-green-500">
        {` ${stress_index}/100`}
      </h2>

      <span className="bg-green-50 text-green-600 px-3 py-1 rounded-lg text-sm font-medium">
        {stress_level}
      </span>

      <div className="p-2">
        <div className="flex justify-between text-sm">
          <span>Bayse Primary Signal</span>
          <span>{stress_index}%</span>
        </div>

        <progress
          value={stress_index}
          max={100}
          className="w-full bg-transparent h-2 rounded-full"
        />
      </div>

      <p className="text-sm text-gray-500">
        {stress_label || "No signal available"}
      </p>

      <div className="flex gap-3">
        <MiniStat
          title="Bayse Crowd"
          value={`${Math.floor(crowd_yes ?? 0) * 100}%`}
          color="orange"
        />
        <MiniStat
          title="Zelta Model"
          value={`${Math.floor(market_probability ?? 0) * 100}%`}
          color="green"
        />
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
  return (
    <div className="flex-1 p-3 bg-gray-50 rounded-lg">
      <p className="text-sm">{title}</p>
      <p className={`font-semibold text-${color}-500`}>{value}</p>
    </div>
  );
}