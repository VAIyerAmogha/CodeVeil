"use client";

import React, { useState } from 'react';
import { useIndexing } from '@/hooks/useIndexing';
import IndexingStatus from './IndexingStatus';

export default function IndexingForm() {
  const [url, setUrl] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);

  const { state, submit, progress, jobStatus, error, repoId, reset } = useIndexing();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    const trimmedUrl = url.trim();
    if (!/^https:\/\/github\.com\/[\w.-]+\/[\w.-]+$/.test(trimmedUrl)) {
      setValidationError('Please enter a valid GitHub repository URL starting with https://github.com/owner/repo');
      return;
    }

    submit(trimmedUrl);
  };

  if (state !== 'idle' && state !== 'submitting') {
    return (
      <IndexingStatus
        state={state}
        progress={progress}
        error={error}
        repoId={repoId}
        jobStatus={jobStatus}
        onReset={reset}
      />
    );
  }

  return (
    <form onSubmit={handleSubmit} className="w-full mx-auto max-w-lg mb-4 flex flex-col gap-3">
      <div className="flex flex-col sm:flex-row gap-3">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://github.com/owner/repo"
          className="flex-1 glass-panel border border-green-500/30 focus:border-green-400 focus:outline-none focus:ring-1 focus:ring-green-400 rounded-lg px-4 py-3 text-green-50 placeholder:text-zinc-600 transition-colors"
          required
          disabled={state === 'submitting'}
        />
        <button
          type="submit"
          disabled={state === 'submitting'}
          className="bg-green-600 hover:bg-green-500 text-green-50 font-medium px-6 py-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center min-w-[180px]"
        >
          {state === 'submitting' ? (
            <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2"></span>
          ) : null}
          {state === 'submitting' ? 'Analyzing...' : 'Analyze Repository'}
        </button>
      </div>
      {(validationError || error) && (
        <p className="text-red-400 text-sm text-left px-1">{validationError || error}</p>
      )}
    </form>
  );
}
