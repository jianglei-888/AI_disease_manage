# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目结构

两端分离的慢性病管理系统，根目录下两个独立工程：

- [AI_disease_backend/](AI_disease_backend/) — FastAPI 后端 + LangGraph/LangChain AI 服务
- [AI_disease_front/](AI_disease_front/) — 微信小程序前端

非代码目录（设计 / 资料，已纳入 git）：[1-需求分析/](1-需求分析/)、[2-UI设计/](2-UI设计/)、[3-项目架构/](3-项目架构/)、[docs/](docs/)。后端 README 在 [AI_disease_backend/README.md](AI_disease_backend/README.md)；架构文档以 [3-项目架构/1-项目后端架构文档.md](3-项目架构/1-项目后端架构文档.md) 为准（与 README 略有出入时以代码为准）。

## 常用命令

后端（cwd = `AI_disease_backend/`）：

```bash
pip install -r requirements.txt   # requirements.txt 已是 UTF-8 编码
python main.py                    # 启动 API：端口 / Host 走 .env 的 APP_PORT / APP_HOST（默认 8001 / 0.0.0.0）
# 备选：uvicorn main:app --reload  # 不传 port 时默认 8000，与 .env 的 APP_PORT 不一致；建议显式传
```

数据库（MySQL 8，schema 在 `diease.sql`；启动时也会 `Tortoise.generate_schemas(safe=True)` 自动建表，所以 aerich 不是强制要求）：

```bash
mysql -u root -p < diease.sql     # 首次建库（库名 diease，密码见 .env）
# 仅当需要管理迁移时（pyproject.toml 不再含 db_url，必须显式传）
export $(grep -v '^#' AI_disease_backend/.env | xargs)   # 临时把 .env 注入当前 shell
aerich init -t config.settings --db-url "$DATABASE_URL"
aerich init-db --db-url "$DATABASE_URL"
aerich migrate --db-url "$DATABASE_URL"
aerich upgrade --db-url "$DATABASE_URL"
```

AI 依赖服务（必须先起来，否则 chat / RAG 报错）：

```bash
# Milvus（向量库，地址在 .env 的 MILVUS_URI；本机默认 http://localhost:19530）
python scripts/creat_milvus_new.py   # 首次执行：会 drop 重建 medical_RAG.medical_knowledge，运行前需输入 YES（或传 --yes）

# 嵌入（阿里 DashScope 云端，配置在 .env 的 EMBEDDING_MODEL=text-embedding-v3 / DASHSCOPE_API_KEY）
# 仅需在 .env 配 DASHSCOPE_API_KEY，无需本地进程

# MCP 工具服务（可选，独立进程，HTTP 8888）
python scripts/mcp_server.py
```

知识库灌库走后台页面：启动后端后访问 `http://localhost:<APP_PORT>/v1/backend/`，上传 PDF / DOCX / MD / XLSX / CSV / TXT（这个入口"仅限内部测试，切勿给用户使用"，见 [main.py:71](AI_disease_backend/main.py#L71)）。

前端（微信开发者工具打开 `AI_disease_front/` 目录即可）。后端地址写死在 [AI_disease_front/utils/api.js:4](AI_disease_front/utils/api.js#L4)（默认 `http://127.0.0.1:8001`）——**换机器开发必须改这里**，微信小程序不会用 `127.0.0.1`。

## 架构要点

### 后端分层

```
main.py                     # 注册路由 + lifespan 起停 Tortoise + 全局异常 handler
config/settings.py          # Pydantic Settings，DATABASE_URL 等；.env 会覆盖默认值；启动时强制校验
app/api/                    # FastAPI 路由：auth / health / chat / personal_info
app/services/               # 业务逻辑层（与 api 一一对应）
app/models/                 # Tortoise ORM 模型：user / health / chat / personal_info
app/schemas/                # Pydantic 请求 / 响应模型
app/utils/                  # database / security / email / logger / exceptions / ratelimit
app/backend/                # Jinja2 模板的"内部"上传 / 检索后台（前缀 /v1/backend）
lang_chain_core/rag_core.py # RAG 单例 MedicalRAG + retrieve_medical_context（被 LangGraph node_rag 共享）
lang_graph_core/            # LangGraph 工作流：config(State+llm) / nodes / core(builder)
```

API 全部 `/api/auth`、`/api/health`、`/api/chat`、`/api/personal-info` 前缀；用户认证统一 `Authorization: Bearer <jwt>`。

### 聊天的真实链路

用户消息 → [app/api/chat.py](AI_disease_backend/app/api/chat.py) → [AIService.send_message](AI_disease_backend/app/services/ai_service.py) → 拉用户最近周分析（HealthService）+ 个人信息 → 调 `lang_graph_core.core.workflow.invoke(...)` → 保存 user / ai 两条 ChatRecord 返回。

LangGraph 拓扑（入口 `risk`，再按 query 关键词路由）：

```
risk ──▶ router ──┬─▶ rag    (含 "药 / 说明书 / 指南 / 治疗 / 副作用")
                  ├─▶ diet   (含 "吃 / 饮食 / 忌口")
                  ├─▶ email  (含 "邮件 / 发送")
                  └─▶ qa     (其他)
所有分支 ──▶ END
```

State / 节点定义在 [lang_graph_core/config.py](AI_disease_backend/lang_graph_core/config.py) 与 [nodes.py](AI_disease_backend/lang_graph_core/nodes.py)；编译在 [core.py](AI_disease_backend/lang_graph_core/core.py)。

### 两份"几乎相同"的代码——别改错位置

- **LangGraph**：[lang_graph_core/](AI_disease_backend/lang_graph_core/) 是被 `AIService` 真正调用的版本；等价的精简调试入口保留为 [scripts/demo_workflow.py](AI_disease_backend/scripts/demo_workflow.py)。改 LangGraph 逻辑只需改 `lang_graph_core/`，调试时跑 `demo_workflow.py`。
- **RAG**：[lang_chain_core/rag_core.py](AI_disease_backend/lang_chain_core/rag_core.py) 的 `MedicalRAG` 被后台 `/v1/backend/search` 用（同时负责文档入库）；[lang_graph_core/nodes.py](AI_disease_backend/lang_graph_core/nodes.py) 的 `node_rag` 已通过 [retrieve_medical_context](AI_disease_backend/lang_chain_core/rag_core.py) 共享检索函数，不再独立实现。**修改 prompt / top-k / 检索字段只改 `retrieve_medical_context` 一处即可**。
- **`get_current_user`**：全局统一到 [app/utils/security.py](AI_disease_backend/app/utils/security.py) 一份；`auth.py` / `health.py` / `chat.py` / `personal_info.py` 都从这里 import。**新接口直接 import，别再写第二份**。

### 配置与密钥管理

- 后端进程读 [AI_disease_backend/.env](AI_disease_backend/.env)（DB / LLM / Milvus / Embedding / SMTP）。脚本没有独立 `.env`，跑 `scripts/*.py` 也走这份。
- LLM 默认走通义千问兼容接口（`BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1`，`LLM_MODEL=qwen3.6-plus`）；嵌入走阿里 DashScope 云端（`EMBEDDING_MODEL=text-embedding-v3`，维度 1024 对齐 Milvus schema），需配 `DASHSCOPE_API_KEY`。
- **源码硬编码密钥现状**（v0.1 已清理）：
  - DB / LLM / SMTP / JWT 全部通过 `.env` 注入，**源码里无明文密钥**。`config/settings.py` 的 `DATABASE_URL` 默认值为 `None`，启动时若未配会 `RuntimeError` 失败。
  - `.env`（不入库）和 `.env.example`（入库模板）按 GitHub 标准管理；不要把真实的 `.env` 内容粘贴到文档、Issue、PR 或聊天记录里。

### 前端

微信原生小程序。Page → `services/*.service.js` → `utils/api.js` 统一 `wx.request`，所有请求带 `Authorization: Bearer <token>`（token 从 `wx.getStorageSync('token')` 取）。全局态在 [app.js](AI_disease_front/app.js) 的 `globalData`。`app.json` 里的 tabBar 是 home / submit / chat / profile 四项，但 pages 列表还有 `personal-info` 与 `analysis` 两个非 tab 页。

## 改动后的验证

- 接口改动：起 `uvicorn main:app --reload`，FastAPI 自带的 `http://localhost:<APP_PORT>/docs` 直接打。
- LangGraph 节点：跑 `python scripts/demo_workflow.py`。
- RAG：经 `/v1/backend/` 页面上传 + 查询；或起后端后用 `curl` / `requests` 调 `/api/chat/messages`，关键词带"说明书 / 治疗"等触发 rag 分支。
- 前端：微信开发者工具点"编译"，看 Network 面板请求是否 200；接口域名出错优先查 [utils/api.js](AI_disease_front/utils/api.js)。

## 这个项目的红线（除全局红线外，本项目特殊）

- 不要改 `diease.sql` 与 `app/models/*.py` 的字段而不同步另一边；项目同时存在"启动自动建表"和"手动 SQL"两条路径，schema 漂移很难发现。
- 不要 `python scripts/creat_milvus_new.py` 用于"刷新"——脚本会 `drop_collection` 后重建。**运行前必须输入 `YES`（或传 `--yes` flag）才会真正执行**；脚本默认安全（拒答自动退出），但仍要确认是首次初始化再跑。
- 不要把真实的 `.env` 内容、API_KEY、SMTP 授权码、JWT 密钥推到公开仓库；如果要清洗、轮换或分享配置，统一改成 `os.getenv()` 读。
- 上传到 git 前再扫一遍：`git status` 检查是否有 `.env` / `uploads/` / `*.log` / `.idea/` / `.vscode/` 等本应被忽略的文件被误入。
