"""
Service layer: chứa toàn bộ logic xử lý dữ liệu tin tức trên DataFrame
đã có sẵn trong RAM (`news_store.df`).

Không có hàm nào ở đây đọc lại file CSV — tất cả chỉ thao tác trên
DataFrame được truyền vào.
"""

import math

import pandas as pd

from app.config import DEFAULT_PAGE_LIMIT, MAX_PAGE_LIMIT, SEARCH_SCORE_THRESHOLD, SEARCH_TOP_K
from app.data_loader import _strip_accents_lower
from app.embeddings import EmbeddingStore
from app.schemas import (
    CategoriesList,
    CategoryItem,
    NewsItem,
    NewsList,
    SearchResult,
    SearchResultItem,
)


def _clamp_limit(limit: int) -> int:
    return max(1, min(limit, MAX_PAGE_LIMIT))


def _clamp_page(page: int) -> int:
    return max(1, page)


def _row_to_news_item(row: "pd.Series") -> NewsItem:
    comments = row["so_binh_luan"]
    return NewsItem(
        id=int(row["id"]),
        title=row["tieu_de"],
        publish_date=row["ngay_dang"],
        author=row["tac_gia"],
        source=row["nguon"],
        url=row["link"],
        comments=None if pd.isna(comments) else int(comments),
        summary=row["summary"],
        image=None,
    )


def _paginate_df(df: pd.DataFrame, page: int, limit: int) -> tuple[pd.DataFrame, int, int]:
    page = _clamp_page(page)
    limit = _clamp_limit(limit)
    total = len(df)
    total_pages = max(1, math.ceil(total / limit))
    start = (page - 1) * limit
    page_df = df.iloc[start : start + limit]
    return page_df, page, limit


def get_news_list(df: pd.DataFrame, page: int = 1, limit: int = DEFAULT_PAGE_LIMIT) -> NewsList:
    """Danh sách tin mới nhất, sắp xếp theo thứ tự trong CSV (mới nhất trước, theo ngày_dang)."""
    sorted_df = df.sort_values(by="ngay_dang", ascending=False, kind="stable")
    page_df, page, limit = _paginate_df(sorted_df, page, limit)
    total = len(df)
    return NewsList(
        total=total,
        page=page,
        limit=limit,
        total_pages=max(1, math.ceil(total / limit)),
        items=[_row_to_news_item(row) for _, row in page_df.iterrows()],
    )


def get_featured_news(df: pd.DataFrame, limit: int = 5) -> NewsList:
    """Tin nổi bật: lấy N tin có nhiều bình luận nhất làm tiêu chí 'nổi bật'."""
    limit = _clamp_limit(limit)
    featured_df = df.sort_values(by="so_binh_luan", ascending=False, kind="stable").head(limit)
    total = len(df)
    return NewsList(
        total=total,
        page=1,
        limit=limit,
        total_pages=max(1, math.ceil(total / limit)),
        items=[_row_to_news_item(row) for _, row in featured_df.iterrows()],
    )


def get_categories(df: pd.DataFrame) -> CategoriesList:
    """Danh mục = nhóm theo nguồn báo (cột `nguon`)."""
    counts = df["nguon"].fillna("Khác").value_counts()
    items = [CategoryItem(name=str(name), count=int(count)) for name, count in counts.items()]
    return CategoriesList(total=len(items), items=items)


def search_news(
    df: pd.DataFrame, query: str, page: int = 1, limit: int = DEFAULT_PAGE_LIMIT
) -> SearchResult:
    """Tìm kiếm theo tiêu đề + tóm tắt, không phân biệt hoa/thường, không dấu."""
    q = _strip_accents_lower(query.strip())

    if not q:
        matched = df.iloc[0:0]
    else:
        mask = df["_search_blob"].str.contains(q, regex=False, na=False)
        matched = df[mask]

    page_df, page, limit = _paginate_df(matched, page, limit)
    total = len(matched)
    return SearchResult(
        query=query,
        total=total,
        page=page,
        limit=limit,
        total_pages=max(1, math.ceil(total / limit)),
        items=[_row_to_news_item(row) for _, row in page_df.iterrows()],
    )


def _rows_by_ids(df: pd.DataFrame, ids: list[int]) -> list["pd.Series"]:
    """
    Lấy các dòng trong `df` theo đúng thứ tự `ids` (giá trị cột `id`, KHÔNG
    phải vị trí dòng). Đây là bước "lấy content theo id từ database" của
    Search Pipeline — `df` chính là database (đọc 1 lần từ CSV, giữ trong RAM).
    """
    indexed = df.set_index("id", drop=False)
    return [indexed.loc[i] for i in ids]


def _row_to_search_result(row: "pd.Series", score: float) -> SearchResultItem:
    """
    Build kết quả trả về API từ 1 dòng database.

    `content` lấy từ cột `noi_dung` — nội dung ĐẦY ĐỦ của bài báo, KHÔNG
    phải `summary`. Đây là phần dùng làm context khi gửi cho AI.
    """
    return SearchResultItem(
        id=int(row["id"]),
        title=row["tieu_de"],
        summary=row["summary"],
        content=row.get("noi_dung"),
        url=row["link"],
        image=None,  # dữ liệu gốc không có ảnh bài báo
        date=row["ngay_dang"],
        source=row["nguon"],
        score=score,
    )


def search_articles(
    df: pd.DataFrame,
    embedding_store: EmbeddingStore,
    query: str,
    top_k: int = SEARCH_TOP_K,
    score_threshold: float | None = SEARCH_SCORE_THRESHOLD,
) -> list[SearchResultItem]:
    """
    Search Pipeline — luồng DUY NHẤT cho tìm kiếm trong project:

        User Query
          -> Embedding Query        (embedding_store.embed_query, có
                                      instruction prefix cho query — xem
                                      app/embeddings.py)
          -> Qdrant Search          (embedding_store.search, top_k,
                                      score_threshold)
          -> Top K (id, score)
          -> Lấy content đầy đủ theo id từ database (df, cột `noi_dung`)
          -> Trả về API (SearchResultItem)

    KHÔNG có giai đoạn rerank, KHÔNG dùng CrossEncoder, KHÔNG tự viết
    semantic search/cosine, KHÔNG chunk văn bản. Toàn bộ việc tìm k-NN do
    Qdrant Search API đảm nhiệm (xem `vector_store.py`); hàm này chỉ điều
    phối 2 bước còn lại: sinh embedding cho query và hydrate kết quả từ
    database.

    Nếu query rỗng/toàn khoảng trắng, trả về danh sách rỗng ngay — không
    gọi model/Qdrant (giống hành vi `search_news` ở keyword search).
    Nếu Qdrant không trả kết quả nào (collection rỗng, hoặc không có bài
    nào đạt `score_threshold`), cũng trả về danh sách rỗng thay vì lỗi.
    """
    if not query or not query.strip():
        return []

    query_vector = embedding_store.embed_query(query)
    hits = embedding_store.search(
        query_vector, top_k=top_k, score_threshold=score_threshold
    )  # [(article_id, score), ...]

    if not hits:
        return []

    ids = [article_id for article_id, _ in hits]
    scores = {article_id: score for article_id, score in hits}

    rows = _rows_by_ids(df, ids)
    return [_row_to_search_result(row, scores[int(row["id"])]) for row in rows]
