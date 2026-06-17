import { useMutation, useQueryClient } from '@tanstack/react-query';
import { del } from '@/shared/services/apiClient';

// Deleting an analysis is a cross-feature action (used from History and Detail),
// so the hook lives in shared/. It invalidates the lists + dashboard on success.
export function useDeleteAnalysis() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: (id: string) => del(`/api/v1/analysis/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['analyses'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}
