# Plan.md — CodeVeil Build Plan

> One task per Claude Code session. Read CLAUDE.md first. Update CLAUDE.md + mark [DONE] after each task.

**Session prompt template:**
> "Read CLAUDE.md and Plan.md. Complete the task marked as current. Update CLAUDE.md when done."

---

## BUILD ORDER

Auth and database connections come last. Build the working product core first.

1. Backend skeleton
2. Ingestion pipeline (clone → AST chunk → index) ← core product
3. Query pipeline (classify → retrieve → rerank → respond) ← core product
4. Frontend (full UI)
5. Auth (JWT + Google OAuth)
6. Database wiring (MongoDB Atlas + ChromaDB persistence)
7. Polish, evaluation, history, profile
8. Deployment

---

## PHASE 1 — BACKEND SKELETON

### 1.1 FastAPI init + config
**Files:** `main.py`, `config.py`, `.env`, `requirements.txt`
- FastAPI app, CORS, Pydantic BaseSettings for all env vars
- `GET /health` → `{"status": "ok"}`
- requirements.txt: fastapi uvicorn motor chromadb pydantic-settings python-dotenv groq sentence-transformers rank-bm25 tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript tree-sitter-java gitpython passlib python-jose httpx pytest pytest-asyncio

**✓ Done when:** `uvicorn app.main:app --reload` starts. `/health` → 200.

---

### 1.2 DB singletons
**Files:** `db/mongodb.py`, `db/chromadb.py`
- MongoDB: async Motor singleton using Atlas URL from env, `get_database()`
- ChromaDB: client singleton, `get_chroma_client()`
- Update `/health` to ping both → `{"mongodb":"ok","chromadb":"ok"}`

**✓ Done when:** `/health` returns both green with Atlas connected.

---

### 1.3 DB models
**Files:** `db/models/user.py`, `repository.py`, `job.py`, `chunk.py`
- Pydantic models matching all schemas in CLAUDE.md exactly

**✓ Done when:** All models importable with no errors.

---

### 1.4 Next.js init + layout
**Files:** `frontend/` scaffold, `tailwind.config.ts`, `layout.tsx`, `components/layout/`
- Next.js 14 App Router + TypeScript + Tailwind dark mode
- Colors: primary #2563EB, success #22C55E, warning #F59E0B · Inter font · black/green gradient bg
- Sidebar, Navbar, PageWrapper components
- Zustand installed · authStore + repoStore scaffolds
- `frontend/.env.local` with NEXT_PUBLIC_API_URL

**✓ Done when:** `npm run dev` → dark page loads. `npm run build` → 0 errors.

---

## PHASE 2 — INGESTION PIPELINE

### 2.1 GitHub cloner + language detector
**Files:** `ingestion/cloner.py`, `ingestion/language_detector.py`, `services/github.py`
- cloner: validate URL (strict regex), path traversal protection, gitpython clone to temp dir
- language_detector: extension → language, marks Python/JS/TS/Java as AST-supported
- github service: fetch stars, forks, languages, file_count via GitHub API

**✓ Done when:** Valid URL clones. Invalid URLs raise. Language detected correctly.

---

### 2.2 AST chunker — Python + JS
**Files:** `ingestion/ast_chunker.py` (Python + JS only)
- tree-sitter extract functions, classes, docstrings as atomic units
- Never cut mid-body · every chunk has: file_path, start_line, end_line, language, parent_class, function_name, chunk_type

**✓ Done when:** Correct chunks + full metadata for .py and .js files. [DONE]

---

### 2.3 AST chunker — TS + Java + fallback
**Files:** update `ast_chunker.py`, `ingestion/fallback_chunker.py`
- Add TS + Java grammars
- fallback_chunker: character split for unsupported langs ONLY — never for Python/JS/TS/Java

**✓ Done when:** All 4 langs use AST. Unknown lang falls back. [DONE]

---

### 2.4 Enricher
**Files:** `ingestion/enricher.py`
- AsyncGroq client pool (llama-3.1-8b-instant) with round-robin key cycling
- Concurrent processing using asyncio.gather with rate limiting
- Only for function chunks with no docstring → one-line summary
- Caching: MongoDB summaries_cache by sha256 to avoid redundant API calls
- Toggle: Disabled by default (ENABLE_ENRICHMENT=False) to prevent rate limit bottlenecks during demo
- On error: return None, don't crash

**✓ Done when:** Generates summaries for undocumented functions (when enabled) and caches them. [DONE]

---

### 2.5 Indexer
**Files:** `ingestion/indexer.py`
- bge-small-en-v1.5 singleton loaded at module level
- Embed chunks → write to ChromaDB (one collection per repo_id)
- Build BM25 index → save to disk
- Store chunk metadata in MongoDB chunks collection
- SHA256 cache — skip unchanged files on re-index

**✓ Done when:** After indexing: ChromaDB has vectors, MongoDB has chunk docs, BM25 file on disk.

---

### 2.6 Job tracking + ingestion routes
**Files:** `services/indexing_job.py`, `api/routes/repositories.py`
- indexing_job: create job, update progress, status transitions
- `POST /repositories/index` → validate URL, create job, run pipeline as background task, return job_id immediately
- `GET /repositories/{repo_id}/status` → live job progress

**✓ Done when:** POST returns job_id instantly. GET shows live progress. Completion stored in MongoDB.

---

## PHASE 3 — QUERY PIPELINE

### 3.1 Classifier
**Files:** `retrieval/classifier.py`
- Zero-shot to llama-3.1-8b-instant via Groq
- Returns: lookup | explanation | architectural
- Default to "explanation" on error

**✓ Done when:** Correct type for test queries of each category.

---

### 3.2 BM25 + dense retrievers
**Files:** `retrieval/bm25_retriever.py`, `retrieval/dense_retriever.py`
- bm25: load index from disk → top-20 with scores
- dense: bge-small-en-v1.5 singleton + ChromaDB → top-20 with scores

**✓ Done when:** Both return 20 results with scores.

---

### 3.3 Hybrid reranker + context builder
**Files:** `retrieval/hybrid.py`, `retrieval/context_builder.py`
- hybrid: merge → dedupe by chunk_id → cross-encoder rerank (always) → top-5 with all 3 scores
- context_builder: architectural queries expand callees depth 2 · all chunks get `# file/path.py:start-end` headers

**✓ Done when:** hybrid → 5 chunks with bm25_score + dense_score + rerank_score. Context has file:line headers.

---

### 3.4 Responder
**Files:** `generation/responder.py`
- llama-3.3-70b-versatile via Groq
- System prompt: every claim must cite `file/path.py:42` · uncitable = omit
- Input: question, context, query_type → Output: answer, citations[{file,line,chunk_id}], chunks_used
- Handle Groq errors without crashing

**✓ Done when:** Returns answer with inline citations for a test query. [DONE]

---

### 3.5 Query service + endpoint
**Files:** `services/query_service.py`, `api/routes/query.py`
- query_service: orchestrate full pipeline, record latency_ms, save to MongoDB queries
- `POST /query` → {repo_id, question} → calls query_service only, returns answer + citations + query_type + retrieval_scores + latency_ms

**✓ Done when:** POST /query returns all fields. MongoDB has new query doc. [DONE]

---

## PHASE 4 — FULL FRONTEND

### 4.1 Auth pages + stores
**Files:** `app/page.tsx`, `auth/login/page.tsx`, `auth/signup/page.tsx`, `store/authStore.ts`, `lib/auth.ts`, `lib/api.ts`
- Landing: hero "Understand Any GitHub Repository in Minutes", login CTA, GitHub URL input
- Login + Signup forms → call api.ts → store token in authStore → redirect to /dashboard
- api.ts: axios wrapper attaching Bearer token · auth.ts: token get/set/clear only here
- Protected route guard: no token → redirect to /login

**✓ Done when:** Signup → login flow works in browser.

---

### 4.2 Dashboard + indexing UI
**Files:** `app/dashboard/page.tsx`, `components/indexing/`, `hooks/useIndexing.ts`, `store/repoStore.ts`
- Dashboard: URL input → POST /repositories/index → store job_id
- RepoCard: name, owner, stars, forks, language, file count + skeleton
- useIndexing: poll GET status every 2s, stop on complete/failed
- IndexingProgress: live metric bars
- RepoStructure: live folder tree
- On complete: success → auto-redirect to /repository/[id] after 2s

**✓ Done when:** Full indexing flow visible in browser with live updates.

---

### 4.3 Repository Knowledge Hub
**Files:** `app/repository/[id]/page.tsx`, `components/repository/`, `hooks/useRepository.ts`
- HealthOverview: file count, function count, language badges, status
- RepoSummary: AI summary with skeleton
- ArchitectureGraph: react-flow, dark styled, clickable nodes, zoom + pan

**✓ Done when:** Knowledge Hub loads all 3 sections.

---

### 4.4 Query workspace
**Files:** `app/repository/[id]/query/page.tsx`, `components/query/`, `hooks/useQuery.ts`
- 3-panel: QueryInput · AnswerPanel (inline citation markers) · EvidencePanel (file:line list)
- RetrievalStats: query type badge, scores, chunk counts
- CodeViewer: Monaco Editor, citation click → exact line + highlight
- CallFlowGraph: react-flow call flow for architectural/explanation queries

**✓ Done when:** Query → answer → citation click → Monaco at correct line.

---

### 4.5 History, evaluation, profile pages
**Files:** `app/repository/[id]/history/`, `evaluation/`, `app/profile/`
- History: past queries list, pin toggle, click to re-open
- EvalDashboard: MetricsCard grid + run eval button
- Profile: usage stats, repo list with re-index/delete/logs actions

**✓ Done when:** All 3 pages load with correct data and actions work.

---

## PHASE 5 — AUTH

### 5.1 JWT + user model + auth dependency
**Files:** `core/auth/jwt.py`, `db/models/user.py`, `core/auth/dependencies.py`
- jwt.py: create_access_token, decode_access_token (HS256)
- dependencies.py: get_current_user — extracts user from Bearer, 401 on fail

**✓ Done when:** Dependency raises 401 on bad/missing token.

---

### 5.2 Auth routes
**Files:** `api/routes/auth.py`
- POST /auth/signup · POST /auth/login · GET /auth/google · GET /auth/google/callback
- No logic in route handler — calls services only

**✓ Done when:** signup + login work. OAuth redirect reachable.

---

### 5.3 Wire auth onto all routes
- Apply dependencies.py guard to all non-auth routes
- Frontend: confirm api.ts sends token on every request

**✓ Done when:** Protected endpoints return 401 without token.

---

## PHASE 6 — DATABASE WIRING

### 6.1 MongoDB Atlas persistence
- Confirm all collections write correctly to Atlas
- Verify indexes on: repositories.user_id, chunks.repo_id, queries.user_id

**✓ Done when:** Atlas dashboard shows all collections with data.

---

### 6.2 ChromaDB persistence + BM25 disk
- Confirm ChromaDB collections persist across restarts
- Confirm BM25 indexes load correctly from disk on restart

**✓ Done when:** Restart server → existing repo queryable without re-indexing.

---

## PHASE 7 — EVALUATION + MANAGEMENT

### 7.1 Evaluation backend + UI
**Files:** `evaluation/golden_dataset.json`, `evaluation/ragas_runner.py`, `api/routes/evaluation.py`
- 20 hand-labeled QA pairs from FastAPI + LangChain repos
- POST /evaluation/run · GET /evaluation/results
- EvalDashboard shows: Context Precision, Context Recall, Faithfulness, Answer Relevance, Latency, Coverage

**✓ Done when:** Eval runs, returns RAGAS scores, dashboard shows them.

---

### 7.2 Repo management backend
**Files:** update `api/routes/repositories.py`, `api/routes/users.py`
- GET/PATCH /users/me · POST /repositories/{id}/reindex · DELETE /repositories/{id} · GET /repositories/{id}/logs

**✓ Done when:** All 5 endpoints work.

---

## PHASE 8 — TESTING + POLISH

### 8.1 Backend tests
**Files:** `tests/test_ingestion.py`, `test_retrieval.py`, `test_query.py`
- Ingestion: URL validation, AST completeness, fallback never for Python/JS/TS/Java
- Retrieval: BM25→20, hybrid→5, scores attached
- Query: POST /query returns all required fields

**✓ Done when:** `pytest tests/ -v` all pass.

---

### 8.2 Frontend polish + E2E
- Dark mode consistency · Inter font everywhere · mobile responsive
- Full flow: signup → index → query → citations → history

**✓ Done when:** 0 visual inconsistencies. Full flow works.

---

## PHASE 9 — DEPLOYMENT

### 9.1 Backend
- FastAPI → Railway or Render · MongoDB Atlas (already configured) · ChromaDB self-hosted

### 9.2 Frontend
- Next.js → Vercel · Set NEXT_PUBLIC_API_URL to production backend

**✓ Done when:** Production URL loads, full flow completes.

---

## STATUS TRACKER

| Task | Status |
|---|---|
| 1.1 FastAPI init | DONE |
| 1.2 DB singletons | DONE |
| 1.3 DB models | DONE |
| 1.4 Next.js + layout | DONE |
| 2.1 Cloner + language detector | DONE |
| 2.2 AST chunker Python+JS | DONE |
| 2.3 AST chunker TS+Java+fallback | DONE |
| 2.4 Enricher | DONE |
| 2.5 Indexer | DONE |
| 2.6 Job tracking + routes | DONE |
| 3.1 Classifier | DONE |
| 3.2 BM25 + dense retrievers | DONE |
| 3.3 Hybrid + context builder | DONE |
| 3.4 Responder | DONE |
| 3.5 Query service + endpoint | DONE |
| 4.1 Auth pages + stores | DONE |
| 4.2 Dashboard + indexing UI | DONE |
| 4.3 Knowledge Hub | DONE |
| 4.4 Query workspace | DONE |
| 4.6 Query workspace | DONE |
| 4.7 Interactive Code Viewer | DONE |
| 4.8 Query History | DONE |
| Design: Black + Green Glassmorphism | DONE |
| 5.1 JWT + user model | IN PROGRESS |
| 5.2 Auth routes | TODO |
| 5.3 Wire auth | TODO |
| 6.1 MongoDB Atlas persistence | TODO |
| 6.2 ChromaDB + BM25 persistence | TODO |
| 7.1 Evaluation | TODO |
| 7.2 Repo management | TODO |
| 8.1 Backend tests | TODO |
| 8.2 Frontend polish + E2E | TODO |
| 9.1 Backend deploy | TODO |
| 9.2 Frontend deploy | TODO |