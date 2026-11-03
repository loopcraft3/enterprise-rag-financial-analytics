import io
import os
import tempfile
import traceback
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, File, HTTPException, UploadFile
from pypdf import PdfReader
from supabase import create_client

from app.ingestion import ingest_document
from app.vectorstore import get_connection

load_dotenv()

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
)

BUCKET_NAME = "documents"

# Limits. Defaults keep local development unchanged; set lower values on the deployed demo.
MAX_UPLOAD_MB = float(os.getenv("MAX_UPLOAD_MB", "50"))
MAX_FILE_SIZE = int(MAX_UPLOAD_MB * 1024 * 1024)
MAX_PDF_PAGES = int(os.getenv("MAX_PDF_PAGES", "0"))      # 0 = no page limit
MAX_DOCUMENTS = int(os.getenv("MAX_DOCUMENTS", "0"))      # 0 = no document limit


def count_documents() -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select count(*) from public.documents")
            return cur.fetchone()[0]


@router.post("/upload")
def upload_pdf(
    file: UploadFile = File(...)
):
    # Only PDF files
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # Read at most the limit + 1 byte, so an oversized file is never fully loaded into memory
    file_data = file.file.read(MAX_FILE_SIZE + 1)

    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File size must not exceed {MAX_UPLOAD_MB:g} MB."
        )

    if len(file_data) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    # Page limit (large documents use a lot of memory during semantic chunking)
    if MAX_PDF_PAGES > 0:
        try:
            page_count = len(PdfReader(io.BytesIO(file_data)).pages)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Could not read this PDF. It may be corrupted or password-protected."
            )

        if page_count > MAX_PDF_PAGES:
            raise HTTPException(
                status_code=413,
                detail=f"This demo accepts PDFs up to {MAX_PDF_PAGES} pages (yours has {page_count})."
            )

    # Document limit (keeps the free database small)
    if MAX_DOCUMENTS > 0:
        try:
            if count_documents() >= MAX_DOCUMENTS:
                raise HTTPException(
                    status_code=429,
                    detail="Demo limit reached. Delete a document before uploading another."
                )
        except HTTPException:
            raise
        except Exception:
            print("Document count check failed:\n", traceback.format_exc())
            raise HTTPException(
                status_code=503,
                detail="Database is unavailable right now. Please try again shortly."
            )

    filename = Path(file.filename).name
    storage_path = filename

    # Upload PDF to Supabase Storage
    try:
        supabase.storage.from_(BUCKET_NAME).upload(
            storage_path,
            file_data,
            {
                "content-type": "application/pdf",
                "upsert": False,
            },
        )

    except Exception as e:
        print("Storage upload failed:", repr(e))
        message = str(e).lower()

        if "duplicate" in message or "already exists" in message or "409" in message:
            raise HTTPException(
                status_code=409,
                detail="A document with this name already exists. Rename the file or delete the old one."
            )

        raise HTTPException(
            status_code=502,
            detail="Could not store the file. Please try again."
        )

    # Temporarily save the PDF for the existing ingestion pipeline
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False,
        ) as temp_file:
            temp_file.write(file_data)
            temp_path = temp_file.name

        # Existing RAG ingestion
        ingest_document(
            file_path=temp_path,
            source=f"data/uploads/{filename}",
        )

    except Exception:
        print("Ingestion failed:\n", traceback.format_exc())

        # Roll back Storage upload if ingestion fails
        try:
            supabase.storage.from_(BUCKET_NAME).remove(
                [storage_path]
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail="Document processing failed. Please try a different PDF."
        )

    finally:
        # Remove temporary local copy
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

    return {
        "message": "Document uploaded successfully. You can start asking questions strictly grounded to the document.",
        "filename": filename,
    }