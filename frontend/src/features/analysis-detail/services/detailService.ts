import { getJson } from '@/shared/services/apiClient';
import type { Analysis } from '@/shared/types/analysis';

export async function getAnalysis(id: string): Promise<Analysis> {
  return getJson<Analysis>(`/api/v1/analysis/${id}`);
}
