import React, { useState, useEffect } from 'react';
import { RiskReport as RiskReportType } from '@/types/repository';
import { Citation } from '@/types/query';
import { getRisks, runRisks } from '@/lib/api';
import RiskScoreGauge from './RiskScoreGauge';
import RiskFindingCard from './RiskFindingCard';

const PROGRESS_MESSAGES = [
  "Scanning for secrets...",
  "Checking injection risks...",
  "Reviewing authentication...",
  "Analyzing cryptography...",
  "Checking error handling...",
  "Computing score..."
];

export default function RiskReport({ repoId, onCitationClick }: { repoId: string, onCitationClick: (c: Citation) => void }) {
  const [report, setReport] = useState<RiskReportType | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasRun, setHasRun] = useState(false);
  const [progressMsgIndex, setProgressMsgIndex] = useState(0);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    const fetchStatus = async () => {
      try {
        const data = await getRisks(repoId);
        if (data.status === 'none') {
          setHasRun(false);
          setLoading(false);
        } else if (data.status === 'running') {
          setHasRun(true);
          setLoading(true);
        } else if (data.status === 'complete') {
          setHasRun(true);
          setLoading(false);
          setReport(data);
        } else if (data.status === 'failed') {
          setHasRun(true);
          setLoading(false);
          setError(data.error || 'Analysis failed');
        }
      } catch (err) {
        // ignore errors during polling
      }
    };

    fetchStatus();

    if (loading || (!hasRun && !error && !report)) {
      // Poll initially to see if it's running, or if explicitly loading
      interval = setInterval(fetchStatus, 5000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [repoId, loading, hasRun, error, report]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (loading) {
      interval = setInterval(() => {
        setProgressMsgIndex(prev => (prev + 1) % PROGRESS_MESSAGES.length);
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [loading]);

  const runAnalysis = async () => {
    setHasRun(true);
    setLoading(true);
    setError(null);
    try {
      await runRisks(repoId);
    } catch (err: any) {
      setError(err.message || 'Failed to start analysis');
      setLoading(false);
    }
  };

  if (!hasRun) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center glass-panel border border-green-500/20 rounded-xl">
        <div className="w-16 h-16 rounded-full bg-green-500/10 flex items-center justify-center mb-6">
          <svg className="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <h2 className="text-2xl font-semibold text-zinc-100 mb-3">Security Analysis</h2>
        <p className="text-green-100/60 max-w-md mb-8">
          Run a comprehensive security sweep of this repository to identify potential vulnerabilities, hardcoded secrets, and unsafe coding patterns.
        </p>
        <button
          onClick={runAnalysis}
          className="px-6 py-3 bg-green-500/20 text-green-300 border border-green-500/30 rounded-xl hover:bg-green-500/30 transition-colors font-medium flex items-center gap-2"
        >
          Run Security Analysis
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-16 glass-panel border border-green-500/20 rounded-xl">
        <svg className="animate-spin h-10 w-10 text-green-400 mb-6" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
        </svg>
        <p className="text-lg text-zinc-300 font-medium animate-pulse">{PROGRESS_MESSAGES[progressMsgIndex]}</p>
        <p className="text-sm text-green-100/50 mt-2">This may take a few minutes for large repositories.</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-12 glass-panel border border-red-500/20 rounded-xl bg-red-500/5 text-center">
        <svg className="w-12 h-12 text-red-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 className="text-xl font-medium text-red-200 mb-2">Analysis Failed</h3>
        <p className="text-red-300/70 mb-6 max-w-md">{error}</p>
        <button
          onClick={runAnalysis}
          className="px-5 py-2 bg-red-500/20 text-red-300 border border-red-500/30 rounded-lg hover:bg-red-500/30 transition-colors font-medium"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (!report) return null;

  const sortedFindings = [...report.findings].sort((a, b) => {
    const order = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3, NONE: 4 };
    return order[a.severity] - order[b.severity];
  });

  return (
    <div className="space-y-6">
      <RiskScoreGauge score={report.score} grade={report.grade} />
      
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="flex flex-col items-center p-4 glass-panel border border-red-500/20 rounded-xl">
          <span className="text-3xl font-bold text-red-400">{report.critical_count}</span>
          <span className="text-xs text-zinc-400 uppercase tracking-wider mt-1">Critical</span>
        </div>
        <div className="flex flex-col items-center p-4 glass-panel border border-orange-500/20 rounded-xl">
          <span className="text-3xl font-bold text-orange-400">{report.high_count}</span>
          <span className="text-xs text-zinc-400 uppercase tracking-wider mt-1">High</span>
        </div>
        <div className="flex flex-col items-center p-4 glass-panel border border-yellow-500/20 rounded-xl">
          <span className="text-3xl font-bold text-yellow-400">{report.medium_count}</span>
          <span className="text-xs text-zinc-400 uppercase tracking-wider mt-1">Medium</span>
        </div>
        <div className="flex flex-col items-center p-4 glass-panel border border-zinc-500/20 rounded-xl">
          <span className="text-3xl font-bold text-zinc-400">{report.low_count}</span>
          <span className="text-xs text-zinc-400 uppercase tracking-wider mt-1">Low</span>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-zinc-200 mb-4 flex items-center justify-between">
          <span>Detailed Findings</span>
          <button 
            onClick={runAnalysis}
            className="text-sm font-normal text-green-400/70 hover:text-green-400 px-3 py-1 rounded-md hover:bg-green-500/10 transition-colors"
          >
            Re-analyze
          </button>
        </h3>
        <div className="space-y-3">
          {sortedFindings.map(finding => (
            <RiskFindingCard 
              key={finding.id} 
              finding={finding} 
              onCitationClick={onCitationClick} 
            />
          ))}
        </div>
      </div>
    </div>
  );
}
