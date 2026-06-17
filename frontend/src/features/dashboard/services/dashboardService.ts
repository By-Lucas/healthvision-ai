import { getJson } from '@/shared/services/apiClient';
import type { DashboardSummary } from '@/shared/types/analysis';

export async function getDashboardSummary(): Promise<DashboardSummary> {
  return getJson<DashboardSummary>('/api/v1/dashboard/summary');
}
