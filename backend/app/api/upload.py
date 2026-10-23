# from pathlib import Path
# import shutil
# from app.ingestion import ingest_document

# from fastapi import APIRouter, File, HTTPException, UploadFile

# router = APIRouter()

# UPLOAD_DIRECTORY = Path("data/uploads")

# UPLOAD_DIRECTORY.mkdir(
#     parents=True,
#     exist_ok=True,
# )

# @router.post("/upload")
# def upload_pdf(
#     file: UploadFile = File(...)
# ):
#     if not file.filename.lower().endswith(".pdf"):
#         raise HTTPException(
#         status_code=400,
#         detail="Only PDF files are allowed for now, please wait for the next version update for other document type support."
#     )
#     file_path = UPLOAD_DIRECTORY / file.filename
 
#     if file_path.exists():       
#         raise HTTPException(
#         status_code=409,
#         detail="Document already exists, multiple entry not allowed."
#     )
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(
#         file.file,
#         buffer,

#     )
        
#     ingest_document(
#     file_path=str(file_path)
#     )
        
#     return {
#     "message": "Document uploaded successfully. You can start asking question structly grounded to document",
#     "filename": file.filename,
#     }
 





import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, File, HTTPException, UploadFile
from supabase import create_client

from app.ingestion import ingest_document

load_dotenv()

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
)

BUCKET_NAME = "documents"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


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

    # Read file into memory
    file_data = file.file.read()

    # Maximum 50 MB
    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size must not exceed 50 MB."
        )

    if len(file_data) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
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
        raise HTTPException(
            status_code=409,
            detail="Document already exists or could not be uploaded."
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

    except Exception as e:
        # Roll back Storage upload if ingestion fails
        try:
            supabase.storage.from_(BUCKET_NAME).remove(
                [storage_path]
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail=f"Document ingestion failed: {str(e)}"
        )

    finally:
        # Remove temporary local copy
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

    return {
        "message": "Document uploaded successfully. You can start asking questions strictly grounded to the document.",
        "filename": filename,
    } 