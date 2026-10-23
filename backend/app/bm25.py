from rank_bm25 import BM25Okapi


class BM25Retriever:

    def __init__(self, documents):
        """
        documents: List[Document]
        """

        self.documents = documents

        self.tokenized_documents = [
            doc.page_content.lower().split()
            for doc in documents
        ]

        self.bm25 = BM25Okapi(self.tokenized_documents)

    def search(
        self,
        query,
        k=30,
    ):
        """
        Returns:
            List[(Document, score)]
        """

        tokenized_query = query.lower().split()

        scores = self.bm25.get_scores(tokenized_query)

        ranked = sorted(
            zip(self.documents, scores),
            key=lambda x: x[1],
            reverse=True,
        )

        return ranked[:k]