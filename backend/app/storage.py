import os

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
)

BUCKET_NAME = "documents"


def storage_path(session_id, filename: str) -> str:
    """
    Every visitor's PDFs live in their own folder inside the bucket, so two
    visitors can upload files with the same name. Old files uploaded before
    sessions existed have no folder (session_id is None).
    """
    return f"{session_id}/{filename}" if session_id else filename


def remove_files(paths) -> None:
    """Best effort: a failed clean-up is logged but never breaks a request."""
    paths = list(paths)

    if not paths:
        return

    try:
        supabase.storage.from_(BUCKET_NAME).remove(paths)
    except Exception as e:
        print("Storage clean-up failed:", repr(e))
