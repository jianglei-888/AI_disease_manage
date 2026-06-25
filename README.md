# AI 慢性病管理系统

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.1-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![LangChain](https://img.shields.io/badge/LangChain-1.2-green.svg)](https://www.langchain.com/)
[![Milvus](https://img.shields.io/badge/Milvus-2.6-00a1b2.svg)](https://milvus.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

基于 FastAPI + LangGraph + RAG 的慢性病（高血压 / 糖尿病）管理后端，配套微信小程序前端。让用户在小程序里录入健康指标 + 与 AI 健康助手对话，AI 基于用户近期数据、个人档案、医疗知识库给出个性化建议。

> 首个对外发布版本：[CHANGELOG.md](CHANGELOG.md) v0.1（2026-06-25）

## 核心能力

- 🩺 **健康记录与趋势分析** — 血压 + 血糖的录入、历史查询、按 day / week / month / year 聚合
- 🤖 **多分支 AI 助手** — LangGraph `risk → router → qa / rag / diet / email`，按 query 关键词路由
  - `qa`：通用健康问答
  - `rag`：基于 Milvus 的医疗知识库检索（DashScope 嵌入 + 通义千问 LLM）
  - `diet`：饮食建议
  - `email`：把建议通过 SMTP 推送到用户邮箱
- 👤 **个人档案** — 年龄、用药史、禁忌（AI 回答时一并注入上下文）
- 📚 **内部文档管理** — 后台页 `/v1/backend/` 上传 PDF / DOCX / MD / XLSX / CSV / TXT 入库，配套 RAG 检索测试
- 🛡️ **工程化** — Pydantic Settings 集中配置、JWT + PBKDF2 鉴权、slowapi 限流、自定义异常体系、pytest 套件、Docker Compose

## 截图

> 截图待补充。当前占位位于 [docs/screenshots/](docs/screenshots/)。

<!-- 推荐后续添加：
![聊天界面](docs/screenshots/chat.png)
![健康数据记录](docs/screenshots/submit.png)
![内部文档管理后台](docs/screenshots/backend.png)
-->

## 技术架构

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

聊天历史持久化：每次 LangGraph 调用前从 `chat_records` 加载最近 20 条转成 `BaseMessage` 注入 `state.history`，调用后用户消息和 AI 回复都落库。

## 项目结构

```
AI_disease_manage/
├── AI_disease_backend/         # FastAPI + LangGraph + RAG 后端
│   ├── app/                    # api / services / models / schemas / utils
│   ├── lang_graph_core/        # LangGraph 拓扑 + 节点 + State
│   ├── lang_chain_core/        # RAG 单例 + retrieve_medical_context
│   ├── scripts/                # Milvus 初始化 / demo_workflow / mcp_server
│   ├── tests/                  # pytest + RAG 评估套件
│   ├── main.py
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── docker-compose.yml
│
├── AI_disease_front/           # 微信小程序前端
│   ├── pages/                  # 8 个页面（login/register/home/submit/chat/profile/analysis/personal-info）
│   ├── services/               # auth / health / chat / personal-info service 封装
│   ├── components/             # 可复用组件
│   ├── utils/                  # api / auth / storage / common
│   ├── app.js / app.json / app.wxss
│   └── project.config.json
│
├── 1-需求分析/                  # 需求分析
├── 2-UI设计/                    # UI 草稿（HTML 静态页）
├── 3-项目架构/                  # 后端架构 / 小程序架构文档
├── docs/                       # 文档与截图
│
├── CLAUDE.md                   # Claude Code 项目说明（开发用）
├── CHANGELOG.md                # 变更日志
├── LICENSE                     # MIT
└── README.md                   # 本文件
```

## 快速开始

### 后端

```bash
cd AI_disease_backend
cp .env.example .env             # 填入数据库 / API_KEY / JWT 密钥
pip install -r requirements.txt
python scripts/creat_milvus_new.py   # 首次：会要求输入 YES 确认 drop 重建
uvicorn main:app --reload
```

启动后：
- API 文档：http://localhost:8001/docs
- 内部文档管理（仅测试用）：http://localhost:8001/v1/backend/

> 详细配置 / 故障排查见 [AI_disease_backend/README.md](AI_disease_backend/README.md)

### 前端

```bash
# 用微信开发者工具打开 AI_disease_front/ 目录
# 修改 utils/api.js 第 4 行 API_BASE_URL 为后端局域网 IP
```

> 详细联调步骤见 [AI_disease_front/README.md](AI_disease_front/README.md)

### Docker Compose

```bash
cd AI_disease_backend
cp .env.example .env
docker-compose up -d             # 启动 MySQL + backend
```

> Milvus 默认走外部虚拟机，地址在 `.env` 的 `MILVUS_URI`；嵌入走 DashScope 云端 API。

## 文档导航

| 文档 | 用途 |
|---|---|
| [AI_disease_backend/README.md](AI_disease_backend/README.md) | 后端详细说明：技术栈 / 快速启动 / 目录 / API / 架构图 |
| [AI_disease_front/README.md](AI_disease_front/README.md) | 前端快速开始 / 页面 / 目录结构 |
| [3-项目架构/1-项目后端架构文档.md](3-项目架构/1-项目后端架构文档.md) | 后端架构详细：ER 图 / API 设计 / 配置管理 / 部署 |
| [3-项目架构/2-微信小程序架构文档.md](3-项目架构/2-微信小程序架构文档.md) | 小程序架构详细：页面 / 组件 / API 调用 / 状态管理 |
| [1-需求分析/项目需求.md](1-需求分析/项目需求.md) | 产品需求 / 功能 / 数据结构 / 安全 |
| [CHANGELOG.md](CHANGELOG.md) | 变更日志 |
| [CLAUDE.md](CLAUDE.md) | Claude Code 项目说明（开发用） |

## 安全说明

- **全部密钥通过 `.env` 注入**，源码中无明文 DB 密码 / API_KEY / SMTP 授权码 / JWT 密钥
- `.env.example` 入仓（占位符），`.env` 由 `.gitignore` 排除
- `config/settings.py` 启动时强制校验 `DATABASE_URL`，缺失直接 `RuntimeError` 退出
- 全局异常 handler 接管业务异常，不向客户端泄露内部错误

## Roadmap

- [ ] 流式输出（`workflow.stream` + SSE / WebSocket）
- [ ] 父子 chunk / 小到大检索（RAG 精度优化）
- [ ] 接微信原生登录（`wx.login`）
- [ ] 健康数据图表可视化（前端）
- [ ] 接入更多 LLM 提供商（DeepSeek / Ollama 本地模型）
- [ ] CI / 自动化部署

## License

MIT — 详见 [LICENSE](LICENSE)
