import React, { useState } from 'react';
import { RetrievalScores } from '@/types/query';

interface RetrievalStatsProps {
  scores: RetrievalScores | null;
}

export default function RetrievalStats({ scores }: RetrievalStatsProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (!scores) return null;

  return (
    <div className="mb-8 border border-green-500/20 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3 glass-panel/50 hover:bg-green-900/20 border-green-500/20 transition-colors text-left"
      >
        <span className="text-green-100/40 text-sm font-medium">Retrieval Details</span>
        <svg
          className={`w-4 h-4 text-green-100/40 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      
      {isOpen && (
        <div className="p-4 glass-panel border-t border-green-500/20">
          <table className="w-full text-xs text-green-100/60">
            <tbody>
              <tr className="border-b border-green-500/20/50">
                <td className="py-2 font-medium">BM25 Top Score</td>
                <td className="py-2 text-right font-mono">{scores.bm25_top?.toFixed(4) || 'N/A'}</td>
              </tr>
              <tr className="border-b border-green-500/20/50">
                <td className="py-2 font-medium">Dense Top Score</td>
                <td className="py-2 text-right font-mono">{scores.dense_top?.toFixed(4) || 'N/A'}</td>
              </tr>
              <tr className="border-b border-green-500/20/50">
                <td className="py-2 font-medium">Reranker Top Score</td>
                <td className="py-2 text-right font-mono">{scores.rerank_top?.toFixed(4) || 'N/A'}</td>
              </tr>
              <tr className="border-b border-green-500/20/50">
                <td className="py-2 font-medium">Chunks Retrieved</td>
                <td className="py-2 text-right font-mono">{scores.chunks_retrieved || 0}</td>
              </tr>
              <tr>
                <td className="py-2 font-medium">Chunks Used</td>
                <td className="py-2 text-right font-mono">{scores.chunks_used || 0}</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
