"""DashScope 嵌入薄封装。

走 LLM_BASE_URL 兼容模式下的 /v1/embeddings（与 LLM 走同一条白名单路径），
避开旧 path /api/v1/services/embeddings/... 在部分代理下被 RST 的问题。
对调用方保持与 langchain_community.embeddings.DashScopeEmbeddings 一致的最小接口：
.embed_query(text) -> list[float]
.embed_documents(texts) -> list[list[float]]
"""
from typing import List

from openai import OpenAI

from config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DashScopeCompatibleEmbeddings:
    def __init__(self):
        self.model = settings.EMBEDDING_MODEL
        self._client = OpenAI(
            api_key=settings.DASHSCOPE_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )

    def _embed(self, inputs: List[str]) -> List[List[float]]:
        resp = self._client.embeddings.create(model=self.model, input=inputs)
        # 兼容模式返回按 input 顺序排好，下游按入参顺序取即可
        return [d.embedding for d in resp.data]

    def embed_query(self, text: str) -> List[float]:
        return self._embed([text])[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embed(texts)
