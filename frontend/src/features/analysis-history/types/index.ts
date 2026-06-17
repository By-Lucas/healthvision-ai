import type { AnalysisStatus, PredictedClass } from '@/shared/types/analysis';

export interface HistoryFilters {
  status?: AnalysisStatus;
  predicted_class?: PredictedClass;
}
