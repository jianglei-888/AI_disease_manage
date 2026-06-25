from tortoise import models, fields
from datetime import datetime

class ChatRecord(models.Model):
    id = fields.IntField(pk=True, auto_increment=True)
    user_id = fields.IntField(nullable=False)
    message = fields.TextField(nullable=False)
    role = fields.CharField(max_length=10, nullable=False)  # 'user' or 'ai'
    created_at = fields.DatetimeField(default=datetime.now)
    
    class Meta:
        table = "chat_records"
