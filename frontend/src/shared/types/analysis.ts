// Shared domain types mirroring the backend API contract.

export type AnalysisStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';

export type PredictedClass = 'NORMAL' | 'PNEUMONIA' | 'UNCERTAIN';

export interface Analysis {
  id: string;
  original_filename: string;
  image_path: string;
  status: AnalysisStatus;
  predicted_class: PredictedClass | null;
  confidence_score: number | null;
  explanation: string | null;
  processing_time_ms: number | null;
  error_message: string | null;
  findings: Record<string, number> | null;
  created_at: string;
  updated_at: string;
  warning: string;
}

export interface AnalysisList {
  items: Analysis[];
  count: number;
}

export interface DashboardSummary {
  total_analyses: number;
  average_confidence: number;
  by_class: Record<string, number>;
  by_status: Record<string, number>;
  recent_analyses: Analysis[];
}
