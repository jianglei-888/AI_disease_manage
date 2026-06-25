"""邮件发送工具。

所有 SMTP 配置从 settings 读取，不再硬编码账号密码。
"""
import smtplib
from email.mime.text import MIMEText
from typing import Optional

from config.settings import settings


def _smtp_configured() -> bool:
    return bool(settings.SMTP_USERNAME and settings.SMTP_PASSWORD and settings.SMTP_SENDER_EMAIL)


def send_email(
    to_email: str,
    subject: str,
    content: str,
) -> str:
    """发送一封纯文本邮件。

    返回人类可读的状态字符串，便于 LangGraph node 直接作为回答返回。
    """
    if not _smtp_configured():
        return "邮件未发送：SMTP 配置不完整，请在 .env 中配置 SMTP_USERNAME / SMTP_PASSWORD / SMTP_SENDER_EMAIL"

    if not to_email:
        return "邮件未发送：缺少收件人邮箱"

    try:
        msg = MIMEText(content, "plain", "utf-8")
        msg["From"] = settings.SMTP_SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_SENDER_EMAIL, [to_email], msg.as_string())

        return f"建议已发送到 {to_email}"
    except Exception as exc:
        return f"邮件发送失败：{exc}"


def send_email_via_mcp(
    to_email: str,
    subject: str,
    content: str,
    mcp_server_url: Optional[str] = None,
) -> str:
    """通过 MCP 工具服务发送邮件（备用通道）。

    默认尝试 localhost:8888 上的 FastMCP 服务。
    """
    import requests

    url = mcp_server_url or settings.MCP_SERVER_URL
    try:
        resp = requests.post(
            f"{url}/tools/send_email",
            json={"to_email": to_email, "subject": subject, "content": content},
            timeout=10,
        )
        if resp.ok:
            return f"建议已发送到 {to_email}"
        return f"邮件发送失败：HTTP {resp.status_code}"
    except Exception as exc:
        return f"邮件发送失败：{exc}"