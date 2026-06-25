"""聊天相关接口。"""
from fastapi import APIRouter, Depends, Query, Request

from app.schemas.chat import ChatResponse, MessageCreate, MessageList
from app.services.ai_service import AIService
from app.utils.ratelimit import limiter
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/messages", response_model=ChatResponse)
@limiter.limit("20/minute")
async def send_message(
    request: Request,
    message_data: MessageCreate,
    current_user_id: int = Depends(get_current_user),
):
    return await AIService.send_message(current_user_id, message_data)


@router.get("/messages", response_model=MessageList)
async def get_messages(
    limit: int = Query(50, ge=1, le=100, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user_id: int = Depends(get_current_user),
):
    return await AIService.get_messages(current_user_id, limit, offset)
