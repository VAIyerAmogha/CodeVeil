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
      
      <div className="text-sm">
        <ReactMarkdown
          components={{
            h1: ({node, ...props}) => <h1 className="text-2xl font-bold text-green-300 mt-6 mb-4 border-b border-green-500/30 pb-2" {...props} />,
            h2: ({node, ...props}) => <h2 className="text-xl font-semibold text-green-300 mt-5 mb-3 border-b border-green-500/20 pb-1" {...props} />,
            h3: ({node, ...props}) => <h3 className="text-lg font-medium text-emerald-300 mt-4 mb-2" {...props} />,
            p: ({node, ...props}) => <p className="text-green-50/90 leading-relaxed mb-4" {...props} />,
            ul: ({node, ...props}) => <ul className="list-disc list-outside ml-5 mb-4 text-green-50/80 marker:text-green-500" {...props} />,
            ol: ({node, ...props}) => <ol className="list-decimal list-outside ml-5 mb-4 text-green-50/80 marker:text-green-500" {...props} />,
            li: ({node, ...props}) => <li className="mb-1" {...props} />,
            code: ({node, inline, className, children, ...props}: any) => {
              const match = /language-(\w+)/.exec(className || '');
              return !inline ? (
                <div className="rounded-md border border-green-500/30 bg-black/60 overflow-hidden my-4">
                  {match && <div className="bg-green-900/40 text-green-300 text-xs px-3 py-1 border-b border-green-500/30 font-mono uppercase">{match[1]}</div>}
                  <pre className="p-4 overflow-x-auto text-sm text-green-100 font-mono">
                    <code className={className} {...props}>
                      {children}
                    </code>
                  </pre>
                </div>
              ) : (
                <code className="bg-green-500/10 text-green-300 rounded px-1.5 py-0.5 text-sm font-mono border border-green-500/20" {...props}>
                  {children}
                </code>
              )
            },
            blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-green-500/50 pl-4 py-1 italic bg-green-900/10 text-green-200/80 my-4 rounded-r-md" {...props} />,
            a: ({node, ...props}) => <a className="text-emerald-400 hover:text-emerald-300 hover:underline transition-colors" {...props} />,
            strong: ({node, ...props}) => <strong className="font-semibold text-green-200" {...props} />
          }}
        >
          {answer}
        </ReactMarkdown>
      </div>
    </div>
  );
}
