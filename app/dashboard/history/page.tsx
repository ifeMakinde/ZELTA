"use client";

import React from "react";
import PageHeader from "@/components/PageHeader";
import { CheckCircle, XCircle, Clock } from "lucide-react";

// ─── Types ───────────────────────────────────────────────────────

type OutcomeStatus = "CORRECT" | "INCORRECT" | "TRACKING";

interface DecisionRecord {
  id: number;
  title: string;
  date: string;
  time: string;
  daysTracked: number;
  status: OutcomeStatus;
  verdict: string;
  amount: number;
  actualOutcome?: string;
}

// ─── Mock Data ───────────────────────────────────────────────────

const decisions: DecisionRecord[] = [
  {
    id: 1,
    title: "Side Hustle Reinvestment (Catering)",
    date: "Apr 12, 2026",
    time: "07:47 AM",
    daysTracked: 21,
    status: "CORRECT",
    verdict: "INVEST",
    amount: 15000,
    actualOutcome: "Returned ₦19,200 — 28% gain",
  },
  {
    id: 2,
    title: "Impulse Spend — Clothes",
    date: "Apr 5, 2026",
    time: "03:12 PM",
    daysTracked: 28,
    status: "INCORRECT",
    verdict: "HOLD",
    amount: 8500,
    actualOutcome: "Spent above budget by ₦3,400",
  },
  {
    id: 3,
    title: "Savings Lock — Hostel Fee",
    date: "Mar 28, 2026",
    time: "10:00 AM",
    daysTracked: 35,
    status: "CORRECT",
    verdict: "SAVE",
    amount: 20000,
    actualOutcome: "Reached goal 4 days early",
  },
  {
    id: 4,
    title: "Data Bundle Subscription",
    date: "Mar 20, 2026",
    time: "08:55 AM",
    daysTracked: 14,
    status: "TRACKING",
    verdict: "HOLD",
    amount: 3200,
  },
  {
    id: 5,
    title: "Reselling (Electronics)",
    date: "Mar 10, 2026",
    time: "02:30 PM",
    daysTracked: 52,
    status: "CORRECT",
    verdict: "INVEST",
    amount: 12000,
    actualOutcome: "Net ₦4,800 profit after expenses",
  },
];

// ─── Performance Stats ────────────────────────────────────────────

const totalDecisions = decisions.length;
const correctDecisions = decisions.filter((d) => d.status === "CORRECT").length;
const zeltaAccuracy = Math.round((correctDecisions / totalDecisions) * 100);
const avgDecisionScore = 1.72;
const valueProtected = 23900;

// ─── Sub-components ───────────────────────────────────────────────

function StatusBadge({ status }: { status: OutcomeStatus }) {
  if (status === "CORRECT") {
    return (
      <span className="flex items-center gap-1.5 rounded-full bg-green-100 px-3 py-1 text-xs font-bold text-green-700">
        <CheckCircle className="h-3.5 w-3.5" />
        CORRECT
      </span>
    );
  }
  if (status === "INCORRECT") {
    return (
      <span className="flex items-center gap-1.5 rounded-full bg-red-100 px-3 py-1 text-xs font-bold text-red-600">
        <XCircle className="h-3.5 w-3.5" />
        INCORRECT
      </span>
    );
  }
  return (
    <span className="flex items-center gap-1.5 rounded-full bg-orange-100 px-3 py-1 text-xs font-bold text-orange-600">
      <Clock className="h-3.5 w-3.5" />
      TRACKING
    </span>
  );
}

function VerdictPill({ verdict }: { verdict: string }) {
  const colors: Record<string, string> = {
    INVEST: "bg-green-50 text-green-700",
    SAVE: "bg-blue-50 text-blue-700",
    HOLD: "bg-gray-100 text-gray-600",
  };
  return (
    <span
      className={`rounded-md px-2 py-0.5 text-xs font-semibold ${colors[verdict] ?? "bg-gray-100 text-gray-500"}`}
    >
      {verdict}
    </span>
  );
}

function StatusIcon({ status }: { status: OutcomeStatus }) {
  if (status === "CORRECT")
    return (
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-green-100">
        <CheckCircle className="h-5 w-5 text-green-500" />
      </div>
    );
  if (status === "INCORRECT")
    return (
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-red-100">
        <XCircle className="h-5 w-5 text-red-500" />
      </div>
    );
  return (
    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-orange-100">
      <Clock className="h-5 w-5 text-orange-500" />
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────

export default function DecisionHistoryPage() {
  return (
    <div className="pb-10">
      <PageHeader
        title="Decision History"
        description="Every ZELTA recommendation logged with outcome tracking"
      />

      {/* BQ Performance Card */}
      <div className="mt-6 rounded-2xl bg-green-50 p-5 lg:p-6">
        <h2 className="mb-5 font-bold text-gray-800">Your BQ Performance</h2>

        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          <StatCard label="Total Decisions" value={String(totalDecisions)} />
          <StatCard
            label="ZELTA Accuracy"
            value={`${zeltaAccuracy}%`}
            valueColor="text-[#10b981]"
          />
          <StatCard
            label="Avg Decision Score"
            value={`${avgDecisionScore}/5.0`}
          />
          <StatCard
            label="Value Protected"
            value={`₦${valueProtected.toLocaleString()}`}
            valueColor="text-[#10b981]"
          />
        </div>
      </div>

      {/* Timeline */}
      <div className="mt-8">
        <h2 className="mb-4 text-xl font-bold text-gray-800">Timeline</h2>

        <div className="space-y-3">
          {decisions.map((decision) => (
            <div
              key={decision.id}
              className="flex items-start gap-4 rounded-2xl bg-green-50 p-4 lg:p-5"
            >
              <StatusIcon status={decision.status} />

              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <h3 className="font-semibold text-gray-900 text-sm lg:text-base">
                      {decision.title}
                    </h3>
                    <p className="mt-0.5 text-xs text-gray-500">
                      {decision.date} • {decision.time}
                    </p>
                  </div>
                  <div className="flex shrink-0 flex-col items-end gap-1.5">
                    <StatusBadge status={decision.status} />
                    <span className="text-xs text-gray-400">
                      {decision.daysTracked} days tracked
                    </span>
                  </div>
                </div>

                <div className="mt-3 flex flex-wrap items-center gap-3">
                  <VerdictPill verdict={decision.verdict} />
                  <span className="text-sm font-semibold text-gray-800">
                    ₦{decision.amount.toLocaleString()}
                  </span>
                  {decision.actualOutcome && (
                    <span className="text-xs text-gray-500">
                      → {decision.actualOutcome}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  valueColor = "text-gray-900",
}: {
  label: string;
  value: string;
  valueColor?: string;
}) {
  return (
    <div className="rounded-2xl bg-white p-4">
      <p className="text-xs text-gray-500">{label}</p>
      <p className={`mt-1 text-xl font-bold lg:text-2xl ${valueColor}`}>
        {value}
      </p>
    </div>
  );
}