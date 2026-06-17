import type { AnalysisStatus, PredictedClass } from '@/shared/types/analysis';
import type { HistoryFilters } from '../types';

const STATUSES: AnalysisStatus[] = ['PENDING', 'PROCESSING', 'COMPLETED', 'FAILED'];
const CLASSES: PredictedClass[] = ['NORMAL', 'PNEUMONIA', 'UNCERTAIN'];

interface FilterBarProps {
  filters: HistoryFilters;
  onChange: (filters: HistoryFilters) => void;
}

export function FilterBar({ filters, onChange }: FilterBarProps) {
  return (
    <div className="flex flex-wrap items-end gap-4">
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-slate-500">Status</label>
        <select
          value={filters.status ?? ''}
          onChange={(e) =>
            onChange({
              ...filters,
              status: (e.target.value || undefined) as AnalysisStatus | undefined,
            })
          }
          className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm"
        >
          <option value="">All</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-slate-500">Class</label>
        <select
          value={filters.predicted_class ?? ''}
          onChange={(e) =>
            onChange({
              ...filters,
              predicted_class: (e.target.value || undefined) as
                | PredictedClass
                | undefined,
            })
          }
          className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm"
        >
          <option value="">All</option>
          {CLASSES.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      {(filters.status || filters.predicted_class) && (
        <button
          onClick={() => onChange({})}
          className="rounded-md px-3 py-1.5 text-sm font-medium text-brand-600 hover:bg-brand-50"
        >
          Clear filters
        </button>
      )}
    </div>
  );
}
