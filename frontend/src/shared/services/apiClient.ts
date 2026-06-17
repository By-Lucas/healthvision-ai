// Thin fetch wrapper shared by every feature service.
// Centralizes base URL, JSON handling and error normalization so feature code
// stays declarative.

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function parseError(res: Response): Promise<never> {
  let detail = res.statusText;
  try {
    const body = await res.json();
    detail = body.detail ?? detail;
  } catch {
    // ignore non-JSON error bodies
  }
  throw new ApiError(detail, res.status);
}

export async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) await parseError(res);
  return res.json() as Promise<T>;
}

export async function postForm<T>(path: string, form: FormData): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, { method: 'POST', body: form });
  if (!res.ok) await parseError(res);
  return res.json() as Promise<T>;
}

export async function del(path: string): Promise<void> {
  const res = await fetch(`${BASE_URL}${path}`, { method: 'DELETE' });
  if (!res.ok && res.status !== 204) await parseError(res);
}

// Resolve a stored image path (e.g. "/uploads/x.jpg") to a loadable URL.
export function resolveAssetUrl(path: string): string {
  if (path.startsWith('http')) return path;
  return `${BASE_URL}${path}`;
}
