import React from 'react';
import { RetrievalScores } from '@/types/query';

interface RetrievalStatsProps {
  scores: RetrievalScores | null;
}

export default function RetrievalStats({ scores }: RetrievalStatsProps) {
  if (!scores) return null;

  // Use server-computed multi-factor confidence (dense similarity + coverage + keyword overlap).
  // Fall back to a raw dense_top conversion for older cached queries without the field.
  const confidence = scores.confidence ?? Math.round((scores.dense_top ?? 0) * 100);
  const level = scores.confidence_level ?? (confidence >= 68 ? 'high' : confidence >= 38 ? 'medium' : 'low');

  let colorClass = 'text-red-400 bg-red-400';
  let borderClass = 'border-red-500/20';
  let labelText = 'Low Confidence';

  if (level === 'high') {
    colorClass = 'text-emerald-400 bg-emerald-400';
    borderClass = 'border-emerald-500/20';
    labelText = 'High Confidence';
  } else if (level === 'medium') {
    colorClass = 'text-amber-400 bg-amber-400';
    borderClass = 'border-amber-500/20';
    labelText = 'Moderate Confidence';
  } else if (level === 'none') {
    colorClass = 'text-red-500 bg-red-500';
    borderClass = 'border-red-500/30';
    labelText = 'No Relevant Code Found';
  }

  return (
    <div className={`mb-8 border ${borderClass} rounded-lg p-4 glass-panel flex flex-col md:flex-row md:items-center justify-between gap-4`}>
      <div className="flex-1">
        <div className="flex justify-between items-end mb-2">
          <div className="flex flex-col">
            <span className="text-sm font-medium text-green-100/80">Response Confidence</span>
            <span className="text-[10px] text-green-100/40 uppercase tracking-wider">{labelText}</span>
          </div>
          <span className={`text-lg font-bold ${colorClass.split(' ')[0]}`}>{confidence}%</span>
        </div>

        {/* Progress bar */}
        <div className="h-2 w-full bg-black/40 rounded-full overflow-hidden border border-green-500/10">
          <div
            className={`h-full ${colorClass.split(' ')[1]} transition-all duration-1000 ease-out`}
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>

      <div className="flex gap-4 md:ml-6 mt-2 md:mt-0 pt-3 md:pt-0 border-t md:border-t-0 md:border-l border-green-500/20 md:pl-6 text-center">
        <div className="flex flex-col items-center px-2">
          <span className="text-xl font-bold text-green-50">{scores.chunks_used || 0}</span>
          <span className="text-xs text-green-100/50 mt-1">Chunks Used</span>
        </div>
        <div className="flex flex-col items-center px-2">
          <span className="text-xl font-bold text-green-50">{scores.chunks_retrieved || 0}</span>
          <span className="text-xs text-green-100/50 mt-1">Chunks Found</span>
        </div>
      </div>
    </div>
  );
}
