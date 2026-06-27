"use client";

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { getRepo, getRepoStatus } from '@/lib/api';
import { Repository, Job } from '@/types/repository';
import RepoHeader from '@/components/repository/RepoHeader';
import RepoStats from '@/components/repository/RepoStats';
import AISummary from '@/components/repository/AISummary';
import { useQuery } from '@/hooks/useQuery';
import QueryInput from '@/components/query/QueryInput';
import AnswerCard from '@/components/query/AnswerCard';
import CitationList from '@/components/query/CitationList';
import RetrievalStats from '@/components/query/RetrievalStats';
import QueryHistory from '@/components/query/QueryHistory';
import CodeViewer from '@/components/code/CodeViewer';
import { Citation } from '@/types/query';

export default function RepositoryPage() {
  const { id } = useParams() as { id: string };
  
  const [repo, setRepo] = useState<Repository | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'history'>('overview');

  const { 
    state: queryState, 
    answer, 
    citations, 
    retrievalScores, 
    queryType, 
    latencyMs, 
    error: queryError, 
    submit: submitQuery,
    setResult
  } = useQuery();

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [repoData, jobData] = await Promise.all([
          getRepo(id),
          getRepoStatus(id).catch(() => null), // Status might fail if no job exists yet
        ]);
        
        // Handle backend returning { repository: ..., stats: ... } vs direct Repository
        const repoResponse = repoData as unknown as { repository?: Repository } | Repository;
        const r = ('repository' in repoResponse && repoResponse.repository) 
          ? repoResponse.repository 
          : (repoResponse as Repository);
          
        setRepo(r);
        setJob(jobData);
      } catch (err: unknown) {
        console.error(err);
        setError('Repository not found');
      } finally {
        setLoading(false);
      }
    }
    
    if (id) {
      fetchData();
    }
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-transparent p-6 md:p-10">
        <div className="max-w-5xl mx-auto">
          {/* Header Skeleton */}
          <div className="h-20 glass-panel rounded-lg animate-pulse mb-6 border border-green-500/20"></div>
          {/* Stats Skeleton */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-24 glass-panel rounded-lg animate-pulse border border-green-500/20"></div>
            ))}
          </div>
          {/* Summary Skeleton */}
          <div className="h-40 glass-panel rounded-xl animate-pulse border border-green-500/20 mb-8"></div>
        </div>
      </div>
    );
  }

  if (error || !repo) {
    return (
      <div className="min-h-screen bg-transparent flex flex-col items-center justify-center p-6 text-center">
        <h2 className="text-2xl font-semibold text-red-400 mb-4">{error || 'Repository not found'}</h2>
        <Link href="/dashboard" className="px-6 py-2 bg-green-900/20 border-green-500/20 hover:bg-green-800/40 text-green-50 rounded-lg transition-colors">
          Return to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-transparent text-green-50 p-6 md:p-10">
      <div className="max-w-[1400px] mx-auto">
        <div className="flex flex-col lg:grid lg:grid-cols-3 lg:gap-8">
          
          {/* Left Column */}
          <div className="lg:col-span-1 flex flex-col h-[calc(100vh-80px)] sticky top-6">
            <RepoHeader repo={repo} />
            
            {/* Tabs */}
            <div className="flex border-b border-green-500/20 mt-4 mb-4">
              <button 
                onClick={() => setActiveTab('overview')}
                className={`px-4 py-2 font-medium transition-colors border-b-2 flex-1 ${activeTab === 'overview' ? 'text-green-300 border-green-500' : 'text-green-50/50 border-transparent hover:text-green-50/80'}`}
              >
                Overview
              </button>
              <button 
                onClick={() => setActiveTab('history')}
                className={`px-4 py-2 font-medium transition-colors border-b-2 flex-1 ${activeTab === 'history' ? 'text-green-300 border-green-500' : 'text-green-50/50 border-transparent hover:text-green-50/80'}`}
              >
                Query History
              </button>
            </div>

            <div className="flex-1 overflow-y-auto pr-2 pb-10 scrollbar-thin scrollbar-thumb-green-500/20">
              {activeTab === 'overview' ? (
                <div className="space-y-6">
                  <RepoStats repo={repo} job={job} />
                  <AISummary summary={repo.ai_summary} />
                </div>
              ) : (
                <QueryHistory repoId={id} onSelect={setResult} />
              )}
            </div>
          </div>
          
          {/* Right Column */}
          <div className="lg:col-span-2 flex flex-col mt-10 lg:mt-0 pt-8 lg:pt-0 border-t lg:border-t-0 border-green-500/20">
            <QueryInput 
              state={queryState} 
              queryType={queryType}
              error={queryError}
              onSubmit={(q) => submitQuery(id, q)} 
            />
            
            {queryState === 'answered' && (
              <>
                <AnswerCard 
                  answer={answer}
                  latencyMs={latencyMs}
                  queryType={queryType}
                />
                <CitationList 
                  citations={citations}
                  onCitationClick={(c) => setSelectedCitation(c)}
                />
                {selectedCitation && (
                  <CodeViewer 
                    filePath={selectedCitation.file}
                    highlightLine={selectedCitation.line}
                    repoId={id}
                    repoName={repo.repo_name}
                    onClose={() => setSelectedCitation(null)}
                  />
                )}
                <RetrievalStats scores={retrievalScores} />
              </>
            )}
          </div>
          
        </div>
      </div>
    </div>
  );
}
