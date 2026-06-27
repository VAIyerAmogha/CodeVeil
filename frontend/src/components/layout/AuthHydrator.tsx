"use client";

import { useEffect, useRef } from 'react';
import { useAuthStore } from '@/store/authStore';
import { getToken, clearToken } from '@/lib/auth';
import { getCurrentUser } from '@/lib/api';

export default function AuthHydrator() {
  const { setUser, logout } = useAuthStore();
  const hydrated = useRef(false);

  useEffect(() => {
    if (hydrated.current) return;
    hydrated.current = true;

    const token = getToken();
    if (token) {
      getCurrentUser()
        .then((user) => {
          setUser(user, token);
        })
        .catch(() => {
          // If token is invalid (e.g. 401), logout
          logout();
        });
    }
  }, [setUser, logout]);

  return null;
}
