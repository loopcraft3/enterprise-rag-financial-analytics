# Indian Financial Document Analytics (RAG)

Ask questions about financial PDFs (GST invoices, Form 16, balance sheets, annual reports) and get answers with page citations. The assistant answers only from the uploaded document and says so when it can't find something.

**Live demo:** <your-live-demo-link>  
**Built by:** Shrushti

> **Credit:** This project is built on top of the open-source [PixelCraftLab/custom-RAG](https://github.com/PixelCraftLab/custom-RAG) (FastAPI + React RAG pipeline with hybrid retrieval). The finance-specific features listed below are my additions.

## What I added to the base project

| Area | Change |
|---|---|
| Document understanding | Detects the document type (GST invoice, Form 16, financial statement, or general) and extracts GSTIN, TAN and assessment/financial year into chunk metadata |
| Chunking | Invoices and Form 16 use larger fixed chunks so tables stay together; statements and reports keep semantic chunking with size caps and merging of tiny chunks |
| Prompting | Rewrote the system prompt for financial analysis: exact figures and units, calculations shown and labelled, no invented period labels (Q1/Q3), no guessed currency, no tax or investment advice |
| Citations | Every chunk is tagged with file and page; answers end with `(file, page N)` and the API returns de-duplicated sources with 1-based page numbers |
| Answer caching | In-memory LRU cache with a 24-hour TTL for repeated standalone questions. The cache key includes the question, a fingerprint of the stored chunks and a hash of the prompt, so re-uploading a document or editing the prompt never serves stale answers |
| Frontend | Markdown rendering for answers (bold, lists, tables) and a fix for text-to-speech reading the formatting symbols aloud |
| Fixes | Diagnosed and fixed storage upload and database setup issues; replaced the "built by" fallback line |

## How it works

```
React + Vite UI
      │  REST
      ▼
FastAPI backend
  ├─ Upload:  PDF → Supabase Storage bucket "documents"
  │           → page loader → document-type detection
  │           → finance-aware chunking → bge-small embeddings (384-d)
  │           → Postgres + pgvector (documents, chunks tables)
  └─ Chat:    question → cache lookup
              → hybrid retrieval (pgvector cosine + BM25, merged with
                Reciprocal Rank Fusion) → top chunks tagged with file/page
              → prompt (history + context + doc-type guide)
              → Groq llama-3.3-70b-versatile (temperature 0)
              → answer + sources
```

**Tech stack:** Python, FastAPI, LangChain, PostgreSQL + pgvector (Supabase), Supabase Storage, BAAI/bge-small-en-v1.5 embeddings, BM25, Groq API, React, Vite, Tailwind CSS.

## Evaluation

I wrote a test set of questions with known answers from a public filing (Apple's condensed quarterly statements): direct lookups, calculations (growth, margin, tax rate, current ratio, free cash flow), a reconciliation question, and out-of-document questions that must be refused.

| Check | Result |
|---|---|
| Answerable questions answered correctly (figure, period, page) | <x / y> |
| Out-of-document questions correctly refused | <x / y> |
| Median response time, uncached | <x> s |
| Median response time, cached | <x> s |

**Failure found during testing:** the model invented a fiscal-quarter label ("Q3") that the document did not contain, and guessed a currency symbol when the PDF text had a garbled one. I fixed both with explicit prompt constraints and re-tested.

## Run it locally

**Prerequisites:** Python 3.12+, Node 20+, a free [Groq API key](https://console.groq.com/keys), and a free [Supabase](https://supabase.com) project.

### 1. Database (Supabase SQL Editor)

```sql
create extension if not exists vector;

create table if not exists public.documents (
  id         bigint generated always as identity primary key,
  filename   text not null unique,
  source     text,
  created_at timestamptz not null default now()
);

create table if not exists public.chunks (
  id          bigint generated always as identity primary key,
  document_id bigint not null references public.documents(id) on delete cascade,
  chunk_index integer not null,
  content     text not null,
  page        integer,
  metadata    jsonb not null default '{}'::jsonb,
  embedding   vector(384) not null,
  unique (document_id, chunk_index)
);

create index if not exists chunks_embedding_idx
  on public.chunks using hnsw (embedding vector_cosine_ops);

alter table public.documents enable row level security;
alter table public.chunks enable row level security;
```

The app also stores conversation history; create the conversation tables used by `backend/app/memory.py` if your database does not have them yet.

Then create a **private Storage bucket named `documents`**.

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:

```
GROQ_API_KEY=your_groq_key
DATABASE_URL=your_supabase_postgres_connection_string
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

`SUPABASE_URL` must be the bare project URL, with no `/rest/v1` and no trailing slash. Never commit `.env` and never expose the service role key to the frontend.

```bash
uvicorn main:app --reload
```

The first start downloads the embedding model. Wait for `Application startup complete`, then open http://127.0.0.1:8000/docs.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173, upload a PDF, wait for the backend to finish processing, and ask questions.

### 4. Tests

```bash
cd backend
pip install pytest
pytest app/test_cache.py
```

## Limitations

- **Scanned PDFs and photos** have no text layer, so they return nothing. OCR is not implemented yet.
- **Tables** are extracted as plain text, so complex multi-column layouts can lose their structure. The model is told to say so when a table looks garbled instead of guessing.
- **Currency symbols** (including ₹) can be lost or garbled by PDF text extraction. The prompt instructs the model not to guess a currency.
- **The cache lives in memory**, per server process, and resets on restart.
- **Free-tier hosting:** the Supabase project pauses after a week of inactivity and the backend host may sleep when idle, so the first request after a quiet period can be slow or need a resume.
- Not financial, tax or legal advice. Answers explain what the uploaded document says.
- Do not upload documents containing real personal data (PAN, salary details) to a public demo.

## Roadmap

Streaming answers, a sources panel in the UI, OCR for scanned documents, structured field extraction for invoices with an automatic taxable-value-plus-tax check, a shared cache, and a connection pool for the database.

## Credits and license

Based on [PixelCraftLab/custom-RAG](https://github.com/PixelCraftLab/custom-RAG), whose README states an MIT license. Finance-specific additions by Shrushti.
