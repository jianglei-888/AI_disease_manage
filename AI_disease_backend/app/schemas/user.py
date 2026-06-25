from pydantic import BaseModel, EmailStr, field_serializer
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    confirm_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
    
    @field_serializer('created_at')
    def serialize_datetime(self, value: datetime) -> str:
        import datetime
        import time
        timezone_offset = time.localtime().tm_gmtoff
        local_tz = datetime.timezone(datetime.timedelta(seconds=timezone_offset))

        if value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None:
            local_time = value.astimezone(local_tz)
        else:
            local_time = value.replace(tzinfo=local_tz)
        
        return local_time.strftime('%Y-%m-%d %H:%M:%S')

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
