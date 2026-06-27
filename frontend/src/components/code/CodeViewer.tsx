import React, { useEffect, useState, useRef } from 'react';
import Editor, { useMonaco } from '@monaco-editor/react';
import type { editor } from 'monaco-editor';
import { getFileContent } from '@/lib/api';
import FilePathBreadcrumb from './FilePathBreadcrumb';

interface CodeViewerProps {
  filePath: string;
  repoId: string;
  repoName?: string;
  highlightLine: number | null;
  onClose: () => void;
}

export default function CodeViewer({ filePath, repoId, repoName = "Repository", highlightLine, onClose }: CodeViewerProps) {
  const [content, setContent] = useState<string>('');
  const [language, setLanguage] = useState<string>('plaintext');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const decorationsRef = useRef<string[]>([]);
  const monaco = useMonaco();

  useEffect(() => {
    let isMounted = true;
    
    async function loadFile() {
      try {
        setLoading(true);
        setError(null);
        const res = await getFileContent(repoId, filePath);
        if (isMounted) {
          setContent(res.content);
          setLanguage(res.language);
          setLoading(false);
        }
      } catch (err: unknown) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Could not load file');
          setLoading(false);
        }
      }
    }
    
    if (filePath && repoId) {
      loadFile();
    }
    
    return () => {
      isMounted = false;
    };
  }, [filePath, repoId]);

  useEffect(() => {
    if (editorRef.current && monaco && highlightLine && !loading) {
      const editorInstance = editorRef.current;
      
      // Reveal line in center
      editorInstance.revealLineInCenter(highlightLine);
      
      // Highlight line
      decorationsRef.current = editorInstance.deltaDecorations(decorationsRef.current, [{
        range: new monaco.Range(highlightLine, 1, highlightLine, 1),
        options: { 
          isWholeLine: true, 
          className: 'highlight-line' 
        }
      }]);
    }
  }, [highlightLine, loading, monaco, content]);

  const handleEditorDidMount = (editorInstance: editor.IStandaloneCodeEditor) => {
    editorRef.current = editorInstance;
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden mb-6 flex flex-col shadow-2xl mt-8">
      <div className="flex items-center justify-between px-4 py-3 bg-zinc-950 border-b border-zinc-800">
        <FilePathBreadcrumb filePath={filePath} repoName={repoName} />
        <button 
          onClick={onClose}
          className="text-zinc-400 hover:text-white transition-colors"
          title="Close viewer"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div className="relative" style={{ height: '500px' }}>
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-zinc-900 z-10">
            <div className="flex flex-col items-center">
              <span className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mb-4"></span>
              <span className="text-zinc-400 text-sm font-medium">Loading file...</span>
            </div>
          </div>
        )}
        
        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-zinc-900 z-10">
            <div className="text-red-400 text-center">
              <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <p className="font-medium">{error}</p>
            </div>
          </div>
        )}
        
        {!error && (
          <Editor
            height="500px"
            theme="vs-dark"
            language={language}
            value={content}
            options={{
              readOnly: true,
              minimap: { enabled: false },
              fontSize: 13,
              lineNumbers: 'on',
              scrollBeyondLastLine: false,
              wordWrap: 'on'
            }}
            onMount={handleEditorDidMount}
          />
        )}
      </div>
    </div>
  );
}
