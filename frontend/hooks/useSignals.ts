import { useQuery } from '@tanstack/react-query';
import { fetchScores, fetchResearch, fetchScoreHistory, fetchRiskScores } from '../lib/gradientApi';
import { MOCK_SIGNALS, filterFeed, findSignal, Signal } from '../lib/signals';
import { TierID } from '../constants/tiers';

export interface SignalsResult {
  signals: Signal[];
  isLoading: boolean;
  isError: boolean;
  isSample: boolean; // true when falling back to the offline mock dataset
  refetch: () => void;
}

// Fetches live Gradient Score data; falls back to the mock dataset on failure.
export function useSignals(): SignalsResult {
  const q = useQuery({
    queryKey: ['scores'],
    queryFn: fetchScores,
    staleTime: 60 * 1000,
    retry: 1,
  });

  const live = q.data && q.data.length > 0;
  return {
    signals: live ? (q.data as Signal[]) : MOCK_SIGNALS,
    isLoading: q.isLoading,
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

export function useRiskScores() {
  const q = useQuery({
    queryKey: ['risk-scores'],
    queryFn: fetchRiskScores,
    staleTime: 60 * 1000,
    retry: 1,
  });
  return { risks: q.data ?? [], isLoading: q.isLoading, isError: q.isError, refetch: q.refetch };
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
