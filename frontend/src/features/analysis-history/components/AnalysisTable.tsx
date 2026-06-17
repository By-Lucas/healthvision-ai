import { Link } from 'react-router-dom';
import type { Analysis } from '@/shared/types/analysis';
import { ClassBadge, StatusBadge } from '@/shared/components/StatusBadge';
import { formatDateTime, formatPercent } from '@/shared/utils/format';

interface AnalysisTableProps {
  items: Analysis[];
  onDelete?: (id: string) => void;
  deletingId?: string;
}

export function AnalysisTable({ items, onDelete, deletingId }: AnalysisTableProps) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-4 py-3">File</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Class</th>
            <th className="px-4 py-3">Confidence</th>
            <th className="px-4 py-3">Created</th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {items.map((a) => (
            <tr key={a.id} className="hover:bg-slate-50">
              <td className="max-w-[12rem] truncate px-4 py-3 font-medium text-slate-700">
                {a.original_filename}
              </td>
              <td className="px-4 py-3">
                <StatusBadge status={a.status} />
              </td>
              <td className="px-4 py-3">
                <ClassBadge value={a.predicted_class} />
              </td>
              <td className="px-4 py-3 text-slate-600">
                {formatPercent(a.confidence_score)}
              </td>
              <td className="px-4 py-3 text-slate-500">
                {formatDateTime(a.created_at)}
              </td>
              <td className="px-4 py-3 text-right">
                <div className="flex items-center justify-end gap-3">
                  <Link
                    to={`/analysis/${a.id}`}
                    className="font-medium text-brand-600 hover:underline"
                  >
                    View →
                  </Link>
                  {onDelete && (
                    <button
                      onClick={() => onDelete(a.id)}
                      disabled={deletingId === a.id}
                      aria-label={`Delete ${a.original_filename}`}
                      className="font-medium text-rose-600 hover:underline disabled:opacity-50"
                    >
                      {deletingId === a.id ? 'Deleting…' : 'Delete'}
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
