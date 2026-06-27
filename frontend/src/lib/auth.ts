export const getToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('cv_token');
};

export const setToken = (token: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('cv_token', token);
  }
};

export const clearToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('cv_token');
  }
};

export const isAuthenticated = (): boolean => {
  return !!getToken();
};

export const getUserFromToken = (): { user_id: string; email: string } | null => {
  const token = getToken();
  if (!token) return null;
  try {
    const payload = token.split('.')[1];
    const decoded = atob(payload);
    return JSON.parse(decoded);
  } catch (e) {
    return null;
  }
};
