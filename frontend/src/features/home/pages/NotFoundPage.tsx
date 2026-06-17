import { Link } from 'react-router-dom';

export function NotFoundPage() {
  return (
    <div className="flex flex-col items-center gap-4 py-24 text-center">
      <p className="text-5xl font-bold text-slate-300">404</p>
      <p className="text-slate-600">This page does not exist.</p>
      <Link to="/" className="font-medium text-brand-600 hover:underline">
        ← Back home
      </Link>
    </div>
  );
}
