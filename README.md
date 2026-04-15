<div align="center">

# BoncFlow

**下一代可视化 RAG 工作流引擎**

*Production-grade RAG workflow engine — deep document understanding, grounded citations, visual agent orchestration, and 20+ LLM integrations in one platform*

[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?logo=react)](https://react.dev/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python)](https://python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql)](https://www.postgresql.org/)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.x-005571?logo=elasticsearch)](https://www.elastic.co/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Apache_2.0-D22128.svg)](LICENSE)

[English](#overview) · [快速开始](#quick-start) · [功能特性](#key-features) · [架构设计](#architecture)

</div>

---

## Overview

企业落地 RAG 系统时普遍面临四大瓶颈：

- **文档解析精度低** — PDF 表格错位、扫描件无法识别、PPT 图文混排丢失结构
- **检索结果不可信** — LLM 回答无法溯源，用户不知道答案从哪来
- **工作流编排靠硬编码** — 每个业务场景都要写代码，迭代成本高
- **模型绑定单一厂商** — 切换 LLM 需要改代码，无法灵活选型

BoncFlow 是一套 **端到端的 RAG + Agent 工作流平台**，从文档入库到智能问答全链路覆盖。自研 `deepdoc` 引擎支持 12+ 文档格式的高精度解析，模板化分块让每个 chunk 可追溯到原文位置，画布式拖拽编辑器内置 22 个 Agent 组件，无需编码即可编排复杂业务流程。同时集成 20+ 主流 LLM、GraphRAG 图谱增强检索、MCP 工具协议、gVisor 安全沙箱，开箱即用。

```
┌─────────────────────────────────────────────────────────────────────┐
│                     React Frontend (UmiJS + Ant Design)              │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌───────┐ │
│  │文档管理 │ │知识库   │ │Agent   │ │对话界面 │ │数据看板 │ │系统    │ │
│  │        │ │        │ │Canvas  │ │Chat    │ │Dashboard│ │Admin  │ │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └───────┘ │
├─────────────────────────────────────────────────────────────────────┤
│                  Flask/Quart Backend (Async)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ deepdoc  │ │ RAG Core │ │  Agent   │ │ GraphRAG │ │   MCP    │ │
│  │ 12+ 格式 │ │ 检索+排序 │ │ 22 组件  │ │ 图谱增强  │ │ 工具协议 │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
├─────────────────────────────────────────────────────────────────────┤
│  PostgreSQL  │ Elasticsearch │  Redis  │  S3/MinIO  │   LanceDB   │
│  (Metadata)  │ (Fulltext)    │ (Cache) │  (Object)  │  (Vector)   │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Features

### Deep Document Understanding

自研 `deepdoc` 文档理解引擎，集成 OCR、版面识别、表格结构检测，从复杂排版中精确提取知识。

| 格式 | 解析器 | 能力 |
|------|--------|------|
| PDF | `RAGFlowPdfParser` / `VisionParser` / `MinerUParser` | 文本提取、版面识别、图表分离、扫描件 OCR |
| Word | `RAGFlowDocxParser` | 段落、表格、嵌入图片、样式保留 |
| Excel | `RAGFlowExcelParser` | 多 Sheet 解析、公式计算、数据类型识别 |
| PPT | `RAGFlowPptParser` | 幻灯片文本、备注、嵌入对象 |
| HTML | `RAGFlowHtmlParser` | 网页正文提取、标签清洗 |
| Markdown | `RAGFlowMarkdownParser` | 结构化元素提取、代码块保留 |
| JSON | `RAGFlowJsonParser` | 嵌套结构展平、Schema 感知 |
| 简历 | Resume Parser (两阶段) | 实体抽取、字段归一化 |
| 图片 | `VisionFigureParser` | 图表识别、OCR 文字提取 |

### Template-Based Intelligent Chunking

提供多种分块策略，每个 chunk 保留原文页码与坐标定位：

- **递归字符分块** — 按 token 数（默认 512）+ 自定义分隔符切分，支持重叠窗口
- **语义分块** — 基于嵌入相似度自动识别语义边界
- **层级合并** — `HierarchicalMerger` 多层级 chunk 合并，保留文档结构
- **RAPTOR** — 递归抽象处理，构建树状检索结构，适合长文档

### Grounded Citations & Traceability

每条检索结果附带原文引用与高亮定位，用户可一键跳转原文验证。分块可视化界面直观展示切分效果，从源头建立对 AI 回答的信任，大幅降低幻觉率。

### Visual Agent Workflow Canvas

画布式拖拽工作流编辑器，内置 **22 个 Agent 组件**，无需编码即可编排复杂业务流程：

| 类别 | 组件 | 说明 |
|------|------|------|
| 流程控制 | `Begin` / `Switch` / `Loop` / `ExitLoop` / `Iteration` | 入口、条件分支、循环、迭代 |
| AI 能力 | `LLM` / `AgentWithTools` / `Categorize` | 大模型调用、工具增强 Agent、分类 |
| 数据处理 | `StringTransform` / `DataOperations` / `ListOperations` / `ExcelProcessor` | 字符串变换、数据运算、列表操作、Excel 处理 |
| 变量管理 | `VariableAssigner` / `VariableAggregator` / `FillUp` | 赋值、聚合、用户输入填充 |
| 输出生成 | `DocsGenerator` / `Message` | PDF/文档生成、消息输出 |
| 外部集成 | `Invoke` | HTTP 调用外部服务 |

**典型场景**：客服知识库问答、合同条款审查、财报数据提取、简历筛选、技术文档搜索

### Multi-LLM Ecosystem

一套代码对接 20+ 主流大模型，切换模型只需改配置，业务代码零改动：

| 类别 | 支持的模型/厂商 |
|------|----------------|
| 国际模型 | OpenAI (GPT-4o/5)、Anthropic (Claude 4.x)、Google (Gemini)、Mistral、Cohere、Groq |
| 国产模型 | 通义千问 (Qwen)、智谱 (GLM)、百川、DeepSeek、百度文心、讯飞星火、腾讯混元 |
| 本地部署 | Ollama、vLLM、LM Studio、LocalAI、Replicate |
| Embedding | sentence-transformers、Jina、NVIDIA、SiliconFlow、多厂商 API |
| Reranker | Jina、NVIDIA、SiliconFlow、LocalAI、302AI 等 8+ 实现 |
| TTS/语音 | FishAudio、Qwen TTS、OpenAI TTS 等 12+ 实现 |

### GraphRAG — 图谱增强检索

超越传统向量检索，构建实体关系图谱提升复杂问题的推理能力：

- **实体抽取** — LLM 驱动的命名实体识别与关系抽取
- **社区发现** — Leiden 算法自动聚类相关实体
- **知识图谱索引** — 实体、关系、社区三级索引
- **图谱检索** — 结合向量相似度与图结构的混合检索
- **查询改写** — LLM 自动改写用户查询，提升召回率

### MCP (Model Context Protocol) Integration

内置 MCP Server 与 Client，支持标准化工具调用协议。Agent 可通过 MCP 调用外部工具、数据库、API，扩展能力边界无上限。

### Secure Code Execution Sandbox

基于 gVisor 的安全沙箱，支持 Python / JavaScript 代码执行：
- 资源隔离：CPU、内存、网络严格限制
- 速率控制：防止滥用的请求频率限制
- 安全审计：完整的执行日志与安全测试套件

### 20+ Data Source Sync

| 类别 | 数据源 |
|------|--------|
| 协作平台 | Confluence、Notion、Airtable、Asana |
| 云存储 | AWS S3、Google Drive、Dropbox、Box |
| 开发工具 | Jira、GitLab、GitHub |
| 通讯工具 | Slack、Discord、Moodle |
| 网页抓取 | Firecrawl、Crawl4AI、Selenium |

### Multi-Tenant & Enterprise Auth

多租户架构，支持 OAuth 2.0、OIDC、GitHub 登录等企业级认证方式。Langfuse 集成提供 LLM 可观测性。

## Use Cases

| 场景 | 描述 | 核心组件 |
|------|------|----------|
| 企业知识库问答 | 上传内部文档，员工自然语言提问获取精准答案 | deepdoc + RAG + Chat |
| 合同条款审查 | 自动提取合同关键条款，对比标准模板识别风险点 | PDF Parser + LLM + Extractor |
| 财报数据分析 | 解析 Excel/PDF 财报，自然语言查询财务指标 | Excel Parser + Agent + DataOps |
| 智能客服 | 基于产品文档的多轮对话客服，支持引用溯源 | RAG + Chat + Citations |
| 简历智能筛选 | 批量解析简历，按岗位要求自动评分排序 | Resume Parser + Categorize + LLM |
| 技术文档搜索 | Confluence/GitHub 文档自动同步，语义检索 | DataSource Sync + RAG |
| 自动化报告生成 | 从多源数据提取信息，自动生成 PDF 报告 | Agent Canvas + DocsGenerator |

## Tech Stack

```
Frontend                          Backend                         Data Layer
─────────────────                 ─────────────────               ─────────────────
React 18.2 + UmiJS 4              Flask / Quart (Async)           PostgreSQL 16 (Metadata)
Ant Design 5 + Tailwind 3         Python 3.12-3.14                Elasticsearch 8 (Fulltext)
Monaco Editor (Code)              SQLAlchemy (ORM)                Redis / Valkey (Cache)
Zustand + Immer (State)           Celery (Task Queue)             S3 / MinIO (Object)
TanStack Table + Query            ONNX Runtime (ML Inference)     LanceDB (Vector)
Recharts + AntV G6 (Graph)        Pydantic (Validation)
Lexical (Rich Text Editor)        beartype (Type Check)
i18next (i18n)                    aiosmtplib (Email)

AI & NLP                          Infrastructure
─────────────────                 ─────────────────
sentence-transformers             Docker Compose (Orchestration)
scikit-learn / XGBoost            gVisor (Code Sandbox)
LangChain Text Splitters          GitHub Actions (CI/CD)
20+ LLM SDKs                     nginx (Gateway)
RAPTOR (Tree Retrieval)           Langfuse (LLM Observability)
GraphRAG (Knowledge Graph)        OAuth / OIDC (Enterprise Auth)
```

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                      Frontend (React + UmiJS)                         │
│  ┌────────┐ ┌────────┐ ┌──────────┐ ┌────────┐ ┌───────┐ ┌──────┐ │
│  │Document│ │Knowledge│ │  Agent   │ │  Chat  │ │ Admin │ │Search│ │
│  │Manager │ │  Base   │ │  Canvas  │ │Interface│ │ Panel │ │ Page │ │
│  └───┬────┘ └───┬────┘ └────┬─────┘ └───┬────┘ └───┬───┘ └──┬───┘ │
│      └──────────┴───────────┴────────────┴──────────┴────────┘      │
├──────────────────────────────────────────────────────────────────────┤
│                      REST API (Flask / Quart)                         │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  /document  /chunk  /retrieval  /chat  /agent  /datasource  │    │
│  │  /canvas    /mcp    /evaluation /plugin /system /tenant      │    │
│  └──────────────────────────────────────────────────────────────┘    │
├──────────────────────────────────────────────────────────────────────┤
│                         Core Engines                                  │
│                                                                       │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  ┌──────────────┐   │
│  │ deepdoc  │  │  RAG Engine  │  │  Agent    │  │  GraphRAG    │   │
│  │          │  │              │  │  Engine   │  │              │   │
│  │ 12 格式   │  │ Parse →      │  │ 22 组件   │  │ Entity →     │   │
│  │ OCR      │  │ Split →      │  │ Canvas   │  │ Community →  │   │
│  │ 版面识别  │  │ Embed →      │  │ 拖拽编排  │  │ Index →      │   │
│  │ 表格检测  │  │ Retrieve →   │  │ 条件分支  │  │ Hybrid       │   │
│  │          │  │ Rerank →     │  │ 循环迭代  │  │ Search       │   │
│  │          │  │ Generate     │  │ 工具调用  │  │              │   │
│  └──────────┘  └──────────────┘  └───────────┘  └──────────────┘   │
│                                                                       │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  ┌──────────────┐   │
│  │ MCP      │  │  Multi-LLM   │  │ Sandbox   │  │  DataSource  │   │
│  │ Server   │  │  20+ Models  │  │ gVisor    │  │  20+ Sync    │   │
│  └──────────┘  └──────────────┘  └───────────┘  └──────────────┘   │
├──────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌─────────────┐ ┌────────┐ ┌────────┐ ┌───────────┐  │
│  │PostgreSQL│ │Elasticsearch│ │ Redis  │ │S3/MinIO│ │  LanceDB  │  │
│  │(Metadata)│ │(Fulltext)   │ │(Cache) │ │(Object)│ │ (Vector)  │  │
│  └──────────┘ └─────────────┘ └────────┘ └────────┘ └───────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Docker Compose (推荐)

```bash
# 1. Clone
git clone https://github.com/854875058/boncflow.git
cd boncflow

# 2. Start all services
docker compose up -d

# 3. Access
# Web UI → http://localhost
# API Docs → http://localhost/api/docs
```

### Manual Setup

```bash
# Backend
cd boncflow
pip install -e .
python -m api.ragflow_server

# Frontend
cd web
npm install
npm run build    # Production
npm run dev      # Development (HMR)
```

## Project Structure

```
boncflow/
├── api/                             # Backend API server
│   ├── ragflow_server.py            # Entry point
│   ├── apps/                        # 15+ API modules
│   │   ├── conversation_app.py      # Chat & conversation
│   │   ├── document_app.py          # Document management
│   │   ├── chunk_app.py             # Chunk operations
│   │   ├── canvas_app.py            # Agent workflow canvas
│   │   ├── dataset_app.py           # Knowledge base
│   │   ├── mcp_server_app.py        # MCP server management
│   │   └── ...                      # + 10 more modules
│   └── db/                          # Database models & services
├── deepdoc/                         # Document understanding engine
│   ├── parser/                      # 12+ format parsers
│   │   ├── pdf_parser.py            # PDF (text + vision)
│   │   ├── docx_parser.py           # Word documents
│   │   ├── excel_parser.py          # Spreadsheets
│   │   ├── ppt_parser.py            # PowerPoint
│   │   ├── html_parser.py           # Web pages
│   │   └── resume/                  # Resume-specific (2-stage)
│   └── vision/                      # OCR & layout recognition
│       ├── ocr.py                   # Optical character recognition
│       ├── layout_recognizer.py     # Document layout analysis
│       └── table_structure_recognizer.py
├── rag/                             # RAG core engine
│   ├── app/                         # Pipeline orchestration
│   │   ├── parser.py / splitter.py  # Parse & chunk
│   │   ├── extractor.py             # LLM field extraction
│   │   └── hierarchical_merger.py   # Multi-level merging
│   ├── llm/                         # 20+ LLM integrations
│   ├── nlp/                         # Search & retrieval
│   ├── raptor.py                    # RAPTOR tree retrieval
│   └── retrieval/                   # Ranking & reranking
├── agent/                           # Agent framework
│   ├── canvas/                      # Visual workflow engine
│   └── component/                   # 22 built-in components
├── graphrag/                        # Graph-enhanced RAG
│   ├── entity_resolution.py         # Entity deduplication
│   ├── community_reports_extractor.py
│   └── search.py                    # Graph + vector hybrid search
├── mcp/                             # Model Context Protocol
│   ├── server/                      # MCP server implementation
│   └── client/                      # MCP client
├── sandbox/                         # gVisor code execution
├── web/                             # React frontend
│   ├── src/
│   │   ├── pages/                   # 10+ page views
│   │   ├── components/              # UI component library
│   │   └── hooks/                   # Custom React hooks
│   └── package.json
├── intergrations/                   # Third-party integrations
│   ├── chatgpt-on-wechat/           # WeChat bot
│   ├── chrome-extension/            # Browser extension
│   └── firecrawl/                   # Web scraping
├── docker-compose.yml               # Container orchestration
├── Dockerfile                       # Backend image
└── pyproject.toml                   # Python project config
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/document/upload` | 文档上传与解析 |
| `GET` | `/api/document/list` | 文档列表与状态 |
| `POST` | `/api/chunk/parse` | 文档分块处理 |
| `GET` | `/api/chunk/list` | 分块列表与预览 |
| `POST` | `/api/retrieval/search` | RAG 语义检索 |
| `POST` | `/api/chat/completion` | 对话补全 (SSE Streaming) |
| `POST` | `/api/agent/run` | 执行 Agent 工作流 |
| `GET` | `/api/canvas/{id}` | 获取工作流画布定义 |
| `PUT` | `/api/canvas/{id}` | 保存工作流画布 |
| `POST` | `/api/datasource/sync` | 触发数据源同步 |
| `POST` | `/api/mcp/server` | 注册 MCP Server |
| `GET` | `/api/evaluation/list` | RAG 评估结果 |
| `POST` | `/api/plugin/install` | 安装插件 |
| `GET` | `/api/system/status` | 系统状态与健康检查 |

## License

Apache 2.0
