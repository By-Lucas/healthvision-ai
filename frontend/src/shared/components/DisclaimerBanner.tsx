// The educational disclaimer is shown prominently across the app. Single source
// of truth so the wording stays consistent with the README and backend.
export const DISCLAIMER_TEXT =
  'This project is for educational and portfolio purposes only. It is not a medical diagnosis tool.';

export function DisclaimerBanner({ compact = false }: { compact?: boolean }) {
  return (
    <div
      role="note"
      className={`flex items-start gap-2 border-amber-200 bg-amber-50 text-amber-800 ${
        compact ? 'rounded-md border px-3 py-2 text-xs' : 'rounded-lg border px-4 py-3 text-sm'
      }`}
    >
      <span aria-hidden>⚠️</span>
      <p>{DISCLAIMER_TEXT}</p>
    </div>
  );
}
