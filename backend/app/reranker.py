import os
import importlib.util

from app.config import RERANK_TOP_K

_HAS_SENTENCE_TRANSFORMERS = importlib.util.find_spec("sentence_transformers") is not None

RERANK_MODE = os.getenv(
    "RERANK_MODE", "cross_encoder" if _HAS_SENTENCE_TRANSFORMERS else "off"
).strip().lower()

if RERANK_MODE != "off" and not _HAS_SENTENCE_TRANSFORMERS:
    print("sentence_transformers not installed: reranking disabled")
    RERANK_MODE = "off"

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