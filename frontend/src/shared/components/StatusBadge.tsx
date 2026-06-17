import type { AnalysisStatus, PredictedClass } from '@/shared/types/analysis';

const STATUS_STYLES: Record<AnalysisStatus, string> = {
  PENDING: 'bg-amber-100 text-amber-700',
  PROCESSING: 'bg-blue-100 text-blue-700',
  COMPLETED: 'bg-emerald-100 text-emerald-700',
  FAILED: 'bg-rose-100 text-rose-700',
};

const CLASS_STYLES: Record<PredictedClass, string> = {
  NORMAL: 'bg-emerald-100 text-emerald-700',
  PNEUMONIA: 'bg-rose-100 text-rose-700',
  UNCERTAIN: 'bg-slate-200 text-slate-700',
};

export function StatusBadge({ status }: { status: AnalysisStatus }) {
  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLES[status]}`}
    >
      {status}
    </span>
  );
}

export function ClassBadge({ value }: { value: PredictedClass | null }) {
  if (!value) return <span className="text-slate-400">—</span>;
  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${CLASS_STYLES[value]}`}
    >
      {value}
    </span>
  );
}
