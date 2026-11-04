import os
from urllib.parse import quote

# On Render, build DATABASE_URL from the separate DB_* variables so every module sees a valid URL.
# This must run before the app imports below, because they read DATABASE_URL when they load.
if os.getenv("DB_HOST"):
    os.environ["DATABASE_URL"] = (
        f"postgresql://{quote(os.getenv('DB_USER', ''), safe='')}:{quote(os.getenv('DB_PASSWORD', ''), safe='')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'postgres')}?sslmode=require"
    )

import traceback

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.upload import router as upload_router
from app.api.documents import router as documents_router
from app.ratelimit import install_rate_limit  # NEW

app = FastAPI(
    title="Custom RAG API",
    version="5.2.3",
)

install_rate_limit(app)  # NEW: keep this ABOVE the CORS lines below

# Comma-separated list in the ALLOWED_ORIGINS variable; "*" (allow all) when it is not set.
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
app.include_router(upload_router)
app.include_router(documents_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to Custom RAG API"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/health/db")
def health_db():
    """Runs a real database query. Used by the keep-alive job so Supabase stays active."""
    from app.vectorstore import get_connection

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("select count(*) from public.chunks")
                count = cur.fetchone()[0]
    except Exception:
        # Full error goes to the server logs only; visitors see a short message.
        print("HEALTH/DB FAILED:\n", traceback.format_exc())
        raise HTTPException(status_code=503, detail="database unavailable")

    return {"status": "healthy", "chunks": count}