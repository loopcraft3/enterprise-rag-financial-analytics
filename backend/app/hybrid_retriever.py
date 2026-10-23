from app.vector_search import vector_search
from app.bm25_loader import load_bm25
from app.rrf import reciprocal_rank_fusion


def hybrid_retrieve(
    question: str,

    k: int,
):
    dense_results = vector_search(
        question=question,

        k=k,
    )

    bm25 = load_bm25()

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