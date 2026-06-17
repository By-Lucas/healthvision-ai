import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader } from '@/shared/components/Card';
import { DisclaimerBanner } from '@/shared/components/DisclaimerBanner';
import { Dropzone } from '../components/Dropzone';
import { validateFile } from '../services/uploadService';
import { useUploadExam } from '../hooks/useUploadExam';

export function UploadPage() {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const upload = useUploadExam();

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  function handleFile(selected: File) {
    const result = validateFile(selected);
    if (!result.ok) {
      setValidationError(result.error ?? 'Invalid file.');
      setFile(null);
      return;
    }
    setValidationError(null);
    setFile(selected);
  }

  function handleSubmit() {
    if (!file) return;
    upload.mutate(file, {
      onSuccess: (analysis) => navigate(`/analysis/${analysis.id}`),
    });
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Upload an exam</h1>
        <p className="mt-1 text-slate-500">
          Upload a simulated or public chest X-ray image for AI analysis.
        </p>
      </div>

      <DisclaimerBanner />

      <Card>
        <CardHeader title="Select image" subtitle="JPG, JPEG or PNG · max 10 MB" />
        <div className="space-y-4 p-5">
          <Dropzone onFile={handleFile} disabled={upload.isPending} />

          {validationError && (
            <p className="rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700">
              {validationError}
            </p>
          )}

          {previewUrl && (
            <div className="space-y-3">
              <p className="text-sm font-medium text-slate-600">Preview</p>
              <img
                src={previewUrl}
                alt="Selected exam preview"
                className="max-h-72 w-full rounded-lg border border-slate-200 object-contain bg-slate-900/5"
              />
              <p className="truncate text-xs text-slate-400">{file?.name}</p>
            </div>
          )}

          {upload.isError && (
            <p className="rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700">
              Upload failed: {upload.error.message}
            </p>
          )}

          <button
            onClick={handleSubmit}
            disabled={!file || upload.isPending}
            data-testid="submit-upload"
            className="w-full rounded-lg bg-brand-600 px-4 py-2.5 font-medium text-white shadow-sm transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {upload.isPending ? 'Uploading…' : 'Analyze image'}
          </button>
        </div>
      </Card>
    </div>
  );
}
