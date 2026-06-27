import { create } from 'zustand';
import { Repository } from '../types/repository';

interface RepoState {
  repos: Repository[];
  activeRepo: Repository | null;
  setRepos: (repos: Repository[]) => void;
  setActiveRepo: (repo: Repository | null) => void;
}

export const useRepoStore = create<RepoState>((set) => ({
  repos: [],
  activeRepo: null,
  setRepos: (repos) => set({ repos }),
  setActiveRepo: (activeRepo) => set({ activeRepo }),
}));
