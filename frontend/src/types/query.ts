export interface Citation {
  file: string;
  line: number;
  chunk_id: string;
}

export interface RetrievalScores {
  bm25_top: number;
  dense_top: number;
  rerank_top: number;
  chunks_retrieved: number;
  chunks_used: number;
}

export interface Query {
  id: string;
  user_id: string;
  repo_id: string;
  question: string;
  query_type: 'lookup' | 'explanation' | 'architectural';
  answer: string;
  citations: Citation[];
  retrieval_scores: RetrievalScores;
  latency_ms: number;
  pinned: boolean;
  created_at: string;
}
