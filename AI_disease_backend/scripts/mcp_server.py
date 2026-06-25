"""FastMCP 工具服务（独立进程，启动：python scripts/mcp_server.py）。

为 LangGraph 的 email 节点提供另一种调用通道。
默认端口 8888，与 config.settings.MCP_SERVER_URL 保持一致。
"""
from fastmcp import FastMCP

from app.utils.email import send_email as backend_send_email

app = FastMCP(
    name="disease-mcp",
    instructions="为 AI 慢性病管理项目提供工具",
)


@app.tool()
def send_email(to_email: str, subject: str, content: str) -> str:
    """根据提供的参数发送电子邮件。

    参数
    ----------
    to_email : str
        收件人的电子邮件地址。
    subject : str
        邮件的主题行。
    content : str
        邮件的主要内容。

    返回
    -------
    str
        成功消息或错误描述字符串。
    """
    return backend_send_email(to_email=to_email, subject=subject, content=content)


if __name__ == "__main__":
    print("mcp-server 启动在 8888 端口")
    app.run(transport="http", port=8888)