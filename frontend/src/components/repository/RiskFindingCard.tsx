import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { RiskFinding } from '@/types/repository';
import { Citation } from '@/types/query';
import CitationList from '@/components/query/CitationList';

export default function RiskFindingCard({
  finding,
  onCitationClick
}: {
  finding: RiskFinding;
  onCitationClick: (citation: Citation) => void;
}) {
  const [expanded, setExpanded] = useState(finding.severity === 'CRITICAL' || finding.severity === 'HIGH');

  const severityColors = {
    CRITICAL: 'bg-red-500/20 text-red-400 border-red-500/30',
    HIGH: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    MEDIUM: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    LOW: 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30',
    NONE: 'bg-green-500/20 text-green-400 border-green-500/30'
  };

  return (
    <div className="glass-panel border border-green-500/20 rounded-xl overflow-hidden mb-4">
      <div 
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-green-500/5 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3">
          <span className={`px-2.5 py-1 text-xs font-semibold rounded-md border ${severityColors[finding.severity]}`}>
            {finding.severity}
          </span>
          <h4 className="font-medium text-zinc-200">{finding.category}</h4>
        </div>
        <svg 
          className={`w-5 h-5 text-zinc-400 transform transition-transform ${expanded ? 'rotate-180' : ''}`} 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
      
      {expanded && (
        <div className="p-4 pt-0 border-t border-green-500/10">
          <div className="text-sm mt-4 mb-4">
            <ReactMarkdown
              components={{
                h1: ({node, ...props}) => <h1 className="text-xl font-bold text-green-300 mt-5 mb-3 border-b border-green-500/30 pb-2" {...props} />,
                h2: ({node, ...props}) => <h2 className="text-lg font-semibold text-green-300 mt-4 mb-2 border-b border-green-500/20 pb-1" {...props} />,
                h3: ({node, ...props}) => <h3 className="text-md font-medium text-emerald-300 mt-3 mb-2" {...props} />,
                p: ({node, ...props}) => <p className="text-green-50/90 leading-relaxed mb-3" {...props} />,
                ul: ({node, ...props}) => <ul className="list-disc list-outside ml-5 mb-3 text-green-50/80 marker:text-green-500" {...props} />,
                ol: ({node, ...props}) => <ol className="list-decimal list-outside ml-5 mb-3 text-green-50/80 marker:text-green-500" {...props} />,
                li: ({node, ...props}) => <li className="mb-1" {...props} />,
                code: ({node, inline, className, children, ...props}: any) => {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline ? (
                    <div className="rounded-md border border-green-500/30 bg-black/60 overflow-hidden my-3">
                      {match && <div className="bg-green-900/40 text-green-300 text-xs px-3 py-1 border-b border-green-500/30 font-mono uppercase">{match[1]}</div>}
                      <pre className="p-3 overflow-x-auto text-sm text-green-100 font-mono">
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
                blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-green-500/50 pl-4 py-1 italic bg-green-900/10 text-green-200/80 my-3 rounded-r-md" {...props} />,
                a: ({node, ...props}) => <a className="text-emerald-400 hover:text-emerald-300 hover:underline transition-colors" {...props} />,
                strong: ({node, ...props}) => <strong className="font-semibold text-green-200" {...props} />
              }}
            >
              {finding.answer}
            </ReactMarkdown>
          </div>
          {finding.citations && finding.citations.length > 0 && (
            <div className="mt-4">
              <h5 className="text-xs font-semibold text-zinc-500 mb-2 uppercase tracking-wider">Evidence</h5>
              <CitationList citations={finding.citations} onCitationClick={onCitationClick} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
