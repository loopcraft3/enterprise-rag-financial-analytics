# Hisaab: ask your financial documents

Ask questions about financial PDFs (GST invoices, Form 16, balance sheets, annual reports) and get answers with page citations. The assistant answers only from the uploaded document and says so when it can't find something.

**Live demo:** https://enterprise-rag-financial-analytics.vercel.app/  
**Built by:** Shrushti Waghmare

<img width="1915" height="820" alt="image" src="https://github.com/user-attachments/assets/249de29c-c321-4512-9ff2-36db441dd093" />

![Uploading image.png…]()


> The backend runs on a free server that sleeps when idle. The first question after a quiet period can take up to a minute. The app only shows a "waking up" note when the server has really been idle.

> **Credit:** This project is built on top of the open-source [PixelCraftLab/custom-RAG](https://github.com/PixelCraftLab/custom-RAG) (FastAPI + React RAG pipeline with hybrid retrieval). The finance-specific features listed below are my additions.

## What I added to the base project

| Area | Change |
|---|---|
| Document understanding | Detects the document type (GST invoice, Form 16, financial statement, or general) and extracts GSTIN, TAN and assessment/financial year into chunk metadata |
| Chunking | Invoices and Form 16 use larger fixed chunks so tables stay together; statements and reports keep semantic chunking with size caps and merging of tiny chunks |
| Prompting | Rewrote the system prompt for financial analysis: exact figures and units, calculations shown and labelled, no invented period labels (Q1/Q3), no guessed currency, no tax or investment advice |
| Citations | Every chunk is tagged with file and page; answers end with `(file, page N)` and the API returns de-duplicated sources with 1-based page numbers |
| Answer caching | In-memory LRU cache with a 24-hour TTL for repeated standalone questions. The cache key includes the question, a fingerprint of that chat's stored chunks and a hash of the prompt, so re-uploading a document or editing the prompt never serves stale answers |
| Private chats | Every visit and every "New chat" gets its own random session id, sent as an `X-Session-Id` header. Uploads, vector search, BM25, the cache and the file list are all limited to it, so a visitor never sees another visitor's files, and a refresh starts empty. "New chat" deletes the chat's files from the server; anything left is deleted automatically after 6 hours |
| Chat history | A History tab lists past chats and lets you read them again. It is saved only in the visitor's own browser (localStorage): questions, answers and page numbers, never the PDFs. Saved chats open read-only, can be deleted one by one or all at once, and the app still works if browser storage is blocked |
| Frontend | Redesigned the whole interface: animated loading states, answers that scroll to their first line, source chips, a cold-start note shown only when the server may be asleep, voice chat, Markdown tables in answers, and an empty-state upload button |
| Abuse protection | In-memory rate limits per visitor (6 questions per minute, 5 uploads per hour) and a daily cap for the whole site, so the free Groq quota cannot be used up. Optional limits on file size, pages and number of files |
| Deployment | Render (FastAPI), Vercel (React), Supabase (Postgres + pgvector + Storage), plus a scheduled GitHub Action that keeps the free database from pausing. Embeddings run with fastembed (ONNX) so the app fits in 512 MB |
| Fixes | Diagnosed and fixed storage upload, database setup, environment-variable and memory issues on the free tier; replaced the "built by" fallback line |

## How it works

```
React + Vite UI  (chat history is kept in the browser only)
      │  REST, every request carries X-Session-Id
      ▼
FastAPI backend
  ├─ Upload:  PDF → Supabase Storage bucket "documents" (path: session id / file name)
  │           → page loader → document-type detection
  │           → finance-aware chunking → bge-small embeddings (384-d)
  │           → Postgres + pgvector (documents, chunks tables)
  └─ Chat:    question → cache lookup
              → hybrid retrieval (pgvector cosine + BM25, merged with
                Reciprocal Rank Fusion), limited to this chat's documents
              → top chunks tagged with file/page
              → prompt (history + context + doc-type guide)
              → Groq llama-3.3-70b-versatile (temperature 0)
              → answer + sources
```

Each chat's documents live under its session id, and search only looks inside it. Old documents and old chat messages are deleted automatically after `DOCUMENT_TTL_HOURS` (6 by default), when someone uploads a file or when the keep-alive job runs.

**Tech stack:** Python, FastAPI, LangChain, PostgreSQL + pgvector (Supabase), Supabase Storage, BAAI/bge-small-en-v1.5 embeddings (fastembed), BM25, Groq API, React, Vite, Tailwind CSS, Framer Motion.

## Evaluation

I wrote a set of 21 questions with known answers from a public filing (Apple's condensed quarterly statements): direct lookups, calculations (growth, margin, tax rate, current ratio, free cash flow), a reconciliation question, and out-of-document questions that must be refused.

| Check | Result |
|---|---|
| Test questions answered correctly (figure, period, page) | **21 / 21** |
| Repeated-question response time with the answer cache | 5.5 s down to 1.6 s (one question, measured on my laptop) |

This is a small test I wrote myself, so it shows the pipeline works on that filing. It is not a general accuracy claim.

**Failure found during testing:** the model invented a fiscal-quarter label ("Q3") that the document did not contain, and guessed a currency symbol when the PDF text had a garbled one. I fixed both with explicit prompt constraints and re-tested.

## Run it locally

**Prerequisites:** Python 3.12+, Node 20+, a free [Groq API key](https://console.groq.com/keys), and a free [Supabase](https://supabase.com) project.

### 1. Database (Supabase SQL Editor)

```sql
create extension if not exists vector;

create table if not exists public.documents (
  id         bigint generated always as identity primary key,
  session_id text,
  filename   text not null,
  source     text,
  created_at timestamptz not null default now()
);

-- one file name per chat (two chats can upload files with the same name)
create unique index if not exists documents_session_filename_key
  on public.documents (session_id, filename);
create index if not exists documents_created_at_idx
  on public.documents (created_at);

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

-- chat memory used by backend/app/memory.py
create table if not exists public.conversations (
  id         uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now()
);

create table if not exists public.conversation_messages (
  id              bigint generated always as identity primary key,
  conversation_id uuid not null references public.conversations(id) on delete cascade,
  role            text not null,
  content         text,
  metadata        jsonb,
  created_at      timestamptz not null default now()
);

alter table public.documents enable row level security;
alter table public.chunks enable row level security;
alter table public.conversations enable row level security;
alter table public.conversation_messages enable row level security;
```

Already have a database from an older version? Run `backend/migrations/001_per_chat_documents.sql` once instead. It adds `session_id` and the per-chat unique rule, and it is safe to run twice.

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

The first start downloads the embedding model. Wait for `Application startup complete`, then open http://127.0.0.1:8000/docs. Endpoints that touch documents need an `X-Session-Id` header containing any UUID (the website sends one automatically).

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173, upload a PDF, wait for the backend to finish processing, and ask questions. To point the website at a deployed backend, set `VITE_API_URL`.

### 4. Tests

```bash
cd backend
pip install pytest
pytest app/test_cache.py
```

## Optional settings (Render environment variables)

| Variable | Default | Meaning |
|---|---|---|
| `ALLOWED_ORIGINS` | `*` | Comma-separated list of website addresses allowed to call the API |
| `CHAT_LIMIT_PER_MIN` | 6 | Questions per visitor per minute |
| `UPLOAD_LIMIT_PER_HOUR` | 5 | Uploads per visitor per hour |
| `DAILY_CHAT_CAP` | 300 | Questions per day for the whole site |
| `MAX_UPLOAD_MB` | 50 | Largest PDF accepted (the live demo uses 5) |
| `MAX_PDF_PAGES` | 0 | Most pages per PDF (0 = no limit) |
| `MAX_DOCUMENTS` | 0 | Most files in one chat (0 = no limit) |
| `MAX_TOTAL_DOCUMENTS` | 100 | Most files stored on the whole site (0 = no limit) |
| `DOCUMENT_TTL_HOURS` | 6 | Documents and chat messages older than this are deleted (0 turns clean-up off) |
| `CACHE_ENABLED` | 1 | Set to 0 to turn the answer cache off |
| `RERANK_MODE` | off if the reranker library is missing | `off` skips the optional cross-encoder reranker |

## Limitations

- **Scanned PDFs and photos** have no text layer, so they return nothing. OCR is not implemented yet.
- **Tables** are extracted as plain text, so complex multi-column layouts can lose their structure. The model is told to say so when a table looks garbled instead of guessing.
- **Currency symbols** (including ₹) can be lost or garbled by PDF text extraction. The prompt instructs the model not to guess a currency.
- **The cache and the rate limits live in memory**, per server process, and reset on restart.
- **There is no login.** A random session id separates visitors. That keeps documents apart, but anyone holding the id could read that chat's documents.
- **Chat history is per browser.** It is saved in the browser's local storage, so it does not follow you to another device, and clearing site data removes it. Saved chats are read-only because the PDFs are not kept; upload them again to ask new questions.
- **Clean-up is lazy.** Expired documents and chat messages are deleted when someone uploads a file or when the keep-alive job runs (every 2 days), so they can stay a little longer than the 6-hour setting. They are never shown to other visitors in the meantime.
- **Free-tier hosting:** the Supabase project pauses after a week of inactivity and the backend host may sleep when idle, so the first request after a quiet period can be slow or need a resume.
- Not financial, tax or legal advice. Answers explain what the uploaded document says.
- Do not upload documents containing real personal data (PAN, salary details) to a public demo.

## Roadmap

Streaming answers, click-through citations that open the PDF page, OCR for scanned documents, structured field extraction for invoices with an automatic taxable-value-plus-tax check, automated retrieval evaluation, Redis for the cache and rate limits, and a connection pool for the database.

## Credits and license

Based on [PixelCraftLab/custom-RAG](https://github.com/PixelCraftLab/custom-RAG), whose README states an MIT license. Finance-specific additions by Shrushti.
