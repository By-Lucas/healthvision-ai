import { Card, CardHeader } from '@/shared/components/Card';
import { formatPercent } from '@/shared/utils/format';

// Shows every pathology the model scored (not just pneumonia), sorted by
// probability. The real torchxrayvision model returns ~18 chest findings; the
// mock returns its two-class probabilities.
export function FindingsPanel({ findings }: { findings: Record<string, number> }) {
  const entries = Object.entries(findings).sort((a, b) => b[1] - a[1]);

  if (entries.length === 0) return null;

  return (
    <Card>
      <CardHeader
        title="All detected findings"
        subtitle="Per-pathology probabilities from the chest X-ray model"
      />
      <div className="space-y-2.5 p-5">
        {entries.map(([name, prob]) => {
          const pct = Math.round(prob * 100);
          const color =
            pct >= 50 ? 'bg-rose-500' : pct >= 25 ? 'bg-amber-500' : 'bg-slate-300';
          return (
            <div key={name} className="flex items-center gap-3 text-sm">
              <span className="w-44 flex-none truncate text-slate-600">{name}</span>
              <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
                <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
              </div>
              <span className="w-12 flex-none text-right font-medium text-slate-700">
                {formatPercent(prob)}
              </span>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
