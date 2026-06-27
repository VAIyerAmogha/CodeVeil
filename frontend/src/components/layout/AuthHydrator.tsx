"use client";

import { useEffect, useRef, useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { getToken } from '@/lib/auth';
import { getCurrentUser } from '@/lib/api';
import { usePathname, useRouter } from 'next/navigation';

export default function AuthHydrator({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, setUser, logout } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const hydrated = useRef(false);
  const pathname = usePathname();
  const router = useRouter();

  const publicRoutes = ['/', '/auth/login', '/auth/signup', '/auth/callback'];
  const isPublicRoute = publicRoutes.includes(pathname);

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
          logout();
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, [setUser, logout]);

  useEffect(() => {
    if (!loading && !isAuthenticated && !isPublicRoute) {
      router.push('/auth/login');
    }
  }, [loading, isAuthenticated, isPublicRoute, router]);

  // For public routes, don't block the UI with a loading screen.
  // The navbar will just show "Sign In" until hydration is complete.
  if (loading) {
    if (isPublicRoute) {
      return <>{children}</>;
    }
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <span className="text-green-500 animate-pulse text-lg">Loading...</span>
      </div>
    );
  }

  // Prevent flash of protected content while redirecting
  if (!isAuthenticated && !isPublicRoute) {
    return null;
  }

  return <>{children}</>;
}
