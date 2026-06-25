from pydantic import BaseModel, field_serializer
from datetime import datetime
from typing import List

class MessageBase(BaseModel):
    message: str

class MessageCreate(MessageBase):
    pass

class MessageResponse(BaseModel):
    id: int
    message: str
    role: str
    created_at: datetime
    
    @field_serializer('created_at')
    def serialize_datetime(self, value: datetime) -> str:
        import datetime
        if isinstance(value, datetime.datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return str(value)
    
    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    user_message: MessageResponse
    ai_response: MessageResponse

class MessageList(BaseModel):
    total: int
    messages: List[MessageResponse]
