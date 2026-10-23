from pydantic import BaseModel
from uuid import UUID

class ChatRequest(BaseModel):
    question: str
    conversation_id: UUID | None = None


class Source(BaseModel):
    source: str
    page: int | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    conversation_id: UUID

    