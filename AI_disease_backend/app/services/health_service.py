"""健康数据服务：血压血糖记录提交 / 查询 / 分析。"""
from datetime import datetime, timedelta
from statistics import mean
from typing import List, Optional

from app.models.health import HealthRecord
from app.schemas.health import (
    HealthAnalysis,
    HealthRecordCreate,
    HealthRecordList,
    HealthRecordResponse,
)
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.logger import get_logger

logger = get_logger(__name__)

_PERIOD_DAYS = {
    "day": 1,
    "week": 7,
    "month": 30,
    "year": 365,
}


class HealthService:
    @staticmethod
    async def submit_record(user_id: int, data: HealthRecordCreate) -> HealthRecordResponse:
        if data.systolic <= 0 or data.diastolic <= 0:
            raise ValidationError("血压必须为正数")
        if data.blood_sugar <= 0:
            raise ValidationError("血糖必须为正数")

        record = await HealthRecord.create(
            user_id=user_id,
            systolic=data.systolic,
            diastolic=data.diastolic,
            blood_sugar=data.blood_sugar,
            measured_at=data.measured_at,
        )
        logger.info("提交健康记录：user_id=%s record_id=%s", user_id, record.id)
        return HealthRecordResponse.model_validate(record)

    @staticmethod
    async def get_records(
        user_id: int,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        limit: int,
        offset: int,
    ) -> HealthRecordList:
        query = HealthRecord.filter(user_id=user_id)
        if start_date:
            query = query.filter(measured_at__gte=start_date)
        if end_date:
            query = query.filter(measured_at__lte=end_date)

        total = await query.count()
        records = await query.order_by("-measured_at").offset(offset).limit(limit).all()
        return HealthRecordList(
            total=total,
            records=[HealthRecordResponse.model_validate(r) for r in records],
        )

    @staticmethod
    async def get_analysis(user_id: int, period: str) -> HealthAnalysis:
        if period not in _PERIOD_DAYS:
            raise ValidationError(f"不支持的分析周期：{period}")

        end = datetime.now()
        start = end - timedelta(days=_PERIOD_DAYS[period])

        records: List[HealthRecord] = await (
            HealthRecord.filter(user_id=user_id, measured_at__gte=start)
            .order_by("measured_at")
            .all()
        )
        if not records:
            raise NotFoundError("该周期内暂无健康记录")

        avg_systolic = round(mean(r.systolic for r in records))
        avg_diastolic = round(mean(r.diastolic for r in records))
        avg_blood_sugar = round(mean(r.blood_sugar for r in records), 2)

        abnormal_count = sum(
            1
            for r in records
            if r.systolic >= 140 or r.diastolic >= 90 or r.blood_sugar >= 7.0
        )

        trend = HealthService._calc_trend(records)
        suggestions = HealthService._gen_suggestions(avg_systolic, avg_diastolic, avg_blood_sugar)

        return HealthAnalysis(
            average={
                "systolic": avg_systolic,
                "diastolic": avg_diastolic,
                "blood_sugar": avg_blood_sugar,
            },
            trend=trend,
            abnormal_count=abnormal_count,
            suggestions=suggestions,
        )

    @staticmethod
    def _calc_trend(records: List[HealthRecord]) -> str:
        if len(records) < 2:
            return "stable"
        half = len(records) // 2
        early = mean(r.systolic for r in records[:half])
        late = mean(r.systolic for r in records[half:])
        diff = late - early
        if diff > 5:
            return "rising"
        if diff < -5:
            return "falling"
        return "stable"

    @staticmethod
    def _gen_suggestions(systolic: int, diastolic: int, blood_sugar: float) -> List[str]:
        suggestions: List[str] = []
        if systolic >= 140 or diastolic >= 90:
            suggestions.append("血压偏高，建议减少盐分摄入（每天 < 5g），规律运动")
        elif systolic < 90 or diastolic < 60:
            suggestions.append("血压偏低，建议适当增加盐分摄入，避免长时间站立")
        else:
            suggestions.append("血压在正常范围内，继续保持")
        if blood_sugar >= 7.0:
            suggestions.append("血糖偏高，建议控制碳水化合物摄入，选择低 GI 食物")
        elif blood_sugar < 3.9:
            suggestions.append("血糖偏低，建议随身携带糖果，定时进餐")
        else:
            suggestions.append("血糖在正常范围内，继续保持")
        suggestions.append("每周至少 150 分钟中等强度运动；定期复查")
        return suggestions