"""限流工具。

只对登录和聊天接口限流（重资源 / 易被刷的接口）。
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)