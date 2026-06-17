import { getJson } from '@/shared/services/apiClient';
import type { AnalysisList } from '@/shared/types/analysis';
import type { HistoryFilters } from '../types';

export async function listAnalyses(filters: HistoryFilters): Promise<AnalysisList> {
  const params = new URLSearchParams();
  if (filters.status) params.set('status', filters.status);
  if (filters.predicted_class) params.set('predicted_class', filters.predicted_class);
  const qs = params.toString();
  return getJson<AnalysisList>(`/api/v1/analysis${qs ? `?${qs}` : ''}`);
}
