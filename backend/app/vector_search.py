from typing import List, Tuple

from langchain_core.documents import Document
from app.vectorstore import vector_search as pgvector_search
from app.embeddings import get_embedding_model

def vector_search(
    question: str,
    vector_store=None,
    k: int=5,
) -> List[Tuple[Document, float]]:
    """
    Perform vector similarity search using PostgreSQL + pgvector.
    """
    embedding_model = get_embedding_model()

    return pgvector_search(
        question=question,
        embedding_model=embedding_model,
        k=k,
    )

    # return results