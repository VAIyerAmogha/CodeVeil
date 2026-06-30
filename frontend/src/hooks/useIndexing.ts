import { useState, useEffect, useCallback, useRef } from 'react';
import { indexRepo, getRepoStatus, triggerBatch } from '@/lib/api';
import { JobProgress } from '@/types/repository';

export type IndexingState = 'idle' | 'submitting' | 'polling' | 'complete' | 'failed';

export function useIndexing() {
  const [state, setState] = useState<IndexingState>('idle');
  const [repoId, setRepoId] = useState<string | null>(null);
  const [progress, setProgress] = useState<JobProgress | null>(null);
  const [jobStatus, setJobStatus] = useState<string>('pending');
  const [error, setError] = useState<string | null>(null);
  
  const pollingRef = useRef<boolean>(false);

  const reset = useCallback(() => {
    pollingRef.current = false;
    setState('idle');
    setRepoId(null);
    setProgress(null);
    setJobStatus('pending');
    setError(null);
  }, []);

  useEffect(() => {
    return () => {
      pollingRef.current = false;
    };
  }, []);

  const submit = useCallback(async (url: string) => {
    try {
      reset();
      setState('submitting');
      const res = await indexRepo(url);
      setRepoId(res.repo_id);
      setState('polling');
      
      pollingRef.current = true;
      let isDone = false;
      let retries = 0;
      
      while (pollingRef.current && !isDone) {
        try {
          const batchRes = await triggerBatch(res.job_id);
          const statusRes = await getRepoStatus(res.repo_id);
          
          setJobStatus(statusRes.status);
          setProgress(statusRes.progress);
          
          if (batchRes.done || statusRes.status === 'complete') {
            isDone = true;
            setState('complete');
            pollingRef.current = false;
            break;
          }
          
          if (statusRes.status === 'failed') {
            isDone = true;
            setError(statusRes.error || 'Indexing failed');
            setState('failed');
            pollingRef.current = false;
            break;
          }
          
          retries = 0; // reset on success
          await new Promise(r => setTimeout(r, 500));
        } catch (err: unknown) {
          retries++;
          if (retries > 3) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to process batch';
            setError(errorMessage);
            setState('failed');
            pollingRef.current = false;
            break;
          }
          // Exponential backoff
          await new Promise(r => setTimeout(r, 500 * Math.pow(2, retries - 1)));
        }
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to submit repository';
      setError(errorMessage);
      setState('failed');
      pollingRef.current = false;
    }
  }, [reset]);

  return { state, jobStatus, progress, error, repoId, submit, reset };
}
