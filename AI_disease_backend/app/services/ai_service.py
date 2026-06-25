"""AI 服务：编排 LangGraph workflow 完成风险评估 + 意图路由 + 回复生成。

`send_message` 是聊天接口的主入口：
  1. 把用户消息写入 chat_records
  2. 加载健康数据 + 个人信息作为 LangGraph State
  3. 调 workflow.invoke 得到 AI 回复
  4. 把 AI 回复写入 chat_records
"""
from app.models.chat import ChatRecord
from app.schemas.chat import ChatResponse, MessageCreate, MessageList, MessageResponse
from app.services.health_service import HealthService
from app.services.personal_info_service import PersonalInfoService
from app.utils.exceptions import NotFoundError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AIService:
    @staticmethod
    async def send_message(user_id: int, message_data: MessageCreate) -> ChatResponse:
        # 1. 持久化用户消息
        user_message = await ChatRecord.create(
            user_id=user_id,
            message=message_data.message,
            role="user",
        )

        # 2. 组装 LangGraph State
        state = await AIService._build_state(user_id, message_data.message)

        # 3. 跑工作流
        from lang_graph_core.core import workflow
        try:
            result = workflow.invoke(state)
            ai_reply = result.get("answer") or "抱歉，我暂时无法回答，请稍后再试。"
        except Exception as exc:
            logger.exception("LangGraph 调用失败：%s", exc)
            ai_reply = f"AI 服务暂时不可用：{exc}"

        # 4. 持久化 AI 回复
        ai_message = await ChatRecord.create(
            user_id=user_id,
            message=ai_reply,
            role="ai",
        )

        logger.info(
            "聊天完成：user_id=%s user_msg_id=%s ai_msg_id=%s",
            user_id, user_message.id, ai_message.id,
        )

        return ChatResponse(
            user_message=MessageResponse.model_validate(user_message),
            ai_response=MessageResponse.model_validate(ai_message),
        )

    @staticmethod
    async def get_messages(user_id: int, limit: int, offset: int) -> MessageList:
        query = ChatRecord.filter(user_id=user_id)
        total = await query.count()
        messages = await query.order_by("created_at").offset(offset).limit(limit).all()
        return MessageList(
            total=total,
            messages=[MessageResponse.model_validate(m) for m in messages],
        )

    @staticmethod
    async def load_recent_history(user_id: int, limit: int = 20) -> list:
        """加载最近的聊天历史（LangGraph add_messages 用）。"""
        records = await (
            ChatRecord.filter(user_id=user_id)
            .order_by("-created_at")
            .limit(limit)
            .all()
        )
        # 倒序回来，再统一转 BaseMessage
        from langchain_core.messages import AIMessage, HumanMessage
        records.reverse()
        result = []
        for r in records:
            if r.role == "user":
                result.append(HumanMessage(content=r.message))
            else:
                result.append(AIMessage(content=r.message))
        return result

    @staticmethod
    async def _build_state(user_id: int, message: str) -> dict:
        """组装 LangGraph 初始 State。

        优先从健康数据 + 个人信息里取；取不到就用默认值。
        """
        try:
            analysis = await HealthService.get_analysis(user_id, "week")
            avg = analysis.average
            blood_pressure = f"{avg.get('systolic', 120)}/{avg.get('diastolic', 80)}"
            blood_sugar = avg.get("blood_sugar", 5.5)
        except NotFoundError:
            blood_pressure = "120/80"
            blood_sugar = 5.5

        personal = await PersonalInfoService.get_personal_info(user_id)
        history = await AIService.load_recent_history(user_id)

        return {
            "user_id": str(user_id),
            "condition": "",
            "age": personal.age or 0,
            "blood_pressure": blood_pressure,
            "blood_sugar": blood_sugar,
            "query": message,
            "email": personal.email or "",
            "history": history,
        }