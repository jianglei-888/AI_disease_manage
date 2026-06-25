from tortoise import models, fields
from datetime import datetime

class PersonalInfo(models.Model):
    id = fields.IntField(pk=True, auto_increment=True)
    user_id = fields.IntField(nullable=False, unique=True)
    name = fields.CharField(max_length=50, nullable=True)
    gender = fields.CharField(max_length=10, nullable=True)
    age = fields.IntField(nullable=True)
    medication_history = fields.TextField(nullable=True)
    medication_contraindications = fields.TextField(nullable=True)
    created_at = fields.DatetimeField(default=datetime.now)
    updated_at = fields.DatetimeField(default=datetime.now, auto_now=True)
    
    class Meta:
        table = "personal_infos"
