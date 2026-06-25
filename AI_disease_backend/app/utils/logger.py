"""统一日志配置。

替代代码中散落的 print() 调用。
"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def setup_logging(log_dir: str = "logs", level: str = "INFO") -> None:
    """初始化全局日志。

    - 控制台：INFO 级别
    - 文件：DEBUG 级别，10MB 滚动
    """
    os.makedirs(log_dir, exist_ok=True)

    root = logging.getLogger()
    if root.handlers:
        # 幂等：避免重复添加 handler（uvicorn --reload 场景）
        return

    root.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    root.addHandler(console)

    file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, "app.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)