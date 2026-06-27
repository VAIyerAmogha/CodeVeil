import React, { useState } from 'react';
import { RetrievalScores } from '@/types/query';

interface RetrievalStatsProps {
  scores: RetrievalScores | null;
}

export default function RetrievalStats({ scores }: RetrievalStatsProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (!scores) return null;

  return (
    <div className="mb-8 border border-zinc-800 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3 bg-zinc-900/50 hover:bg-zinc-800 transition-colors text-left"
      >
        <span className="text-zinc-500 text-sm font-medium">Retrieval Details</span>
        <svg
          className={`w-4 h-4 text-zinc-500 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      
      {isOpen && (
        <div className="p-4 bg-zinc-900 border-t border-zinc-800">
          <table className="w-full text-xs text-zinc-400">
            <tbody>
              <tr className="border-b border-zinc-800/50">
                <td className="py-2 font-medium">BM25 Top Score</td>
                <td className="py-2 text-right font-mono">{scores.bm25_top?.toFixed(4) || 'N/A'}</td>
              </tr>
              <tr className="border-b border-zinc-800/50">
                <td className="py-2 font-medium">Dense Top Score</td>
                <td className="py-2 text-right font-mono">{scores.dense_top?.toFixed(4) || 'N/A'}</td>
              </tr>
              <tr className="border-b border-zinc-800/50">
                <td className="py-2 font-medium">Reranker Top Score</td>
                <td className="py-2 text-right font-mono">{scores.rerank_top?.toFixed(4) || 'N/A'}</td>
              </tr>
              <tr className="border-b border-zinc-800/50">
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
