"""开发期调试脚本：直接调 LangGraph workflow，验证节点逻辑。

⚠️ 不被服务调用，是 scripts/langGraph_main.py 的精简等价版。
   跑之前确保 MySQL / Milvus 已启动并完成首次入库；嵌入走 DashScope 云端 API。
"""
import os

from dotenv import load_dotenv

load_dotenv()  # noqa: E402  必须在 import lang_graph_core 之前

from lang_graph_core.core import workflow  # noqa: E402


def main():
    # 第一次调用：触发 risk → qa 分支
    result1 = workflow.invoke({
        "user_id": "demo_user",
        "condition": "",
        "age": 58,
        "blood_pressure": "150/95",
        "blood_sugar": "5.3",
        "query": "你好",
        "email": os.getenv("DEMO_EMAIL", ""),
        "history": [],
    })
    print("=" * 50)
    print("【风险评估】", result1.get("condition"))
    print("【首次回答】", result1.get("answer"))

    # 第二次调用：基于同一份 history 继续（验证 add_messages）
    result2 = workflow.invoke({
        "user_id": "demo_user",
        "condition": result1.get("condition", ""),
        "age": 58,
        "blood_pressure": "150/95",
        "blood_sugar": "5.3",
        "query": "饮食上要注意什么？",
        "email": os.getenv("DEMO_EMAIL", ""),
        "history": result1.get("history", []),
    })
    print("【饮食建议】", result2.get("answer"))
    print("【历史消息数】", len(result2.get("history", [])))
    print("=" * 50)


if __name__ == "__main__":
    main()