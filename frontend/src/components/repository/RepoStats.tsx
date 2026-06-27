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
    <div className="flex flex-col gap-3 mb-8">
      <div className="glass-panel rounded-lg p-4 flex justify-between items-center border border-green-500/20">
        <div className="text-sm font-medium text-green-100/60">Total Chunks</div>
        <div className="text-lg font-bold text-green-50">{totalChunks}</div>
      </div>
      <div className="glass-panel rounded-lg p-4 flex justify-between items-center border border-green-500/20">
        <div className="text-sm font-medium text-green-100/60">Files Processed</div>
        <div className="text-lg font-bold text-green-50">{filesProcessed} / {totalFiles}</div>
      </div>
      <div className="glass-panel rounded-lg p-4 flex justify-between items-center border border-green-500/20">
        <div className="text-sm font-medium text-green-100/60">Functions Extracted</div>
        <div className="text-lg font-bold text-green-50">{functionsExtracted}</div>
      </div>
      <div className="glass-panel rounded-lg p-4 flex justify-between items-center border border-green-500/20">
        <div className="text-sm font-medium text-green-100/60">Primary Language</div>
        <div className="text-lg font-bold text-green-50 px-2">{repo.primary_language || 'Unknown'}</div>
      </div>
    </div>
  );
}
