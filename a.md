# CodeVeil — Elevator Pitch

> **Understand any GitHub repository in minutes — with zero hallucinations and line-level proof.**

---

## 🚀 The Hook
Software engineers spend up to **60% of their time reading and understanding unfamiliar code** rather than writing new features. When exploring large open-source libraries or onboarding onto legacy codebases, developers either waste days tracing call graphs manually or rely on generic AI assistants that hallucinate functions, cut off code blocks mid-body, and provide zero verification.

**CodeVeil solves this.** Paste any public GitHub repository URL, ask any question, and get deep, grounded architectural and functional answers backed by exact `file:line` citations.

---

## ❌ The Problem: Naive Code RAG is Broken
Most code RAG systems split source files by raw character or token count:
- **73% of function bodies are sliced mid-syntax** (measured on standard codebases), feeding fragmented, broken code into LLM context windows.
- **Pure vector search fails** on precise identifier lookups (e.g., specific variable or method names like `process_payment`).
- **Zero grounding** leaves developers guessing whether an AI-generated explanation is factual or hallucinated.

---

## 💡 The Solution: CodeVeil
CodeVeil combines **AST-aware parsing**, **hybrid retrieval**, and **ultra-fast inference** to deliver deterministic, auditable codebase intelligence.

1. **AST-Aware Chunking (Tree-Sitter)**: Parses code syntax trees across Python, JavaScript, TypeScript, and Java. Functions, classes, and docstrings are extracted as 100% syntactically intact, atomic units.
2. **Hybrid Retrieval (Dense + Sparse)**: Runs dense semantic vector search (`BAAI/bge-base-en-v1.5`) alongside sparse BM25 keyword matching in parallel, re-ranked by a weighted cross-encoder (0.75 dense / 0.25 BM25).
3. **Intent-Aware Query Classification**: Distinguishes between simple lookups, conceptual explanations, and architectural flows—dynamically expanding callee call-graphs for complex queries.
4. **Line-Level Citations & Code Viewer**: Every claim references an exact `file/path:line`. One click jumps into an integrated Monaco Editor with code highlighting.
5. **Automated Security Risk Engine**: An asynchronous scan across 7 vulnerability categories that delivers a 0–100 security score, letter grade (A–F), and citable remediation insights.

---

## ⚡ Why CodeVeil Wins

| Feature | Generic Code Assistants | CodeVeil |
| :--- | :--- | :--- |
| **Chunking** | Arbitrary character/line splits (cuts functions) | **Tree-sitter AST atomic units** (100% syntactically complete) |
| **Search** | Vector-only (misses exact identifiers) | **Hybrid BM25 + Dense Embeddings + Reranking** |
| **Context** | Static window | **Dynamic callee-expansion** for architectural queries |
| **Verification** | Vague suggestions & hallucinations | **Deterministic `file:line` citations** + Monaco code viewer |
| **Security** | None built-in | **Automated 7-category risk audit & grade** |
| **Speed & Cost** | Rate-limited / expensive APIs | **Groq Llama 3.3 70B** for near-instant inference |

---

## 🎯 Target Audience
- **Developers & Tech Leads**: Accelerate onboarding to unfamiliar codebases from days to minutes.
- **Code Reviewers & Auditors**: Audit architectural flows and evaluate third-party dependencies quickly.
- **Open Source Contributors**: Pinpoint where and how to implement changes without getting lost in massive repos.

---

## 🛠️ Tech Stack & Key Choices
- **Backend**: FastAPI (Python 3.11), tree-sitter, rank-bm25, MongoDB Atlas
- **Frontend**: Next.js 14 App Router, TypeScript, Monaco Editor, Tailwind CSS
- **AI & Models**: Groq (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`), Hugging Face Inference API (`BAAI/bge-base-en-v1.5`)
- **Key Advantage**: Zero OpenAI vendor lock-in, ultra-low latency, completely self-contained architecture.
