# Changelog

记录本项目对外可见的版本变更。

## v0.1 - 2026-06-25

首个对外发布版本。包含一个完整的慢性病管理 Demo：FastAPI + LangGraph + RAG 后端，配套微信小程序前端。

### 主要能力

- 用户体系：邮箱注册 / 登录 / JWT 鉴权
- 健康记录：血压 + 血糖的录入、历史查询、按 day / week / month / year 聚合分析
- AI 健康助手：LangGraph 多分支工作流（`risk → router → qa / rag / diet / email`）
  - `qa`：通用健康问答
  - `rag`：基于 Milvus 的医疗知识库检索
  - `diet`：饮食建议
  - `email`：把建议通过 SMTP 推送到用户邮箱
- 个人档案：年龄、用药史、禁忌（AI 回答时一并注入上下文）
- 内部文档管理页 `/v1/backend/`：上传 PDF / DOCX / MD / XLSX / CSV / TXT 入库，配套 RAG 检索测试入口

### 工程化

- 全部密钥（DB 密码、LLM / DashScope API_KEY、JWT SECRET_KEY、SMTP 授权码）通过 `.env` 注入，源码中无明文
- `.env.example` 模板入仓、`.env` 本身由 `.gitignore` 排除
- Pydantic Settings 统一配置加载；`config/settings.py` 启动时校验 `DATABASE_URL`，缺失直接 `RuntimeError` 退出
- Docker Compose 一键启动 MySQL + Milvus + backend
- pytest 套件覆盖 `auth_service` / `health_service`
- slowapi IP 限流：登录与聊天接口
- 自定义业务异常体系（`BusinessError / AuthError / NotFoundError / ValidationError / ExternalServiceError`）+ 全局 handler
- 统一 `logging` 替代全部 `print()`
- 聊天历史持久化到 MySQL `chat_records`，跨会话保留

### 文档

- 根 `CLAUDE.md`：项目结构 + 常用命令 + 架构要点 + 本项目红线
- `AI_disease_backend/README.md`：项目背景 / 技术栈 / 快速启动 / 目录结构 / API 一览 / 架构图
- `AI_disease_front/README.md`：快速开始 / 页面 / 目录结构 / 注意事项
- `3-项目架构/1-项目后端架构文档.md`：技术栈 / 目录 / ER 图 / 接口设计 / 核心服务 / 配置 / 部署 / 安全 / 性能 / 监控
- `3-项目架构/2-微信小程序架构文档.md`：技术栈 / 目录 / 页面 / 组件 / API 调用 / 状态 / 路由 / 存储
- `1-需求分析/项目需求.md`：产品背景 / 功能需求 / 技术架构 / 数据结构 / 界面 / 安全 / 部署
- `LICENSE`：MIT
