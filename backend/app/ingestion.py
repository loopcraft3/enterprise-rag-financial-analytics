# from app.loader import load_documents, load_document
# from app.splitter import split_documents
# from app.embeddings import get_embedding_model
# from app.vectorstore import create_vector_store
# from app.bm25 import BM25Retriever
# import pickle


# def _ingest(
#     documents,
#     persist_directory="db",
# ):
#     """
#     Common ingestion pipeline.
#     """

#     chunks = split_documents(documents) 

#     bm25 = BM25Retriever(chunks)

#     with open("data/bm25.pkl", "wb") as f:
#         pickle.dump(bm25, f)

#     print("BM25 index created")

#     embedding_model = get_embedding_model()

#     vector_store = create_vector_store(
#         chunks=chunks,
#         embedding_model=embedding_model,
#         persist_directory=persist_directory,
#     )

#     return vector_store

# def ingest_documents(
#     document_path="data/default",
#     persist_directory="db"
# ):
#     """
#     Ingest all PDFs inside a folder.
#     """

#     documents = load_documents(document_path)

#     return _ingest(
#         documents,
#         persist_directory,
#     )


# def ingest_document(
#     file_path,
#     persist_directory="db",
# ):
#     """
#     Ingest a single PDF.
#     """

#     documents = load_document(file_path)

#     return _ingest(
#         documents,
#         persist_directory,
#     )





from app.loader import load_documents, load_document
from app.splitter import split_documents
from app.embeddings import get_embedding_model
from app.vectorstore import add_documents


def _ingest(documents):
    chunks = split_documents(documents)

    print(f"Total chunks created: {len(chunks)}")

    embedding_model = get_embedding_model()

    add_documents(
        chunks=chunks,
        embedding_model=embedding_model,
    )

    return chunks


def ingest_documents(document_path="data/default"):
    documents = load_documents(document_path)
    return _ingest(documents)


def ingest_document(file_path, source=None):
    documents = load_document(file_path)

    if source:
        for document in documents:
            document.metadata["source"] = source

    return _ingest(documents)