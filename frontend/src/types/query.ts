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
  confidence: number;           // 0-100, multi-factor score from server
  confidence_level: string;     // "high" | "medium" | "low" | "none"
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
