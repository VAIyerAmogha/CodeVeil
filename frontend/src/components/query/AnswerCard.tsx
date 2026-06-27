import React from 'react';
import ReactMarkdown from 'react-markdown';

interface AnswerCardProps {
  answer: string;
  latencyMs: number;
  queryType: string;
}

export default function AnswerCard({ answer, latencyMs, queryType }: AnswerCardProps) {
  const getBadgeColor = (type: string) => {
    if (type === 'lookup') return 'bg-emerald-500/20 text-emerald-400';
    if (type === 'explanation') return 'bg-purple-500/20 text-purple-400';
    if (type === 'architectural') return 'bg-orange-500/20 text-orange-400';
    return 'bg-zinc-500/20 text-green-100/60';
  };

  return (
    <div className="glass-panel border border-green-500/20 rounded-xl p-6 mb-6">
      <div className="flex items-center justify-between mb-4 pb-4 border-b border-green-500/20">
        <h3 className="text-lg font-medium text-green-50 flex items-center gap-3">
          Answer
          <span className="bg-green-900/20 border-green-500/20 text-green-100/60 text-xs rounded px-2 py-0.5 font-mono font-normal">
            {(latencyMs / 1000).toFixed(1)}s
          </span>
        </h3>
        <span className={`text-xs px-2 py-0.5 rounded capitalize ${getBadgeColor(queryType)}`}>
          {queryType || 'unknown'}
        </span>
      </div>
      
      <div className="prose prose-invert prose-sm max-w-none prose-pre:bg-transparent/60 prose-pre:border prose-pre:border-green-500/20">
        <ReactMarkdown>{answer}</ReactMarkdown>
      </div>
    </div>
  );
}
