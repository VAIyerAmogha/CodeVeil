import { useState, useCallback } from 'react';
import { postQuery } from '@/lib/api';
import { Citation, RetrievalScores, Query } from '@/types/query';

export type QueryState = 'idle' | 'loading' | 'answered' | 'error';

export function useQuery() {
  const [state, setState] = useState<QueryState>('idle');
  const [answer, setAnswer] = useState<string>('');
  const [citations, setCitations] = useState<Citation[]>([]);
  const [retrievalScores, setRetrievalScores] = useState<RetrievalScores | null>(null);
  const [queryType, setQueryType] = useState<string>('');
  const [latencyMs, setLatencyMs] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);

  const reset = useCallback(() => {
    setState('idle');
    setAnswer('');
    setCitations([]);
    setRetrievalScores(null);
    setQueryType('');
    setLatencyMs(0);
    setError(null);
  }, []);

  const setResult = useCallback((query: Query) => {
    setAnswer(query.answer);
    setCitations(query.citations || []);
    setRetrievalScores(query.retrieval_scores || null);
    setQueryType(query.query_type || '');
    setLatencyMs(query.latency_ms || 0);
    setError(null);
    setState('answered');
  }, []);

  const submit = useCallback(async (repoId: string, question: string) => {
    if (!question.trim() || !repoId) return;
    
    try {
      reset();
      setState('loading');
      const start = performance.now();
      
      const response = await postQuery(repoId, question);
      
      const end = performance.now();
      
      setAnswer(response.answer);
      setCitations(response.citations || []);
      setRetrievalScores(response.retrieval_scores || null);
      setQueryType(response.query_type || '');
      setLatencyMs(Math.round(end - start));
      setState('answered');
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to query repository';
      setError(errorMessage);
      setState('error');
    }
  }, [reset]);

  return {
    state,
    answer,
    citations,
    retrievalScores,
    queryType,
    latencyMs,
    error,
    submit,
    reset,
    setResult
  };
}
