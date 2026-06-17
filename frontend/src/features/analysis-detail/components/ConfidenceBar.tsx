import { formatPercent } from '@/shared/utils/format';

export function ConfidenceBar({ value }: { value: number | null }) {
  const pct = value != null ? Math.round(value * 100) : 0;
  const color =
    pct >= 80 ? 'bg-emerald-500' : pct >= 55 ? 'bg-amber-500' : 'bg-rose-500';
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm">
        <span className="text-slate-500">Confidence</span>
        <span className="font-semibold text-slate-800">{formatPercent(value)}</span>
      </div>
      <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
