import { Route, Routes } from 'react-router-dom';
import { AppLayout } from '@/shared/layout/AppLayout';
import { HomePage } from '@/features/home/pages/HomePage';
import { UploadPage } from '@/features/exam-upload/pages/UploadPage';
import { DashboardPage } from '@/features/dashboard/pages/DashboardPage';
import { HistoryPage } from '@/features/analysis-history/pages/HistoryPage';
import { AnalysisDetailPage } from '@/features/analysis-detail/pages/AnalysisDetailPage';
import { NotFoundPage } from '@/features/home/pages/NotFoundPage';

export function AppRouter() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/analysis/:id" element={<AnalysisDetailPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </AppLayout>
  );
}
