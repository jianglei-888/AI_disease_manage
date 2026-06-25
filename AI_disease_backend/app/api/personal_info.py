"""个人信息接口。"""
from datetime import datetime

from fastapi import APIRouter, Depends

from app.schemas.personal_info import PersonalInfoCreate, PersonalInfoResponse
from app.services.personal_info_service import PersonalInfoService
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/personal-info", tags=["personal-info"])


def _empty_response(user_id: int) -> PersonalInfoResponse:
    now = datetime.now()
    return PersonalInfoResponse(
        id=0,
        user_id=user_id,
        name="",
        gender="",
        age=None,
        email="",
        medication_history="",
        medication_contraindications="",
        created_at=now,
        updated_at=now,
    )


@router.get("/", response_model=PersonalInfoResponse)
async def get_personal_info(current_user_id: int = Depends(get_current_user)):
    info = await PersonalInfoService.get_personal_info(current_user_id)
    if info.id == 0:
        return _empty_response(current_user_id)
    return info


@router.post("/", response_model=PersonalInfoResponse)
async def create_or_update_personal_info(
    data: PersonalInfoCreate,
    current_user_id: int = Depends(get_current_user),
):
    return await PersonalInfoService.create_or_update_personal_info(current_user_id, data)