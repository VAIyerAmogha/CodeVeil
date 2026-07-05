"use client";

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import Editor from '@monaco-editor/react';
import type { editor } from 'monaco-editor';
import { getRepo, getFileTree, getFileContent } from '@/lib/api';
import { Repository } from '@/types/repository';
import FileTree from '@/components/code/FileTree';
import FilePathBreadcrumb from '@/components/code/FilePathBreadcrumb';

const SIDEBAR_W = 280;

export default function CodeExplorerPage() {
  const { id } = useParams() as { id: string };

  const [repo, setRepo] = useState<Repository | null>(null);
  const [files, setFiles] = useState<string[]>([]);
  const [loadingMeta, setLoadingMeta] = useState(true);
  const [metaError, setMetaError] = useState<string | null>(null);

  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [fileLanguage, setFileLanguage] = useState<string>('plaintext');
  const [fileLoading, setFileLoading] = useState(false);
  const [fileError, setFileError] = useState<string | null>(null);

  // Mobile: sidebar drawer open/closed
  const [drawerOpen, setDrawerOpen] = useState(false);

  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

  // ── Fetch repo + file list ────────────────────────────────────────────────
  useEffect(() => {
    async function load() {
      try {
        setLoadingMeta(true);
        const [repoData, treeData] = await Promise.all([
          getRepo(id),
          getFileTree(id),
        ]);
        const repoResponse = repoData as unknown as { repository?: Repository } | Repository;
        const r = ('repository' in repoResponse && repoResponse.repository)
          ? repoResponse.repository
          : (repoResponse as Repository);
        setRepo(r);
        setFiles(treeData.files);
      } catch (err: unknown) {
        setMetaError(err instanceof Error ? err.message : 'Failed to load repository');
      } finally {
        setLoadingMeta(false);
      }
    }
    if (id) load();
  }, [id]);

  // ── Open a file ────────────────────────────────────────────────────────────
  const openFile = useCallback(async (path: string) => {
    setDrawerOpen(false); // close drawer on mobile after selecting
    if (path === selectedFile) return;
    setSelectedFile(path);
    setFileError(null);
    setFileLoading(true);
    try {
      const res = await getFileContent(id, path);
      setFileContent(res.content);
      setFileLanguage(res.language);
    } catch (err: unknown) {
      setFileError(err instanceof Error ? err.message : 'Could not load file');
    } finally {
      setFileLoading(false);
    }
  }, [id, selectedFile]);

  // ── Scroll editor to top when a new file opens ────────────────────────────
  useEffect(() => {
    if (editorRef.current && !fileLoading) {
      editorRef.current.setScrollTop(0);
    }
  }, [selectedFile, fileLoading]);

  // ── Close drawer + deselect on Escape ────────────────────────────────────
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        if (drawerOpen) setDrawerOpen(false);
        else setSelectedFile(null);
      }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [drawerOpen]);

  // ── Loading / error states ────────────────────────────────────────────────
  if (loadingMeta) {
    return (
      <div className="min-h-screen bg-transparent flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <span className="animate-spin h-8 w-8 border-4 border-green-500 border-t-transparent rounded-full" />
          <span className="text-green-100/60 text-sm">Loading repository…</span>
        </div>
      </div>
    );
  }

  if (metaError || !repo) {
    return (
      <div className="min-h-screen bg-transparent flex flex-col items-center justify-center gap-4 text-center p-6">
        <p className="text-red-400 text-lg font-semibold">{metaError || 'Repository not found'}</p>
        <Link href="/dashboard" className="px-5 py-2 rounded-lg border border-green-500/30 text-green-100/80 hover:bg-green-500/10 transition-colors text-sm">
          Back to Dashboard
        </Link>
      </div>
    );
  }

  // ── Shared sidebar inner content ──────────────────────────────────────────
  const SidebarContent = (
    <>
      {/* Sidebar header */}
      <div className="flex-shrink-0 px-4 pt-4 pb-3 border-b border-green-500/15">
        <div className="flex items-center justify-between mb-1">
          <span className="text-[10px] font-semibold text-green-300 uppercase tracking-widest">Files</span>
          <Link
            href="/dashboard"
            className="text-[10px] text-green-100/40 hover:text-green-300 transition-colors"
          >
            ← Dashboard
          </Link>
        </div>
        <p className="text-xs text-green-100/60 font-medium truncate">
          {repo.owner}/{repo.repo_name}
        </p>
        <p className="text-[10px] text-green-100/30 mt-0.5">
          {files.length} file{files.length !== 1 ? 's' : ''} indexed
        </p>
      </div>

      {/* Tree scroll area */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden py-2 scrollbar-thin scrollbar-thumb-green-500/20">
        <FileTree
          files={files}
          selectedFile={selectedFile}
          onFileSelect={openFile}
        />
      </div>
    </>
  );

  return (
    <div className="min-h-screen bg-transparent text-green-50 flex flex-col">

      {/* ── DESKTOP: Fixed left sidebar ── */}
      <aside
        style={{ width: SIDEBAR_W }}
        className="hidden md:flex fixed left-0 top-16 bottom-0 z-40 flex-col bg-black/70 backdrop-blur-xl border-r border-green-500/20"
      >
        {SidebarContent}
      </aside>

      {/* ── MOBILE: Backdrop ── */}
      {drawerOpen && (
        <div
          className="md:hidden fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
          onClick={() => setDrawerOpen(false)}
        />
      )}

      {/* ── MOBILE: Drawer sidebar ── */}
      <aside
        style={{ width: SIDEBAR_W }}
        className={[
          'md:hidden fixed left-0 top-16 bottom-0 z-50 flex flex-col bg-black/90 backdrop-blur-xl border-r border-green-500/20',
          'transition-transform duration-300 ease-in-out',
          drawerOpen ? 'translate-x-0' : '-translate-x-full',
        ].join(' ')}
      >
        {SidebarContent}
      </aside>

      {/* ── Main area ── */}
      <main
        style={{ transition: 'padding 300ms ease-in-out' }}
        className="flex-1 flex flex-col min-h-screen md:pl-[280px]"
      >
        {selectedFile ? (
          /* ── File viewer ── */
          <div className="flex flex-col h-screen">
            {/* Toolbar */}
            <div className="flex-shrink-0 flex items-center gap-3 px-4 py-3 border-b border-green-500/20 bg-black/40 backdrop-blur-sm">
              {/* Hamburger — mobile only */}
              <button
                id="toggle-file-tree"
                aria-label="Toggle file tree"
                onClick={() => setDrawerOpen(v => !v)}
                className="md:hidden flex-shrink-0 p-1.5 rounded-md text-green-100/60 hover:text-green-100 hover:bg-green-500/10 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>

              <div className="flex-1 min-w-0">
                <FilePathBreadcrumb filePath={selectedFile} repoName={repo.repo_name} />
              </div>

              <button
                onClick={() => setSelectedFile(null)}
                title="Close file (Esc)"
                className="flex-shrink-0 p-1.5 rounded-md text-green-100/40 hover:text-green-100 hover:bg-green-500/10 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Monaco editor — fills remaining height */}
            <div className="flex-1 relative">
              {fileLoading && (
                <div className="absolute inset-0 z-10 flex items-center justify-center bg-black/60 backdrop-blur-sm">
                  <span className="animate-spin h-7 w-7 border-4 border-green-500 border-t-transparent rounded-full" />
                </div>
              )}
              {fileError && (
                <div className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-2 text-red-400">
                  <svg className="w-10 h-10 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <p className="text-sm font-medium">{fileError}</p>
                </div>
              )}
              {!fileError && (
                <Editor
                  height="100%"
                  theme="vs-dark"
                  language={fileLanguage}
                  value={fileContent}
                  options={{
                    readOnly: true,
                    minimap: { enabled: true },
                    fontSize: 13,
                    lineNumbers: 'on',
                    scrollBeyondLastLine: false,
                    wordWrap: 'off',
                    folding: true,
                    renderLineHighlight: 'all',
                  }}
                  onMount={(ed) => { editorRef.current = ed; }}
                />
              )}
            </div>
          </div>
        ) : (
          /* ── Empty state — no file selected ── */
          <div className="flex-1 flex flex-col items-center justify-center gap-5 text-center px-8">
            {/* Mobile hamburger — shown in empty state too */}
            <button
              id="toggle-file-tree-empty"
              aria-label="Browse files"
              onClick={() => setDrawerOpen(true)}
              className="md:hidden flex items-center gap-2 px-4 py-2 rounded-lg border border-green-500/30 text-green-300 hover:bg-green-500/10 transition-colors text-sm mb-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              Browse Files
            </button>

            <div className="w-16 h-16 rounded-2xl bg-green-500/10 border border-green-500/20 flex items-center justify-center">
              <svg className="w-8 h-8 text-green-400/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-green-50/80 mb-1">Select a file to view</h2>
              <p className="text-sm text-green-100/40">
                Browse the file tree on the left and click any file to open it in the editor.
              </p>
            </div>
            <div className="flex flex-wrap justify-center gap-3 mt-2">
              <Link
                href="/dashboard"
                className="px-4 py-2 rounded-lg border border-green-500/30 text-green-100/70 hover:bg-green-500/10 transition-colors text-sm"
              >
                ← Dashboard
              </Link>
              <Link
                href={`/repository/${id}`}
                className="px-4 py-2 rounded-lg border border-green-500/30 text-green-100/70 hover:bg-green-500/10 transition-colors text-sm"
              >
                Query workspace
              </Link>
              {repo.github_url && (
                <a
                  href={repo.github_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 rounded-lg border border-green-500/30 text-green-100/70 hover:bg-green-500/10 transition-colors text-sm flex items-center gap-1.5"
                >
                  View on GitHub
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
