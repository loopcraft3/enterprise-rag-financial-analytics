import os
from fastapi import FastAPI
# from app.loader import load_documents
# from app.splitter import split_documents

from app.api.chat import router as chat_router
from app.api.upload import router as upload_router
from app.api.documents import router as documents_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Custom RAG API",
    version="5.2.3",
)

ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

# @app.get("/health/db")
# def health_db():
#     from app.vectorstore import get_connection

#     with get_connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute("select count(*) from public.chunks")
#             count = cur.fetchone()[0]

#     return {"status": "healthy", "chunks": count}

@app.get("/health/db")
def health_db():
    import os
    from urllib.parse import urlparse
    from app.vectorstore import get_connection

    url = os.getenv("DATABASE_URL") or ""
    try:
        p = urlparse(url)
        info = {
            "has_url": bool(url),
            "host": p.hostname,
            "port": p.port,
            "user_prefix": (p.username or "")[:9],
        }
    except Exception as e:
        info = {"has_url": bool(url), "url_parse_error": type(e).__name__}

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("select count(*) from public.chunks")
                count = cur.fetchone()[0]
        return {"status": "healthy", "chunks": count}
    except Exception as e:
        return {"status": "error", "error": str(e)[:300], "connection": info}

app.include_router(upload_router)
app.include_router(documents_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to Custom RAG API"
    }


