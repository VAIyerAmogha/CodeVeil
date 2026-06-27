import React from 'react';
import { Repository, Job } from '@/types/repository';

interface RepoStatsProps {
  repo: Repository;
  job: Job | null;
}

export default function RepoStats({ repo, job }: RepoStatsProps) {
  const totalChunks = job?.progress?.chunks_generated || 0;
  const filesProcessed = job?.progress?.files_processed || 0;
  const totalFiles = job?.progress?.total_files || 0;
  const functionsExtracted = job?.progress?.functions_extracted || 0;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div className="bg-zinc-900 rounded-lg p-4 text-center border border-zinc-800">
        <div className="text-2xl font-bold text-white">{totalChunks}</div>
        <div className="text-xs text-zinc-400 mt-1">Total Chunks</div>
      </div>
      <div className="bg-zinc-900 rounded-lg p-4 text-center border border-zinc-800">
        <div className="text-2xl font-bold text-white">{filesProcessed} / {totalFiles}</div>
        <div className="text-xs text-zinc-400 mt-1">Files Processed</div>
      </div>
      <div className="bg-zinc-900 rounded-lg p-4 text-center border border-zinc-800">
        <div className="text-2xl font-bold text-white">{functionsExtracted}</div>
        <div className="text-xs text-zinc-400 mt-1">Functions Extracted</div>
      </div>
      <div className="bg-zinc-900 rounded-lg p-4 text-center border border-zinc-800">
        <div className="text-2xl font-bold text-white truncate px-2">{repo.primary_language || 'Unknown'}</div>
        <div className="text-xs text-zinc-400 mt-1">Primary Language</div>
      </div>
    </div>
  );
}
