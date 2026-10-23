# # from openai import OpenAI

# from app.llm import get_llm

# from app.prompt import SYSTEM_PROMPT
# from app.retriever import retrieve_documents 
# from app.memory import (add_user_message, add_assistant_message, get_conversation, add_retrieved_chunks)

# # client = OpenAI()

# def generate_answer(
#     question: str,
#     vector_store,
#     k: int = 10,
#     # score_threshold: float = 0.20,
# ):
#     """
#     Generate an answer using the retrieved document chunks.
#     """

#     add_user_message(question)

#     results = retrieve_documents(
#         question=question,
#         vector_store=vector_store,
#         k=k,
#     )
#     add_retrieved_chunks(results)
   
#     print("\nRetrieved Results:")
#     for i, (doc, score) in enumerate(results, start=1):
#         print(f"{i}. Score: {score:.4f}")
#         print(doc.page_content[:120])
#         print("-" * 50)
    


#     relevant_documents = [
#     document
#     for document, score in results
#     # if score <= score_threshold
#     ]

#     if not relevant_documents:
#         return {
#         "answer": "Sorry, I couldn't find the answer in the uploaded document. Vishal who built me has strictly grounded me.",
#         "sources": [],
#         }
    
#     context = "\n\n".join(
#     document.page_content
#     for document in relevant_documents

#     )

#     history_parts = []

# for message in get_conversation():

#     if message["role"] == "user":
#         history_parts.append(
#             f"User: {message['content']}"
#         )

#     elif message["role"] == "assistant":
#         history_parts.append(
#             f"Assistant: {message['content']}"
#         )

#     elif message["role"] == "retrieval":

#         chunks = "\n".join(
#             chunk["content"]
#             for chunk in message["chunks"]
#         )

#         history_parts.append(
#             f"Retrieved Document Chunks:\n{chunks}"
#         )

#     history = "\n\n".join(history_parts)

#     prompt = SYSTEM_PROMPT.format(
#     context=context,
#     history=history,
#     question=question,
#     )

#     llm = get_llm()



#     response = llm.invoke(prompt)

#     answer = response.content
#     add_assistant_message(answer)


#     sources = [
#     {
#         "source": document.metadata.get("source"),
#         "page": document.metadata.get("page"),
#     }
#     for document in relevant_documents
#     ]

#     return {
#         "answer": answer,
#         "sources": sources,
#     }









# from app.llm import get_llm
# from app.prompt import SYSTEM_PROMPT
# from app.retriever import retrieve_documents
# from app.memory import (
#     add_user_message,
#     add_assistant_message,
#     add_retrieved_chunks,
#     get_conversation,
# )
# from app.config import DEFAULT_TOP_K, FINAL_CONTEXT_K


# def generate_answer(
#     question: str,
#     vector_store,
#     k: int = DEFAULT_TOP_K,
# ):
#     """
#     Generate an answer using the retrieved document chunks.
#     """

#     add_user_message(question)

#     results = retrieve_documents(
#         question=question,
#         vector_store=vector_store,
#         k=k,
#     )

#     print("\nRetrieved Results:")
#     for i, (doc, score) in enumerate(results, start=1):
#         print(f"{i}. Score: {score:.4f}")
#         print(doc.page_content[:120])
#         print("-" * 50)

#     relevant_documents = [
#     document
#     for document, score in results[:FINAL_CONTEXT_K]
#     ]

#     if not relevant_documents:
#         return {
#             "answer": "Sorry, I couldn't find the answer in the uploaded document. Vishal who built me has strictly grounded me.",
#             "sources": [],
#         }

#     context = "\n\n".join(
#         document.page_content
#         for document in relevant_documents
#     )


#     history_parts = []

#     for message in get_conversation():

#         if message["role"] == "user":
#             history_parts.append(
#                 f"User: {message['content']}"
#             )

#         elif message["role"] == "assistant":
#             history_parts.append(
#                 f"Assistant: {message['content']}"
#             )

#         elif message["role"] == "retrieval":

#             chunks = "\n".join(
#                 chunk["content"][:150] + "..."
#                 for chunk in message["chunks"]
#             )

#             history_parts.append(
#                 f"Previous Retrieved Chunks:\n{chunks}"
#             )

#     history = "\n\n".join(history_parts)

#     prompt = SYSTEM_PROMPT.format(
#         history=history,
#         context=context,
#         question=question,
#     )

#     llm = get_llm()

#     # response = llm.invoke(prompt)

#     # answer = response.content

#     full_answer = ""

#     for chunk in llm.stream(prompt):
#         if chunk.content:
#             full_answer += chunk.content
#             yield chunk.content

#     answer = full_answer

#     add_retrieved_chunks(results)

#     add_assistant_message(answer)

#     sources = [
#         {
#             "source": document.metadata.get("source"),
#             "page": document.metadata.get("page"),
#         }
#         for document in relevant_documents
#     ]

#     return {
#         "answer": answer,
#         "sources": sources,
#     }






from uuid import UUID

from app.llm import get_llm
from app.prompt import SYSTEM_PROMPT
from app.retriever import retrieve_documents
from app.memory import (
    add_user_message,
    add_assistant_message,
    add_retrieved_chunks,
    get_conversation,
    get_or_create_conversation,
)
from app.config import DEFAULT_TOP_K, FINAL_CONTEXT_K


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
        answer = (
            "Sorry, I couldn't find the answer in the uploaded document. "
            "Vishal who built me has strictly grounded me."
        )

        add_assistant_message(
            conversation_id,
            answer,
        )

        return {
            "answer": answer,
            "sources": [],
            "conversation_id": conversation_id,
        }

    context = "\n\n".join(
        document.page_content
        for document in relevant_documents
    )

    history_parts = []

    for message in get_conversation(conversation_id):

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
    )

    llm = get_llm()

    response = llm.invoke(prompt)

    answer = response.content

    # Save retrieval and assistant response.
    add_retrieved_chunks(
        conversation_id,
        results,
    )

    add_assistant_message(
        conversation_id,
        answer,
    )

    sources = [
        {
            "source": document.metadata.get("source"),
            "page": document.metadata.get("page"),
        }
        for document in relevant_documents
    ]

    return {
        "answer": answer,
        "sources": sources,
        "conversation_id": conversation_id,
    }