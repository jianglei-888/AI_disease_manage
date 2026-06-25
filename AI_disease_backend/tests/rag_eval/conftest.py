"""RAG 评估专用 conftest。

注意：
- 父 conftest.py 的 `db_init` fixture 在这里被覆写为 no-op，
  因为评估完全不需要 DB（不读 user / health / chat record）。
- 所有重资源（embedder / milvus / llm / rag_chain）都用 scope="session"，
  20 条样本共用一份。
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml


DATA_DIR = Path(__file__).resolve().parent / "data"


@pytest.fixture(scope="session")
def qa_samples():
    """从 qa_set.yaml 读 QASample 列表。"""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tests.rag_eval.runner import load_qa_samples
    return load_qa_samples(str(DATA_DIR / "qa_set.yaml"))


@pytest.fixture(scope="session")
def embedder():
    """嵌入模型实例（session 级，20 条样本共用）。"""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.utils.embeddings import DashScopeCompatibleEmbeddings
    return DashScopeCompatibleEmbeddings()


@pytest.fixture(scope="session")
def milvus_client():
    """Milvus 客户端（只读，评估绝不 insert/delete）。"""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from pymilvus import MilvusClient
    from config.settings import settings
    return MilvusClient(uri=settings.MILVUS_URI, db_name=settings.MILVUS_DB)


@pytest.fixture(scope="session")
def judge_llm():
    """Judge LLM：温度 0 保证结果可复现。"""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from langchain_openai import ChatOpenAI
    from config.settings import settings
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        temperature=0,
    )


@pytest.fixture(scope="session")
def rag_chain():
    """RAG 问答 chain（被测对象）。"""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from lang_chain_core.rag_core import rag
    return rag.get_chain()


# 覆写父 conftest 的 db_init 为 no-op —— 评估完全不需要 DB
@pytest.fixture
def db_init():
    yield


# 让 pytest 默认收集时看到这个目录的文件
collect_ignore_glob = []  # 不忽略任何文件