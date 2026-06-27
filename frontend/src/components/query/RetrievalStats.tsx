import React from 'react';
import { RetrievalScores } from '@/types/query';

interface RetrievalStatsProps {
  scores: RetrievalScores | null;
}

export default function RetrievalStats({ scores }: RetrievalStatsProps) {
  if (!scores) return null;

  // Simple heuristic for confidence score
  const calculateConfidence = (score: number) => {
    if (!score) return 0;
    if (score >= 0 && score <= 1) return Math.round(score * 100);
    if (score > 1 && score <= 100) return Math.round(score);
    // Sigmoid for logits
    return Math.round((1 / (1 + Math.exp(-score))) * 100);
  };

  const confidence = calculateConfidence(scores.rerank_top ?? scores.dense_top ?? 0);
  
  // Determine color based on confidence
  let colorClass = 'text-red-400 bg-red-400';
  let borderClass = 'border-red-500/20';
  if (confidence > 70) {
    colorClass = 'text-emerald-400 bg-emerald-400';
    borderClass = 'border-emerald-500/20';
  } else if (confidence > 40) {
    colorClass = 'text-orange-400 bg-orange-400';
    borderClass = 'border-orange-500/20';
  }

  return (
    <div className={`mb-8 border ${borderClass} rounded-lg p-4 glass-panel flex flex-col md:flex-row md:items-center justify-between gap-4`}>
      <div className="flex-1">
        <div className="flex justify-between items-end mb-2">
          <span className="text-sm font-medium text-green-100/80">Response Confidence</span>
          <span className={`text-lg font-bold ${colorClass.split(' ')[0]}`}>{confidence}%</span>
        </div>
        
        {/* Simple Progress Bar Graph */}
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
