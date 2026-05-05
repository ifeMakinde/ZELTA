"use client";

import { createContext, useContext, type ReactNode, useMemo, useCallback } from "react";
import {
  useBrain,
  useIntelligence,
  useStress,
  useBayseMarkets,
  useBayseSignals,
  useProfile,
} from "@/hooks/zelta";
import type {
  BrainData,
  IntelligenceData,
  StressData,
  MarketsData,
  BayseSignalsData,
  UserProfile,
} from "@/types/zelta";

// ─── context shape ───────────────────────────────────────────────

interface HookResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface ZeltaContextValue {
  brain: HookResult<BrainData> & { refetch: (force?: boolean) => void };
  intelligence: HookResult<IntelligenceData> & { refetch: () => void };
  stress: HookResult<StressData>;
  markets: HookResult<MarketsData> & { refetch: () => void };
  bayse: HookResult<BayseSignalsData> & { refetch: () => void };
  profile: HookResult<UserProfile> & { refetch: () => void };
  // Global state
  globalError: string | null;
  globalLoading: boolean;
  retryAll: () => void;
}

const ZeltaContext = createContext<ZeltaContextValue | null>(null);

// ─── provider ────────────────────────────────────────────────────

export function ZeltaProvider({ children }: { children: ReactNode }) {
  const brain = useBrain();
  const intelligence = useIntelligence();
  const stress = useStress();
  const markets = useBayseMarkets();
  const bayse = useBayseSignals();
  const profile = useProfile();

  // Compute global state
  const globalError = useMemo(() => {
    return (
      brain.error ||
      intelligence.error ||
      stress.error ||
      markets.error ||
      bayse.error ||
      null
    );
  }, [brain.error, intelligence.error, stress.error, markets.error, bayse.error]);

  const globalLoading = useMemo(() => {
    return (
      brain.loading ||
      intelligence.loading ||
      stress.loading ||
      markets.loading ||
      bayse.loading
    );
  }, [brain.loading, intelligence.loading, stress.loading, markets.loading, bayse.loading]);

  // Retry all failed requests
  const retryAll = useCallback(() => {
    if (brain.error) brain.refetch(true);
    if (intelligence.error) intelligence.refetch();
    if (stress.error) {
      // stress doesn't have manual refetch, it's automatic
    }
    if (markets.error) markets.refetch();
    if (bayse.error) bayse.refetch();
  }, [brain, intelligence, stress, markets, bayse]);

  const value = useMemo(
    () => ({
      brain,
      intelligence,
      stress,
      markets,
      bayse,
      profile,
      globalError,
      globalLoading,
      retryAll,
    }),
    [brain, intelligence, stress, markets, bayse, profile, globalError, globalLoading, retryAll]
  );

  return (
    <ZeltaContext.Provider value={value}>
      {children}
    </ZeltaContext.Provider>
  );
}

// ─── consumer hook ───────────────────────────────────────────────

export function useZelta(): ZeltaContextValue {
  const context = useContext(ZeltaContext);
  if (!context) throw new Error("useZelta must be used inside <ZeltaProvider>");
  return context;
}