import io
import os
import tempfile
import traceback
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pypdf import PdfReader

from app.ingestion import ingest_document
from app.sessions import get_session_id, purge_expired_sessions
from app.storage import BUCKET_NAME, remove_files, storage_path, supabase
from app.vectorstore import count_all_documents, list_session_documents

router = APIRouter()

# Limits. Defaults keep local development unchanged; set lower values on the deployed demo.
MAX_UPLOAD_MB = float(os.getenv("MAX_UPLOAD_MB", "50"))
MAX_FILE_SIZE = int(MAX_UPLOAD_MB * 1024 * 1024)
MAX_PDF_PAGES = int(os.getenv("MAX_PDF_PAGES", "0"))              # 0 = no page limit
MAX_DOCUMENTS = int(os.getenv("MAX_DOCUMENTS", "0"))              # per chat. 0 = no limit
MAX_TOTAL_DOCUMENTS = int(os.getenv("MAX_TOTAL_DOCUMENTS", "100"))  # whole site. 0 = no limit


@router.post("/upload")
def upload_pdf(
    file: UploadFile = File(...),
    session_id: str = Depends(get_session_id),
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

    filename = Path(file.filename).name

    # Free the space of old chats first (never fails the upload)
    purge_expired_sessions()

    # Per-chat and whole-site limits, and duplicate check
    try:
        existing = [name for name, _ in list_session_documents(session_id)]

        if filename in existing:
            raise HTTPException(
                status_code=409,
                detail="This file is already in this chat. Rename it or delete the old one first."
            )

        if MAX_DOCUMENTS > 0 and len(existing) >= MAX_DOCUMENTS:
            raise HTTPException(
                status_code=429,
                detail=f"A chat can hold up to {MAX_DOCUMENTS} documents. Delete one before uploading another."
            )

        if MAX_TOTAL_DOCUMENTS > 0 and count_all_documents() >= MAX_TOTAL_DOCUMENTS:
            raise HTTPException(
                status_code=503,
                detail="The free demo storage is full right now. Please try again in a few hours."
            )

    except HTTPException:
        raise
    except Exception:
        print("Document check failed:\n", traceback.format_exc())
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable right now. Please try again shortly."
        )

    path = storage_path(session_id, filename)

    # Upload PDF to Supabase Storage. upsert=True replaces a leftover file with the
    # same name; the duplicate check above already uses the database as the truth.
    try:
        supabase.storage.from_(BUCKET_NAME).upload(
            path,
            file_data,
            {
                "content-type": "application/pdf",
                "upsert": "true",
            },
        )

    except Exception as e:
        print("Storage upload failed:", repr(e))

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

        # Existing RAG ingestion, stored for this chat only
        ingest_document(
            file_path=temp_path,
            session_id=session_id,
            source=f"data/uploads/{session_id}/{filename}",
        )

    except Exception:
        print("Ingestion failed:\n", traceback.format_exc())

        # Roll back Storage upload if ingestion fails
        remove_files([path])

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
