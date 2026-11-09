import os
from uuid import UUID

from fastapi import Header, HTTPException

from app.storage import remove_files, storage_path
from app.vectorstore import purge_expired_documents

# Uploaded documents are deleted automatically after this many hours.
# 0 turns the automatic clean-up off.
DOCUMENT_TTL_HOURS = float(os.getenv("DOCUMENT_TTL_HOURS", "6"))


def get_session_id(x_session_id: str | None = Header(default=None)) -> str:
    """
    Every request from the website carries an X-Session-Id header (a random UUID
    made in the browser). Everything a visitor uploads is stored under it, and
    every search is limited to it.
    """
    try:
        return str(UUID(x_session_id))
    except (TypeError, ValueError, AttributeError):
        raise HTTPException(
            status_code=400,
            detail="Missing or invalid session id. Please refresh the page.",
        )


def purge_expired_sessions() -> int:
    """
    Delete old documents (database rows, chunks and stored PDFs).
    Never raises, so it can run in front of any request.
    """
    if DOCUMENT_TTL_HOURS <= 0:
        return 0

    try:
        expired = purge_expired_documents(DOCUMENT_TTL_HOURS)
        remove_files(storage_path(session, filename) for session, filename in expired)

        if expired:
            print(f"🧹 Removed {len(expired)} expired document(s)")

        return len(expired)

    except Exception as e:
        print("Purge of expired documents failed:", repr(e))
        return 0
