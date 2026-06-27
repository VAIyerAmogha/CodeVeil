import React from 'react';
import Link from 'next/link';
import { Repository } from '@/types/repository';
import RepoCard from './RepoCard';

export default function RepoGrid({ repos, onDelete }: { repos: Repository[], onDelete?: (id: string) => void }) {
  if (repos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="text-6xl mb-4">📦</div>
        <h3 className="text-xl font-medium text-zinc-200 mb-2">No repositories indexed yet.</h3>
        <p className="text-green-100/60 mb-6">Start by analyzing your first GitHub repository.</p>
        <Link 
          href="/"
          className="bg-green-600 hover:bg-green-500 text-green-50 font-medium px-6 py-2.5 rounded-lg transition-colors"
        >
          Index a Repository
        </Link>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {repos.map(repo => (
        <RepoCard key={repo.id} repo={repo} onDelete={onDelete} />
      ))}
    </div>
  );
}
