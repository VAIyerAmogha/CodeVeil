"use client";

import React from 'react';
import Link from 'next/link';
import { useRepository } from '@/hooks/useRepository';
import RepoGrid from '@/components/repository/RepoGrid';

export default function DashboardPage() {
  const { repos, loading, error } = useRepository();

  return (
    <div className="min-h-screen bg-black text-white p-6 md:p-10">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Your Repositories</h1>
          <Link 
            href="/"
            className="bg-zinc-800 hover:bg-zinc-700 text-zinc-100 font-medium px-4 py-2 rounded-lg transition-colors text-sm"
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
              <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 h-[200px] animate-pulse">
                <div className="flex justify-between mb-4">
                  <div className="w-1/2 h-6 bg-zinc-800 rounded"></div>
                  <div className="w-16 h-5 bg-zinc-800 rounded-full"></div>
                </div>
                <div className="w-1/3 h-4 bg-zinc-800 rounded mb-6"></div>
                <div className="w-full h-4 bg-zinc-800 rounded mb-2"></div>
                <div className="w-4/5 h-4 bg-zinc-800 rounded mb-4"></div>
                <div className="w-1/4 h-3 bg-zinc-800 rounded mt-auto"></div>
              </div>
            ))}
          </div>
        ) : (
          <RepoGrid repos={repos} />
        )}
      </div>
    </div>
  );
}
