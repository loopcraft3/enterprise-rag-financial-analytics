# import pickle

# def load_bm25():

#     with open("data/bm25.pkl", "rb") as f:
#         return pickle.load(f)





from app.bm25 import BM25Retriever
from app.vectorstore import load_all_documents


def load_bm25():
    """
    Build the BM25 index from the current PostgreSQL documents.
    """

    documents = load_all_documents() 

    if not documents:
        return None

    return BM25Retriever(documents)