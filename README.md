<div align="center">

# CodeVeil

**Understand any GitHub repository in minutes.**

Paste a public GitHub URL. Ask anything. Get grounded answers with exact file:line citations — powered by AST-aware retrieval, hybrid search, and Groq LLMs.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat&logo=next.js)](https://nextjs.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat&logo=mongodb)](https://mongodb.com/atlas)
[![Groq](https://img.shields.io/badge/LLM-Groq-F55036?style=flat)](https://groq.com)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat)](LICENSE)


</div>

---

## What is CodeVeil?

CodeVeil is an AI-powered codebase intelligence platform. Point it at any public GitHub repository and it indexes the entire codebase at the AST level — extracting every function, class, and docstring as a syntactically complete unit. Then ask it anything.

> *"How does the authentication middleware work?"*
> *"What calls `process_payment` and what does it return?"*
> *"Walk me through the request lifecycle."*

Every answer comes with exact `file/path.py:42` citations you can click to open in a built-in code viewer. You can also browse the full indexed repo directly through the built-in file explorer, or run an automated security risk analysis across the codebase.

---

## Why AST chunking?

Most RAG systems split code by character count. This cuts functions mid-body 73% of the time on real codebases (measured on CPython stdlib), producing retrieval units that are syntactically broken and contextually useless.

CodeVeil uses **tree-sitter** to parse every file into its AST and extract functions, classes, and docstrings as atomic units. Every retrieved chunk is syntactically complete — guaranteed.

---

## Features

- **AST-aware indexing** — tree-sitter parsing for Python, JavaScript, TypeScript, Java. Character splitting never used for supported languages.
- **Hybrid retrieval** — BM25 keyword search + dense vector search run in parallel and merged via a weighted cross-encoder rerank (dense × 0.75 + BM25 × 0.25). Always returns the top-5 most relevant chunks.
- **Query classification** — automatically detects lookup, explanation, or architectural queries and adapts retrieval strategy (including callee-expansion context for architectural queries) at runtime.
- **Grounded answers** — every claim in every answer has a `file:line` citation. Uncitable claims are omitted.
- **Security risk analysis** — background-task-driven scan across 7 security categories, producing a weighted 0–100 score, letter grade (A–F), and per-finding severity breakdown with citations back into the code viewer. Runs asynchronously so you can navigate away while it completes.
- **Code Explorer** — browse the full file tree of any indexed repository in a Monaco-powered viewer, independent of the Q&A flow.
- **Citation deep dive** — click any citation to open Monaco Editor at the exact line with highlight.

---

## Tech stack

| Layer | Choice |
|---|---|
| Backend | FastAPI, Python 3.11 |
| Frontend | Next.js 14 App Router, TypeScript |
| Metadata | MongoDB Atlas |
| Vectors | ChromaDB |
| LLM | Groq — `llama-3.3-70b-versatile` (generation), `llama-3.1-8b-instant` (enrichment + classification) |
| Embeddings | `BAAI/bge-base-en-v1.5` (768-dim) via HuggingFace Inference API |
| AST parsing | tree-sitter (Python, JS, TS, Java) |
| Keyword search | rank-bm25 |
| Code viewer | Monaco Editor |
| Auth | JWT + Google OAuth |
| Styling | Tailwind CSS |

---

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Groq API key](https://console.groq.com) (free tier works)
- [MongoDB Atlas](https://mongodb.com/atlas) free cluster
- ChromaDB running locally
- HuggingFace account (for Inference API access used for embeddings)

### 1. Clone the repo

```bash
git clone https://github.com/VAIyerAmogha/CodeVeil.git
cd CodeVeil
```

### 2. Backend setup

```bash
cd backend
pip install -r requirements.txt
```

Copy `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
MONGODB_URL=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/
MONGODB_DB_NAME=codeveil
GROQ_API_KEY=your_groq_key_here
GITHUB_CLIENT_ID=optional_for_higher_rate_limits
GITHUB_CLIENT_SECRET=optional_for_higher_rate_limits
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_secret
JWT_SECRET_KEY=generate_a_random_secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```


Start the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

Verify:

```bash
curl http://localhost:8000/health
# {"mongodb":"ok"}
```

### 3. Frontend setup

```bash
cd frontend
npm install
```

```bash
cp .env.local.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

```bash
npm run dev
# localhost:3000
```

---

## How it works

```
GitHub URL
    │
    ▼
┌─────────────┐
│   Cloner    │  validates URL, clones to temp dir
└──────┬──────┘
       │
    ▼
┌─────────────┐
│ AST Chunker │  tree-sitter → functions, classes, docstrings
└──────┬──────┘
       │
       │
    ▼
┌─────────────────────────────────┐
│           Indexer               │
│  bge-base-en-v1.5 embeddings   │
│  (HuggingFace Inference API)   │
└──────┬──────────────────────────┘
       │
    ▼  (on query)
┌─────────────┐
│ Classifier  │  lookup | explanation | architectural
└──────┬──────┘
       │
    ▼
┌────────────────────────────────┐
│        Hybrid Retrieval        │
│  BM25 + Dense in parallel      │
│    
└──────┬─────────────────────────┘
       │
    ▼
┌─────────────────┐
│ Context Builder │  callee expansion for architectural queries
└──────┬──────────┘
       │
    ▼
┌─────────────┐
│  Responder  │  llama-3.3-70b-versatile → answer + file:line citations
└─────────────┘
```

---

## Project structure

```
CodeVeil/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app + health endpoint
│   │   ├── config.py                # Pydantic settings
│   │   ├── api/routes/              # Route handlers (thin — call services only)
│   │   ├── core/auth/               # JWT, Google OAuth, auth dependency
│   │   ├── ingestion/               # clone → AST chunk → enrich → index
│   │   ├── retrieval/               # classify → BM25 + dense → rerank → context
│   │   ├── generation/              # responder.py — all generation Groq calls
│   │   ├── db/                      # MongoDB + ChromaDB singletons + models
│   │   └── services/                # Business logic layer (incl. risk_analyzer)
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                     # Next.js App Router pages (incl. code/ explorer)
│   │   ├── components/              # UI components by feature
│   │   ├── lib/                     # api.ts + auth.ts (all calls go through here)
│   │   ├── hooks/                   # useIndexing, useQuery, useRepository
│   │   ├── store/                   # Zustand stores
│   │   └── types/                   # TypeScript types
│   └── tailwind.config.ts
└── README.md
```

---

## Architecture decisions

**Why Groq?** Inference speed. `llama-3.3-70b-versatile` at Groq latency makes real-time Q&A feel instant. No OpenAI dependency.

**Why HuggingFace Inference API for embeddings?** Voyage AI's free tier is rate-limited without a payment method, and Gemini's embeddings carry a hard daily request cap. `BAAI/bge-base-en-v1.5` via HuggingFace Inference API has no card-gated rate limit on the free tier; the client handles cold-start 503s and 429 backoff.

---

## Running tests

```bash
cd backend
pytest tests/ -v
```

---

## Roadmap

- [ ] RAGAS evaluation dashboard against a hand-labeled golden dataset
- [ ] Interactive call graph visualization for architectural queries
- [ ] Support for more languages (Go, Rust, Ruby)
- [ ] Private repository support via GitHub App
- [ ] Streaming answers
- [ ] Team workspaces
- [ ] VS Code extension

---

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit: `git commit -m "feat(scope): description"`
4. Push and open a PR

Please read the architecture rules in `CLAUDE.md` before contributing. PRs that introduce OpenAI usage, bypass AST chunking, or add business logic to route handlers will not be merged.

---

<div align="center">
Built by <a href="https://github.com/VAIyerAmogha">Amogha Iyer</a>
</div>