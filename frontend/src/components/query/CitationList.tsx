import React from 'react';
import { Citation } from '@/types/query';

interface CitationListProps {
  citations: Citation[];
  onCitationClick: (citation: Citation) => void;
}

export default function CitationList({ citations, onCitationClick }: CitationListProps) {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="mb-6">
      <h4 className="text-sm font-medium text-zinc-400 mb-3 flex items-center gap-2">
        Sources
        <span className="bg-zinc-800 text-zinc-300 text-xs rounded-full px-2 py-0.5">
          {citations.length}
        </span>
      </h4>
      <div className="flex flex-wrap gap-2">
        {citations.map((citation, idx) => {
          // Extract filename from the full path
          const filename = citation.file.split('/').pop() || citation.file;
          
          return (
            <button
              key={`${citation.chunk_id}-${idx}`}
              onClick={() => onCitationClick(citation)}
              className="bg-zinc-800 hover:bg-zinc-700 rounded px-3 py-1 text-sm font-mono text-green-400 cursor-pointer transition-colors border border-transparent hover:border-green-500/30"
            >
              [{filename}:{citation.line}]
            </button>
          );
        })}
      </div>
    </div>
  );
}
