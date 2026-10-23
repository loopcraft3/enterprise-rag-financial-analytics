# from langchain_core.documents import Document
# from app.config import DEFAULT_TOP_K, MIN_RELEVANCE_SCORE
# from app.hybrid_retriever import hybrid_retrieve
# from app.reranker import rerank

# def retrieve_documents(
#     question: str,
#     vector_store,
#     k: int = DEFAULT_TOP_K, 
# ): 
#     """
#     Retrieve the most relevant document chunks
#     along with their similarity scores.
#     """

#     results = hybrid_retrieve(
#         question=question,
#         vector_store=vector_store,
#         k=k, 
#     )
#     filtered_results = []

#     for document, score in results:

#         if score <= MIN_RELEVANCE_SCORE:
#             filtered_results.append((document, score))

#     reranked_results = rerank(
#     question,
#     filtered_results
#     )

#     return reranked_results 


from app.config import DEFAULT_TOP_K
from app.hybrid_retriever import hybrid_retrieve
from app.reranker import rerank


def retrieve_documents(
    question: str,

    k: int = DEFAULT_TOP_K,
):
    """
    Retrieve documents using hybrid search and rerank them.
    """

    documents = hybrid_retrieve(
        question=question,

        k=k,
    )

    reranked_results = rerank(
        question,
        documents,
    )

    return reranked_results