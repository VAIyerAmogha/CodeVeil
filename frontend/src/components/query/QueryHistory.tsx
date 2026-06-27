import React, { useEffect, useState } from 'react';
import { getQueries } from '@/lib/api';
import { Query } from '@/types/query';
import { formatDate } from '@/lib/utils';

interface QueryHistoryProps {
  repoId: string;
  onSelect: (query: Query) => void;
}

export default function QueryHistory({ repoId, onSelect }: QueryHistoryProps) {
  const [queries, setQueries] = useState<Query[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    async function loadHistory() {
      try {
        setLoading(true);
        const data = await getQueries(repoId);
        if (isMounted) setQueries(data);
      } catch (err: unknown) {
        if (isMounted) setError(err instanceof Error ? err.message : 'Failed to load history');
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    
    if (repoId) loadHistory();
    
    return () => { isMounted = false; };
  }, [repoId]);

  const getBadgeColor = (type: string) => {
    if (type === 'lookup') return 'bg-emerald-500/20 text-emerald-400';
    if (type === 'explanation') return 'bg-purple-500/20 text-purple-400';
    if (type === 'architectural') return 'bg-orange-500/20 text-orange-400';
    return 'bg-zinc-500/20 text-green-100/60';
  };

  if (error) {
    return (
      <div className="glass-panel border border-green-500/20 rounded-lg p-4 mt-6">
        <h4 className="text-green-100/60 text-sm font-medium mb-2">Recent Queries</h4>
        <div className="text-red-400 text-sm">{error}</div>
      </div>
    );
  }

  return (
    <div className="glass-panel border border-green-500/20 rounded-lg p-4 mt-6">
      <h4 className="text-green-100/60 text-sm font-medium mb-3 flex items-center gap-2">
        Recent Queries
        {!loading && queries.length > 0 && (
          <span className="bg-green-900/20 border-green-500/20 text-green-100/80 text-xs rounded-full px-2 py-0.5">
            {queries.length}
          </span>
        )}
      </h4>
      
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-14 bg-green-900/20 border-green-500/20 rounded-lg animate-pulse"></div>
          ))}
        </div>
      ) : queries.length === 0 ? (
        <div className="text-green-100/40 text-sm py-4 text-center border border-dashed border-green-500/20 rounded-lg">
          No queries yet — ask your first question below
        </div>
      ) : (
        <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
          {queries.map(q => (
            <div 
              key={q.id}
              onClick={() => onSelect(q)}
              className="hover:bg-green-900/20 border-green-500/20 rounded-lg p-3 cursor-pointer transition-colors border border-transparent hover:border-green-500/30"
            >
              <div className="text-sm text-zinc-200 font-medium mb-1 truncate">
                {q.question.length > 60 ? q.question.substring(0, 60) + '...' : q.question}
              </div>
              <div className="flex items-center justify-between mt-2">
                <span className={`text-xs px-2 py-0.5 rounded capitalize ${getBadgeColor(q.query_type)}`}>
                  {q.query_type}
                </span>
                <span className="text-xs text-green-100/40">
                  {formatDate(q.created_at)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
