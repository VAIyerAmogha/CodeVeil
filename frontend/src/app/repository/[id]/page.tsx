"use client";

import React, { useEffect, useRef, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { getRepo, getRepoStatus } from '@/lib/api';
import { Repository, Job } from '@/types/repository';
import RepoHeader from '@/components/repository/RepoHeader';
import { useQuery } from '@/hooks/useQuery';
import QueryInput from '@/components/query/QueryInput';
import AnswerCard from '@/components/query/AnswerCard';
import CitationList from '@/components/query/CitationList';
import RetrievalStats from '@/components/query/RetrievalStats';
import QueryHistory from '@/components/query/QueryHistory';
import CodeViewer from '@/components/code/CodeViewer';
import { Citation } from '@/types/query';
import RiskReport from '@/components/repository/RiskReport';

const PANEL_W = 320;

export default function RepositoryPage() {
  const { id } = useParams() as { id: string };

  const [repo, setRepo] = useState<Repository | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [activeTab, setActiveTab] = useState<'history' | 'risks'>('history');
  const [chatOpen, setChatOpen] = useState(false);
  const [spotlightInView, setSpotlightInView] = useState(true);
  // Track viewport size to switch between push (desktop) and overlay (mobile)
  const [isMobile, setIsMobile] = useState(false);

  const spotlightRef = useRef<HTMLElement>(null);

  const {
    state: queryState,
    answer,
    citations,
    retrievalScores,
    queryType,
    latencyMs,
    error: queryError,
    submit: submitQuery,
    setResult,
  } = useQuery();

  // Detect mobile breakpoint
  useEffect(() => {
    const mql = window.matchMedia('(max-width: 767px)');
    setIsMobile(mql.matches);
    const handler = (e: MediaQueryListEvent) => {
      setIsMobile(e.matches);
      // Close panel when resizing to desktop to avoid stale overlay state
      if (!e.matches) setChatOpen(false);
    };
    mql.addEventListener('change', handler);
    return () => mql.removeEventListener('change', handler);
  }, []);

  // Always start with the left panel closed when entering or restoring this page.
  useEffect(() => {
    setChatOpen(false);
    setActiveTab('history');
    setSelectedCitation(null);
  }, [id]);

  useEffect(() => {
    function onPageShow(event: PageTransitionEvent) {
      if (event.persisted) {
        setChatOpen(false);
        setActiveTab('history');
        setSelectedCitation(null);
      }
    }

    window.addEventListener('pageshow', onPageShow);
    return () => window.removeEventListener('pageshow', onPageShow);
  }, []);

  // IntersectionObserver: show right panel when spotlight scrolls out of view
  useEffect(() => {
    const el = spotlightRef.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => setSpotlightInView(entry.isIntersecting),
      { threshold: 0 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [loading]);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [repoData, jobData] = await Promise.all([
          getRepo(id),
          getRepoStatus(id).catch(() => null),
        ]);
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
    if (id) fetchData();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-transparent p-6 md:p-10">
        <div className="max-w-5xl mx-auto">
          <div className="h-20 glass-panel rounded-lg animate-pulse mb-6 border border-green-500/20" />
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {[1,2,3,4].map(i => <div key={i} className="h-24 glass-panel rounded-lg animate-pulse border border-green-500/20" />)}
          </div>
          <div className="h-40 glass-panel rounded-xl animate-pulse border border-green-500/20 mb-8" />
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

  // Right panel: never on mobile
  const rightPanelOpen = !spotlightInView && !isMobile;
  // Left panel pushes content only on desktop
  const leftPx  = (!isMobile && chatOpen) ? PANEL_W : 0;
  const rightPx = rightPanelOpen ? PANEL_W : 0;

  const statsItems = [
    { label: 'Total Chunks',    value: job?.progress?.chunks_generated ?? 0 },
    { label: 'Files Processed', value: `${job?.progress?.files_processed ?? 0} / ${job?.progress?.total_files ?? 0}` },
    { label: 'Functions',       value: job?.progress?.functions_extracted ?? 0 },
    { label: 'Language',        value: repo.primary_language || 'Unknown' },
  ];

  return (
    <div className="min-h-screen bg-transparent text-green-50">

      {/* ── Mobile backdrop for left panel ── */}
      {isMobile && chatOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
          onClick={() => setChatOpen(false)}
        />
      )}

      {/* ── LEFT PANEL (chat / history / risk) ──
          Desktop: width-collapse pushes content.
          Mobile: full-width slide-in overlay above backdrop. */}
      <aside
        aria-hidden={!chatOpen}
        style={{
          width: PANEL_W,
          // Desktop: clip via max-width so it doesn't overflow; Mobile: translate in/out
          transform: isMobile
            ? (chatOpen ? 'translateX(0)' : `translateX(-${PANEL_W}px)`)
            : (chatOpen ? 'translateX(0)' : `translateX(-${PANEL_W}px)`),
        }}
        className={[
          'fixed left-0 top-16 bottom-0 z-50 flex flex-col bg-black/70 backdrop-blur-xl border-r border-green-500/20 overflow-hidden transition-transform duration-300 ease-in-out',
          chatOpen ? 'pointer-events-auto' : 'pointer-events-none',
        ].join(' ')}
      >
        <div className="flex flex-col h-full p-5 overflow-hidden" style={{ width: PANEL_W }}>
          {/* close */}
          <div className="flex justify-end mb-3 flex-shrink-0">
            <button id="close-chat-panel" aria-label="Close panel" onClick={() => setChatOpen(false)}
              className="p-1.5 rounded-lg text-green-100/50 hover:text-green-100 hover:bg-green-500/10 transition-colors">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          {/* tabs */}
          <div className="flex border-b border-green-500/20 mb-4 flex-shrink-0">
            {(['history','risks'] as const).map(tab => (
              <button key={tab} id={`tab-${tab}`} onClick={() => setActiveTab(tab)}
                className={['flex-1 px-2 py-2 text-xs font-medium transition-colors border-b-2',
                  activeTab === tab ? 'text-green-300 border-green-500' : 'text-green-50/50 border-transparent hover:text-green-50/80',
                ].join(' ')}>
                {tab === 'history' ? 'History' : 'Risk'}
              </button>
            ))}
          </div>
          {/* content */}
          <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-green-500/20 pb-6">
            {activeTab === 'history'
              ? <QueryHistory repoId={id} onSelect={setResult} />
              : <RiskReport repoId={id} onCitationClick={(c) => setSelectedCitation(c)} />}
          </div>
        </div>
      </aside>

      {/* ── RIGHT PANEL (stats + summary) — desktop only ── */}
      <aside
        aria-hidden={!rightPanelOpen}
        style={{ width: rightPanelOpen ? PANEL_W : 0 }}
        className="hidden md:flex fixed right-0 top-16 bottom-0 z-40 flex-col bg-black/70 backdrop-blur-xl border-l border-green-500/20 overflow-hidden transition-all duration-300 ease-in-out"
      >
        <div style={{ width: PANEL_W }} className="flex flex-col h-full p-5 overflow-y-auto scrollbar-thin scrollbar-thumb-green-500/20">
          <p className="text-xs font-semibold text-green-300 uppercase tracking-widest mb-4 flex-shrink-0">Repository</p>
          <div className="grid grid-cols-2 gap-2 mb-4">
            {statsItems.map(({ label, value }) => (
              <div key={label} className="glass-panel border border-green-500/20 rounded-xl p-3 flex flex-col gap-1">
                <span className="text-[10px] font-medium text-green-100/50 uppercase tracking-wider">{label}</span>
                <span className="text-base font-bold text-green-50">{value}</span>
              </div>
            ))}
          </div>
          <div className="glass-panel border border-green-500/30 border-l-4 border-l-green-400 rounded-xl p-4 relative overflow-hidden">
            <div className="flex items-center gap-2 mb-2">
              <span className="inline-flex items-center justify-center w-6 h-6 rounded-lg bg-green-500/15 text-green-400">
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.347.347a3.5 3.5 0 00-1.041 2.483V19a2 2 0 01-2 2h-2.586a2 2 0 01-2-2v-.618A3.5 3.5 0 006.05 16.23l-.347-.347z" />
                </svg>
              </span>
              <h2 className="text-sm font-semibold text-green-200">AI Summary</h2>
            </div>
            {repo.ai_summary
              ? <p className="text-green-100/80 leading-relaxed text-xs whitespace-pre-wrap">{repo.ai_summary}</p>
              : <p className="text-green-100/40 text-xs italic">Summary not yet generated</p>}
          </div>
        </div>
      </aside>

      {/* ── MAIN — padding pushes content on desktop; full-width on mobile ── */}
      <main
        style={{
          paddingLeft:  leftPx,
          paddingRight: rightPx,
          transition: 'padding 300ms ease-in-out',
        }}
        className="min-h-screen flex flex-col"
      >
        <div className="mx-auto w-full max-w-3xl px-4 md:px-10 py-6 md:py-8">

          {/* Header + toggle */}
          <div className="flex items-start gap-3 mb-6 md:mb-8">
            <div className="flex-1 min-w-0">
              <RepoHeader repo={repo} />
            </div>
            {/* Toggle button: icon-only on mobile, icon+label on desktop */}
            <button
              id="toggle-chat-panel"
              aria-label={chatOpen ? 'Close panel' : 'Open panel'}
              onClick={() => setChatOpen(v => !v)}
              className={[
                'flex-shrink-0 mt-1 flex items-center gap-2 px-3 md:px-4 py-2 rounded-lg border text-sm font-medium transition-all duration-200',
                chatOpen
                  ? 'bg-green-500/20 border-green-400/40 text-green-300 hover:bg-green-500/30'
                  : 'bg-black/40 border-green-500/30 text-green-100/70 hover:bg-green-900/30 hover:text-green-200',
              ].join(' ')}
            >
              <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-3 3z" />
              </svg>
              <span className="hidden md:inline">
                {chatOpen ? 'Hide Panel' : 'Show Panel'}
              </span>
            </button>
          </div>

          {/* ── SPOTLIGHT: Stats + AI Summary ── */}
          <section ref={spotlightRef} aria-label="Repository overview" className="mb-6 md:mb-8">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
              {statsItems.map(({ label, value }) => (
                <div key={label} className="glass-panel border border-green-500/20 rounded-xl p-3 md:p-4 flex flex-col gap-1 hover:border-green-400/40 transition-colors">
                  <span className="text-[10px] md:text-xs font-medium text-green-100/50 uppercase tracking-wider">{label}</span>
                  <span className="text-lg md:text-xl font-bold text-green-50">{value}</span>
                </div>
              ))}
            </div>
            <div className="glass-panel border border-green-500/30 border-l-4 border-l-green-400 rounded-xl p-4 md:p-6 relative overflow-hidden">
              <div className="absolute -top-10 -right-10 w-48 h-48 bg-green-500/5 rounded-full blur-3xl pointer-events-none" />
              <div className="flex items-center gap-2 mb-3">
                <span className="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-green-500/15 text-green-400">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.347.347a3.5 3.5 0 00-1.041 2.483V19a2 2 0 01-2 2h-2.586a2 2 0 01-2-2v-.618A3.5 3.5 0 006.05 16.23l-.347-.347z" />
                  </svg>
                </span>
                <h2 className="text-base font-semibold text-green-200">AI Summary</h2>
              </div>
              {repo.ai_summary
                ? <p className="text-green-100/80 leading-relaxed text-sm whitespace-pre-wrap relative z-10">{repo.ai_summary}</p>
                : <p className="text-green-100/40 text-sm italic">Summary not yet generated</p>}
            </div>
          </section>

          {/* ── QUERY WORKSPACE ── */}
          <section aria-label="Query workspace">
            <QueryInput state={queryState} queryType={queryType} error={queryError} onSubmit={(q) => submitQuery(id, q)} />
            {queryState === 'answered' && (
              <>
                <AnswerCard answer={answer} latencyMs={latencyMs} queryType={queryType} confidenceLevel={retrievalScores?.confidence_level ?? 'high'} />
                <CitationList citations={citations} onCitationClick={(c) => setSelectedCitation(c)} />
                {selectedCitation && (
                  <CodeViewer filePath={selectedCitation.file} highlightLine={selectedCitation.line} repoId={id} repoName={repo.repo_name} onClose={() => setSelectedCitation(null)} />
                )}
                <RetrievalStats scores={retrievalScores} />
              </>
            )}
          </section>

        </div>
      </main>
    </div>
  );
}
