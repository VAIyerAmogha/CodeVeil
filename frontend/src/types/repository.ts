import { Citation } from './query';

export type IndexingStatus = 'pending' | 'running' | 'complete' | 'failed';

export interface Repository {
  id: string;
  user_id: string;
  github_url: string;
  owner: string;
  repo_name: string;
  stars: number;
  forks: number;
  primary_language: string;
  languages: Record<string, number>;
  file_count: number;
  indexed_status: IndexingStatus;
  last_indexed_at: string | null;
  chroma_collection_id: string | null;
  ai_summary: string | null;
}

export interface JobProgress {
  files_processed: number;
  functions_extracted: number;
  chunks_generated: number;
  embeddings_created: number;
  total_files: number;
}

export interface Job {
  id: string;
  repo_id: string;
  github_url: string;
  status: string;
  progress: JobProgress;
  started_at: string;
  completed_at: string | null;
  error: string | null;
}

export interface Chunk {
  id: string;
  repo_id: string;
  file_path: string;
  function_name: string | null;
  parent_class: string | null;
  start_line: number;
  end_line: number;
  language: string;
  chunk_type: 'function' | 'class' | 'docstring' | 'fallback';
  sha256: string;
  summary: string | null;
  chroma_id: string;
}

export interface RiskFinding {
  id: string;
  category: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'NONE';
  answer: string;
  citations: Citation[];
  weight: number;
}

export interface RiskReport {
  repo_id: string;
  score: number;
  grade: string;
  findings: RiskFinding[];
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  analyzed_at: string;
  status?: string;
  error?: string;
}
