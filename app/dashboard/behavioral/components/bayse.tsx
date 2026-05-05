"use client";

import { Activity } from "lucide-react";
import {
  useBehavioralDataContext,
} from "@/context/BehavioralSnapshotContext";
import { DEFAULT_BEHAVIORAL_SNAPSHOT } from "@/hooks/zelta";
import { LoadingState } from "@/components/ui/State";

export default function Bayse() {
  const { snapshot, loading } = useBehavioralDataContext();
  const data = snapshot ?? DEFAULT_BEHAVIORAL_SNAPSHOT;

  if (loading) return <LoadingState text="Loading Bayse snapshot..." />;

  const crowdFear = Math.round(Number(data.bayse_crowd_fear ?? 0) * 100);
  const zeltaModel = Math.round(Number(data.bayse_zelta_model ?? 0) * 100);
  const gapRaw = Number(data.bayse_gap ?? 0);
  const gap = Math.round(Math.abs(gapRaw) * 100);

  const comparison =
    crowdFear > zeltaModel
      ? "more fearful"
      : crowdFear < zeltaModel
        ? "less fearful"
        : "exactly aligned with";

  return (
    <section className="mt-5 w-full rounded-2xl bg-white p-5 shadow-sm lg:p-6">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-orange-200">
          <Activity className="h-5 w-5 text-orange-400" />
        </div>

        <div className="w-full">
          <h2 className="text-lg font-bold text-gray-800">
            Bayse vs ZELTA Model
          </h2>

          <div className="mt-4 flex flex-col gap-6 sm:flex-row sm:gap-10">
            <div>
              <p className="text-sm font-light text-gray-500">Bayse Crowd Fear</p>
              <p className="text-3xl font-bold text-orange-400">{crowdFear}%</p>
            </div>

            <div>
              <p className="text-sm font-light text-gray-500">
                ZELTA Relational Model
              </p>
              <p className="text-3xl font-bold text-green-500">{zeltaModel}%</p>
            </div>
          </div>

          <p className="mt-4 text-sm text-gray-500">
            The Bayse crowd was {gap}% {comparison} the data warranted. This is
            the behavioral panic gap that ZELTA corrects.
          </p>
        </div>
      </div>
    </section>
  );
}