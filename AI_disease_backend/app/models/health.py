from tortoise import models, fields
from datetime import datetime

class HealthRecord(models.Model):
    id = fields.IntField(pk=True, auto_increment=True)
    user_id = fields.IntField(nullable=False)
    systolic = fields.IntField(nullable=False)  # 收缩压（高压）
    diastolic = fields.IntField(nullable=False)  # 舒张压（低压）
    blood_sugar = fields.FloatField(nullable=False)  # 血糖值
    measured_at = fields.DatetimeField(nullable=False)  # 测量时间
    created_at = fields.DatetimeField(default=datetime.now)
    
    class Meta:
        table = "health_records"
