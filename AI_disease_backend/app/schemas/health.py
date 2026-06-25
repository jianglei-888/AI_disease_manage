from pydantic import BaseModel, field_serializer
from datetime import datetime
from typing import List, Optional

class HealthRecordBase(BaseModel):
    systolic: int
    diastolic: int
    blood_sugar: float
    measured_at: datetime

class HealthRecordCreate(HealthRecordBase):
    pass

class HealthRecordResponse(HealthRecordBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
    
    @field_serializer('measured_at', 'created_at')
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

class HealthRecordList(BaseModel):
    total: int
    records: List[HealthRecordResponse]

class HealthAnalysis(BaseModel):
    average: dict
    trend: str
    abnormal_count: int
    suggestions: List[str]
