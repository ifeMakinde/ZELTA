"use client";

import { Brain, MessageSquare } from "lucide-react";
import {
  useBehavioralDataContext,
} from "@/context/BehavioralSnapshotContext";
import { DEFAULT_BEHAVIORAL_SNAPSHOT } from "@/hooks/zelta";
import { LoadingState } from "@/components/ui/State";

export default function Zelta() {
  const { snapshot, loading } = useBehavioralDataContext();
  const data = snapshot ?? DEFAULT_BEHAVIORAL_SNAPSHOT;

  if (loading) return <LoadingState text="Loading ZELTA recommendation..." />;

  const showBiasTag =
    !!data.active_bias && data.active_bias.toLowerCase() !== "none";

  return (
    <div className="relative mt-3 rounded-2xl border border-green-400/30 bg-green-50 p-5 lg:ml-5">
      <div className="ml-0 flex items-center gap-2 lg:ml-2">
        <Brain className="mt-1 h-4 w-4 text-green-400" />
        <h2 className="text-lg font-bold text-gray-800">
          ZELTA Recommendation
        </h2>
      </div>

      <p className="mt-2 pr-4 text-sm text-gray-500 lg:ml-7">
        {data.recommendation ||
          "Your behavioral patterns are being monitored. ZELTA will provide personalized recommendations based on your decision-making trends."}
      </p>

      <div className="mt-4 flex flex-wrap gap-2 lg:ml-7">
        <div className="flex h-6 w-auto items-center rounded-full bg-green-100 px-3 text-sm font-bold text-green-400">
          Bayse-Aware Decisions
        </div>

        <div className="flex h-6 w-auto items-center rounded-full bg-green-100 px-3 text-sm font-bold text-green-400">
          24-Hour Rule
        </div>

        {showBiasTag && (
          <div className="flex h-6 w-auto items-center rounded-full bg-green-100 px-3 text-sm font-bold text-green-400">
            {data.active_bias} Management
          </div>
        )}
      </div>

      <button className="fixed bottom-10 right-5 z-50 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500 shadow-lg lg:right-10 lg:h-14 lg:w-14">
        <MessageSquare className="h-4 w-4 text-white lg:h-5 lg:w-5" />
      </button>
    </div>
  );
}