import { create } from 'zustand';

interface RepoState {
  currentRepoId: string | null;
  jobId: string | null;
  setRepo: (id: string | null) => void;
  setJob: (id: string | null) => void;
}

export const useRepoStore = create<RepoState>((set) => ({
  currentRepoId: null,
  jobId: null,
  setRepo: (id) => set({ currentRepoId: id }),
  setJob: (id) => set({ jobId: id }),
}));
