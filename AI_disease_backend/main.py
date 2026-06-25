"""FastAPI 应用入口。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api import auth, chat, health, personal_info
from app.backend.views import backend
from app.utils.database import close_db, init_db
from app.utils.exceptions import BusinessError
from app.utils.logger import get_logger, setup_logging
from app.utils.ratelimit import limiter

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("应用启动完成")
    yield
    await close_db()
    logger.info("应用关闭")


app = FastAPI(
    title="AI 慢性病管理系统 API",
    description="管理血压 / 血糖 + AI 健康咨询",
    version="0.2.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    return JSONResponse(
        status_code=exc.http_status,
        content={"detail": exc.message},
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": f"请求过于频繁：{exc.detail}"},
    )


app.include_router(auth.router)
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(personal_info.router)

# 内部测试入口：文档上传 + RAG 查询
app.include_router(backend, prefix="/v1/backend", tags=["upload-internal"])


@app.get("/")
async def root():
    return {"message": "API is running. Visit /docs for OpenAPI."}


if __name__ == "__main__":
    import uvicorn

    from config.settings import settings

    uvicorn.run("main:app", host=settings.app_host, port=settings.app_port, reload=False)