
# from langchain_chroma import Chroma


# def create_vector_store(
#     chunks,
#     embedding_model,
#     persist_directory="db",
# ):
#     """
#     Create and store embeddings in ChromaDB.
#     """

#     vector_store = Chroma.from_documents(
#         documents=chunks,
#         embedding=embedding_model,
#         persist_directory=persist_directory,
#     )

#     vector_store._all_chunks = chunks

#     return vector_store 

# def load_vector_store(
#     embedding_model,
#     persist_directory="db",
# ):
#     """
#     Load an existing ChromaDB vector store.
#     """

#     vector_store = Chroma(
#         persist_directory=persist_directory,
#         embedding_function=embedding_model,
#     )

#     return vector_store




# def delete_document_vectors(
#     embedding_model,
#     source: str,
#     persist_directory="db",
# ):
#     """
#     Delete all vectors belonging to one document.
#     """

#     vector_store = load_vector_store(
#         embedding_model=embedding_model,
#         persist_directory=persist_directory,
#     )

#     vector_store.delete(
#         where={
#             "source": source,
#         }
#     ) 





import json
import os
import psycopg
from dotenv import load_dotenv
from langchain_core.documents import Document

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not found in .env")

    return psycopg.connect(DATABASE_URL)


def add_documents(chunks, embedding_model):
    """
    Store document chunks and their embeddings in PostgreSQL + pgvector.
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:

            # Group chunks by source/document
            documents = {}

            for chunk in chunks:
                source = chunk.metadata.get("source")

                if source not in documents:
                    documents[source] = {
                        "filename": os.path.basename(source) if source else "unknown",
                        "source": source,
                    }

            # Insert documents
            document_ids = {}

            for source, document in documents.items():

                cursor.execute(
                    """
                    INSERT INTO public.documents (filename, source)
                    VALUES (%s, %s)
                    ON CONFLICT (filename)
                    DO UPDATE SET source = EXCLUDED.source
                    RETURNING id;
                    """,
                    (
                        document["filename"],
                        document["source"],
                    ),
                )

                document_ids[source] = cursor.fetchone()[0]

            # Insert chunks
            texts = [chunk.page_content for chunk in chunks]

            embeddings = embedding_model.embed_documents(texts)

            for chunk, embedding in zip(chunks, embeddings):

                source = chunk.metadata.get("source")
                document_id = document_ids[source]

                cursor.execute(
                    """
                    INSERT INTO public.chunks (
                        document_id,
                        chunk_index,
                        content,
                        page,
                        metadata,
                        embedding
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    ON CONFLICT (document_id, chunk_index)
                    DO UPDATE SET
                        content = EXCLUDED.content,
                        page = EXCLUDED.page,
                        metadata = EXCLUDED.metadata,
                        embedding = EXCLUDED.embedding;
                    """,
                    (
                        document_id,
                        chunk.metadata.get("chunk_index"),
                        chunk.page_content,
                        chunk.metadata.get("page"),
                        json.dumps(chunk.metadata),
                        embedding,
                    ),
                )

        conn.commit()

    print(f"✅ Stored {len(chunks)} chunks in PostgreSQL")


def delete_document_vectors(source: str):
    """
    Delete a document and all its chunks from PostgreSQL.
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM public.documents
                WHERE source = %s;
                """,
                (source,),
            )

        conn.commit()

    print(f"✅ Deleted document: {source}")


def vector_search(question: str, embedding_model, k: int):
    """
    Perform cosine similarity search using pgvector.
    """
    query_embedding = embedding_model.embed_query(question)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    c.content,
                    c.page,
                    c.metadata,
                    1 - (c.embedding <=> %s::vector) AS similarity
                FROM public.chunks c
                ORDER BY c.embedding <=> %s::vector
                LIMIT %s;
                """,
                (
                    query_embedding,
                    query_embedding,
                    k,
                ),
            )

            rows = cursor.fetchall()

    results = []

    for content, page, metadata, similarity in rows:
        metadata = metadata or {}

        if page is not None:
            metadata["page"] = page

        results.append(
            (
                Document(
                    page_content=content,
                    metadata=metadata,
                ),
                float(similarity),
            )
        )

    return results



def load_all_documents():
    """
    Load all document chunks from PostgreSQL.
    Used to rebuild the BM25 index from the current database state.
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    c.content,
                    c.page,
                    c.metadata
                FROM public.chunks c
                ORDER BY c.document_id, c.chunk_index;
                """
            )

            rows = cursor.fetchall()

    documents = []

    for content, page, metadata in rows:
        metadata = metadata or {}

        if page is not None:
            metadata["page"] = page

        documents.append(
            Document(
                page_content=content,
                metadata=metadata,
            )
        )

    return documents