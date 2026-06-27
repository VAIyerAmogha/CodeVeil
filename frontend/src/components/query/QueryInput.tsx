import React, { useState, KeyboardEvent, useRef } from 'react';

interface QueryInputProps {
  state: 'idle' | 'loading' | 'answered' | 'error';
  queryType: string;
  error: string | null;
  onSubmit: (question: string) => void;
}

export default function QueryInput({ state, queryType, error, onSubmit }: QueryInputProps) {
  const [question, setQuestion] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (question.trim() && state !== 'loading') {
      onSubmit(question);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };
  
  const getBadgeColor = (type: string) => {
    if (type === 'lookup') return 'bg-blue-500/20 text-blue-400';
    if (type === 'explanation') return 'bg-purple-500/20 text-purple-400';
    if (type === 'architectural') return 'bg-orange-500/20 text-orange-400';
    return 'bg-zinc-500/20 text-zinc-400';
  };

  return (
    <div className="w-full mb-8">
      <div className="relative">
        <textarea
          ref={textareaRef}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about this repository..."
          className="w-full bg-zinc-900 border border-zinc-700 focus:border-blue-500 rounded-lg p-4 pr-32 text-white resize-none outline-none transition-colors"
          rows={3}
          disabled={state === 'loading'}
        />
        <div className="absolute bottom-4 right-4 flex items-center gap-3">
          <span className="text-zinc-500 text-xs">
            {question.length} chars
          </span>
          <button
            onClick={handleSubmit}
            disabled={state === 'loading' || !question.trim()}
            className="bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-1.5 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {state === 'loading' ? (
              <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2"></span>
            ) : null}
            Send
          </button>
        </div>
      </div>
      
      {state === 'answered' && queryType && (
        <div className="mt-2 flex items-center gap-2">
          <span className="text-zinc-400 text-sm">Identified as:</span>
          <span className={`text-xs px-2 py-0.5 rounded capitalize ${getBadgeColor(queryType)}`}>
            {queryType}
          </span>
        </div>
      )}
      
      {error && (
        <div className="mt-2 text-red-400 text-sm">
          {error}
        </div>
      )}
    </div>
  );
}
