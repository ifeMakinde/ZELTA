"use client";

import { MessageSquareQuote } from "lucide-react";
import { useBehavioralDataContext } from "@/context/BehavioralSnapshotContext";
import { DEFAULT_BEHAVIORAL_SNAPSHOT } from "@/hooks/zelta";
import { LoadingState } from "@/components/ui/State";

export default function Active() {
  const { snapshot, loading } = useBehavioralDataContext();
  const data = snapshot ?? DEFAULT_BEHAVIORAL_SNAPSHOT;

  if (loading) return <LoadingState text="Loading active bias..." />;

  const evidence = Array.isArray(data.evidence) ? data.evidence : [];

  const hasActiveBias =
    data.active_bias && data.active_bias.toLowerCase() !== "none";

  return (
    <div className="p-2 lg:p-0">
      <section className="mt-5 rounded-2xl bg-white pb-6 shadow-sm lg:pb-0">
        <div className="flex gap-3 px-4 pt-7 lg:px-7">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-orange-200">
            <MessageSquareQuote className="h-5 w-5 text-orange-400" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-gray-800">
              Active Bias Detected
            </h2>
            <p className="text-sm text-gray-500">
              Based on bias signals + wallet patterns
            </p>
          </div>
        </div>

        <div className="mx-auto mt-5 w-[94%] rounded-2xl bg-white pb-6 lg:mx-0 lg:ml-7 lg:pb-0">
          <h1 className="relative top-5 ml-5 text-3xl font-bold uppercase text-orange-400 lg:text-4xl">
            {hasActiveBias ? data.active_bias : "None"}
          </h1>

          <p className="mt-10 ml-5 pr-4 text-sm text-gray-500 lg:mt-7 lg:pr-0">
            {data.explanation || "No explanation available"}
          </p>

          <div className="mt-6 flex justify-between px-5 lg:mt-3 lg:justify-start lg:gap-40 lg:px-0">
            <p className="text-gray-500">Bias Strength</p>
            <p className="text-sm font-bold text-orange-400">
              {data.bias_strength_label || "LOW"}
            </p>
          </div>

          <div className="mx-auto mt-2 h-3 w-[90%] overflow-hidden rounded-full bg-green-100 lg:ml-5 lg:w-[94%]">
            <div
              className="h-3 rounded-full bg-[#10b981]"
              style={{
                width: `${Math.min(Math.max(data.bias_strength_value ?? 0, 0), 100)}%`,
              }}
            />
          </div>

          <div className="mx-auto mt-5 w-[92%] rounded-2xl border border-orange-400/30 bg-orange-200/20 pb-4 lg:ml-5 lg:mt-3 lg:w-[95%] lg:pb-0">
            <h2 className="ml-5 mt-5 text-sm font-bold text-gray-800">
              Evidence from Transactions
            </h2>

            <div className="mt-2 space-y-2">
              {evidence.length > 0 ? (
                evidence.map((item, index) => (
                  <div key={index} className="ml-5 flex gap-2">
                    <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 border-orange-300 text-orange-300">
                      <span className="text-sm leading-none">×</span>
                    </div>
                    <p className="text-sm text-gray-500">
                      {item.plain_english || "No explanation available"}
                    </p>
                  </div>
                ))
              ) : (
                <p className="ml-5 text-sm text-gray-500">
                  No evidence available
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="mx-auto mt-5 w-[94%] rounded-2xl bg-white p-5 lg:mx-0 lg:ml-7 lg:p-0">
          <h1 className="font-bold text-gray-800 lg:relative lg:top-2 lg:ml-5">
            ZELTA Correction Applied:
          </h1>
          <p className="mt-3 text-sm text-gray-500 lg:ml-5">
            {data.correction_plain || "No correction available."}
          </p>
        </div>
      </section>
    </div>
  );
}