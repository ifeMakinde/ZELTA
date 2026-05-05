"use client";

import {
  useBehavioralDataContext,
} from "@/context/BehavioralSnapshotContext";
import { DEFAULT_BEHAVIORAL_PATTERN } from "@/hooks/zelta";
import { LoadingState } from "@/components/ui/State";

export default function Weeks() {
  const { pattern, loading } = useBehavioralDataContext();
  const data = pattern ?? DEFAULT_BEHAVIORAL_PATTERN;

  if (loading) return <LoadingState text="Loading 8-week pattern..." />;

  const weeks = Array.isArray(data.weeks) ? data.weeks : [];

  const getBgColor = (bias: string) => {
    switch (bias.toLowerCase()) {
      case "loss aversion":
      case "present bias":
      case "herd behavior":
      case "overconfidence":
        return "bg-orange-400";
      case "none":
        return "bg-emerald-500";
      default:
        return "bg-gray-400";
    }
  };

  return (
    <div className="mt-3 w-full rounded-2xl border border-gray-100 bg-white p-5 lg:ml-5">
      <h1 className="text-2xl font-bold text-gray-800">
        8-Week Behavioral Pattern
      </h1>

      {weeks.length === 0 ? (
        <div className="mt-6 rounded-2xl bg-gray-50 p-5 text-sm text-gray-500">
          No weekly pattern data yet. ZELTA will show the last 8 weeks here once enough history is available.
        </div>
      ) : (
        <section className="mt-6 space-y-4">
          {weeks.slice(0, 8).map((weekData, index) => {
            const strengthPct = Math.round((weekData.strength ?? 0) * 100);
            return (
            <div key={index} className="flex items-center gap-3">
              <h3 className="w-14 shrink-0 text-sm text-gray-500">
                Week {weekData.week}
              </h3>

              <div className="h-10 flex-1 overflow-hidden rounded-full bg-gray-100">
                <div
                  className={`flex h-full items-center rounded-full text-sm font-bold text-white ${getBgColor(
                    weekData.bias,
                  )}`}
                  style={{ width: `${Math.max(strengthPct, 8)}%` }}
                >
                  <span className="ml-3 whitespace-nowrap text-xs">{weekData.bias}</span>
                </div>
              </div>

              <p className="shrink-0 text-sm font-bold text-gray-800">
                {strengthPct}%
              </p>
            </div>
            );
          })}
        </section>
      )}
    </div>
  );
}