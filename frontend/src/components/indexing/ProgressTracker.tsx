import React from 'react';
import { JobProgress } from '@/types/repository';

interface ProgressTrackerProps {
  progress: JobProgress | null;
  status: string;
}

export default function ProgressTracker({ progress, status }: ProgressTrackerProps) {
  if (!progress) return null;

  const total = progress.total_files || 1;
  const percentage = Math.min(100, Math.round((progress.files_processed / total) * 100));
  
  const isFailed = status === 'failed';
  const innerColor = isFailed ? 'bg-red-500' : 'bg-green-500';

  return (
    <div className="w-full flex flex-col gap-4 mt-2">
      <div className="w-full bg-green-900/20 border-green-500/20 rounded-full h-2 overflow-hidden">
        <div 
          className={`h-2 rounded-full transition-all duration-500 ${innerColor}`} 
          style={{ width: `${percentage}%` }}
        />
      </div>
      
      <div className="flex flex-col gap-2">
        <div className="flex justify-between text-sm text-green-100/60">
          <span>Files Processed</span>
          <span className="text-zinc-200">{progress.files_processed} / {progress.total_files}</span>
        </div>
        <div className="flex justify-between text-sm text-green-100/60">
          <span>Functions Extracted</span>
          <span className="text-zinc-200">{progress.functions_extracted}</span>
        </div>
        <div className="flex justify-between text-sm text-green-100/60">
          <span>Chunks Generated</span>
          <span className="text-zinc-200">{progress.chunks_generated}</span>
        </div>
        <div className="flex justify-between text-sm text-green-100/60">
          <span>Embeddings Created</span>
          <span className="text-zinc-200">{progress.embeddings_created}</span>
        </div>
      </div>
    </div>
  );
}
