import { Link, useNavigate, useParams } from 'react-router-dom';
import { ErrorState, Spinner } from '@/shared/components/States';
import { useDeleteAnalysis } from '@/shared/hooks/useDeleteAnalysis';
import { ResultPanel } from '../components/ResultPanel';
import { FindingsPanel } from '../components/FindingsPanel';
import { useAnalysisDetail } from '../hooks/useAnalysisDetail';

export function AnalysisDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data, isLoading, isError, error, refetch } = useAnalysisDetail(id);
  const deleteAnalysis = useDeleteAnalysis();

  function handleDelete() {
    if (!id) return;
    if (window.confirm('Delete this analysis? This cannot be undone.')) {
      deleteAnalysis.mutate(id, { onSuccess: () => navigate('/history') });
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Link
          to="/history"
          className="text-sm font-medium text-brand-600 hover:underline"
        >
          ← Back to history
        </Link>
        {data && (
          <button
            onClick={handleDelete}
            disabled={deleteAnalysis.isPending}
            className="rounded-md border border-rose-200 bg-rose-50 px-3 py-1.5 text-sm font-medium text-rose-700 hover:bg-rose-100 disabled:opacity-50"
          >
            {deleteAnalysis.isPending ? 'Deleting…' : 'Delete analysis'}
          </button>
        )}
      </div>
      <h1 className="text-2xl font-bold text-slate-900">Analysis detail</h1>

      {isLoading && <Spinner label="Loading analysis…" />}
      {isError && <ErrorState message={(error as Error).message} onRetry={refetch} />}
      {data && <ResultPanel analysis={data} />}
      {data?.status === 'COMPLETED' && data.findings && (
        <FindingsPanel findings={data.findings} />
      )}
    </div>
  );
}
