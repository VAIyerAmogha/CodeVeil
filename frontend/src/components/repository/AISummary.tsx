import React from 'react';

interface AISummaryProps {
  summary: string | undefined | null;
}

export default function AISummary({ summary }: AISummaryProps) {
  return (
    <div className="glass-panel border border-green-500/20 rounded-xl p-6 border-l-4 border-l-green-400 mb-8">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-green-50">AI Summary</h3>

      </div>
      {summary ? (
        <p className="text-green-100/80 leading-relaxed text-sm whitespace-pre-wrap">
          {summary}
        </p>
      ) : (
        <p className="text-green-100/40 text-sm italic">
          Summary not yet generated
        </p>
      )}
    </div>
  );
}
