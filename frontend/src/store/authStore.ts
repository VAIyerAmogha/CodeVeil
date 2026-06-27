import { create } from 'zustand';
import { User } from '../types/user';
import { setToken, clearToken } from '../lib/auth';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  setUser: (user: User, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  setUser: (user, token) => {
    setToken(token);
    set({ user, token, isAuthenticated: true });
  },
  logout: () => {
    clearToken();
    set({ user: null, token: null, isAuthenticated: false });
  },
}));
