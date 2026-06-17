import { describe, expect, it } from 'vitest';
import { validateFile } from '@/features/exam-upload/services/uploadService';

function makeFile(name: string, type: string, sizeBytes: number): File {
  const blob = new Blob([new Uint8Array(sizeBytes)], { type });
  return new File([blob], name, { type });
}

describe('validateFile', () => {
  it('accepts a valid PNG', () => {
    expect(validateFile(makeFile('scan.png', 'image/png', 1024)).ok).toBe(true);
  });

  it('rejects unsupported extensions', () => {
    const result = validateFile(makeFile('notes.txt', 'text/plain', 1024));
    expect(result.ok).toBe(false);
    expect(result.error).toMatch(/JPG|PNG/i);
  });

  it('rejects files over the size limit', () => {
    const result = validateFile(makeFile('huge.png', 'image/png', 11 * 1024 * 1024));
    expect(result.ok).toBe(false);
    expect(result.error).toMatch(/larger/i);
  });

  it('rejects empty files', () => {
    expect(validateFile(makeFile('empty.png', 'image/png', 0)).ok).toBe(false);
  });
});
