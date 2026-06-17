import type { Analysis } from '@/shared/types/analysis';
import { Card, CardHeader } from '@/shared/components/Card';
import { ClassBadge, StatusBadge } from '@/shared/components/StatusBadge';
import { DisclaimerBanner } from '@/shared/components/DisclaimerBanner';
import { resolveAssetUrl } from '@/shared/services/apiClient';
import { formatDateTime, formatMs } from '@/shared/utils/format';
import { ConfidenceBar } from './ConfidenceBar';

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4 py-1.5 text-sm">
      <span className="text-slate-500">{label}</span>
      <span className="text-right font-medium text-slate-700">{value}</span>
    </div>
  );
}

export function ResultPanel({ analysis }: { analysis: Analysis }) {
  const processing = analysis.status === 'PENDING' || analysis.status === 'PROCESSING';

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader title="Exam image" subtitle={analysis.original_filename} />
        <div className="p-5">
          <img
            src={resolveAssetUrl(analysis.image_path)}
            alt={`Exam ${analysis.original_filename}`}
            className="max-h-96 w-full rounded-lg border border-slate-200 bg-slate-900/5 object-contain"
          />
        </div>
      </Card>

      <div className="space-y-6">
        <Card>
          <CardHeader title="AI result" />
          <div className="space-y-4 p-5">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-500">Status</span>
              <StatusBadge status={analysis.status} />
            </div>

            {processing && (
              <p className="rounded-md bg-blue-50 px-3 py-2 text-sm text-blue-700">
                The image is being analyzed by the worker. This page updates
                automatically…
              </p>
            )}

            {analysis.status === 'FAILED' && (
              <p className="rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700">
                {analysis.error_message ?? 'Processing failed.'}
              </p>
            )}

            {analysis.status === 'COMPLETED' && (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-500">Predicted class</span>
                  <ClassBadge value={analysis.predicted_class} />
                </div>
                <ConfidenceBar value={analysis.confidence_score} />
                {analysis.explanation && (
                  <div className="rounded-lg bg-slate-50 p-3 text-sm text-slate-600">
                    {analysis.explanation}
                  </div>
                )}
              </>
            )}
          </div>
        </Card>

        <Card>
          <CardHeader title="Metadata" />
          <div className="px-5 py-3">
            <Meta label="Analysis ID" value={analysis.id} />
            <Meta label="Created" value={formatDateTime(analysis.created_at)} />
            <Meta label="Updated" value={formatDateTime(analysis.updated_at)} />
            <Meta
              label="Processing time"
              value={formatMs(analysis.processing_time_ms)}
            />
          </div>
        </Card>

        <DisclaimerBanner compact />
      </div>
    </div>
  );
}
