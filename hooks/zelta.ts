"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { apiFetch } from "@/hooks/useFetch";
import type {
  BrainData,
  IntelligenceData,
  StressData,
  MarketsData,
  BayseStressData,
  BayseSentimentData,
  BayseSignalsData,
  BehavioralSnapshot,
  BehavioralPattern,
  SideHustleSimRequest,
  SavingsSimRequest,
  SimulationResponse,
  WalletSummary,
  CopilotRequest,
  CopilotResponse,
  UserProfile,
  PortfolioSummary,
  ProfileResponse,
  PortfolioResponse,
  LogDecisionRequest,
  UpdateOutcomeRequest,
  UpdateProfileRequest,
} from "@/types/zelta";

// --- DEVTOOLS DEBUGGER SETUP ---
declare global {
  interface Window {
    __ZELTA_DEBUG__: {
      state: Record<string, any>;
      enableLogs: () => void;
      disableLogs: () => void;
      logHistory: Array<{ timestamp: Date; hook: string; state: any }>;
    };
  }
}

if (typeof window !== "undefined" && !window.__ZELTA_DEBUG__) {
  window.__ZELTA_DEBUG__ = {
    state: {},
    logHistory: [],
    enableLogs: () => {
      localStorage.setItem("ZELTA_DEBUG_LOGS", "true");
      console.log("%c[Zelta Debug] Console logging enabled.", "color: #00ff00");
    },
    disableLogs: () => {
      localStorage.removeItem("ZELTA_DEBUG_LOGS");
      console.log("%c[Zelta Debug] Console logging disabled.", "color: #ff0000");
    },
  };
}

const trackDebugState = (hookName: string, state: any) => {
  if (typeof window === "undefined") return;

  window.__ZELTA_DEBUG__.state[hookName] = state;
  window.__ZELTA_DEBUG__.logHistory.push({
    timestamp: new Date(),
    hook: hookName,
    state: { ...state },
  });

  if (window.__ZELTA_DEBUG__.logHistory.length > 200) {
    window.__ZELTA_DEBUG__.logHistory.shift();
  }

  if (localStorage.getItem("ZELTA_DEBUG_LOGS") === "true") {
    console.log(`%c[Zelta Debug] %c${hookName} updated:`, "color: #00aaff; font-weight: bold", "color: inherit", state);
  }
};
// -------------------------------

interface HookState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

function useAsyncData<T>(
  fetcher: () => Promise<T>,
  debugKey?: string
): HookState<T> & { refetch: () => void } {
  const [state, setState] = useState<HookState<T>>({
    data: null,
    loading: true,
    error: null,
  });

  const fetcherRef = useRef(fetcher);
  const mountedRef = useRef(true);

  useEffect(() => {
    if (debugKey) trackDebugState(debugKey, state);
  }, [state, debugKey]);

  useEffect(() => {
    fetcherRef.current = fetcher;
  }, [fetcher]);

  const run = useCallback(async () => {
    if (!mountedRef.current) return;

    setState((s) => ({ ...s, loading: true, error: null }));

    try {
      const data = await fetcherRef.current();

      if (data === null || data === undefined) {
        throw new Error("Empty response from API");
      }

      if (mountedRef.current) {
        setState({ data, loading: false, error: null });
      }
    } catch (err) {
      if (mountedRef.current) {
        setState({
          data: null,
          loading: false,
          error: (err as Error).message,
        });
      }
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    run();

    return () => {
      mountedRef.current = false;
    };
  }, [run]);

  return { ...state, refetch: run };
}

// --- NORMALIZERS ---

function normalizeBehavioralSnapshot(input: unknown): BehavioralSnapshot | null {
  if (!input || typeof input !== "object") return null;
  const raw = input as Record<string, any>;
  
  // Checks if data is at root or wrapped in a standard payload key
  if ("active_bias" in raw) return input as BehavioralSnapshot;

  const candidate = raw.data ?? raw.snapshot ?? raw.result ?? raw.payload ?? null;
  return candidate as BehavioralSnapshot;
}

function normalizeBehavioralPattern(input: unknown): BehavioralPattern | null {
  if (!input || typeof input !== "object") return null;
  const raw = input as Record<string, any>;
  
  if ("weeks" in raw) return input as BehavioralPattern;

  const candidate = raw.data ?? raw.result ?? raw.payload ?? null;
  return candidate as BehavioralPattern;
}

// --- DEFAULTS ---

export const DEFAULT_BEHAVIORAL_SNAPSHOT: BehavioralSnapshot = {
  active_bias: "None",
  confidence: "Unknown",
  explanation: "No behavioral data available.",
  bayse_crowd_fear: 0,
  bayse_zelta_model: 0,
  bayse_gap: 0,
  bayse_market_title: "",
  rational_pct: 0,
  behavioral_pct: 0,
  decision_gap: 0,
  confidence_score: 0,
  confidence_tier: "Low",
  intervention_urgency: "LOW",
  decision_plain_english: "No snapshot data.",
  bias_strength_label: "LOW",
  bias_strength_value: 0,
  evidence: [],
  tracked_biases: [],
  instinct_says: { action: "", amount: 0 },
  math_says: { action: "", amount: 0 },
  correction_value: 0,
  correction_plain: "No correction available.",
  recommendation: "No recommendation available.",
};

export const DEFAULT_BEHAVIORAL_PATTERN: BehavioralPattern = {
  weeks: [],
  dominant_bias: "None",
  summary: "No behavioral history yet.",
  recommendation: "Log decisions to build your pattern.",
  confidence_gap: 0,
};

// --- FETCHERS ---

export async function fetchBehavioralSnapshot(): Promise<BehavioralSnapshot> {
  const response = await apiFetch<unknown>("/api/behavioral/snapshot");
  const snapshot = normalizeBehavioralSnapshot(response);
  if (!snapshot) throw new Error("Could not parse snapshot data structure");
  return snapshot;
}

export async function fetchBehavioralPattern(): Promise<BehavioralPattern> {
  const response = await apiFetch<unknown>("/api/behavioral/pattern");
  const pattern = normalizeBehavioralPattern(response);
  if (!pattern) throw new Error("Could not parse pattern data structure");
  return pattern;
}

// --- HOOKS ---

export function useBrain(): HookState<BrainData> & {
  refetch: (force?: boolean) => void;
} {
  const cacheRef = useRef<{ data: BrainData | null; ts: number }>({ data: null, ts: 0 });
  const [state, setState] = useState<HookState<BrainData>>({
    data: cacheRef.current.data,
    loading: !cacheRef.current.data,
    error: null,
  });

  const BRAIN_TTL = 30_000;

  useEffect(() => {
    trackDebugState("useBrain", state);
  }, [state]);

  const fetch = useCallback(async (force = false) => {
    const now = Date.now();
    if (!force && cacheRef.current.data && now - cacheRef.current.ts < BRAIN_TTL) {
      setState({ data: cacheRef.current.data, loading: false, error: null });
      return;
    }

    setState((s) => ({ ...s, loading: true, error: null }));

    try {
      const data = await apiFetch<BrainData>("/api/brain");
      cacheRef.current.data = data;
      cacheRef.current.ts = Date.now();
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { ...state, refetch: fetch };
}

export function useIntelligence() {
  return useAsyncData<IntelligenceData>(() => apiFetch("/api/intelligence"), "useIntelligence");
}

export function useStress(pollInterval = 0): HookState<StressData> {
  const [state, setState] = useState<HookState<StressData>>({
    data: null,
    loading: true,
    error: null,
  });
  const activeRef = useRef(true);
  const abortControllerRef = useRef<AbortController | null>(null);
  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    trackDebugState("useStress", state);
  }, [state]);

  useEffect(() => {
    activeRef.current = true;

    const run = async () => {
      try {
        abortControllerRef.current = new AbortController();
        const data = await apiFetch<StressData>("/api/stress");
        if (activeRef.current) setState({ data, loading: false, error: null });
      } catch (err) {
        if (activeRef.current && !(err as Error).message.includes("aborted")) {
          setState({
            data: null,
            loading: false,
            error: (err as Error).message,
          });
        }
      }
    };

    run();

    if (pollInterval > 0) {
      intervalRef.current = window.setInterval(run, pollInterval);
    }

    return () => {
      activeRef.current = false;
      abortControllerRef.current?.abort();
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [pollInterval]);

  return state;
}

export function useBayseMarkets() {
  return useAsyncData<MarketsData>(() => apiFetch("/api/bayse/markets"), "useBayseMarkets");
}

export function useBayseSignals(): HookState<BayseSignalsData> & {
  refetch: () => void;
} {
  const [state, setState] = useState<HookState<BayseSignalsData>>({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    trackDebugState("useBayseSignals", state);
  }, [state]);

  const fetch = useCallback(async () => {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const [stress, sentiment] = await Promise.all([
        apiFetch<BayseStressData>("/api/bayse/stress"),
        apiFetch<BayseSentimentData>("/api/bayse/sentiment"),
      ]);
      setState({ data: { stress, sentiment }, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { ...state, refetch: fetch };
}

export function useBehavioralSnapshot() {
  return useAsyncData<BehavioralSnapshot>(fetchBehavioralSnapshot, "useBehavioralSnapshot");
}

export function useBehavioralPattern() {
  return useAsyncData<BehavioralPattern>(fetchBehavioralPattern, "useBehavioralPattern");
}

export function useWallet() {
  return useAsyncData<WalletSummary>(() => apiFetch<WalletSummary>("/api/wallet"), "useWallet");
}

export function useCopilot() {
  const [state, setState] = useState<HookState<CopilotResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  useEffect(() => {
    trackDebugState("useCopilot", state);
  }, [state]);

  const runCopilot = useCallback(async (request: CopilotRequest) => {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const data = await apiFetch<CopilotResponse>("/api/copilot", {
        method: "POST",
        body: JSON.stringify(request),
      });
      setState({ data, loading: false, error: null });
      return data;
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
      return null;
    }
  }, []);

  return { ...state, runCopilot };
}

export function useSideHustleSimulation() {
  const [state, setState] = useState<HookState<SimulationResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  useEffect(() => {
    trackDebugState("useSideHustleSimulation", state);
  }, [state]);

  const runSimulation = useCallback(async (request: SideHustleSimRequest) => {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const data = await apiFetch<SimulationResponse>("/api/simulation/side-hustle", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      });
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, []);

  return { ...state, runSimulation };
}

export function useSavingsSimulation() {
  const [state, setState] = useState<HookState<SimulationResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  useEffect(() => {
    trackDebugState("useSavingsSimulation", state);
  }, [state]);

  const runSimulation = useCallback(async (request: SavingsSimRequest) => {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const data = await apiFetch<SimulationResponse>("/api/simulation/savings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      });
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
  }, []);

  return { ...state, runSimulation };
}

export function useProfile() {
  return useAsyncData<UserProfile>(
    () => apiFetch<ProfileResponse>("/api/profile").then((res) => res.data),
    "useProfile"
  );
}

export function useUpdateProfile() {
  const [state, setState] = useState<HookState<UserProfile>>({
    data: null,
    loading: false,
    error: null,
  });

  useEffect(() => {
    trackDebugState("useUpdateProfile", state);
  }, [state]);

  const updateProfile = useCallback(async (updates: UpdateProfileRequest) => {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const response = await apiFetch<ProfileResponse>("/api/profile", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates),
      });
      setState({ data: response.data, loading: false, error: null });
      return response.data;
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
      return null;
    }
  }, []);

  return { ...state, updateProfile };
}

export function usePortfolio() {
  return useAsyncData<PortfolioSummary>(
    () => apiFetch<PortfolioResponse>("/api/portfolio").then((res) => res.data),
    "usePortfolio"
  );
}

export function useLogDecision() {
  const [state, setState] = useState<HookState<any>>({
    data: null,
    loading: false,
    error: null,
  });

  useEffect(() => {
    trackDebugState("useLogDecision", state);
  }, [state]);

  const logDecision = useCallback(async (decision: LogDecisionRequest) => {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const data = await apiFetch<any>("/api/portfolio/decisions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(decision),
      });
      setState({ data, loading: false, error: null });
      return data;
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
      return null;
    }
  }, []);

  return { ...state, logDecision };
}

export function useRecordOutcome() {
  const [state, setState] = useState<HookState<any>>({
    data: null,
    loading: false,
    error: null,
  });

  useEffect(() => {
    trackDebugState("useRecordOutcome", state);
  }, [state]);

  const recordOutcome = useCallback(async (outcome: UpdateOutcomeRequest) => {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const data = await apiFetch<any>("/api/portfolio/decisions/outcome", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(outcome),
      });
      setState({ data, loading: false, error: null });
      return data;
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
      return null;
    }
  }, []);

  return { ...state, recordOutcome };
}