import { useState, useEffect, useCallback, useRef } from 'react';
import { indexRepo, getRepoStatus } from '@/lib/api';
import { JobProgress } from '@/types/repository';

export type IndexingState = 'idle' | 'submitting' | 'polling' | 'complete' | 'failed';

export function useIndexing() {
  const [state, setState] = useState<IndexingState>('idle');
  const [repoId, setRepoId] = useState<string | null>(null);
  const [progress, setProgress] = useState<JobProgress | null>(null);
  const [jobStatus, setJobStatus] = useState<string>('pending');
  const [error, setError] = useState<string | null>(null);
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const clearPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const reset = useCallback(() => {
    clearPolling();
    setState('idle');
    setRepoId(null);
    setProgress(null);
    setJobStatus('pending');
    setError(null);
  }, [clearPolling]);

  const submit = useCallback(async (url: string) => {
    try {
      reset();
      setState('submitting');
      const res = await indexRepo(url);
      setRepoId(res.repo_id);
      setState('polling');
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to submit repository';
      setError(errorMessage);
      setState('failed');
    }
  }, [reset]);

  useEffect(() => {
    if (state === 'polling' && repoId) {
      intervalRef.current = setInterval(async () => {
        try {
          const statusRes = await getRepoStatus(repoId);
          setJobStatus(statusRes.status);
          setProgress(statusRes.progress);
          
          if (statusRes.status === 'complete') {
            setState('complete');
            clearPolling();
          } else if (statusRes.status === 'failed') {
            setError(statusRes.error || 'Indexing failed');
            setState('failed');
            clearPolling();
          }
        } catch (err: unknown) {
          const errorMessage = err instanceof Error ? err.message : 'Failed to fetch status';
          setError(errorMessage);
          setState('failed');
          clearPolling();
        }
      }, 2000);
    }

    return () => {
      clearPolling();
    };
  }, [state, repoId, clearPolling]);

  return { state, jobStatus, progress, error, repoId, submit, reset };
}
