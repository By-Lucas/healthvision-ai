import type { ReactNode } from 'react';
import { Navbar } from './Navbar';
import { DisclaimerBanner } from '@/shared/components/DisclaimerBanner';

export function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-6xl px-4 py-8">
        <div className="mb-6">
          <DisclaimerBanner compact />
        </div>
        {children}
      </main>
      <footer className="border-t border-slate-200 py-6 text-center text-xs text-slate-400">
        HealthVision AI — educational portfolio demo · Not a medical diagnosis tool
      </footer>
    </div>
  );
}
