"""
Schemas (Pydantic models) định nghĩa hình dạng dữ liệu trả về cho client.

Các model này được thiết kế để khớp 1-1 với file `frontend/src/types/news.ts`,
nhằm đảm bảo frontend không cần sửa logic xử lý response.
"""

from typing import List, Optional
from pydantic import BaseModel


class NewsItem(BaseModel):
    id: int
    title: Optional[str] = None
    publish_date: Optional[str] = None
    author: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    comments: Optional[int] = None
    summary: Optional[str] = None
    image: Optional[str] = None


class NewsList(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    items: List[NewsItem]


class CategoryItem(BaseModel):
    name: str
    count: int


class CategoriesList(BaseModel):
    total: int
    items: List[CategoryItem]


class SearchQuery(BaseModel):
    query: str


class SearchResult(BaseModel):
    """Kết quả tìm kiếm theo từ khoá (GET /api/search) — khác với semantic search."""

    query: str
    total: int
    page: int
    limit: int
    total_pages: int
    items: List[NewsItem]


class SearchResultItem(BaseModel):
    """
    Một kết quả của Search Pipeline (POST /search).

    Khác với `NewsItem` (dùng cho danh sách/phân trang thông thường):
    - `summary` chỉ phục vụ hiển thị nhanh (cũng là phần đã được embed).
    - `content` là nội dung ĐẦY ĐỦ của bài báo, lấy trực tiếp từ database
      theo `id` sau khi Qdrant trả kết quả — đây là phần PHẢI dùng làm
      context khi gửi cho AI, không phải `summary`.
    """

    id: int
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    image: Optional[str] = None
    date: Optional[str] = None
    source: Optional[str] = None
    score: float
