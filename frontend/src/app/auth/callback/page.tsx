"use client";

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { getCurrentUser } from '@/lib/api';
import { setToken as setLocalToken } from '@/lib/auth';


function AuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setUser } = useAuthStore();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = searchParams.get('token');
    
    const handleAuth = async () => {
      if (!token) {
        setError('No authentication token found.');
        setTimeout(() => router.push('/auth/login'), 2000);
        return;
      }
      
      try {
        // Save token to localStorage so api.ts can use it
        setLocalToken(token);
        
        // Fetch user data
        const userData = await getCurrentUser();
        
        // Hydrate store
        setUser(userData, token);
        
        // Redirect to dashboard
        router.push('/dashboard');
      } catch (err: any) {
        console.error('Authentication error:', err);
        setError('Failed to load user profile.');
        setTimeout(() => router.push('/auth/login'), 2000);
      }
    };

    handleAuth();
  }, [searchParams, router, setUser]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      {error ? (
        <div className="text-red-400 p-4 bg-red-950/20 border border-red-900 rounded-lg">
          {error}
          <div className="text-sm mt-2 text-zinc-400">Redirecting to login...</div>
        </div>
      ) : (
        <div className="flex flex-col items-center space-y-4 text-green-400">
          <svg className="w-8 h-8 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p>Authenticating...</p>
        </div>
      )}
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="text-green-400">Loading...</div>
      </div>
    }>
      <AuthCallbackContent />
    </Suspense>
  );
}
