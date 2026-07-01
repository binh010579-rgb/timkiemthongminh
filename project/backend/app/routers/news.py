"""
Router: định nghĩa các endpoint HTTP cho resource "news".

Router KHÔNG đọc CSV, KHÔNG chứa logic xử lý dữ liệu phức tạp — nó chỉ
nhận tham số từ request, gọi xuống `services/news_service.py` (vốn
thao tác trên DataFrame đã nạp sẵn trong RAM), rồi trả kết quả.
"""

from typing import List

from fastapi import APIRouter, Query, Request

from app.config import SEARCH_TOP_K
from app.schemas import CategoriesList, NewsList, SearchQuery, SearchResult, SearchResultItem
from app.services import news_service

router = APIRouter(tags=["news"])
api_router = APIRouter(prefix="/api", tags=["news"])


def _get_df(request: Request):
    """Lấy DataFrame đã nạp sẵn trong RAM từ app.state (xem main.py)."""
    return request.app.state.news_store.ensure_loaded()


def _get_embedding_store(request: Request):
    """Lấy EmbeddingStore (model embedding + truy vấn Qdrant), đã nạp sẵn khi startup."""
    return request.app.state.embedding_store


@api_router.get("/news", response_model=NewsList)
def list_news(
    request: Request,
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    limit: int = Query(10, ge=1, le=100, description="Số tin mỗi trang"),
):
    """Danh sách tin mới nhất, có phân trang."""
    df = _get_df(request)
    return news_service.get_news_list(df, page=page, limit=limit)


@api_router.get("/news/featured", response_model=NewsList)
def featured_news(
    request: Request,
    limit: int = Query(5, ge=1, le=100, description="Số tin nổi bật cần lấy"),
):
    """Danh sách tin nổi bật (nhiều bình luận nhất)."""
    df = _get_df(request)
    return news_service.get_featured_news(df, limit=limit)


@api_router.get("/categories", response_model=CategoriesList)
def categories(request: Request):
    """Danh mục tin tức, nhóm theo nguồn báo."""
    df = _get_df(request)
    return news_service.get_categories(df)


@api_router.get("/search", response_model=SearchResult)
def search(
    request: Request,
    q: str = Query("", description="Từ khoá tìm kiếm"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    """Tìm kiếm tin tức theo từ khoá (tiêu đề + tóm tắt)."""
    df = _get_df(request)
    return news_service.search_news(df, query=q, page=page, limit=limit)


@router.post("/search", response_model=List[SearchResultItem])
def search_pipeline(request: Request, body: SearchQuery):
    """
    Search Pipeline:

        User Query -> Embedding Query -> Qdrant Search -> Top {SEARCH_TOP_K}
        -> lấy content đầy đủ theo id từ database -> trả về API.

    Không reranker, không CrossEncoder, không semantic search tự viết,
    không chunk. Embedding chỉ dùng title+summary (xem `embeddings.py`);
    `content` trong response là nội dung đầy đủ lấy từ database, dùng làm
    context khi gửi cho AI.
    """
    df = _get_df(request)
    embedding_store = _get_embedding_store(request)
    return news_service.search_articles(
        df, embedding_store, query=body.query, top_k=SEARCH_TOP_K
    )
