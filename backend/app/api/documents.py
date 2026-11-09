import traceback

from fastapi import APIRouter, Depends, HTTPException

from app.sessions import get_session_id
from app.storage import remove_files, storage_path
from app.vectorstore import (
    delete_document_vectors,
    delete_session_documents,
    list_session_documents,
)

router = APIRouter()


@router.get("/documents")
def list_documents(session_id: str = Depends(get_session_id)):
    """The documents uploaded in THIS chat only (a new visit starts empty)."""

    try:
        rows = list_session_documents(session_id)

    except Exception:
        print("Listing documents failed:\n", traceback.format_exc())
        raise HTTPException(
            status_code=503,
            detail="Could not load documents. Please try again.",
        )

    documents = [
        {
            "filename": filename,
            "uploaded_at": created_at.isoformat() if created_at else None,
        }
        for filename, created_at in rows
    ]

    return {
        "total_documents": len(documents),
        "documents": documents,
    }


@router.delete("/documents/{filename}")
def delete_document(
    filename: str,
    session_id: str = Depends(get_session_id),
):
    try:
        deleted = delete_document_vectors(
            session_id=session_id,
            filename=filename,
        )

    except Exception:
        print("Deleting document failed:\n", traceback.format_exc())
        raise HTTPException(
            status_code=503,
            detail="Could not delete the document. Please try again.",
        )

    if deleted == 0:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    remove_files([storage_path(session_id, filename)])

    return {
        "message": "Document deleted successfully.",
        "filename": filename,
    }


@router.delete("/session")
def end_session(session_id: str = Depends(get_session_id)):
    """Called when the visitor starts a new chat: remove everything from the old one."""

    try:
        filenames = delete_session_documents(session_id)

    except Exception:
        print("Ending session failed:\n", traceback.format_exc())
        raise HTTPException(
            status_code=503,
            detail="Could not clear the old chat.",
        )

    remove_files(storage_path(session_id, name) for name in filenames)

    return {"removed": len(filenames)}
