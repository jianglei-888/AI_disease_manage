"""LangGraph 节点：风险评估 / 健康问答 / RAG 检索 / 饮食建议 / 邮件推送。"""
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.utils.email import send_email
from app.utils.logger import get_logger
from config.settings import settings
from lang_chain_core.rag_core import retrieve_medical_context
from lang_graph_core.config import State, llm

logger = get_logger(__name__)


def node_risk(state: State):
    """基于血压 / 血糖 / 年龄做风险评估。"""
    prompt = ChatPromptTemplate.from_template("""
    用户健康数据：
    年龄：{age}
    血压：{blood_pressure}
    血糖：{blood_sugar}

    根据用户血压和血糖，请评估慢性病情况和风险。
    """)
    chain = prompt | llm | StrOutputParser()
    risk = chain.invoke({
        "age": state["age"],
        "blood_pressure": state["blood_pressure"],
        "blood_sugar": state["blood_sugar"],
    })
    return {
        "answer": risk,
        "condition": risk,
        "history": [AIMessage(content=risk)],
    }


def node_qa(state: State):
    """通用健康问答。"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是专业慢性病管理助手，简洁、安全、不夸大、不做诊断。"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{query}"),
    ])
    chain = prompt | llm | StrOutputParser()
    ans = chain.invoke({"history": state["history"], "query": state["query"]})
    return {
        "answer": ans,
        "history": [AIMessage(content=ans)],
    }


def node_rag(state: State):
    """RAG：检索 Milvus → 基于上下文生成回答。"""
    context = retrieve_medical_context(state["query"])
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"根据以下资料严谨回答，不编造。\n资料：{{context}}"),
        ("human", "{query}"),
    ])
    chain = prompt | llm | StrOutputParser()
    ans = chain.invoke({"context": context, "query": state["query"]})
    return {
        "answer": ans,
        "history": [AIMessage(content=ans)],
    }


def node_diet(state: State):
    """基于 condition 给出饮食建议。"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "根据疾病给出简洁饮食建议"),
        ("human", "疾病：{condition}"),
    ])
    chain = prompt | llm | StrOutputParser()
    advice = chain.invoke({"condition": state["condition"]})
    return {
        "answer": advice,
        "history": [AIMessage(content=advice)],
    }


def node_email(state: State):
    """将上一次回答通过邮件推送给用户。"""
    to_email = state.get("email")
    content = state.get("answer", "暂无建议，请先咨询。")
    result = send_email(
        to_email=to_email,
        subject="AI 慢性病管理 - 健康建议",
        content=f"健康管理建议：\n\n{content}",
    )
    logger.info("邮件推送结果：%s", result)
    return {
        "answer": result,
        "history": [AIMessage(content=result)],
    }


def router(state: State) -> str:
    """基于 query 关键词分发到不同节点。"""
    q = state["query"]
    if any(w in q for w in ["药", "说明书", "指南", "治疗", "副作用"]):
        return "rag"
    if any(w in q for w in ["吃", "饮食", "忌口"]):
        return "diet"
    if any(w in q for w in ["邮件", "发送"]):
        return "email"
    return "qa"