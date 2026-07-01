"""
Entrypoint của backend FastAPI.

Quan trọng nhất ở file này: hàm `lifespan`. Đây là nơi DUY NHẤT
`news_store.load()` (và do đó `pd.read_csv`) được gọi — đúng một lần,
khi server khởi động. Sau đó DataFrame được giữ trong
`app.state.news_store` suốt vòng đời server, mọi request chỉ đọc lại
dữ liệu đã có sẵn trong RAM.

Embedding của bài báo (title+summary) KHÔNG được sinh ở đây. Toàn bộ
việc đó do script độc lập `build_vectors.py` đảm nhiệm (chạy thủ công,
xem README). Lifespan chỉ load model embedding (để phục vụ `embed_query`
cho mỗi request `/search`) và kết nối tới collection Qdrant đã có sẵn.

Chạy server (từ thư mục backend/):
    uvicorn main:app --reload --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ALLOWED_ORIGINS
from app.data_loader import news_store
from app.embeddings import embedding_store
from app.routers import news


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup: đọc CSV MỘT LẦN DUY NHẤT, nạp vào RAM ---
    news_store.load()
    app.state.news_store = news_store
    print(f"[startup] Đã nạp {len(news_store.df)} bài báo vào RAM từ CSV.")

    # --- Load model embedding (Qwen3 Embedding) + kết nối Qdrant. KHÔNG
    #     encode lại toàn bộ dữ liệu ở đây — dữ liệu vector phải được sinh
    #     từ trước bằng `python build_vectors.py`. ---
    embedding_store.load()
    app.state.embedding_store = embedding_store
    emb_count, emb_dim = embedding_store.summary()
    print(
        f"[startup] EmbeddingStore sẵn sàng (dim={emb_dim}); "
        f"Qdrant hiện có {emb_count} vector."
    )

    yield  # server phục vụ request trong khoảng thời gian này

    # --- Shutdown: không có tài nguyên gì cần dọn (không dùng DB/file handle) ---


app = FastAPI(
    title="News API (CSV in-memory + Qdrant)",
    description=(
        "Backend đọc dữ liệu tin tức từ CSV, giữ trong RAM (không dùng "
        "database quan hệ); tìm kiếm ngữ nghĩa dùng Qdrant cho vector "
        "embedding title+summary."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news.router)
app.include_router(news.api_router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "message": "News API đang chạy."}
