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


# ---------------------------------------------------------------------------
# Every document belongs to one session (one browser visit / one chat).
# All reads below are filtered by session_id, so a visitor only ever sees,
# searches and deletes their own documents.
# ---------------------------------------------------------------------------


def add_documents(chunks, embedding_model, session_id: str):
    """
    Store document chunks and their embeddings in PostgreSQL + pgvector,
    owned by the given session.
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:

            documents = {}

            for chunk in chunks:
                source = chunk.metadata.get("source")

                if source not in documents:
                    documents[source] = {
                        "filename": os.path.basename(source) if source else "unknown",
                        "source": source,
                    }

            document_ids = {}

            for source, document in documents.items():
                cursor.execute(
                    """
                    INSERT INTO public.documents (filename, source, session_id)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (session_id, filename)
                    DO UPDATE SET source = EXCLUDED.source
                    RETURNING id;
                    """,
                    (
                        document["filename"],
                        document["source"],
                        session_id,
                    ),
                )

                document_ids[source] = cursor.fetchone()[0]

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
                    VALUES (%s, %s, %s, %s, %s, %s)
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


def vector_search(question: str, embedding_model, k: int, session_id: str):
    """
    Cosine similarity search using pgvector, limited to one session's documents.

    ORDER BY (...) + 0 stops Postgres from using the approximate HNSW index.
    A session only holds a few hundred chunks, so an exact search is fast, and
    it can never miss results because other visitors' vectors filled the index
    scan (the index would filter AFTER picking its nearest neighbours).
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
                JOIN public.documents d ON d.id = c.document_id
                WHERE d.session_id = %s
                ORDER BY (c.embedding <=> %s::vector) + 0
                LIMIT %s;
                """,
                (
                    query_embedding,
                    session_id,
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


def load_all_documents(session_id: str):
    """
    Load one session's chunks from PostgreSQL.
    Used to rebuild the BM25 index for that session.
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
                JOIN public.documents d ON d.id = c.document_id
                WHERE d.session_id = %s
                ORDER BY c.document_id, c.chunk_index;
                """,
                (session_id,),
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


# ---------------------------------------------------------------------------
# Document bookkeeping
# ---------------------------------------------------------------------------


def list_session_documents(session_id: str):
    """[(filename, created_at)] for one session, oldest first."""

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT filename, created_at
                FROM public.documents
                WHERE session_id = %s
                ORDER BY created_at, id;
                """,
                (session_id,),
            )

            return cursor.fetchall()


def count_all_documents() -> int:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM public.documents;")
            return cursor.fetchone()[0]


def delete_document_vectors(session_id: str, filename: str) -> int:
    """
    Delete one of the session's documents and all its chunks (ON DELETE CASCADE).
    Returns how many documents were removed (0 = not found).
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM public.documents
                WHERE session_id = %s AND filename = %s;
                """,
                (session_id, filename),
            )

            deleted = cursor.rowcount

        conn.commit()

    print(f"✅ Deleted {deleted} document(s): {filename}")

    return deleted


def delete_session_documents(session_id: str):
    """Delete everything a session uploaded. Returns the removed filenames."""

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM public.documents
                WHERE session_id = %s
                RETURNING filename;
                """,
                (session_id,),
            )

            filenames = [row[0] for row in cursor.fetchall()]

        conn.commit()

    return filenames


def purge_expired_documents(ttl_hours: float):
    """
    Delete every document older than ttl_hours (chunks go with it).
    Returns [(session_id, filename)] so the caller can remove the stored PDFs too.
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM public.documents
                WHERE created_at < now() - (%s * interval '1 hour')
                RETURNING session_id, filename;
                """,
                (ttl_hours,),
            )

            expired = cursor.fetchall()

        conn.commit()

    return expired
