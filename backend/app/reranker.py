import os

from app.config import RERANK_TOP_K

# "cross_encoder" (default, local) or "off" (free-tier deployment)
RERANK_MODE = os.getenv("RERANK_MODE", "cross_encoder")

_reranker = None


def _get_reranker():
    global _reranker

    if _reranker is None:
        from sentence_transformers import CrossEncoder  # imported only when needed

        _reranker = CrossEncoder("BAAI/bge-reranker-base")

    return _reranker


def rerank(question, documents):
    """
    documents: List[Document]
    Returns: List[(Document, rerank_score)]
    """

    if not documents:
        return []

    if RERANK_MODE == "off":
        # Keep the hybrid-retrieval (RRF) order; scores only reflect rank.
        return [
            (doc, 1.0 / (rank + 1))
            for rank, doc in enumerate(documents[:RERANK_TOP_K])
        ]

    pairs = [(question, doc.page_content) for doc in documents]

    scores = _get_reranker().predict(pairs)

    reranked = [(doc, float(score)) for doc, score in zip(documents, scores)]

    reranked.sort(key=lambda x: x[1], reverse=True)

    return reranked[:RERANK_TOP_K]


# Load the model at startup (as before) unless reranking is turned off.
if RERANK_MODE != "off":
    _get_reranker()