from typing import List, Tuple

from langchain_core.documents import Document

from app.vectorstore import vector_search as pgvector_search
from app.embeddings import get_embedding_model


def vector_search(
    question: str,
    session_id: str,
    k: int = 5,
) -> List[Tuple[Document, float]]:
    """
    Vector similarity search using PostgreSQL + pgvector,
    limited to the documents of one session.
    """

    embedding_model = get_embedding_model()

    return pgvector_search(
        question=question,
        embedding_model=embedding_model,
        k=k,
        session_id=session_id,
    )
