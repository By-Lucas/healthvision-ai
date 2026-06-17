import { useState } from 'react';
import { Link } from 'react-router-dom';
import { EmptyState, ErrorState, Spinner } from '@/shared/components/States';
import { FilterBar } from '../components/FilterBar';
import { AnalysisTable } from '../components/AnalysisTable';
import { useAnalysisHistory } from '../hooks/useAnalysisHistory';
import { useDeleteAnalysis } from '@/shared/hooks/useDeleteAnalysis';
import type { HistoryFilters } from '../types';

export function HistoryPage() {
  const [filters, setFilters] = useState<HistoryFilters>({});
  const { data, isLoading, isError, error, refetch } = useAnalysisHistory(filters);
  const deleteAnalysis = useDeleteAnalysis();

  function handleDelete(id: string) {
    if (window.confirm('Delete this analysis? This cannot be undone.')) {
      deleteAnalysis.mutate(id);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Analysis history</h1>
          <p className="mt-1 text-slate-500">Browse and filter past analyses.</p>
        </div>
        <Link
          to="/upload"
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          + New analysis
        </Link>
      </div>

      <FilterBar filters={filters} onChange={setFilters} />

      {isLoading && <Spinner label="Loading analyses…" />}
      {isError && <ErrorState message={(error as Error).message} onRetry={refetch} />}
      {data && data.items.length === 0 && (
        <EmptyState
          title="No analyses yet"
          description="Upload a chest X-ray to see results here."
          action={
            <Link
              to="/upload"
              className="rounded-md bg-brand-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-brand-700"
            >
              Upload an exam
            </Link>
          }
        />
      )}
      {data && data.items.length > 0 && (
        <AnalysisTable
          items={data.items}
          onDelete={handleDelete}
          deletingId={deleteAnalysis.isPending ? deleteAnalysis.variables : undefined}
        />
      )}
    </div>
  );
}
