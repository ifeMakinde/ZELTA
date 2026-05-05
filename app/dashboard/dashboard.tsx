"use client";
import { useSearchParams } from "next/navigation";
import { useState } from "react";
import PageHeader from "@/components/PageHeader";
import ErrorBanner from "@/components/ErrorBanner";
import DashboardOverlay from "@/components/DashboardOverlay";
import BiasAlertCard from "@/app/dashboard/BiasAlertCard";
import MarketAlert from "@/app/dashboard/MarketAlert";
import WeeklyVerdictCard from "@/app/dashboard/WeeklyVerdictCard";
import DecisionScoreCard from "./DecisionScoreCard";
import StressIndexCard from "./StressIndexCard";
import { useZelta } from "@/context/zeltaContext";
import { useProfile } from "@/hooks/zelta";

const hour = new Date().getHours();
const greeting = hour < 12 ? "Good Morning" : hour < 17 ? "Good Afternoon" : "Good Evening";

function Dashboard() {
  const { intelligence, globalError, globalLoading, retryAll } = useZelta();
  const profile = useProfile();
  const [errorDismissed, setErrorDismissed] = useState(false);

  const {
    stress_index,
    stress_level,
    bias_explanation,
    confidence_gap,
    crowd_yes,
    bayse_market,
    market_probability,
    bias_confidence,
    rational_pct,
    behavioral_pct,
    invest_ngn,
    save_ngn,
    hold_ngn,
    allocation_plain,
  } = intelligence.data || {};

  // Name: prefer profile API → Firebase display name → fallback
  const displayName = profile.data?.name || "there";

  return (
    <>
      {/* Global error banner */}
      {globalError && !errorDismissed && (
        <ErrorBanner
          error={globalError}
          onRetry={retryAll}
          onDismiss={() => setErrorDismissed(true)}
          autoHideDuration={0} // Stay until user dismisses or retries
        />
      )}

      {/* Dashboard blur overlay while loading */}
      <DashboardOverlay
        show={globalLoading && !intelligence.data}
        message="Loading your dashboard..."
      />

      <section className="space-y-6">
        <PageHeader
          title={`${greeting}, ${displayName}`}
          description="here's your financial intelligence for today"
        />

        <main className="pb-8 space-y-3">
          {/*  DASHBOARD HOMEPAGE WIWDGET 1 */}
          <MarketAlert
            crowd_yes={crowd_yes}
            bayse_market={bayse_market}
            loading={intelligence.loading}
            error={null}
          />
          {/*  DASHBOARD HOMEPAGE WIWDGET 2 */}

          {/*  DASHBOARD HOMEPAGE WIWDGET 3 */}
          <StressIndexCard
            stress_index={stress_index}
            stress_level={stress_level}
            crowd_yes={crowd_yes}
            market_probability={market_probability}
            loading={intelligence.loading}
            error={null}
          />

          {/* DASHBOARD HOME WODGET 4 */}
          <BiasAlertCard
            bias_explanation={bias_explanation}
            loading={intelligence.loading}
            error={null}
          />

          {/* DASHBOARD HOME 5 */}
          <DecisionScoreCard
            confidence_gap={confidence_gap}
            bias_confidence={bias_confidence}
            rational_pct={rational_pct}
            behavioral_pct={behavioral_pct}
            loading={intelligence.loading}
            error={null}
          />

          <WeeklyVerdictCard
            invest_ngn={invest_ngn ?? 0}
            save_ngn={save_ngn}
            hold_ngn={hold_ngn}
            allocation_plain={allocation_plain ?? ""}
          />
        </main>
      </section>
    </>
  );
}

export default Dashboard;