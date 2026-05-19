import os
import uuid
import shutil
import json
import chromadb
import time
import traceback
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

# ==================== 日志配置 ====================      # ✅ 新增
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("RAG-Service")                 # ✅ 新增

# ==================== 加载环境变量 ====================
load_dotenv()

# ==================== 目录初始化 ====================
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ==================== 全局变量 ====================
vectorstore = None
rag_chain = None
retriever = None
plain_chat_chain = None          # 🆕 普通问答链（不带 RAG）

# ==================== API 配置 ====================
API_BASE_URL = os.getenv("API_BASE_URL", "https://ai-api-prod.qingjiao.art/v1")
API_KEY = os.getenv("API_KEY", "")

logger.info(f"API_BASE_URL: {API_BASE_URL}")              # ✅ 新增
logger.info(f"API_KEY: {'***' + API_KEY[-4:] if len(API_KEY) > 4 else '(empty)'}")  # ✅ 新增（脱敏打印）


# ==================== 文档格式化函数 ====================
def format_docs(docs):
    """把检索到的文档拼接成一个字符串"""
    return "\n\n".join(str(doc.page_content) for doc in docs)


# ==================== 初始化函数 ====================
def init_services():
    """应用启动时连接向量库、构建 RAG 链"""
    global vectorstore, rag_chain, retriever, plain_chat_chain   # 🆕

    # 1. Embedding 模型
    try:                                                    # ✅ 新增 try/except
        logger.info("🔄 正在连接 Embedding 模型 (text-embedding-v4)...")
        embedding_model = OpenAIEmbeddings(
            model="text-embedding-v4",
            openai_api_key=API_KEY,
            openai_api_base=API_BASE_URL,
            check_embedding_ctx_length=False,
        )
        logger.info("✅ Embedding 模型连接成功")              # ✅ 新增
    except Exception as e:                                  # ✅ 新增
        logger.error(f"❌ Embedding 模型连接失败: {e}")      # ✅ 新增
        logger.error(traceback.format_exc())                # ✅ 新增：完整堆栈
        raise                                               # ✅ 新增

    # 2. 连接 Chroma 向量库
    try:                                                    # ✅ 新增 try/except
        chroma_host = os.getenv("CHROMA_HOST", "localhost")
        chroma_port = int(os.getenv("CHROMA_PORT", 8000))
        collection_name = os.getenv("COLLECTION_NAME", "my_local_rag")
        logger.info(f"🔄 正在连接向量库 ({chroma_host}:{chroma_port})...")

        chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embedding_model,
            client=chroma_client,
        )
        logger.info(f"✅ 向量库连接成功 (collection: {collection_name})")  # ✅ 新增
    except Exception as e:                                  # ✅ 新增
        logger.error(f"❌ 向量库连接失败: {e}")              # ✅ 新增
        logger.error(traceback.format_exc())                # ✅ 新增
        raise                                               # ✅ 新增

    # 3. 大语言模型
    try:                                                    # ✅ 新增 try/except
        logger.info("🔄 正在连接大模型 (deepseek-v3)...")
        llm = ChatOpenAI(
            model="deepseek-v3",
            api_key=API_KEY,
            base_url=API_BASE_URL,
            temperature=0.3,
            max_tokens=2048,
        )
        logger.info("✅ 大模型连接成功")                     # ✅ 新增
    except Exception as e:                                  # ✅ 新增
        logger.error(f"❌ 大模型连接失败: {e}")              # ✅ 新增
        logger.error(traceback.format_exc())                # ✅ 新增
        raise                                               # ✅ 新增

    # 4. 构建 LCEL 检索链（RAG）
    try:                                                    # ✅ 新增 try/except
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        logger.info("✅ Retriever 创建成功 (k=3)")          # ✅ 新增

        rag_system_prompt = (
            "你是一个有用的AI助手。请根据用户提供的【背景知识】来回答问题。\n"
            "规则：\n"
            "1. 如果【背景知识】中没有包含答案，请直接说'根据已知信息无法回答'，不要瞎编。\n"
            "2. 回答要简洁精炼，使用中文。\n"
            "\n\n【背景知识】：\n{context}"
        )

        rag_prompt = ChatPromptTemplate.from_messages([
            ("system", rag_system_prompt),
            ("human", "{question}"),
        ])

        rag_chain = (
                RunnableParallel(context=retriever | format_docs, question=RunnablePassthrough())
                | rag_prompt
                | llm
                | StrOutputParser()
        )
        logger.info("✅ RAG Chain 构建完成")                 # ✅ 新增

    except Exception as e:                                  # ✅ 新增
        logger.error(f"❌ RAG Chain 构建失败: {e}")          # ✅ 新增
        logger.error(traceback.format_exc())                # ✅ 新增
        raise                                               # ✅ 新增

    # 🆕 5. 构建普通问答链（不带 RAG）
    try:
        plain_system_prompt = (
            "你是一个有用的AI助手，请用简洁精炼的中文回答用户的问题。"
        )
        plain_prompt = ChatPromptTemplate.from_messages([
            ("system", plain_system_prompt),
            ("human", "{question}"),
        ])

        plain_chat_chain = (
            plain_prompt
            | llm
            | StrOutputParser()
        )
        logger.info("✅ 普通问答链 (Plain Chat Chain) 构建完成")
    except Exception as e:
        logger.error(f"❌ 普通问答链构建失败: {e}")
        logger.error(traceback.format_exc())
        raise

    logger.info("🎉 所有服务初始化完成，RAG 系统已就绪！")


# ==================== 现代化生命周期管理 ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 RAG 服务启动中...")
    init_services()
    yield
    logger.info("🛑 RAG 服务已关闭。")


# ==================== 应用初始化 ====================
app = FastAPI(title="本地 RAG 接口服务", version="2.1.0", lifespan=lifespan)


# ==================== 文档入库接口 ====================
@app.post("/api/v1/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """上传 PDF 文档并解析入库"""
    logger.info(f"📥 收到文件上传请求: {file.filename}")

    if not file.filename.endswith(".pdf"):
        logger.warning(f"⚠️ 文件格式不支持: {file.filename}")
        raise HTTPException(status_code=400, detail="目前仅支持 PDF 格式文件")

    file_id = str(uuid.uuid4())[:8]
    save_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

    try:
        # 保存上传文件
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"💾 文件已保存: {save_path}")

        # 解析与切分
        logger.info(f"📄 正在解析 PDF: {file.filename}...")
        loader = PyPDFLoader(str(save_path))
        docs = loader.load()
        logger.info(f"📄 PDF 解析完成，共 {len(docs)} 页")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
        )
        splits = text_splitter.split_documents(docs)
        logger.info(f"✂️ 文本切分完成，共 {len(splits)} 个 chunk")

        # 为每个 chunk 生成稳定的 ID
        ids = [f"{file_id}_chunk_{i}" for i in range(len(splits))]

        logger.info(f"🔄 正在入库 {len(splits)} 个 chunk...")
        vectorstore.add_documents(splits, ids=ids)
        logger.info(f"✅ 入库成功: {file.filename}, file_id={file_id}")

        return JSONResponse(content={
            "code": 200,
            "message": "入库成功",
            "data": {
                "filename": file.filename,
                "chunks": len(splits),
                "file_id": file_id,
            }
        })

    except Exception as e:
        logger.error(f"❌ 文档处理失败 [{file.filename}]: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")

    finally:
        if save_path.exists():
            save_path.unlink()
            logger.info(f"🗑️ 临时文件已清理: {save_path}")


# ==================== 请求体模型 ====================
class ChatRequest(BaseModel):
    question: str


# ==================== RAG 普通问答接口 ====================
@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    """RAG 问答接口（阻塞式返回完整结果）"""
    logger.info(f"💬 收到 RAG 问答请求: {request.question}")

    if not request.question.strip():
        logger.warning("⚠️ 问题不能为空")
        raise HTTPException(status_code=400, detail="问题不能为空")

    try:
        start_time = time.time()

        # 检索源文档
        docs = retriever.invoke(request.question)
        logger.info(f"🔍 检索到 {len(docs)} 条相关文档")

        answer = rag_chain.invoke(request.question)
        elapsed = time.time() - start_time
        logger.info(f"✅ RAG 问答完成，耗时 {elapsed:.2f}s")

        # 提取引用来源
        sources = [
            {
                "content": doc.page_content[:200] + ("..." if len(doc.page_content) > 200 else ""),
                "source": doc.metadata.get("source", "未知"),
                "page": doc.metadata.get("page", -1),
            }
            for doc in docs
        ]

        return JSONResponse(content={
            "code": 200,
            "data": {"answer": answer, "sources": sources}
        })

    except Exception as e:
        logger.error(f"❌ RAG 问答失败: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")


# ==================== RAG 流式问答接口 ====================
@app.post("/api/v1/chat/stream")
async def chat_stream(request: ChatRequest):
    """RAG 流式问答接口（SSE 方式）"""
    logger.info(f"💬 收到 RAG 流式问答请求: {request.question}")

    if not request.question.strip():
        logger.warning("⚠️ 问题不能为空")
        raise HTTPException(status_code=400, detail="问题不能为空")

    async def event_generator():
        start_time = time.time()
        try:
            async for chunk in rag_chain.astream(request.question):
                logger.debug(f"📤 RAG 流式输出 chunk: {chunk}")
                yield f"data: {json.dumps({'answer': chunk}, ensure_ascii=False)}\n\n"
            elapsed = time.time() - start_time
            logger.info(f"✅ RAG 流式问答完成，总耗时 {elapsed:.2f}s")
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"❌ RAG 流式问答失败: {e}")
            logger.error(traceback.format_exc())
            error_data = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# ==================== 🆕 普通问答接口（不带 RAG） ====================
@app.post("/api/v1/chat/plain")
async def chat_plain(request: ChatRequest):
    """普通问答接口（不使用 RAG 检索，直接调用大模型）"""
    logger.info(f"💬 收到普通问答请求: {request.question}")

    if not request.question.strip():
        logger.warning("⚠️ 问题不能为空")
        raise HTTPException(status_code=400, detail="问题不能为空")

    try:
        start_time = time.time()

        answer = plain_chat_chain.invoke({"question": request.question})
        elapsed = time.time() - start_time

        logger.info(f"✅ 普通问答完成，耗时 {elapsed:.2f}s")
        logger.debug(f"📝 回答内容: {answer[:200]}...")

        return JSONResponse(content={
            "code": 200,
            "data": {"answer": answer}
        })

    except Exception as e:
        logger.error(f"❌ 普通问答失败: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")


# ==================== 🆕 普通问答流式接口（不带 RAG） ====================
@app.post("/api/v1/chat/plain/stream")
async def chat_plain_stream(request: ChatRequest):
    """普通问答流式接口（SSE 方式，不使用 RAG 检索）"""
    logger.info(f"💬 收到普通流式问答请求: {request.question}")

    if not request.question.strip():
        logger.warning("⚠️ 问题不能为空")
        raise HTTPException(status_code=400, detail="问题不能为空")

    async def event_generator():
        start_time = time.time()
        try:
            async for chunk in plain_chat_chain.astream({"question": request.question}):
                logger.debug(f"📤 普通流式输出 chunk: {chunk}")
                yield f"data: {json.dumps({'answer': chunk}, ensure_ascii=False)}\n\n"
            elapsed = time.time() - start_time
            logger.info(f"✅ 普通流式问答完成，总耗时 {elapsed:.2f}s")
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"❌ 普通流式问答失败: {e}")
            logger.error(traceback.format_exc())
            error_data = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# ==================== 健康检查接口 ====================
@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    status = {
        "vectorstore": "disconnected",
        "rag_chain": "not_ready",
        "plain_chat_chain": "not_ready",       # 🆕
        "overall": "unhealthy"
    }

    try:
        if vectorstore is not None:
            status["vectorstore"] = "connected"
        if rag_chain is not None:
            status["rag_chain"] = "ready"
        if plain_chat_chain is not None:       # 🆕
            status["plain_chat_chain"] = "ready"

        if (status["vectorstore"] == "connected"
                and status["rag_chain"] == "ready"
                and status["plain_chat_chain"] == "ready"):    # 🆕
            status["overall"] = "healthy"
            return JSONResponse(content={"code": 200, "data": status})

    except Exception as e:
        logger.error(f"❌ 健康检查异常: {e}")
        logger.error(traceback.format_exc())
        status["error"] = str(e)

    logger.warning(f"⚠️ 健康检查未通过: {status}")
    raise HTTPException(status_code=503, detail=status)


# ==================== 启动入口 ====================
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 启动 RAG 服务 (port=9000, reload=True)")
    uvicorn.run("app:app", host="0.0.0.0", port=9000, reload=True)
