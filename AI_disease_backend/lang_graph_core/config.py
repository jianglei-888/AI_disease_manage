"""LangGraph 全局配置：LLM、嵌入、State schema。"""
import operator
from typing import Annotated, List, TypedDict

from langchain_core.messages import BaseMessage
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages

from config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        temperature=0,
    )


def build_embeddings() -> DashScopeEmbeddings:
    return DashScopeEmbeddings(
        model=settings.EMBEDDING_MODEL,
        dashscope_api_key=settings.DASHSCOPE_API_KEY,
    )


llm = build_llm()
embeddings = build_embeddings()


class State(TypedDict):
    """LangGraph 跨节点共享的状态。

    history 用 add_messages：把 BaseMessage 列表做"追加合并"。
    """

    user_id: str                              # 用户 id
    condition: str                            # 慢性病情况（risk 节点产出）
    age: int                                  # 年龄
    blood_pressure: str                       # 血压（"150/95"）
    blood_sugar: str                          # 血糖
    query: str                                # 用户当前问题
    history: Annotated[List[BaseMessage], add_messages]
    answer: str                               # 最近一次回答（供 email 节点使用）
    email: str                                # 收件邮箱