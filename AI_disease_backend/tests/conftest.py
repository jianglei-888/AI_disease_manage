"""测试公共配置：内存 SQLite + Tortoise 初始化。

测试时 DB 用 aiosqlite://:memory:，不依赖外部 MySQL。
"""
import asyncio
import os
import sys

import pytest
import pytest_asyncio

# 把项目根加进 sys.path（pytest 默认不会加）
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_init():
    """每个测试函数跑前初始化内存 DB，跑完清理。"""
    from tortoise import Tortoise

    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["app.models.user", "app.models.health", "app.models.chat", "app.models.personal_info"]},
    )
    await Tortoise.generate_schemas(safe=True)
    yield
    await Tortoise.close_connections()