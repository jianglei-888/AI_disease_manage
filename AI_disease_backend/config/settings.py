from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv


class Settings(BaseSettings):
    # ============ 服务基础 ============
    app_name: str = "AI 慢性病管理系统"
    app_port: int = 8001
    app_host: str = "0.0.0.0"
    app_env: str = "dev"
    app_debug: bool = True

    # ============ 数据库 ============
    DATABASE_URL: Optional[str] = None

    # ============ JWT ============
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 天，方便小程序调试

    # ============ LLM ============
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "qwen3.6-plus"
    LLM_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # ============ 嵌入模型（DashScope text-embedding-v3，维度 1024 对齐 Milvus schema） ============
    # 走 LLM_BASE_URL 兼容模式（/v1/embeddings），避开旧 path /api/v1/services/embeddings/... 在部分代理下被 RST
    EMBEDDING_MODEL: str = "text-embedding-v3"
    DASHSCOPE_API_KEY: Optional[str] = None
    EMBEDDING_DIM: int = 1024

    # ============ Milvus ============
    MILVUS_URI: str = "http://localhost:19530"
    MILVUS_DB: str = "medical_RAG"
    MILVUS_COLLECTION: str = "medical_knowledge"
    MILVUS_TOKEN: str = ""

    # ============ 文档切分 ============
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # ============ SMTP 邮件 ============
    SMTP_SERVER: str = "smtp.qq.com"
    SMTP_PORT: int = 587
    SMTP_SENDER_EMAIL: Optional[str] = None      # 发件邮箱（<YOUR_EMAIL>@qq.com）
    SMTP_USERNAME: Optional[str] = None          # 通常与 SMTP_SENDER_EMAIL 相同
    SMTP_PASSWORD: Optional[str] = None          # SMTP 授权码（非登录密码）

    # ============ MCP ============
    MCP_SERVER_URL: str = "http://localhost:8888"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **values):
        super().__init__(**values)
        if not self.DATABASE_URL:
            raise RuntimeError(
                "DATABASE_URL 未配置：请在 AI_disease_backend/.env 中设置 DATABASE_URL"
            )


load_dotenv()
settings = Settings()