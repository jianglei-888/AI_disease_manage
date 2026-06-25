"""个人信息服务：用户的年龄 / 用药史 / 禁忌等。

供 LangGraph 的 risk 节点和 email 节点读取。

注意：PersonalInfoResponse.email 字段在 personal_infos 表里没有，
      是从 users 表拼接出来的（保持与原接口兼容）。
"""
from typing import Optional

from app.models.personal_info import PersonalInfo
from app.models.user import User
from app.schemas.personal_info import PersonalInfoCreate, PersonalInfoResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PersonalInfoService:
    @staticmethod
    async def get_personal_info(user_id: int) -> PersonalInfoResponse:
        info: Optional[PersonalInfo] = await PersonalInfo.filter(user_id=user_id).first()
        user: Optional[User] = await User.filter(id=user_id).first()

        if not info:
            return PersonalInfoResponse(
                id=0,
                user_id=user_id,
                name="",
                gender="",
                age=None,
                email=user.email if user else "",
                medication_history="",
                medication_contraindications="",
                created_at=None,
                updated_at=None,
            )
        # 把 user.email 拼进去（兼容 schema 字段）
        resp = PersonalInfoResponse.model_validate(info)
        resp.email = user.email if user else ""
        return resp

    @staticmethod
    async def create_or_update_personal_info(
        user_id: int, data: PersonalInfoCreate
    ) -> PersonalInfoResponse:
        info = await PersonalInfo.filter(user_id=user_id).first()
        update_fields = data.model_dump(exclude_unset=True)
        # CharField 不接受 None：把 None 兜底成空串，避免 schema 字段为可选时触发数据库报错
        for k, v in list(update_fields.items()):
            if v is None:
                update_fields[k] = ""
        if info:
            for field, value in update_fields.items():
                setattr(info, field, value)
            await info.save()
            logger.info("更新个人信息：user_id=%s", user_id)
        else:
            info = await PersonalInfo.create(user_id=user_id, **update_fields)
            logger.info("创建个人信息：user_id=%s info_id=%s", user_id, info.id)
        return await PersonalInfoService.get_personal_info(user_id)