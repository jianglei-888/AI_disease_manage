"""健康数据相关接口。"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.schemas.health import HealthAnalysis, HealthRecordCreate, HealthRecordList, HealthRecordResponse
from app.services.health_service import HealthService
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/health", tags=["health"])

_PERIOD_VALUES = ("day", "week", "month", "year")


@router.post("/records", response_model=HealthRecordResponse)
async def submit_record(
    record_data: HealthRecordCreate,
    current_user_id: int = Depends(get_current_user),
):
    return await HealthService.submit_record(current_user_id, record_data)


@router.get("/records", response_model=HealthRecordList)
async def get_records(
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    limit: int = Query(20, ge=1, le=100, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user_id: int = Depends(get_current_user),
):
    return await HealthService.get_records(
        current_user_id, start_date, end_date, limit, offset
    )


@router.get("/analysis", response_model=HealthAnalysis)
async def get_analysis(
    period: str = Query("week", pattern="^(day|week|month|year)$", description="分析周期"),
    current_user_id: int = Depends(get_current_user),
):
    return await HealthService.get_analysis(current_user_id, period)