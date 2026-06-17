import { useQuery } from '@tanstack/react-query';
import { getAnalysis } from '../services/detailService';
import type { Analysis } from '@/shared/types/analysis';

const ACTIVE_STATUSES = new Set(['PENDING', 'PROCESSING']);

export function useAnalysisDetail(id: string | undefined) {
  return useQuery<Analysis>({
    queryKey: ['analysis', id],
    queryFn: () => getAnalysis(id!),
    enabled: Boolean(id),
    // Poll while the analysis is still being processed by the worker, then stop.
    refetchInterval: (query) =>
      query.state.data && ACTIVE_STATUSES.has(query.state.data.status) ? 2_000 : false,
  });
}
