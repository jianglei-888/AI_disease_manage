from pydantic import BaseModel, field_serializer
from datetime import datetime
from typing import Optional

class PersonalInfoBase(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    medication_history: Optional[str] = None
    medication_contraindications: Optional[str] = None

class PersonalInfoCreate(PersonalInfoBase):
    pass

class PersonalInfoUpdate(PersonalInfoBase):
    pass

class PersonalInfoResponse(PersonalInfoBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    email: str = ""
    
    class Config:
        from_attributes = True
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, value: datetime) -> str:
        # 直接返回时间的字符串表示，不进行任何时区转换
        # 因为数据库中已经存储的是本地时区的时间
        import datetime
        
        # 检查value是否为datetime对象
        if isinstance(value, datetime.datetime):
            # 直接格式化时间
            return value.strftime('%Y-%m-%d %H:%M:%S')
        else:
            # 如果不是datetime对象，直接返回
            return str(value)
