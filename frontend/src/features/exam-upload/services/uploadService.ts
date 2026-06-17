import { postForm } from '@/shared/services/apiClient';
import type { Analysis } from '@/shared/types/analysis';
import {
  ACCEPTED_EXTENSIONS,
  ACCEPTED_TYPES,
  MAX_UPLOAD_MB,
  type UploadValidationResult,
} from '../types';

// Client-side validation mirrors the backend rules so users get instant
// feedback; the backend remains the source of truth.
export function validateFile(file: File): UploadValidationResult {
  const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
  if (!ACCEPTED_EXTENSIONS.includes(ext) && !ACCEPTED_TYPES.includes(file.type)) {
    return { ok: false, error: 'Only JPG, JPEG and PNG files are allowed.' };
  }
  if (file.size > MAX_UPLOAD_MB * 1024 * 1024) {
    return { ok: false, error: `File is larger than ${MAX_UPLOAD_MB} MB.` };
  }
  if (file.size === 0) {
    return { ok: false, error: 'File is empty.' };
  }
  return { ok: true };
}

export async function uploadExamImage(file: File): Promise<Analysis> {
  const form = new FormData();
  form.append('file', file);
  return postForm<Analysis>('/api/v1/analysis/upload', form);
}
