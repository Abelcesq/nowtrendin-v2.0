import { useEffect } from 'react';
import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import { fetchScoresPage, SCORES_PAGE_SIZE, fetchResearch, fetchScoreHistory, fetchRiskScores, fetchAccuracy, fetchAccuracyDetail, fetchMarketAccuracy, fetchMarketAccuracyDetail, fetchCryptoAccuracy, fetchCryptoAccuracyDetail, fetchCrypto, fetchXSignal, fetchExplainer, fetchMacroLeverage, fetchConvergence } from '../lib/gradientApi';
import { MOCK_SIGNALS, filterFeed, findSignal, Signal } from '../lib/signals';
import { TierID } from '../constants/tiers';

export interface SignalsResult {
  signals: Signal[];
  isLoading: boolean;
  isError: boolean;
  isSample: boolean; // true when falling back to the offline mock dataset
  refetch: () => void;
}

// Live Gradient Score feed, loaded PROGRESSIVELY 100 at a time: the first page
// paints immediately (fast), then the rest fill in the background — so a 1,600-row
// feed never blocks the UI or ships one giant payload (which crashed the app).
// Falls back to the mock dataset only if the very first page fails.
export function useSignals(): SignalsResult {
  const q = useInfiniteQuery({
    queryKey: ['scores'],
    queryFn: ({ pageParam = 0 }) => fetchScoresPage(SCORES_PAGE_SIZE, pageParam as number),
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) => {
      const loaded = allPages.reduce((n, p) => n + p.signals.length, 0);
      return loaded < lastPage.total ? loaded : undefined;
    },
    staleTime: 60 * 1000,
    retry: 1,
  });

  // Auto-advance through the remaining pages as soon as each arrives.
  useEffect(() => {
    if (q.hasNextPage && !q.isFetchingNextPage) q.fetchNextPage();
  }, [q.hasNextPage, q.isFetchingNextPage, q.data]);

  const loaded = q.data?.pages.flatMap((p) => p.signals) ?? [];
  const live = loaded.length > 0;
  return {
    signals: live ? loaded : MOCK_SIGNALS,
    isLoading: q.isLoading,        // true only until the FIRST page lands
    isError: q.isError,
    isSample: !live && !q.isLoading,
    refetch: q.refetch,
  };
}

export function useTierFeed(tier: TierID) {
  const { signals, isLoading, isError, isSample, refetch } = useSignals();
  return { ...filterFeed(signals, tier), signals, isLoading, isError, isSample, refetch };
}

export function useSignal(id: string) {
  const { signals, isLoading, isError, isSample } = useSignals();
  return { signal: findSignal(signals, id), isLoading, isError, isSample };
}

export function useScoreHistory(topicKey: string | undefined) {
  const q = useQuery({
    queryKey: ['score-history', topicKey],
    queryFn: () => fetchScoreHistory(topicKey as string),
    enabled: !!topicKey,
    staleTime: 60 * 1000,
    retry: 1,
  });
  return { rows: q.data ?? [], isLoading: q.isLoading };
}

export function useMacroLeverage() {
  const q = useQuery({
    queryKey: ['macro-leverage'],
    queryFn: fetchMacroLeverage,
    staleTime: 30 * 60 * 1000,
    retry: 1,
  });
  return { macro: q.data ?? null, isLoading: q.isLoading };
}

export function useRiskScores() {
  const q = useQuery({
    queryKey: ['risk-scores'],
    queryFn: fetchRiskScores,
    staleTime: 60 * 1000,
    retry: 1,
  });
  return { risks: q.data ?? [], isLoading: q.isLoading, isError: q.isError, refetch: q.refetch };
}

// Crypto Money Gradient roster (/crypto, prewarm-served). On a cold engine boot
// the feed returns status:'warming' with no coins — keep polling every 4s until
// the roster arrives (same behavior as the web Crypto page).
export function useCrypto() {
  const q = useQuery({
    queryKey: ['crypto'],
    queryFn: fetchCrypto,
    staleTime: 5 * 60 * 1000,
    retry: 1,
    refetchInterval: (query) => (query.state.data?.status === 'warming' ? 4000 : false),
  });
  return {
    coins: q.data?.coins ?? [],
    warming: q.data?.status === 'warming',
    isLoading: q.isLoading,
    isError: q.isError,
  };
}

export function useAccuracy() {
  const q = useQuery({ queryKey: ['accuracy'], queryFn: fetchAccuracy, staleTime: 5 * 60 * 1000, retry: 1 });
  return { report: q.data, isLoading: q.isLoading, isError: q.isError };
}

// Attention-ledger per-row detail (for the mobile ledger's filter chips + row list).
export function useAccuracyDetail() {
  const q = useQuery({ queryKey: ['accuracy-detail'], queryFn: fetchAccuracyDetail, staleTime: 5 * 60 * 1000, retry: 1 });
  return { rows: q.data ?? [], isLoading: q.isLoading };
}

// Money + Crypto ledgers (distinct ground truths) — fetched lazily when the mode
// chip is selected so the default Attention view costs no extra requests.
export function useMarketAccuracy(enabled: boolean) {
  const q = useQuery({ queryKey: ['market-accuracy'], queryFn: fetchMarketAccuracy, enabled, staleTime: 5 * 60 * 1000, retry: 1 });
  const d = useQuery({ queryKey: ['market-accuracy-detail'], queryFn: fetchMarketAccuracyDetail, enabled, staleTime: 5 * 60 * 1000, retry: 1 });
  return { report: q.data, rows: d.data ?? [], isLoading: q.isLoading || d.isLoading };
}

export function useCryptoAccuracy(enabled: boolean) {
  const q = useQuery({ queryKey: ['crypto-accuracy'], queryFn: fetchCryptoAccuracy, enabled, staleTime: 5 * 60 * 1000, retry: 1 });
  const d = useQuery({ queryKey: ['crypto-accuracy-detail'], queryFn: fetchCryptoAccuracyDetail, enabled, staleTime: 5 * 60 * 1000, retry: 1 });
  return { report: q.data, rows: d.data ?? [], isLoading: q.isLoading || d.isLoading };
}

export function useXSignal(topic: string | undefined, enabled: boolean) {
  const q = useQuery({
    queryKey: ['x-signal', topic],
    queryFn: () => fetchXSignal(topic as string),
    enabled: !!topic && enabled,
    staleTime: 5 * 60 * 1000,
    retry: 0,
  });
  return { x: q.data, isLoading: q.isLoading };
}

// Evergreen topic explainer — cached forever client-side (server persists it).
export function useExplainer(topicKey: string | undefined, topicName?: string, enabled = true) {
  const q = useQuery({
    queryKey: ['explainer', topicKey],
    queryFn: () => fetchExplainer(topicKey as string, topicName),
    enabled: !!topicKey && enabled,
    staleTime: Infinity,
    gcTime: 24 * 60 * 60 * 1000,
    retry: 0,
  });
  return { explainer: q.data, isLoading: q.isLoading };
}

// Signal Convergence — lazy per-topic directional validation (cached 5 min).
export function useConvergence(topicKey: string | undefined, enabled = true) {
  const q = useQuery({
    queryKey: ['convergence', topicKey],
    queryFn: () => fetchConvergence(topicKey as string),
    enabled: !!topicKey && enabled,
    staleTime: 5 * 60 * 1000,
    retry: 0,
  });
  return { convergence: q.data, isLoading: q.isLoading };
}

export function useRisk(key: string | undefined) {
  const { risks, isLoading } = useRiskScores();
  return { risk: risks.find((r) => r.key === key), isLoading };
}

export function useResearch(topicKey: string | undefined) {
  const q = useQuery({
    queryKey: ['research', topicKey],
    queryFn: () => fetchResearch(topicKey as string),
    enabled: !!topicKey,
    staleTime: 10 * 60 * 1000,
    retry: 1,
  });
  return { research: q.data, isLoading: q.isLoading, isError: q.isError };
}
