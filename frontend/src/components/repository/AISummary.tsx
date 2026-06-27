import React from 'react';

interface AISummaryProps {
  summary: string | undefined | null;
}

export default function AISummary({ summary }: AISummaryProps) {
  return (
    <div className="bg-zinc-900 border border-green-500/20 rounded-xl p-6 border-l-4 border-l-green-400 mb-8">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-white">AI Summary</h3>
        <span className="bg-orange-500/20 text-orange-400 text-xs rounded px-2 py-0.5">
          Powered by Groq
        </span>
      </div>
      {summary ? (
        <p className="text-zinc-300 leading-relaxed text-sm whitespace-pre-wrap">
          {summary}
        </p>
      ) : (
        <p className="text-zinc-500 text-sm italic">
          Summary not yet generated
        </p>
      )}
    </div>
  );
}
