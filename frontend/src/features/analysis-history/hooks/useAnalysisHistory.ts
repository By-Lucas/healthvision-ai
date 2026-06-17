import { useQuery } from '@tanstack/react-query';
import { listAnalyses } from '../services/historyService';
import type { HistoryFilters } from '../types';

export function useAnalysisHistory(filters: HistoryFilters) {
  return useQuery({
    queryKey: ['analyses', filters],
    queryFn: () => listAnalyses(filters),
    // Keep the list fresh while items are still being processed.
    refetchInterval: 5_000,
  });
}
