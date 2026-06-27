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
      <div className="glass-panel rounded-lg p-4 text-center border border-green-500/20">
        <div className="text-2xl font-bold text-green-50">{totalChunks}</div>
        <div className="text-xs text-green-100/60 mt-1">Total Chunks</div>
      </div>
      <div className="glass-panel rounded-lg p-4 text-center border border-green-500/20">
        <div className="text-2xl font-bold text-green-50">{filesProcessed} / {totalFiles}</div>
        <div className="text-xs text-green-100/60 mt-1">Files Processed</div>
      </div>
      <div className="glass-panel rounded-lg p-4 text-center border border-green-500/20">
        <div className="text-2xl font-bold text-green-50">{functionsExtracted}</div>
        <div className="text-xs text-green-100/60 mt-1">Functions Extracted</div>
      </div>
      <div className="glass-panel rounded-lg p-4 text-center border border-green-500/20">
        <div className="text-2xl font-bold text-green-50 truncate px-2">{repo.primary_language || 'Unknown'}</div>
        <div className="text-xs text-green-100/60 mt-1">Primary Language</div>
      </div>
    </div>
  );
}
