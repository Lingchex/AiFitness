# RAG Server

基于 **FastAPI + LangChain + ChromaDB** 的本地 RAG（检索增强生成）HTTP 服务。支持 PDF 文档入库、向量检索问答，以及不依赖知识库的普通对话；同时提供阻塞式与 SSE 流式两种返回方式。

## 功能概览

| 能力 | 说明 |
|------|------|
| 文档入库 | 上传 PDF，切分后写入 Chroma 向量库 |
| RAG 问答 | 检索 Top-K 片段后由大模型生成答案，并返回引用来源 |
| 普通问答 | 直接调用大模型，不走向量检索 |
| 流式输出 | RAG / 普通问答均支持 SSE 流式响应 |
| 健康检查 | 检查向量库与链路是否就绪 |

默认服务端口：**9000**（ChromaDB 默认 **8000**，需单独部署）。

## 应提交到 GitHub 的内容

只提交**源码与配置模板**，不要提交本地环境、密钥和大文件。

### 建议提交

```
rag-server/
├── app.py              # 主程序
├── requirements.txt    # Python 依赖
├── README.md           # 项目说明
├── .gitignore          # 忽略规则
└── .env.example        # 环境变量示例（无真实密钥）
```

### 不要提交

| 路径 / 文件 | 原因 |
|-------------|------|
| `.env` | 含 API Key 等敏感信息 |
| `venv/`、`.venv/` | 虚拟环境，体积大且可本地重建 |
| `models/` | 本地 Embedding 模型权重（数百 MB），当前代码使用远程 `text-embedding-v4`，该目录为历史遗留 |
| `uploads/` | 运行时上传的 PDF 临时文件 |
| `.idea/`、`.vscode/` | IDE 个人配置 |
| `__pycache__/`、`*.pyc` | Python 编译缓存 |
| `models/**/.cache/` | Hugging Face 下载缓存 |

> **安全提示**：若 `.env` 曾被误提交到 Git，请立即在平台轮换 API Key，并用 `git filter-repo` 等工具从历史记录中清除密钥。

## 环境要求

- Python 3.10+
- 已运行的 **ChromaDB** 服务（HTTP 模式，默认 `localhost:8000`）
- 可访问的 **OpenAI 兼容 API**（用于 `deepseek-v3` 对话与 `text-embedding-v4` 向量化）

## 快速开始

### 1. 克隆仓库

```bash
git clone <your-repo-url>
cd rag-server
```

### 2. 创建虚拟环境并安装依赖

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
# source venv/bin/activate

pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
copy .env.example .env   # Windows
# cp .env.example .env  # Linux / macOS
```

编辑 `.env`，填入真实配置：

```env
API_KEY=你的密钥
API_BASE_URL=https://你的网关地址/v1
CHROMA_HOST=localhost
CHROMA_PORT=8000
COLLECTION_NAME=my_local_rag
```

> `app.py` 读取的是 `API_BASE_URL`，不是 `DEEPSEEK_BASE_URL`。若 `.env` 里仍使用旧变量名，请改为 `API_BASE_URL`。

### 4. 启动 ChromaDB

需先在本机或 Docker 中启动 Chroma 服务，并保证 `CHROMA_HOST` / `CHROMA_PORT` 可连通。例如使用官方 Docker 镜像（请以你实际环境为准）：

```bash
docker run -d -p 8000:8000 chromadb/chroma
```

### 5. 启动 RAG 服务

```bash
python app.py
```

或使用 uvicorn：

```bash
uvicorn app:app --host 0.0.0.0 --port 9000 --reload
```

启动后访问 API 文档：<http://127.0.0.1:9000/docs>

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/documents/upload` | 上传 PDF 并入库（`multipart/form-data`，字段名 `file`） |
| `POST` | `/api/v1/chat` | RAG 问答（JSON：`{"question": "..."}`） |
| `POST` | `/api/v1/chat/stream` | RAG 流式问答（SSE） |
| `POST` | `/api/v1/chat/plain` | 普通问答（无检索） |
| `POST` | `/api/v1/chat/plain/stream` | 普通流式问答 |
| `GET` | `/api/v1/health` | 健康检查 |

### 请求示例

**上传 PDF**

```bash
curl -X POST "http://127.0.0.1:9000/api/v1/documents/upload" \
  -F "file=@./example.pdf"
```

**RAG 问答**

```bash
curl -X POST "http://127.0.0.1:9000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"文档里讲了什么？\"}"
```

**流式问答**（SSE）

```bash
curl -N -X POST "http://127.0.0.1:9000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"简要总结\"}"
```

## 架构说明

```
客户端
   │
   ▼
FastAPI (app.py, :9000)
   ├── PDF 解析 / 文本切分 (LangChain)
   ├── Embedding API (text-embedding-v4)
   ├── LLM API (deepseek-v3)
   └── Chroma HTTP Client (:8000)
           └── 向量集合 COLLECTION_NAME
```

- 文本切分：`chunk_size=500`，`chunk_overlap=50`
- 检索：`k=3`
- 上传的 PDF 解析后会删除本地临时文件，向量持久化在 Chroma 中

## 与 Java 后端集成

本服务作为独立 Python 微服务，通常由 Java（Spring Boot 等）通过 HTTP 调用上述接口。Java 项目只需配置 RAG 服务基地址（如 `http://localhost:9000`），无需把 Python 代码打进 Java 仓库。

## 许可证

按项目实际需要补充 License（如 MIT、Apache-2.0 等）。
