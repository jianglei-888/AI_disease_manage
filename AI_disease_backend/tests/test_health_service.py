"""health_service 单元测试。"""
from datetime import datetime, timedelta

import pytest

from app.schemas.health import HealthRecordCreate
from app.services.health_service import HealthService
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate
from app.utils.exceptions import NotFoundError, ValidationError


async def _register_and_get_id() -> int:
    result = await AuthService.register(UserCreate(
        username=f"u{datetime.now().timestamp()}",
        email=f"u{datetime.now().timestamp()}@e.com",
        password="Password123!",
        confirm_password="Password123!",
    ))
    return result.user.id


@pytest.mark.asyncio
async def test_submit_record_success(db_init):
    user_id = await _register_and_get_id()
    record = await HealthService.submit_record(user_id, HealthRecordCreate(
        systolic=120,
        diastolic=80,
        blood_sugar=5.6,
        measured_at=datetime.now(),
    ))
    assert record.id > 0
    assert record.systolic == 120


@pytest.mark.asyncio
async def test_submit_record_invalid(db_init):
    user_id = await _register_and_get_id()
    with pytest.raises(ValidationError):
        await HealthService.submit_record(user_id, HealthRecordCreate(
            systolic=0,
            diastolic=80,
            blood_sugar=5.6,
            measured_at=datetime.now(),
        ))


@pytest.mark.asyncio
async def test_get_records_pagination(db_init):
    user_id = await _register_and_get_id()
    now = datetime.now()
    for i in range(5):
        await HealthService.submit_record(user_id, HealthRecordCreate(
            systolic=120 + i,
            diastolic=80,
            blood_sugar=5.6,
            measured_at=now - timedelta(days=i),
        ))
    result = await HealthService.get_records(user_id, None, None, limit=3, offset=0)
    assert result.total == 5
    assert len(result.records) == 3


@pytest.mark.asyncio
async def test_get_analysis_no_data(db_init):
    user_id = await _register_and_get_id()
    with pytest.raises(NotFoundError):
        await HealthService.get_analysis(user_id, "week")


@pytest.mark.asyncio
async def test_get_analysis_with_data(db_init):
    user_id = await _register_and_get_id()
    now = datetime.now()
    for i in range(3):
        await HealthService.submit_record(user_id, HealthRecordCreate(
            systolic=120 + i,
            diastolic=80 + i,
            blood_sugar=5.5 + i * 0.1,
            measured_at=now - timedelta(days=i),
        ))
    analysis = await HealthService.get_analysis(user_id, "week")
    assert analysis.average["systolic"] == 121  # 120+121+122 / 3 = 121
    assert analysis.trend in ("stable", "rising", "falling")
    assert len(analysis.suggestions) >= 2