from app.bm25 import BM25Retriever
from app.vectorstore import load_all_documents


def load_bm25(session_id: str):
    """
    Build the BM25 index from one session's documents in PostgreSQL.
    """

    documents = load_all_documents(session_id)

    if not documents:
        return None

    return BM25Retriever(documents)
