"use client";

import { Target } from "lucide-react";
import Button from "@/components/Button";
import { useRouter } from "next/navigation";
// import { Verdict } from "@/types/zelta";

interface VerdictProp {
  invest_ngn: number;
  save_ngn?: number;
  hold_ngn?: number;
  allocation_plain: string;
}

export default function WeeklyVerdictCard({
  invest_ngn,
  save_ngn,
  hold_ngn,
  allocation_plain,
}: VerdictProp) {
  const navigate = useRouter();
  return (
    <div className="bg-green-500 text-white p-6 rounded-xl space-y-5 ">
      <div className="flex gap-3">
        <Target />

        <div>
          <h2 className="font-bold uppercase">ZELTA Weekly Verdict</h2>
          <p className="text-sm opacity-80">
            Based on Bayse + Bayesian + Kelly model
          </p>
        </div>
      </div>

      <div>
        <p className="text-sm uppercase opacity-80">Recommendation</p>

        <h3 className="text-2xl lg:text-5xl font-bold">Invest ₦{invest_ngn}</h3>

        <p className="text-sm mt-2 opacity-90">
          {allocation_plain}
          {/* Adjusted for your stress level and market conditions. */}
        </p>
      </div>

      <div className="flex gap-3">
        <Stat title="Save" value={`₦${save_ngn}`} />
        <Stat title="Hold Cash" value={`₦${hold_ngn}`} />
      </div>

      <Button
        className="w-full bg-white p-2 text-green-700 rounded-lg "
        onClick={() => {
          navigate.push("/dashboard/wallet");
        }}
      >
        Run Full Simulation
      </Button>
    </div>
  );
}

function Stat({ title, value }: { title: string; value: string }) {
  return (
    <div className="flex-1 border border-white/40 p-3 rounded-lg">
      <p className="text-xs uppercase">{title}</p>
      <p className="font-bold">{value}</p>
    </div>
  );
}
