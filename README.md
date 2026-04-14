<div align="center">

# BoncFlow

**可视化 RAG 工作流引擎**

*Visual RAG workflow engine with deep document understanding and agentic orchestration*

[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python)](https://python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Apache_2.0-D22128.svg)](LICENSE)

</div>

---

## Overview

传统 RAG 系统面临三大瓶颈：复杂文档解析精度低、检索结果缺乏溯源、工作流编排依赖硬编码。

BoncFlow 将 **深度文档理解**、**可溯源检索** 与 **可视化 Agent 编排** 融为一体。支持 Word、PPT、Excel、扫描件、网页等 10+ 格式的智能解析，通过模板化分块与引用溯源大幅降低幻觉率，并提供画布式拖拽工作流编辑器，让 RAG 流程的构建像画流程图一样直观。

```
┌─────────────────────────────────────────────────────────────┐
│                  React Frontend (UmiJS)                       │
├──────────┬──────────┬──────────┬──────────┬─────────────────┤
│  文档管理 │ 知识库    │ Agent流程 │ 对话界面  │   系统设置      │
├──────────┴──────────┴──────────┴──────────┴─────────────────┤
│           Flask/Quart Backend (RAG + Agent Engine)            │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL │ Elasticsearch │ Redis │ Object Storage (S3)    │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### Deep Document Understanding
自研 `deepdoc` 文档理解引擎，支持 Word、PPT、Excel、PDF、扫描件、网页等复杂格式的高精度知识抽取。表格、图片、公式均可正确解析。

### Template-Based Intelligent Chunking
提供多种分块模板，用户可根据文档类型选择最优策略。分块过程可视化、可解释，每个 chunk 保留原文定位信息。

### Grounded Citations
每条检索结果附带原文引用与高亮定位，从源头减少 LLM 幻觉。用户可一键跳转原文验证，建立对 AI 回答的信任。

### Visual Agent Workflow
画布式拖拽工作流编辑器，内置丰富的组件库（检索、LLM、条件判断、代码执行、HTTP 调用等），无需编码即可编排复杂 RAG + Agent 流程。

### Multi-LLM Support

| Provider | Models |
|----------|--------|
| Anthropic | Claude 4.x / Sonnet / Haiku |
| OpenAI | GPT-4o / GPT-5 |
| Google | Gemini Pro / Ultra |
| 国产模型 | 通义千问 / 智谱 / 百川 / DeepSeek |
| 本地部署 | Ollama / vLLM |

### MCP & Code Execution
支持 Model Context Protocol (MCP) 工具集成，内置 gVisor 沙箱安全执行 Python/JavaScript 代码。

### GraphRAG
图谱增强检索，结合实体关系图谱提升复杂问题的检索召回率与推理准确性。

### Data Source Sync
支持 Confluence、S3、Notion、Discord、Google Drive、Jira、Slack 等 20+ 数据源自动同步。

## Tech Stack

```
Frontend                          Backend                         Data Layer
─────────────────                 ─────────────────               ─────────────────
React 18 + UmiJS                  Flask / Quart (Async)           PostgreSQL (Metadata)
Ant Design 5 + Tailwind           Python 3.12+                    Elasticsearch (Search)
Monaco Editor (Code)              SQLAlchemy (ORM)                Redis / Valkey (Cache)
Zustand (State)                   Celery (Task Queue)             S3 / MinIO (Object)
TanStack Table + Query            ONNX Runtime (ML)               LanceDB (Vector)

AI & NLP                          Infrastructure
─────────────────                 ─────────────────
sentence-transformers             Docker Compose
scikit-learn / XGBoost            gVisor (Sandbox)
LangChain (Text Split)            GitHub Actions (CI/CD)
Multi-LLM SDK                     nginx (Gateway)
```

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Frontend (React + UmiJS)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────┐  │
│  │ Document │ │Knowledge │ │  Agent   │ │   Chat   │ │System │  │
│  │ Manager  │ │   Base   │ │ Canvas   │ │ Interface│ │Config │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬───┘  │
│       └─────────────┴────────────┴─────────────┴───────────┘      │
├──────────────────────────────────────────────────────────────────┤
│                    Backend (Flask / Quart)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────┐  │
│  │ deepdoc  │ │   RAG    │ │  Agent   │ │   MCP    │ │GraphR │  │
│  │ 文档解析  │ │ 检索增强  │ │ 工作流    │ │ 工具协议  │ │ AG    │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬───┘  │
├───────┼─────────────┼────────────┼─────────────┼───────────┼──────┤
│  ┌────▼──────┐ ┌────▼─────┐ ┌───▼─────┐ ┌────▼─────┐ ┌───▼───┐  │
│  │PostgreSQL │ │Elastic   │ │  Redis  │ │ S3/MinIO │ │LanceDB│  │
│  │(Metadata) │ │(Search)  │ │ (Cache) │ │ (Object) │ │(Vector│  │
│  └───────────┘ └──────────┘ └─────────┘ └──────────┘ └───────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# 1. Clone
git clone https://github.com/854875058/boncflow.git
cd boncflow

# 2. Docker Compose (recommended)
docker compose -f docker-compose.yml up -d

# Or manual setup:
# Backend
pip install -e .
python -m api.ragflow_server

# Frontend
cd web && npm install && npm run build
```

## Project Structure

```
boncflow/
├── api/                             # Backend API server
│   ├── ragflow_server.py            # Entry point
│   ├── apps/                        # API endpoints
│   └── db/                          # Database models & services
├── deepdoc/                         # Document understanding engine
│   ├── parser/                      # Format-specific parsers
│   └── vision/                      # OCR & layout analysis
├── rag/                             # RAG core
│   ├── app/                         # Flow orchestration
│   ├── llm/                         # Multi-LLM integration
│   ├── nlp/                         # NLP utilities
│   └── retrieval/                   # Retrieval & ranking
├── agent/                           # Agent framework
│   ├── canvas/                      # Visual workflow definition
│   └── component/                   # Built-in components
├── graphrag/                        # Graph-enhanced RAG
├── mcp/                             # Model Context Protocol
├── sandbox/                         # Code execution sandbox
├── web/                             # React frontend
│   ├── src/
│   │   ├── pages/                   # Page views
│   │   ├── components/              # UI components
│   │   └── hooks/                   # Custom hooks
│   └── package.json
├── docker-compose.yml               # Container orchestration
├── Dockerfile                       # Backend image
└── pyproject.toml                   # Python project config
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/document/upload` | 文档上传与解析 |
| `GET` | `/api/document/list` | 文档列表 |
| `POST` | `/api/chunk/parse` | 文档分块 |
| `POST` | `/api/retrieval/search` | RAG 检索 |
| `POST` | `/api/chat/completion` | 对话补全 (SSE) |
| `POST` | `/api/agent/run` | 执行 Agent 工作流 |
| `GET` | `/api/agent/canvas` | 获取工作流画布 |
| `POST` | `/api/datasource/sync` | 数据源同步 |

## License

Apache 2.0
