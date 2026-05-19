# JavaWeb · 智能健身应用

面向健身场景的 **uni-app 微信小程序** + **Python AI 微服务** 单体仓库。前端提供训练计划、AI 教练对话、知识库管理与动作视频分析；后端由 RAG 问答服务与 MediaPipe 姿态分析服务组成，可通过 HTTP 对接未来的 Java（Spring Boot）业务层。

## 仓库结构

```
JavaWeb/
├── Fit/                          # 前端：uni-app（Vue 3），主要发布为微信小程序
│   ├── pages/ai/                 # AI 教练对话（RAG / 自由对话）
│   ├── pages/plan/               # 训练计划
│   ├── pages/user/               # 用户中心、PDF 知识库上传
│   └── components/planing/       # 动作视频 AI 分析浮层
│
└── LLMService/                   # 后端：Python AI 微服务
    ├── service/
    │   ├── rag-service/          # RAG 检索增强问答（FastAPI，:9000）
    │   └── ai-analysis/          # 健身动作分析（Flask，:5005）
    └── rag-server/               # 与 rag-service 同源的 RAG 副本（开发/部署任选其一）
```

| 模块 | 技术栈 | 默认端口 | 说明 |
|------|--------|----------|------|
| **Fit** | uni-app、Vue 3 | — | 小程序端 UI，调用下方 HTTP API |
| **rag-service** | FastAPI、LangChain、ChromaDB | **9000** | PDF 入库、RAG / 普通问答、SSE 流式 |
| **ai-analysis** | Flask、OpenCV、MediaPipe | **5005** | 训练视频关键帧 + 关节角 + 多模态评估报告 |
| **ChromaDB** | Docker / 独立进程 | **8000** | 向量库（RAG 依赖，需单独启动） |

更细的接口与配置见子目录文档：

- [LLMService/service/rag-service/README.md](LLMService/service/rag-service/README.md)
- [LLMService/service/ai-analysis/README.MD](LLMService/service/ai-analysis/README.MD)

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│  Fit 微信小程序 (uni-app)                                    │
│  · AI 对话 / 知识库上传 / 训练计划 / 动作视频分析              │
└───────────────┬─────────────────────────┬───────────────────┘
                │ HTTP                     │ HTTP (upload)
                ▼                          ▼
┌───────────────────────────┐   ┌────────────────────────────┐
│  RAG Service (FastAPI)     │   │  AI Analysis (Flask)        │
│  :9000                     │   │  :5005                      │
│  · PDF → 向量入库          │   │  · MediaPipe 姿态 / 关节角   │
│  · RAG / Plain / Stream    │   │  · qwen-omni-turbo 报告     │
└─────────────┬─────────────┘   └────────────────────────────┘
              │
              ▼
┌───────────────────────────┐
│  ChromaDB (:8000)         │
│  Embedding + 向量检索      │
└───────────────────────────┘
              ▲
              │ OpenAI 兼容 API（对话 deepseek-v3、向量 text-embedding-v4、
              │                  分析 qwen-omni-turbo）
```

可选：在 RAG / 分析服务前增加 **Java Spring Boot** 网关，统一鉴权、用户与业务数据；Python 服务保持独立进程，Java 仅通过 HTTP 转发（详见 RAG 子文档「与 Java 后端集成」）。

## 功能概览

### 前端（Fit）

- **AI Trainer**：支持「文档库（RAG）」与「自由对话」切换；阻塞 / SSE 流式回复
- **知识库**：上传 PDF 至 RAG 服务入库
- **训练计划**：计划展示与动作条目
- **动作分析**：上传训练视频，展示 AI 结构化评估报告

### RAG 服务（rag-service）

| 能力 | 说明 |
|------|------|
| 文档入库 | 上传 PDF，切分后写入 Chroma |
| RAG 问答 | Top-K 检索 + 大模型生成，返回答案与引用来源 |
| 普通问答 | 不走向量检索，直接调用大模型 |
| 流式输出 | RAG / 普通问答均支持 SSE |
| 健康检查 | 检查向量库与链路就绪 |

### 健身动作分析（ai-analysis）

- 视频上传或服务器本地路径
- MediaPipe 提取 14+ 关节角度（肘、肩、膝、髋等）
- 均匀 / 自适应关键帧抽取
- 调用 `qwen-omni-turbo` 生成结构化健身评估报告

## 环境要求

- **Node / HBuilderX**：编译运行 Fit（uni-app）
- **Python 3.10+**：RAG 服务
- **Python 3.8+**：动作分析服务
- **Docker**（推荐）：运行 ChromaDB
- **OpenAI 兼容 API**：对话、Embedding、多模态分析

## 快速开始

### 1. 启动 ChromaDB（RAG 依赖）

在 `LLMService/service/rag-service/` 下：

```bash
docker compose up -d
```

或单独运行官方镜像（端口需与 `.env` 中 `CHROMA_HOST` / `CHROMA_PORT` 一致）：

```bash
docker run -d -p 8000:8000 chromadb/chroma
```

### 2. 启动 RAG 服务

```bash
cd LLMService/service/rag-service
python -m venv venv
# Windows: venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # 填入 API_KEY、API_BASE_URL 等
python app.py
```

- 服务地址：<http://127.0.0.1:9000>
- API 文档：<http://127.0.0.1:9000/docs>

`.env` 示例：

```env
API_KEY=你的密钥
API_BASE_URL=https://你的网关地址/v1
CHROMA_HOST=localhost
CHROMA_PORT=8000
COLLECTION_NAME=my_local_rag
```

> 应用读取的是 `API_BASE_URL`，不是 `DEEPSEEK_BASE_URL`。

### 3. 启动动作分析服务

```bash
cd LLMService/service/ai-analysis
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# 在 analyzer.py 或环境变量中配置 OpenAI 兼容 API（勿将密钥提交到 Git）
python app.py
```

- 默认端口：**5005**
- 健康检查：`GET /api/health`
- 分析接口：`POST /api/analyze`（`multipart/form-data`，字段 `file`；可选 `exercise_type`、`max_frames`、`frame_strategy`）

### 4. 运行前端

使用 [HBuilderX](https://www.dcloud.io/hbuilderx.html) 打开 `Fit/`，运行到微信开发者工具。

在源码中配置后端地址（生产需 HTTPS 域名并在小程序后台配置合法域名）：

| 文件 | 变量 | 对接服务 |
|------|------|----------|
| `Fit/pages/ai/ai.vue` | `API_BASE` | RAG 服务（如 `http://127.0.0.1:9000`） |
| `Fit/pages/user/repository.vue` | 上传 URL | `POST .../api/v1/documents/upload` |
| `Fit/components/planing/AnalysisOverlay.vue` | `API_BASE_URL` | 分析服务（如 `http://127.0.0.1:5005`） |

本地调试可用内网穿透（如 cpolar）；上线请替换为正式 HTTPS 域名。

## API 速查

### RAG（:9000）

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/documents/upload` | 上传 PDF 入库（`file`） |
| `POST` | `/api/v1/chat` | RAG 问答 |
| `POST` | `/api/v1/chat/stream` | RAG 流式（SSE） |
| `POST` | `/api/v1/chat/plain` | 普通问答 |
| `POST` | `/api/v1/chat/plain/stream` | 普通流式 |
| `GET` | `/api/v1/health` | 健康检查 |

### 动作分析（:5005）

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/health` | 健康检查 |
| `POST` | `/api/analyze` | 分析健身视频 |

**RAG 问答示例：**

```bash
curl -X POST "http://127.0.0.1:9000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"文档里讲了什么？\"}"
```

## RAG 实现要点

- 文本切分：`chunk_size=500`，`chunk_overlap=50`
- 检索：`k=3`
- 模型：`deepseek-v3`（对话）、`text-embedding-v4`（向量）
- 上传 PDF 解析后删除本地临时文件，向量持久化在 Chroma



按项目需要补充 License（如 MIT、Apache-2.0 等）。
