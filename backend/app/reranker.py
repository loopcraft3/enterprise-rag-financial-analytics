# from sentence_transformers import CrossEncoder
# from app.config import RERANK_TOP_K

# reranker = CrossEncoder(
#     "BAAI/bge-reranker-base"
# )


# def rerank(question, retrieved_results):
#     """
#     retrieved_results:
#         List[(Document, score)]

#     Returns:
#         Reranked List[(Document, rerank_score)]
#     """

#     if not retrieved_results:
#         return []

#     pairs = [
#         (question, doc.page_content)
#         for doc, _ in retrieved_results
#     ]

#     scores = reranker.predict(pairs)

#     reranked = []

#     for (doc, _), score in zip(retrieved_results, scores):
#         reranked.append((doc, float(score)))

#     reranked.sort(
#         key=lambda x: x[1],
#         reverse=True
#     )

#     return reranked[:RERANK_TOP_K]


from sentence_transformers import CrossEncoder

from app.config import RERANK_TOP_K

reranker = CrossEncoder(
    "BAAI/bge-reranker-base"
)


def rerank(question, documents):
    """
    documents:
        List[Document]

    Returns:
        List[(Document, rerank_score)]
    """

    if not documents:
        return []

    pairs = [
        (question, doc.page_content)
        for doc in documents
    ]

    scores = reranker.predict(pairs)

    reranked = [
        (doc, float(score))
        for doc, score in zip(documents, scores)
    ]

    reranked.sort(
        key=lambda x: x[1],
        reverse=True,
    )

    return reranked[:RERANK_TOP_K]
