# from pathlib import Path
# from fastapi import APIRouter, HTTPException
# from datetime import datetime

# # from app.embeddings import get_embedding_model
# from app.vectorstore import delete_document_vectors

# router = APIRouter()

# UPLOAD_DIRECTORY = Path("data/uploads")

# @router.get("/documents")
# def list_documents():
#     documents = []

#     for file in UPLOAD_DIRECTORY.glob("*.pdf"):

#         documents.append(
#             {
#                 "filename": file.name,
#                 "size_kb": round(file.stat().st_size / 1024, 2),
#                 "uploaded_at": datetime.fromtimestamp(
#                     file.stat().st_mtime
#                 ).strftime("%Y-%m-%d %H:%M:%S"),
#             }
#         )

#     return {
#         "total_documents": len(documents),
#         "documents": documents,
#     }





# @router.delete("/documents/{filename}")
# def delete_document(filename: str):

#     file_path = UPLOAD_DIRECTORY / filename

#     if not file_path.exists():
#         raise HTTPException(
#             status_code=404,
#             detail="Document not found."
#         )

#     # embedding_model = get_embedding_model()

#     delete_document_vectors(
#         # embedding_model=embedding_model,
#         source=str(file_path),
#     )

#     file_path.unlink()

#     return {
#         "message": "Document deleted successfully.",
#         "filename": filename,
#     }







import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from supabase import create_client

from app.vectorstore import delete_document_vectors

load_dotenv()

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
)

BUCKET_NAME = "documents"


@router.get("/documents")
def list_documents():
    try:
        files = supabase.storage.from_(BUCKET_NAME).list()

        documents = []

        for file in files:
            filename = file.get("name")

            if not filename or not filename.lower().endswith(".pdf"):
                continue

            size_bytes = file.get("metadata", {}).get("size", 0)

            created_at = file.get("created_at")

            if created_at:
                uploaded_at = created_at
            else:
                uploaded_at = datetime.now(
                    timezone.utc
                ).strftime("%Y-%m-%d %H:%M:%S")

            documents.append(
                {
                    "filename": filename,
                    "size_kb": round(
                        size_bytes / 1024,
                        2,
                    ),
                    "uploaded_at": uploaded_at,
                }
            )

        return {
            "total_documents": len(documents),
            "documents": documents,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not load documents: {str(e)}",
        )


@router.delete("/documents/{filename}")
def delete_document(filename: str):

    # Check that the file exists in Supabase Storage
    try:
        files = supabase.storage.from_(BUCKET_NAME).list()

        filenames = [
            file.get("name")
            for file in files
        ]

        if filename not in filenames:
            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not check document: {str(e)}",
        )

    # Delete vectors/chunks from PostgreSQL
    storage_source = f"data/uploads/{filename}"

    delete_document_vectors(
        source=storage_source,
    )

    # Delete PDF from Supabase Storage
    try:
        supabase.storage.from_(BUCKET_NAME).remove(
            [filename]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not delete file from Storage: {str(e)}",
        )

    return {
        "message": "Document deleted successfully.",
        "filename": filename,
    }