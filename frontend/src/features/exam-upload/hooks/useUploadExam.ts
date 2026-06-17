import { useMutation, useQueryClient } from '@tanstack/react-query';
import { uploadExamImage } from '../services/uploadService';
import { useUiStore } from '@/shared/store/uiStore';
import type { Analysis } from '@/shared/types/analysis';

export function useUploadExam() {
  const queryClient = useQueryClient();
  const setLastUploadedId = useUiStore((s) => s.setLastUploadedId);

  return useMutation<Analysis, Error, File>({
    mutationFn: uploadExamImage,
    onSuccess: (analysis) => {
      setLastUploadedId(analysis.id);
      // Freshly created analysis affects history + dashboard lists.
      queryClient.invalidateQueries({ queryKey: ['analyses'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}
