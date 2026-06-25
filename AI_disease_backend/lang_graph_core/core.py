"""LangGraph 工作流编译。

拓扑：risk ──▶ router ──┬─▶ rag ──▶ END
                         ├─▶ diet ──▶ END
                         ├─▶ email ──▶ END
                         └─▶ qa ──▶ END
"""
from langgraph.graph import END, StateGraph

from lang_graph_core.config import State
from lang_graph_core.nodes import (
    node_diet,
    node_email,
    node_qa,
    node_rag,
    node_risk,
    router,
)

builder = StateGraph(State)
builder.add_node("risk", node_risk)
builder.add_node("qa", node_qa)
builder.add_node("rag", node_rag)
builder.add_node("diet", node_diet)
builder.add_node("email", node_email)

builder.set_entry_point("risk")
builder.add_conditional_edges("risk", router)

builder.add_edge("qa", END)
builder.add_edge("rag", END)
builder.add_edge("diet", END)
builder.add_edge("email", END)

workflow = builder.compile()