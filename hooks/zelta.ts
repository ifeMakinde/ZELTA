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
} from "@/types/zelta";

// ─── shared state shape ──────────────────────────────────────────
interface HookState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

// ─── generic one-shot fetch hook ────────────────────────────────
function useAsyncData<T>(
  fetcher: () => Promise<T>,
): HookState<T> & { refetch: () => void } {
  const [state, setState] = useState<HookState<T>>({
    data: null,
    loading: true,
    error: null,
  });

  const run = useCallback(async () => {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const data = await fetcher();
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message });
    }
    // fetcher is defined inline at call site — stable ref not needed
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    run();
  }, [run]);

  return { ...state, refetch: run };
}

// ─── /api/brain ──────────────────────────────────────────────────
// Cached for 30s per component instance. Call refetch(true) to force a fresh pull.
// Note: Cache is per-hook-instance, not global, to avoid user data leaks.

interface BrainCache {
  data: BrainData | null;
  ts: number;
}

const BRAIN_TTL = 30_000;

export function useBrain(): HookState<BrainData> & {
  refetch: (force?: boolean) => void;
} {
  const cacheRef = useRef<BrainCache>({ data: null, ts: 0 });
  const [state, setState] = useState<HookState<BrainData>>({
    data: cacheRef.current.data,
    loading: !cacheRef.current.data,
    error: null,
  });

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

// ─── /api/intelligence ───────────────────────────────────────────

export function useIntelligence() {
  return useAsyncData<IntelligenceData>(() => apiFetch("/api/intelligence"));
}

// ─── /api/stress ─────────────────────────────────────────────────
// Set pollInterval=0 to disable polling and fetch only once.
// Default 10s is for live header widget; most components should use pollInterval=0.

export function useStress(pollInterval = 0): HookState<StressData> {
  const [state, setState] = useState<HookState<StressData>>({
    data: null,
    loading: true,
    error: null,
  });
  const activeRef = useRef(true);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    activeRef.current = true;

    const run = async () => {
      try {
        abortControllerRef.current = new AbortController();
        const data = await apiFetch<StressData>("/api/stress");
        if (activeRef.current) setState({ data, loading: false, error: null });
      } catch (err) {
        if (activeRef.current && !(err as Error).message.includes("aborted"))
          setState({
            data: null,
            loading: false,
            error: (err as Error).message,
          });
      }
    };

    run();
    
    let interval: NodeJS.Timeout | null = null;
    if (pollInterval > 0) {
      interval = setInterval(run, pollInterval);
    }

    return () => {
      activeRef.current = false;
      abortControllerRef.current?.abort();
      if (interval) clearInterval(interval);
    };
  }, [pollInterval]);

  return state;
}

// ─── /api/bayse/markets ──────────────────────────────────────────

export function useBayseMarkets() {
  return useAsyncData<MarketsData>(() => apiFetch("/api/bayse/markets"));
}

// ─── /api/bayse/stress + /api/bayse/sentiment ────────────────────
// Fired in parallel — both are lightweight, no reason to waterfall

export function useBayseSignals(): HookState<BayseSignalsData> & {
  refetch: () => void;
} {
  const [state, setState] = useState<HookState<BayseSignalsData>>({
    data: null,
    loading: true,
    error: null,
  });

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
