"""业务异常体系。

service 层抛这些，api 层 / 全局 handler 统一翻译成 HTTPException。
"""


class BusinessError(Exception):
    """所有业务异常的基类。"""

    http_status: int = 400

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class AuthError(BusinessError):
    http_status = 401


class NotFoundError(BusinessError):
    http_status = 404


class ValidationError(BusinessError):
    http_status = 422


class ExternalServiceError(BusinessError):
    """LLM / Milvus / SMTP 等外部服务失败。"""

    http_status = 502