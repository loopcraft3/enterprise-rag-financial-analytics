from app.loader import load_documents, load_document
from app.splitter import split_documents
from app.embeddings import get_embedding_model
from app.vectorstore import add_documents


def _ingest(documents, session_id: str):
    chunks = split_documents(documents)

    print(f"Total chunks created: {len(chunks)}")

    embedding_model = get_embedding_model()

    add_documents(
        chunks=chunks,
        embedding_model=embedding_model,
        session_id=session_id,
    )

    return chunks


def ingest_documents(session_id: str, document_path="data/default"):
    """Load every PDF in a folder (development helper)."""
    documents = load_documents(document_path)

    return _ingest(documents, session_id)


def ingest_document(file_path, session_id: str, source=None):
    """Load one PDF and store it for the given session."""
    documents = load_document(file_path)

    if source:
        for document in documents:
            document.metadata["source"] = source

    return _ingest(documents, session_id)
