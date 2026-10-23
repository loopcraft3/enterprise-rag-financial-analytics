from collections import defaultdict


def reciprocal_rank_fusion(*rankings, k=60):
    """
    rankings: list of lists containing (Document, score)

    Returns:
        List[Document]
    """

    fused_scores = defaultdict(float)
    documents = {}

    for ranking in rankings:

        for rank, (doc, _) in enumerate(ranking):

            doc_id = doc.page_content 

            documents[doc_id] = doc

            fused_scores[doc_id] += 1 / (k + rank + 1)

    ranked = sorted(
        fused_scores.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    return [documents[doc_id] for doc_id, _ in ranked]