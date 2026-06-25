# AI 慢性病管理系统 - 后端

> 基于 FastAPI + LangGraph + RAG 的慢性病（高血压 / 糖尿病）管理后端，配套微信小程序前端。

## 项目背景

慢性病患者（高血压、糖尿病）需要长期记录血压、血糖并获得专业建议。传统问诊成本高、响应慢，普通健康类 App 缺乏个性化。本项目让用户在小程序里录入健康指标 + 与 AI 健康助手对话，AI 基于：

1. **用户最近一周的健康数据分析**（平均值 + 趋势 + 异常检测）
2. **个人档案**（年龄、用药史、禁忌）
3. **RAG 检索到的医疗知识库**（PDF / DOCX / MD 等）

给出个性化的健康建议，需要时可通过邮件把完整建议推送过去。

## 项目特性

- **安全优先**：全部密钥（DB 密码、LLM / DashScope API_KEY、JWT SECRET_KEY、SMTP 授权码）通过 `.env` 注入，源码中无明文；`config/settings.py` 启动时强制校验 `DATABASE_URL`，缺失直接 `RuntimeError` 退出
- **LangGraph 多分支工作流**：`risk → router → qa / rag / diet / email`，按 query 关键词路由，prompt / top-k 集中可调
- **RAG 共享检索**：`MedicalRAG` 与 LangGraph 的 `node_rag` 共用 `retrieve_medical_context(query)`，避免两份独立实现漂移
- **统一 `get_current_user`**：全局只剩 `app/utils/security.py` 一份
- **异常体系**：`BusinessError / AuthError / NotFoundError / ValidationError / ExternalServiceError` + 全局 handler
- **日志**：`app/utils/logger.py` 替代散落的 `print()`
- **配置集中**：`config/settings.py` 接管所有 `os.getenv()` 散落调用
- **聊天历史持久化**：LangGraph 的 `history` 从内存搬到 MySQL，跨会话保留
- **Docker Compose 一键启动**（MySQL + Milvus standalone + backend）
- **pytest 套件**（`auth_service` / `health_service`）
- **限流**：登录与聊天接口加 IP 限流（slowapi）

## 技术栈

| 类别 | 技术 |
|---|---|
| Web 框架 | FastAPI + Uvicorn |
| ORM | Tortoise ORM + Aerich |
| 数据库 | MySQL 8 |
| 鉴权 | JWT (python-jose) + PBKDF2 (passlib) |
| AI 编排 | LangGraph + LangChain |
| LLM | 通义千问（OpenAI 兼容模式） |
| 嵌入 | 阿里 DashScope（`text-embedding-v3`，1024 维） |
| 向量库 | Milvus 2.6 |
| 文档加载 | PyPDFLoader / Docx2txtLoader / UnstructuredExcelLoader / CSVLoader |
| 工具协议 | FastMCP（独立进程，HTTP 8888） |
| 部署 | Docker Compose |
| 测试 | pytest + aiosqlite |

## 快速启动

### 方式一：Docker Compose（推荐）

```bash
cd AI_disease_backend
cp .env.example .env       # 按需修改配置
docker-compose up -d       # 启动 MySQL + Milvus + backend
```

启动后访问：
- API 文档：`http://localhost:<APP_PORT>/docs`（端口由 `.env` 的 `APP_PORT` 控制）
- 内部文档管理（仅测试用）：`http://localhost:<APP_PORT>/v1/backend/`

> compose 仅起 MySQL + backend。Milvus 走 `.env` 的 `MILVUS_URI`（默认 `http://localhost:19530`，可指向远程虚拟机）；嵌入走 DashScope 云端 API，无需本地服务。

### 方式二：本地手动启动

```bash
# 1. 启动依赖（MySQL / Milvus 各自装好后起来；Milvus 地址在 .env 的 MILVUS_URI）
#    嵌入走 DashScope 云端 API（仅需在 .env 配 DASHSCOPE_API_KEY）

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置
cp .env.example .env       # 填入真实 API_KEY / 数据库密码 / JWT 密钥

# 4. 启动 Milvus 集合（首次；会要求输入 YES 确认 drop 重建）
python scripts/creat_milvus_new.py
# 或跳过交互：python scripts/creat_milvus_new.py --yes

# 5. 启动后端
uvicorn main:app --reload
```

### 微信小程序端联调

修改 [../AI_disease_front/utils/api.js](../AI_disease_front/utils/api.js) 第 4 行，把 `API_BASE_URL` 改成你电脑的局域网 IP（如 `http://192.168.1.100:8001`），端口与后端 `.env` 的 `APP_PORT` 一致。微信开发者工具里把"不校验合法域名"打开。

## 目录结构

```
AI_disease_backend/
├── main.py                     # FastAPI 入口 + 全局异常 handler
├── pyproject.toml              # Aerich 配置（不含 db_url，CLI 显式传）
├── requirements.txt            # 依赖
├── .env.example                # 配置模板（.env 真实文件不入库）
├── diease.sql                  # MySQL 初始化（仅 schema）
│
├── app/
│   ├── api/                    # FastAPI 路由层
│   │   ├── auth.py             # 注册 / 登录 / 当前用户
│   │   ├── health.py           # 健康记录 CRUD + 分析
│   │   ├── chat.py             # 聊天（POST /api/chat/messages）
│   │   └── personal_info.py    # 个人信息
│   ├── services/               # 业务逻辑
│   │   ├── auth_service.py
│   │   ├── health_service.py
│   │   ├── ai_service.py       # 编排 LangGraph
│   │   └── personal_info_service.py
│   ├── models/                 # Tortoise ORM 模型
│   ├── schemas/                # Pydantic 请求/响应模型
│   ├── utils/
│   │   ├── database.py         # Tortoise init / close
│   │   ├── security.py         # JWT + 密码 + get_current_user
│   │   ├── email.py            # SMTP 发送
│   │   ├── logger.py           # 统一日志
│   │   ├── exceptions.py       # 业务异常体系
│   │   └── ratelimit.py        # slowapi 限流
│   └── backend/                # 内部文档管理（Jinja2 + /v1/backend）
│
├── lang_chain_core/
│   └── rag_core.py             # MedicalRAG 单例 + retrieve_medical_context
│
├── lang_graph_core/
│   ├── config.py               # State schema + LLM / 嵌入工厂
│   ├── nodes.py                # 5 个节点 + router
│   └── core.py                 # workflow 编译
│
├── scripts/
│   ├── creat_milvus_new.py     # 首次创建 Milvus collection
│   ├── demo_workflow.py        # 直接跑 workflow 做本地调试
│   └── mcp_server.py           # FastMCP 工具服务（独立进程）
│
├── tests/                      # pytest 套件
├── uploads/                    # 后台上传的文档临时目录（不入库）
└── logs/                       # 应用日志（不入库）
```

## API 一览

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/auth/register` | 注册（邮箱 + 用户名 + 密码） |
| POST | `/api/auth/login` | 登录，返回 JWT |
| GET  | `/api/auth/me` | 当前用户信息 |
| POST | `/api/health/records` | 提交一条血压血糖记录 |
| GET  | `/api/health/records` | 历史记录（分页 + 日期过滤） |
| GET  | `/api/health/analysis` | 按 day / week / month / year 聚合分析 |
| GET  | `/api/personal-info/` | 获取个人信息（无则返回空对象） |
| POST | `/api/personal-info/` | 创建或更新个人信息 |
| POST | `/api/chat/messages` | 发送消息，返回 user + ai 两条 |
| GET  | `/api/chat/messages` | 历史消息（分页） |
| GET  | `/v1/backend/` | 内部：文档管理页（仅测试） |
| POST | `/v1/backend/upload` | 内部：上传医疗文档入库 |
| POST | `/v1/backend/search` | 内部：RAG 检索测试 |

## 架构图

```
┌──────────────┐       ┌─────────────────────────────────────────┐
│  微信小程序   │ ────▶ │            FastAPI (main.py)           │
│  (前端)       │ JWT   │  /api/auth /api/health /api/chat ...   │
└──────────────┘       └──────┬───────────────────┬───────────────┘
                              │                   │
                              ▼                   ▼
                     ┌────────────────┐  ┌──────────────────────┐
                     │   MySQL 8      │  │  LangGraph Workflow  │
                     │  Tortoise ORM  │  │                      │
                     │                │  │  risk → router →     │
                     │ users          │  │   ├ qa               │
                     │ health_records │  │   ├ rag → Milvus     │
                     │ chat_records ◀─┼──┤   ├ diet             │
                     │ personal_infos │  │   └ email → SMTP     │
                     └────────────────┘  └──────┬───────────────┘
                                                │
                                                ▼
                                       ┌────────────────┐
                                       │ DashScope Embed│
                                       │  + 通义千问 LLM │
                                       └────────────────┘
```

聊天历史持久化：每次 LangGraph 调用前从 `chat_records` 加载最近 N 条转成 `BaseMessage` 注入 `state.history`，调用后用户消息和 AI 回复都落库。

## 已知限制

- 没做用户头像上传（schema 暂未设计）
- DashScope `text-embedding-v3` 1024 维与 Milvus schema 绑定，换嵌入模型要重建 collection
- `chat_records` 跨会话读取窗口固定 20 条（`AIService.load_recent_history`）
- `/v1/backend` 上传无鉴权（按 README 顶部说明仅供内部测试）

## Roadmap

- [ ] 接微信原生登录（当前只有邮箱注册）
- [ ] 健康数据图表可视化（前端）
- [ ] 接入更多 LLM 提供商（DeepSeek / Ollama 本地模型）
- [ ] CI / 自动化部署

## License

MIT
