import React from 'react';
import ReactMarkdown from 'react-markdown';

interface AnswerCardProps {
  answer: string;
  latencyMs: number;
  queryType: string;
}

export default function AnswerCard({ answer, latencyMs, queryType }: AnswerCardProps) {
  const getBadgeColor = (type: string) => {
    if (type === 'lookup') return 'bg-blue-500/20 text-blue-400';
    if (type === 'explanation') return 'bg-purple-500/20 text-purple-400';
    if (type === 'architectural') return 'bg-orange-500/20 text-orange-400';
    return 'bg-zinc-500/20 text-zinc-400';
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-6">
      <div className="flex items-center justify-between mb-4 pb-4 border-b border-zinc-800">
        <h3 className="text-lg font-medium text-white flex items-center gap-3">
          Answer
          <span className="bg-zinc-800 text-zinc-400 text-xs rounded px-2 py-0.5 font-mono font-normal">
            {(latencyMs / 1000).toFixed(1)}s
          </span>
        </h3>
        <span className={`text-xs px-2 py-0.5 rounded capitalize ${getBadgeColor(queryType)}`}>
          {queryType || 'unknown'}
        </span>
      </div>
      
      <div className="prose prose-invert prose-sm max-w-none prose-pre:bg-zinc-950 prose-pre:border prose-pre:border-zinc-800">
        <ReactMarkdown>{answer}</ReactMarkdown>
      </div>
    </div>
  );
}
