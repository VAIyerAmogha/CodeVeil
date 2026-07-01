"use client";

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { signup, API_URL } from '@/lib/api';
import { useAuthStore } from '@/store/authStore';

export default function SignupPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { setUser } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await signup(email, name, password);
      setUser(res.user, res.access_token);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col justify-center items-center flex-grow py-12">
      <div className="glass-panel p-8 rounded-2xl border border-green-500/20 max-w-md w-full">
        <h1 className="text-2xl font-bold text-green-50 mb-6 text-center">Create an Account</h1>
        {error && <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-3 rounded-lg mb-4 text-sm">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-green-400 mb-1">Name</label>
            <input 
              type="text" 
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-black/40 border border-green-500/30 rounded-lg px-4 py-2 text-green-50 focus:outline-none focus:border-green-400 focus:ring-1 focus:ring-green-400 transition-all"
              required 
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-green-400 mb-1">Email</label>
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-black/40 border border-green-500/30 rounded-lg px-4 py-2 text-green-50 focus:outline-none focus:border-green-400 focus:ring-1 focus:ring-green-400 transition-all"
              required 
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-green-400 mb-1">Password</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-black/40 border border-green-500/30 rounded-lg px-4 py-2 text-green-50 focus:outline-none focus:border-green-400 focus:ring-1 focus:ring-green-400 transition-all"
              required 
            />
          </div>
          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-green-500/10 border border-green-500/30 text-green-400 hover:bg-green-500/20 py-2 rounded-lg font-medium hover:shadow-[0_0_15px_rgba(34,197,94,0.3)] transition-all duration-300 disabled:opacity-50 mt-4"
          >
            {loading ? 'Signing up...' : 'Sign Up'}
          </button>
        </form>
        
        <div className="mt-6">
          <a href={`${API_URL}/auth/google`} className="block w-full bg-zinc-900 border border-zinc-800 text-zinc-300 hover:bg-zinc-800 hover:text-white py-2 rounded-lg font-medium text-center transition-all">
            Sign in with Google
          </a>
        </div>

        <p className="mt-6 text-center text-zinc-400 text-sm">
          Already have an account? <Link href="/auth/login" className="text-green-400 hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
