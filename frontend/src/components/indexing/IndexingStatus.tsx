import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { JobProgress } from '@/types/repository';
import ProgressTracker from './ProgressTracker';

interface IndexingStatusProps {
  state: 'idle' | 'submitting' | 'polling' | 'complete' | 'failed';
  progress: JobProgress | null;
  error: string | null;
  repoId: string | null;
  jobStatus: string;
  onReset: () => void;
}

export default function IndexingStatus({ state, progress, error, repoId, jobStatus, onReset }: IndexingStatusProps) {
  const router = useRouter();

  useEffect(() => {
    if (state === 'complete' && repoId) {
      const timer = setTimeout(() => {
        router.push(`/repository/${repoId}`);
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [state, repoId, router]);

  if (state === 'polling') {
    return (
      <div className="w-full max-w-lg bg-zinc-900 border border-zinc-800 rounded-xl p-6 text-left">
        <h3 className="text-lg font-medium text-zinc-100 mb-4 flex items-center">
          <span className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full mr-3"></span>
          Indexing Repository...
        </h3>
        <ProgressTracker progress={progress} status={jobStatus} />
      </div>
    );
  }

  if (state === 'complete') {
    return (
      <div className="w-full max-w-lg bg-green-500/10 border border-green-500/20 rounded-xl p-6 flex flex-col items-center justify-center text-center">
        <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center mb-3 text-green-400 text-2xl">
          ✓
        </div>
        <h3 className="text-lg font-medium text-green-400 mb-1">Indexing complete!</h3>
        <p className="text-sm text-zinc-400">Redirecting to knowledge hub...</p>
      </div>
    );
  }

  if (state === 'failed') {
    return (
      <div className="w-full max-w-lg bg-red-500/10 border border-red-500/20 rounded-xl p-6 flex flex-col items-center text-center">
        <div className="w-12 h-12 bg-red-500/20 rounded-full flex items-center justify-center mb-3 text-red-400 text-2xl">
          ✗
        </div>
        <h3 className="text-lg font-medium text-red-400 mb-2">Indexing Failed</h3>
        <p className="text-sm text-zinc-300 mb-6">{error || 'An unknown error occurred during indexing.'}</p>
        <button
          onClick={onReset}
          className="bg-zinc-800 hover:bg-zinc-700 text-white font-medium px-6 py-2 rounded-lg transition-colors text-sm"
        >
          Try Again
        </button>
      </div>
    );
  }

  return null;
}
