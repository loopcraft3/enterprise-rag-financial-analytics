import os
from uuid import UUID

from app.llm import get_llm
from app.prompt import SYSTEM_PROMPT, FALLBACK_MESSAGE, get_doc_guide
from app.retriever import retrieve_documents
from app.memory import (
    add_user_message,
    add_assistant_message,
    add_retrieved_chunks,
    get_conversation,
    get_or_create_conversation,
)
from app.config import DEFAULT_TOP_K, FINAL_CONTEXT_K
from app.cache import answer_cache, make_key, corpus_fingerprint, is_cacheable

CACHE_ENABLED = os.getenv("CACHE_ENABLED", "1") == "1"


def format_context(documents):
    """Tag every chunk with its source file and page so the LLM can cite it."""
    parts = []
    for d in documents:
        name = os.path.basename(str(d.metadata.get("source") or "document"))
        page = d.metadata.get("page")
        page_label = int(page) + 1 if page is not None else "?"
        parts.append(f"[Source: {name}, Page {page_label}]\n{d.page_content}")
    return "\n\n".join(parts)


def build_sources(documents):
    """Unique (file, page) pairs, with page numbers starting from 1."""
    sources = []
    seen = set()
    for document in documents:
        name = os.path.basename(str(document.metadata.get("source") or "document"))
        page = document.metadata.get("page")
        key = (name, page)
        if key in seen:
            continue
        seen.add(key)
        sources.append(
            {
                "source": name,
                "page": int(page) + 1 if page is not None else None,
            }
        )
    return sources


def generate_answer(
    question: str,
    k: int = DEFAULT_TOP_K,
    conversation_id: UUID | None = None,
):
    # Create a new conversation if one was not provided.
    conversation_id = get_or_create_conversation(conversation_id)

    # Save the user's question in PostgreSQL.
    add_user_message(
        conversation_id,
        question,
    )

    conversation = get_conversation(conversation_id)

    # ---- Cache lookup (standalone questions only) ----
    cache_key = None
    if CACHE_ENABLED and is_cacheable(question, conversation):
        fingerprint = corpus_fingerprint()
        if fingerprint:
            cache_key = make_key(question, fingerprint, SYSTEM_PROMPT)
            cached = answer_cache.get(cache_key)
            if cached:
                print("CACHE HIT:", answer_cache.stats())
                add_assistant_message(conversation_id, cached["answer"])
                return {
                    "answer": cached["answer"],
                    "sources": cached["sources"],
                    "conversation_id": conversation_id,
                }
            print("CACHE MISS:", answer_cache.stats())

    results = retrieve_documents(
        question=question,
        k=k,
    )

    print("\nRetrieved Results:")

    for i, (doc, score) in enumerate(results, start=1):
        print(f"{i}. Score: {score:.4f}")
        print(doc.page_content[:120])
        print("-" * 50)

    relevant_documents = [
        document
        for document, score in results[:FINAL_CONTEXT_K]
    ]

    if not relevant_documents:
        answer = FALLBACK_MESSAGE

        add_assistant_message(
            conversation_id,
            answer,
        )

        return {
            "answer": answer,
            "sources": [],
            "conversation_id": conversation_id,
        }

    context = format_context(relevant_documents)

    history_parts = []

    for message in conversation:

        if message["role"] == "user":
            history_parts.append(
                f"User: {message['content']}"
            )

        elif message["role"] == "assistant":
            history_parts.append(
                f"Assistant: {message['content']}"
            )

        elif message["role"] == "retrieval":
            chunks = "\n".join(
                chunk["content"][:150] + "..."
                for chunk in message["chunks"]
            )

            history_parts.append(
                f"Previous Retrieved Chunks:\n{chunks}"
            )

    history = "\n\n".join(history_parts)

    prompt = SYSTEM_PROMPT.format(
        history=history,
        context=context,
        question=question,
        doc_guide=get_doc_guide(relevant_documents),
    )

    llm = get_llm()

    response = llm.invoke(prompt)

    answer = response.content
    answer = answer.replace("【", "(").replace("】", ")")

    # Save retrieval and assistant response.
    add_retrieved_chunks(
        conversation_id,
        results,
    )

    add_assistant_message(
        conversation_id,
        answer,
    )

    sources = build_sources(relevant_documents)

    if cache_key and answer:
        answer_cache.set(cache_key, {"answer": answer, "sources": sources})

    return {
        "answer": answer,
        "sources": sources,
        "conversation_id": conversation_id,
    }