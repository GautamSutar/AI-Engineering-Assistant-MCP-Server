from fastapi import APIRouter
from pydantic import BaseModel

from app.agent.graph import ask

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    reply = await ask(request.message)
    return ChatResponse(response=reply)


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}
