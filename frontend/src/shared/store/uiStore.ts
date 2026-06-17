import { create } from 'zustand';

// Minimal global state (Zustand). Most server state lives in React Query; this
// store only holds genuinely cross-feature UI state — here, the id of the most
// recently uploaded analysis so the History/Detail views can highlight it.
interface UiState {
  lastUploadedId: string | null;
  setLastUploadedId: (id: string | null) => void;
}

export const useUiStore = create<UiState>((set) => ({
  lastUploadedId: null,
  setLastUploadedId: (id) => set({ lastUploadedId: id }),
}));
