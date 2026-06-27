"use client";

import React from 'react';
import Link from 'next/link';
import { useRepository } from '@/hooks/useRepository';
import RepoGrid from '@/components/repository/RepoGrid';
import { deleteRepo } from '@/lib/api';

export default function DashboardPage() {
  const { repos, loading, error, refetch } = useRepository();

  const handleDelete = async (id: string) => {
    try {
      await deleteRepo(id);
      refetch();
    } catch (err: unknown) {
      alert("Failed to delete repository");
    }
  };

  return (
    <div className="min-h-screen bg-transparent text-green-50 p-6 md:p-10">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Your Repositories</h1>
          <Link 
            href="/"
            className="bg-green-900/20 border-green-500/20 hover:bg-green-800/40 text-zinc-100 font-medium px-4 py-2 rounded-lg transition-colors text-sm"
          >
            + Index New Repo
          </Link>
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
  );
}
