# MAX_HISTORY = 10

# conversation_history = []
# # print(conversation_history)


# def add_user_message(message: str):
#     conversation_history.append(
#         {
#             "role": "user",
#             "content": message,
#         }
#     )

# def add_retrieved_chunks(results):
#     """
#     Stores the retrieved chunks in the conversation history.

#     results should be the output of:
#     similarity_search_with_score()
#     """

#     chunks = []

#     for doc, score in results:
#         chunks.append(
#             {
#                 "content": doc.page_content,
#                 "metadata": doc.metadata,
#                 "score": score,
#             }
#         )

#     conversation_history.append(
#         {
#             "role": "retrieval",
#             "chunks": chunks,
#         }
#     )

#     trim_history()


# def add_assistant_message(message: str):
#     conversation_history.append(
#         {
#             "role": "assistant",
#             "content": message,
#         }
#     )

#     trim_history()


# def trim_history():
#     """
#     Keeps only the latest MAX_HISTORY messages.
#     """

#     global conversation_history

#     if len(conversation_history) > MAX_HISTORY:
#         conversation_history = conversation_history[-MAX_HISTORY:]


# def get_conversation():
#     return conversation_history


# def clear_conversation():
#     conversation_history.clear()

# MAX_HISTORY = 50

# conversation_history = []


# def add_user_message(message: str):
#     conversation_history.append(
#         {
#             "role": "user",
#             "content": message,
#         }
#     )
 
#     trim_history()


# def add_retrieved_chunks(results):
#     """
#     Stores the retrieved chunks in the conversation history.

#     results should be the output of:
#     similarity_search_with_score()
#     """

#     chunks = []

#     for doc, score in results:
#         chunks.append(
#             {
#                 "content": doc.page_content,
#                 "metadata": doc.metadata,
#                 "score": score,
#             }
#         )

#     conversation_history.append(
#         {
#             "role": "retrieval",
#             "chunks": chunks,
#         }
#     )

#     trim_history()


# def add_assistant_message(message: str):
#     conversation_history.append(
#         {
#             "role": "assistant",
#             "content": message,
#         }
#     )

#     trim_history()


# def trim_history():
#     global conversation_history

#     if len(conversation_history) > MAX_HISTORY:
#         conversation_history = conversation_history[-MAX_HISTORY:]


# def get_conversation():
#     return conversation_history


# def clear_conversation():
#     conversation_history.clear()








import json
import os
from uuid import UUID

import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

MAX_HISTORY = 10


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not found in .env")

    return psycopg.connect(DATABASE_URL)


def create_conversation():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO public.conversations DEFAULT VALUES
                RETURNING id;
                """
            )
            conversation_id = cursor.fetchone()[0]

        conn.commit()

    return conversation_id


def get_or_create_conversation(conversation_id=None):
    if conversation_id is None:
        return create_conversation()

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM public.conversations
                WHERE id = %s;
                """,
                (conversation_id,),
            )

            row = cursor.fetchone()

    if row is None:
        raise ValueError("Conversation not found.")

    return row[0]


def add_user_message(conversation_id: UUID, message: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO public.conversation_messages (
                    conversation_id,
                    role,
                    content
                )
                VALUES (%s, 'user', %s);
                """,
                (conversation_id, message),
            )

        conn.commit()


def add_retrieved_chunks(conversation_id: UUID, results):
    chunks = []

    for doc, score in results:
        chunks.append(
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score,
            }
        )

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO public.conversation_messages (
                    conversation_id,
                    role,
                    metadata
                )
                VALUES (%s, 'retrieval', %s);
                """,
                (
                    conversation_id,
                    json.dumps({"chunks": chunks}),
                ),
            )

        conn.commit()


def add_assistant_message(conversation_id: UUID, message: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO public.conversation_messages (
                    conversation_id,
                    role,
                    content
                )
                VALUES (%s, 'assistant', %s);
                """,
                (conversation_id, message),
            )

        conn.commit()


def get_conversation(conversation_id: UUID):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    role,
                    content,
                    metadata
                FROM public.conversation_messages
                WHERE conversation_id = %s
                ORDER BY created_at DESC
                LIMIT %s;
                """,
                (
                    conversation_id,
                    MAX_HISTORY,
                ),
            )

            rows = cursor.fetchall()

    rows.reverse()

    conversation = []

    for role, content, metadata in rows:
        if role == "user":
            conversation.append(
                {
                    "role": "user",
                    "content": content,
                }
            )

        elif role == "assistant":
            conversation.append(
                {
                    "role": "assistant",
                    "content": content,
                }
            )

        elif role == "retrieval":
            metadata = metadata or {}

            conversation.append(
                {
                    "role": "retrieval",
                    "chunks": metadata.get("chunks", []),
                }
            )

    return conversation


def clear_conversation(conversation_id: UUID):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM public.conversation_messages
                WHERE conversation_id = %s;
                """,
                (conversation_id,),
            )

        conn.commit()