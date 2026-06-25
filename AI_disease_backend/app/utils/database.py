from tortoise import Tortoise
from config.settings import settings

async def init_db():
    await Tortoise.init(
        db_url=settings.DATABASE_URL,
        modules={
            "models": ["app.models.user", "app.models.health", "app.models.chat", "app.models.personal_info"]
        }
    )
    await Tortoise.generate_schemas(safe=True)

async def close_db():
    await Tortoise.close_connections()
