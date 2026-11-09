from app.vector_search import vector_search
from app.bm25_loader import load_bm25
from app.rrf import reciprocal_rank_fusion


def hybrid_retrieve(
    question: str,
    k: int,
    session_id: str,
):
    """
    Semantic (pgvector) + keyword (BM25) search over one session's documents,
    merged with Reciprocal Rank Fusion.
    """

    dense_results = vector_search(
        question=question,
        session_id=session_id,
        k=k,
    )

    bm25 = load_bm25(session_id)

    if bm25 is None:
        return dense_results[:k]

    bm25_results = bm25.search(
        question,
        k=k,
    )

    fused_results = reciprocal_rank_fusion(
        dense_results,
        bm25_results,
    )

    return fused_results[:k]
