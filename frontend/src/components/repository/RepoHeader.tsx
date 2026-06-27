import React from 'react';
import { Repository } from '@/types/repository';
import LanguageDot from '../ui/LanguageDot';
import { formatDate } from '@/lib/utils';

interface RepoHeaderProps {
  repo: Repository;
}

export default function RepoHeader({ repo }: RepoHeaderProps) {
  return (
    <div className="border-b border-zinc-800 pb-6 mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold text-white mb-2">
          <span className="text-zinc-400 font-normal">{repo.owner}/</span>
          {repo.repo_name}
        </h1>
        <div className="flex flex-wrap items-center gap-4 text-sm text-zinc-400">
          <div className="flex items-center">
            <LanguageDot language={repo.primary_language} />
            {repo.primary_language || 'Unknown'}
          </div>
          <div className="flex items-center gap-1" title="Stars">
            <span>⭐</span> {repo.stars}
          </div>
          <div className="flex items-center gap-1" title="Forks">
            <span>🍴</span> {repo.forks}
          </div>
          <div className="flex items-center">
            Last indexed: {repo.last_indexed_at ? formatDate(repo.last_indexed_at) : 'Never'}
          </div>
        </div>
      </div>
      <div>
        <a
          href={repo.github_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded-lg font-medium text-sm transition-colors"
        >
          View on GitHub
          <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
        </a>
      </div>
    </div>
  );
}
