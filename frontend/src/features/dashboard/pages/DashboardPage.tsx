import { Link } from 'react-router-dom';
import { Card, CardHeader } from '@/shared/components/Card';
import { ErrorState, Spinner } from '@/shared/components/States';
import { AnalysisTable } from '@/features/analysis-history/components/AnalysisTable';
import { formatPercent } from '@/shared/utils/format';
import { StatCard } from '../components/StatCard';
import { ClassDistributionChart } from '../components/ClassDistributionChart';
import { useDashboard } from '../hooks/useDashboard';

export function DashboardPage() {
  const { data, isLoading, isError, error, refetch } = useDashboard();

  if (isLoading) return <Spinner label="Loading dashboard…" />;
  if (isError) return <ErrorState message={(error as Error).message} onRetry={refetch} />;
  if (!data) return null;

  const completed = data.by_status.COMPLETED ?? 0;
  const pending = (data.by_status.PENDING ?? 0) + (data.by_status.PROCESSING ?? 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <p className="mt-1 text-slate-500">Aggregated metrics across all analyses.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total analyses" value={data.total_analyses} />
        <StatCard
          label="Avg. confidence"
          value={formatPercent(data.average_confidence)}
          hint="Across completed analyses"
        />
        <StatCard label="Completed" value={completed} />
        <StatCard label="In progress" value={pending} hint="Pending + processing" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Distribution by class" />
          <div className="p-4">
            <ClassDistributionChart data={data.by_class} />
          </div>
        </Card>

        <Card>
          <CardHeader title="Status breakdown" />
          <div className="space-y-3 p-5">
            {['PENDING', 'PROCESSING', 'COMPLETED', 'FAILED'].map((s) => (
              <div key={s} className="flex items-center justify-between text-sm">
                <span className="text-slate-500">{s}</span>
                <span className="font-semibold text-slate-800">
                  {data.by_status[s] ?? 0}
                </span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">Recent analyses</h2>
          <Link to="/history" className="text-sm font-medium text-brand-600 hover:underline">
            View all →
          </Link>
        </div>
        {data.recent_analyses.length > 0 ? (
          <AnalysisTable items={data.recent_analyses} />
        ) : (
          <p className="rounded-lg border border-dashed border-slate-300 bg-white py-8 text-center text-sm text-slate-400">
            No analyses yet.
          </p>
        )}
      </div>
    </div>
  );
}
