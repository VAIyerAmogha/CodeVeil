import React from 'react';
import Link from 'next/link';
import { Repository } from '@/types/repository';
import StatusBadge from '@/components/ui/StatusBadge';
import LanguageDot from '@/components/ui/LanguageDot';
import { formatDate, truncate } from '@/lib/utils';

export default function RepoCard({ repo }: { repo: Repository }) {
  return (
    <Link 
      href={`/repository/${repo.id}`}
      className="flex flex-col bg-zinc-900 border border-zinc-800 hover:border-zinc-600 rounded-xl p-5 cursor-pointer transition-colors h-[200px]"
    >
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1 overflow-hidden pr-2">
          <h3 className="text-lg font-semibold text-zinc-100 truncate" title={repo.repo_name}>
            {repo.repo_name}
          </h3>
          <p className="text-sm text-zinc-400 truncate">{repo.owner}</p>
        </div>
        <StatusBadge status={repo.indexed_status} />
      </div>

      <div className="flex items-center gap-4 text-xs text-zinc-300 mb-4">
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
      </div>

      <p className="text-zinc-400 text-sm mb-4 line-clamp-2">
        {repo.ai_summary ? truncate(repo.ai_summary, 100) : 'No summary available.'}
      </p>

      <div className="text-xs text-zinc-500 mt-auto">
        Last indexed: {repo.last_indexed_at ? formatDate(repo.last_indexed_at) : 'Never'}
      </div>
    </Link>
  );
}
