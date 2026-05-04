"use client";

import React, { createContext, useContext, useCallback, useMemo } from "react";
import {
  DEFAULT_BEHAVIORAL_SNAPSHOT,
  DEFAULT_BEHAVIORAL_PATTERN,
  useBehavioralSnapshot,
  useBehavioralPattern,
} from "@/hooks/zelta";
import type {
  BehavioralSnapshot,
  BehavioralPattern,
} from "@/types/zelta";

type BehavioralDataContextValue = {
  snapshot: BehavioralSnapshot;
  pattern: BehavioralPattern;
  loading: boolean;
  error: string | null;
  refetch: () => void;
};

const BehavioralDataContext = createContext<
  BehavioralDataContextValue | undefined
>(undefined);

export function BehavioralDataProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const { 
    data: snapshotData, 
    loading: snapshotLoading, 
    error: snapshotError, 
    refetch: refetchSnapshot 
  } = useBehavioralSnapshot();

  const { 
    data: patternData, 
    loading: patternLoading, 
    error: patternError, 
    refetch: refetchPattern 
  } = useBehavioralPattern();

  // Combine refetch logic into a single stable function
  const refetch = useCallback(() => {
    refetchSnapshot();
    refetchPattern();
  }, [refetchSnapshot, refetchPattern]);

  // Memoize the value object to prevent consumers from re-rendering 
  // unless the actual data, loading state, or error state changes.
  const value = useMemo(() => ({
    snapshot: snapshotData ?? DEFAULT_BEHAVIORAL_SNAPSHOT,
    pattern: patternData ?? DEFAULT_BEHAVIORAL_PATTERN,
    loading: snapshotLoading || patternLoading,
    error: snapshotError || patternError,
    refetch,
  }), [
    snapshotData, 
    patternData, 
    snapshotLoading, 
    patternLoading, 
    snapshotError, 
    patternError, 
    refetch
  ]);

  return (
    <BehavioralDataContext.Provider value={value}>
      {children}
    </BehavioralDataContext.Provider>
  );
}

export function useBehavioralDataContext() {
  const context = useContext(BehavioralDataContext);

  if (!context) {
    throw new Error(
      "useBehavioralDataContext must be used inside BehavioralDataProvider",
    );
  }

  return context;
}