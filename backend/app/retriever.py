from app.config import DEFAULT_TOP_K
from app.hybrid_retriever import hybrid_retrieve
from app.reranker import rerank


def retrieve_documents(
    session_id: str,
    question: str,
    k: int = DEFAULT_TOP_K,
):
    """
    Retrieve documents from one session using hybrid search, then rerank them.
    """

    documents = hybrid_retrieve(
        question=question,
        k=k,
        session_id=session_id,
    )

    reranked_results = rerank(
        question,
        documents,
    )

    return reranked_results
