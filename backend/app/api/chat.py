# from fastapi import APIRouter
# from pydantic import BaseModel

# from app.chat import generate_answer
# from app.embeddings import get_embedding_model
# from app.models.schemas import ChatRequest, ChatResponse
# from app.vectorstore import load_vector_store

# from fastapi.responses import StreamingResponse

# router = APIRouter()

# embedding_model = get_embedding_model()
# vector_store = load_vector_store(embedding_model)   







# @router.post("/chat")
# def chat(request: ChatRequest):

#     return StreamingResponse(
#         generate_answer(
#             question=request.question,
#             vector_store=vector_store,
#         ),
#         media_type="text/plain",
#     )


from fastapi import APIRouter, HTTPException

from app.chat import generate_answer
from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        response = generate_answer(
            question=request.question,
            conversation_id=request.conversation_id,
        )

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )