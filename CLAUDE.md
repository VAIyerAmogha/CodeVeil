# CLAUDE.md — CodeVeil

> Read this fully before every session. Update this at the end of every session.

---

## CURRENT STATUS

**Current task:** 2.3 complete  
**Last completed:** ast_chunker.py updated (TS+Java), fallback_chunker.py  
**Next:** 2.4

---

## RECENT COMPLETIONS
_(append after each session)_

- Added backend skeleton files: main.py, config.py, .env, requirements.txt
- ast_chunker.py (Python + JS)
- ast_chunker.py updated (TS+Java), fallback_chunker.py

---

## BLOCKERS
_(append if unresolved)_

---

## DECISIONS LOG
_(format: YYYY-MM-DD: decision — reason)_

2026-06-24: FastAPI chosen, CORS open for dev — aligns backend skeleton with the locked stack and keeps local frontend integration unblocked.
2026-06-25: tree-sitter node positions used for exact line numbers — ensures functions are never cut mid-body as per hard rules.

---

## WHAT IS CODEVEIL

Paste any public GitHub URL → get AI-powered answers with exact file:line citations.
Stack: FastAPI + MongoDB Atlas + ChromaDB + Next.js 14 + Groq + tree-sitter + sentence-transformers.

---

## STACK — LOCKED

| Layer | Choice |
|---|---|
| Backend | FastAPI, Python 3.11 |
| Frontend | Next.js 14 App Router, TypeScript |
| Metadata DB | MongoDB Atlas |
| Vector DB | ChromaDB (local) |
| LLM Generation | llama-3.3-70b-versatile via Groq |
| LLM Enrichment/Classification | llama-3.1-8b-instant via Groq |
| Embeddings | BAAI/bge-small-en-v1.5 via sentence-transformers (local) |
| AST Parsing | tree-sitter (Python, JS, TS, Java) |
| Keyword Search | rank-bm25 |
| Reranking | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| State | Zustand |
| Code Viewer | Monaco Editor |
| Styling | Tailwind CSS |
| Auth | JWT + Google OAuth (Phase 5) |

**No OpenAI. Ever.**

---

## UI — LOCKED

Dark mode · Inter font · Primary `#2563EB` · Success `#22C55E` · Warning `#F59E0B` · Background: black/green gradient · Aesthetic: GitHub + Linear + Vercel + Raycast

---

## HARD RULES

1. No OpenAI — all LLM via Groq, all embeddings local
2. AST chunking never replaced with character splitting for Python/JS/TS/Java
3. Cross-encoder reranking never skipped
4. Query classification always runs before retrieval
5. All Groq calls through `responder.py` or `enricher.py` only
6. Embedding model singleton — never re-instantiated per request
7. Embeddings in ChromaDB only · Metadata in MongoDB only
8. No business logic in route handlers
9. Every answer must have file:line citations
10. All frontend API calls through `lib/api.ts` only
11. Auth token only in `lib/auth.ts`
12. No TypeScript `any` types

---

## FOLDER STRUCTURE — LOCKED

```
CodeVeil/
├── backend/
│   ├── app/
│   │   ├── main.py · config.py
│   │   ├── api/routes/ (auth · repositories · query · evaluation · users)
│   │   ├── core/auth/ (jwt · oauth · dependencies)
│   │   ├── ingestion/ (cloner · language_detector · ast_chunker · fallback_chunker · enricher · indexer)
│   │   ├── retrieval/ (classifier · bm25_retriever · dense_retriever · hybrid · context_builder)
│   │   ├── generation/ (responder)
│   │   ├── evaluation/ (golden_dataset.json · ragas_runner)
│   │   ├── db/ (mongodb · chromadb · models/)
│   │   └── services/ (github · indexing_job · query_service)
│   ├── tests/
│   ├── .env
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/ (page · layout · auth · dashboard · repository/[id] · profile)
│   │   ├── components/ (ui · layout · landing · indexing · repository · query · code · evaluation)
│   │   ├── lib/ (api.ts · auth.ts · utils.ts)
│   │   ├── hooks/ (useIndexing · useQuery · useRepository)
│   │   ├── store/ (authStore · repoStore)
│   │   └── types/ (repository · query · user)
│   ├── .env.local · tailwind.config.ts · next.config.ts
└── README.md
```

---

## ENV VARS

**backend/.env**
```
MONGODB_URL=mongodb+srv://...
MONGODB_DB_NAME=codeveil
CHROMA_HOST=localhost
CHROMA_PORT=8001
GROQ_API_KEY=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

**frontend/.env.local**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## MONGODB SCHEMAS

**users** — email, name, password_hash, oauth_provider, oauth_id, created_at, usage{repos_indexed, queries_made, last_active}
**repositories** — user_id, github_url, owner, repo_name, stars, forks, primary_language, languages, file_count, indexed_status(pending/running/complete/failed), last_indexed_at, chroma_collection_id, ai_summary
**jobs** — repo_id, github_url, status, progress{files_processed, functions_extracted, chunks_generated, embeddings_created, total_files}, started_at, completed_at, error
**chunks** — repo_id, file_path, function_name, parent_class, start_line, end_line, language, chunk_type(function/class/docstring/fallback), sha256, summary, chroma_id
**queries** — user_id, repo_id, question, query_type, answer, citations[{file,line,chunk_id}], retrieval_scores{bm25_top,dense_top,rerank_top,chunks_retrieved,chunks_used}, latency_ms, pinned, created_at

---

## LLM ASSIGNMENTS

| Role | Model |
|---|---|
| Generation | llama-3.3-70b-versatile (Groq) |
| Enrichment + Classification | llama-3.1-8b-instant (Groq) |
| Embeddings | BAAI/bge-small-en-v1.5 (local) |
| Reranking | cross-encoder/ms-marco-MiniLM-L-6-v2 (local) |

---

## TEST COMMAND

```bash
cd backend && pytest tests/ -v
```