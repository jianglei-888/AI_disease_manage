from tortoise import models, fields
from datetime import datetime

class User(models.Model):
    id = fields.IntField(pk=True, auto_increment=True)
    username = fields.CharField(max_length=50, nullable=False)
    email = fields.CharField(max_length=100, unique=True, nullable=False)
    password_hash = fields.CharField(max_length=255, nullable=False)
    created_at = fields.DatetimeField(default=datetime.now)
    updated_at = fields.DatetimeField(default=datetime.now, auto_now=True)
    
    class Meta:
        table = "users"
