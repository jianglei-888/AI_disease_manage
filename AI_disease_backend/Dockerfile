# AI 慢性病管理 - 后端镜像
FROM python:3.11-slim

WORKDIR /app

# 系统依赖（gcc 给 cryptography / cffi 编译用）
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        default-libmysqlclient-dev \
        pkg-config \
        curl \
    && rm -rf /var/lib/apt/lists/*

# 先装依赖，利用 Docker 缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再拷代码（避免代码改动触发依赖重装）
COPY . .

EXPOSE 8000

# 启动：先等 Milvus / MySQL 健康，再启 uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]