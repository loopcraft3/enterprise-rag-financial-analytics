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

@app.get("/health/db")
def health_db():
    from app.vectorstore import get_connection

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select count(*) from public.chunks")
            count = cur.fetchone()[0]

    return {"status": "healthy", "chunks": count}


app.include_router(upload_router)
app.include_router(documents_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to Custom RAG API"
    }


