import React, { useState } from 'react';
import Link from 'next/link';
import { Repository } from '@/types/repository';
import StatusBadge from '@/components/ui/StatusBadge';
import LanguageDot from '@/components/ui/LanguageDot';
import { formatDate, truncate } from '@/lib/utils';

export default function RepoCard({ repo, onDelete }: { repo: Repository, onDelete?: (id: string) => void }) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setShowDeleteModal(true);
  };

  const confirmDelete = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDeleting(true);
    setShowDeleteModal(false);
    if (onDelete) {
      await onDelete(repo.id);
    }
    setIsDeleting(false);
  };

  const cancelDelete = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setShowDeleteModal(false);
  };

  return (
    <>
      <Link 
        href={`/repository/${repo.id}`}
        className="flex flex-col glass-panel border border-green-500/20 hover:border-green-500/40 rounded-xl p-5 cursor-pointer transition-colors h-[200px]"
      >
        <div className="flex justify-between items-start mb-3">
          <div className="flex-1 overflow-hidden pr-2">
            <h3 className="text-lg font-semibold text-zinc-100 truncate" title={repo.repo_name}>
              {repo.repo_name}
            </h3>
            <p className="text-sm text-green-100/60 truncate">{repo.owner}</p>
          </div>
          <div className="flex items-center gap-2">
            <StatusBadge status={repo.indexed_status} />
            {onDelete && (
              <button
                onClick={handleDeleteClick}
                disabled={isDeleting}
                className="text-red-400/70 hover:text-red-400 hover:bg-red-900/20 p-1.5 rounded-md transition-colors"
                title="Delete Repository"
              >
                {isDeleting ? (
                  <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                )}
              </button>
            )}
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs text-green-100/80 mb-4">
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

        <p className="text-green-100/60 text-sm mb-4 line-clamp-2">
          {repo.ai_summary ? truncate(repo.ai_summary, 100) : 'No summary available.'}
        </p>

        <div className="text-xs text-green-100/40 mt-auto">
          Last indexed: {repo.last_indexed_at ? formatDate(repo.last_indexed_at) : 'Never'}
        </div>
      </Link>

      {showDeleteModal && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
          onClick={cancelDelete}
        >
          <div 
            className="glass-panel border border-green-500/30 p-6 rounded-xl max-w-md w-full shadow-2xl m-4"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-xl font-semibold text-zinc-100 mb-2">Delete Repository</h3>
            <p className="text-green-100/70 mb-6">
              Are you sure you want to delete <span className="text-green-400 font-medium">{repo.repo_name}</span>? This action cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button 
                onClick={cancelDelete}
                className="px-4 py-2 rounded-lg border border-green-500/30 text-green-100/80 hover:bg-green-500/10 transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={confirmDelete}
                className="px-4 py-2 rounded-lg bg-red-500/20 text-red-300 border border-red-500/30 hover:bg-red-500/30 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
