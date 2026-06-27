"use client";

import React from 'react';
import { useRepository } from '@/hooks/useRepository';
import RepoGrid from '@/components/repository/RepoGrid';
import { deleteRepo } from '@/lib/api';
import IndexingForm from '@/components/indexing/IndexingForm';
import { useAuthStore } from '@/store/authStore';

export default function DashboardPage() {
  const { repos, loading, error, refetch } = useRepository();
  const { user } = useAuthStore();

  const handleDelete = async (id: string) => {
    try {
      await deleteRepo(id);
      refetch();
    } catch (err: unknown) {
      alert("Failed to delete repository");
    }
  };

  const firstName = user?.name?.split(' ')[0] || 'Developer';

  return (
    <div className="min-h-screen bg-transparent text-green-50 p-6 md:p-10">
      <div className="max-w-6xl mx-auto flex flex-col gap-12">
        
        <div>
          <h1 className="text-3xl md:text-4xl font-bold mb-3 text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-600">Welcome back, {firstName}!</h1>
          <p className="text-green-100/60 mb-8 text-lg">Analyze a new repository or explore your existing ones.</p>
          
          <div className="bg-black/40 border border-green-500/20 p-6 md:p-8 rounded-2xl shadow-[0_4px_30px_rgba(0,255,0,0.05)]">
            <h2 className="text-xl font-semibold mb-6 text-green-50">Index New Repository</h2>
            <IndexingForm />
          </div>
        </div>

        <div>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold">Your Repositories</h2>
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-lg mb-6">
              {error}
            </div>
          )}

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="glass-panel border border-green-500/20 rounded-xl p-5 h-[200px] animate-pulse">
                  <div className="flex justify-between mb-4">
                    <div className="w-1/2 h-6 bg-green-900/20 border-green-500/20 rounded"></div>
                    <div className="w-16 h-5 bg-green-900/20 border-green-500/20 rounded-full"></div>
                  </div>
                  <div className="w-1/3 h-4 bg-green-900/20 border-green-500/20 rounded mb-6"></div>
                  <div className="w-full h-4 bg-green-900/20 border-green-500/20 rounded mb-2"></div>
                  <div className="w-4/5 h-4 bg-green-900/20 border-green-500/20 rounded mb-4"></div>
                  <div className="w-1/4 h-3 bg-green-900/20 border-green-500/20 rounded mt-auto"></div>
                </div>
              ))}
            </div>
          ) : (
            <RepoGrid repos={repos} onDelete={handleDelete} />
          )}
        </div>
      </div>
    </div>
  );
}
