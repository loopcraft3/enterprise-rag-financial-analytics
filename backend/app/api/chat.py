from fastapi import APIRouter, Depends, HTTPException

from app.chat import generate_answer
from app.models.schemas import ChatRequest, ChatResponse
from app.sessions import get_session_id

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    session_id: str = Depends(get_session_id),
):
    try:
        response = generate_answer(
            question=request.question,
            session_id=session_id,
            conversation_id=request.conversation_id,
        )

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
