export interface UploadValidationResult {
  ok: boolean;
  error?: string;
}

export const MAX_UPLOAD_MB = 10;
export const ACCEPTED_TYPES = ['image/jpeg', 'image/png'];
export const ACCEPTED_EXTENSIONS = ['.jpg', '.jpeg', '.png'];
