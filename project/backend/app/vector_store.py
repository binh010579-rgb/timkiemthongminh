"""
Module quản lý kết nối + thao tác với Qdrant — nơi lưu trữ DUY NHẤT cho
vector embedding của bài báo, thay thế hoàn toàn cho mảng numpy + cosine
similarity tự viết tay trước đây.

VectorStore không biết gì về cách sinh embedding (đó là việc của
`app/embeddings.py`) — module này CHỈ chịu trách nhiệm:
- Kết nối tới Qdrant (server riêng qua QDRANT_URL, hoặc chế độ embedded
  lưu trên đĩa tại QDRANT_LOCAL_PATH nếu không cấu hình URL).
- Tạo/đảm bảo collection tồn tại với đúng số chiều vector.
- Upsert (id, vector, payload) theo batch.
- Tìm kiếm k-NN bằng Qdrant Search API.

Toàn bộ việc tìm kiếm/so khớp độ tương đồng do Qdrant đảm nhiệm nội bộ.
Project này KHÔNG dùng cosine similarity tự viết, KHÔNG dùng numpy để
brute-force tìm kiếm, KHÔNG dùng sklearn (cosine_similarity/NearestNeighbors),
KHÔNG dùng faiss — Qdrant Search API là điểm truy vấn vector DUY NHẤT.
"""

from __future__ import annotations

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.config import (
    QDRANT_API_KEY,
    QDRANT_COLLECTION_NAME,
    QDRANT_LOCAL_PATH,
    QDRANT_URL,
)


class VectorStore:
    """Singleton bọc QdrantClient, dùng chung cho cả lúc nạp embedding
    (embeddings.py) và lúc tìm kiếm (news_service.py)."""

    def __init__(self) -> None:
        self.client: QdrantClient | None = None
        self.collection_name = QDRANT_COLLECTION_NAME

    def connect(self) -> None:
        """Tạo kết nối tới Qdrant nếu chưa có. Gọi nhiều lần an toàn (no-op
        nếu đã kết nối)."""
        if self.client is not None:
            return
        if QDRANT_URL:
            print(f"[vector_store] Kết nối Qdrant server tại {QDRANT_URL} ...")
            self.client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY or None)
        else:
            print(f"[vector_store] Dùng Qdrant chế độ embedded, lưu tại '{QDRANT_LOCAL_PATH}' ...")
            self.client = QdrantClient(path=QDRANT_LOCAL_PATH)

    def _client(self) -> QdrantClient:
        if self.client is None:
            raise RuntimeError("VectorStore chưa connect(). Gọi connect() trước khi dùng.")
        return self.client

    def collection_exists(self) -> bool:
        names = [c.name for c in self._client().get_collections().collections]
        return self.collection_name in names

    def ensure_collection(self, vector_size: int) -> None:
        """Tạo collection nếu chưa tồn tại. Không xoá dữ liệu cũ nếu đã có
        (dùng khi biết chắc dữ liệu hiện tại đã khớp, xem embeddings.py)."""
        if not self.collection_exists():
            self._client().create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(
                    size=vector_size, distance=qmodels.Distance.COSINE
                ),
            )

    def recreate_collection(self, vector_size: int) -> None:
        """Xoá collection cũ (nếu có) và tạo lại trống — dùng khi cần encode
        lại toàn bộ từ đầu (dữ liệu/model đã đổi)."""
        if self.collection_exists():
            self._client().delete_collection(self.collection_name)
        self._client().create_collection(
            collection_name=self.collection_name,
            vectors_config=qmodels.VectorParams(
                size=vector_size, distance=qmodels.Distance.COSINE
            ),
        )

    def count(self) -> int:
        """Số vector hiện có trong collection. Trả 0 nếu collection chưa tồn tại."""
        if not self.collection_exists():
            return 0
        info = self._client().get_collection(self.collection_name)
        return int(info.points_count or 0)

    def upsert(
        self,
        ids: list[int],
        vectors: np.ndarray,
        payloads: list[dict] | None = None,
        batch_size: int = 256,
    ) -> None:
        """
        Đẩy (id, vector, payload) vào collection theo batch. `ids[i]`,
        `vectors[i]`, `payloads[i]` (nếu có) phải tương ứng với nhau.

        `payloads` chứa dữ liệu hiển thị đi kèm vector (title, summary,
        category, publish_date...) — xem `embeddings.py` để biết cấu trúc
        payload cụ thể. Nếu không truyền, mỗi điểm sẽ có payload rỗng.
        """
        client = self._client()
        total = len(ids)
        payloads = payloads if payloads is not None else [{} for _ in range(total)]
        for start in range(0, total, batch_size):
            end = min(start + batch_size, total)
            client.upsert(
                collection_name=self.collection_name,
                points=qmodels.Batch(
                    ids=[int(i) for i in ids[start:end]],
                    vectors=[v.tolist() for v in vectors[start:end]],
                    payloads=payloads[start:end],
                ),
            )

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int,
        score_threshold: float | None = None,
    ) -> list[tuple[int, float]]:
        """
        Tìm top_k điểm gần nhất với `query_vector` bằng Qdrant Search API.
        Qdrant tự tính độ tương đồng (cosine) nội bộ vì collection được tạo
        với distance=COSINE — không có phép tính cosine/numpy/sklearn/faiss
        thủ công nào ở module này hay bất kỳ nơi nào khác trong project.

        `score_threshold` (nếu truyền) được đẩy thẳng cho Qdrant lọc ngay
        trong lúc search — Qdrant sẽ chỉ trả về các điểm có score >=
        ngưỡng này, kể cả khi ít hơn `top_k` kết quả (hoặc rỗng nếu không
        có điểm nào đủ gần). Đây vẫn là Qdrant Search API đảm nhiệm việc
        lọc, không phải code Python tự lọc lại sau khi nhận kết quả.

        Chỉ lấy `id` + `score` (with_payload=False, with_vectors=False) —
        việc hydrate đầy đủ thông tin bài báo (title, summary, url...) để
        trả về cho client là trách nhiệm của tầng service, đọc từ
        DataFrame (nguồn dữ liệu chính), không phải từ payload Qdrant.

        Trả về list[(article_id, score)] đã sắp xếp giảm dần theo score.
        """
        hits = self._client().search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist(),
            limit=top_k,
            score_threshold=score_threshold,
            with_payload=False,
            with_vectors=False,
        )
        return [(int(hit.id), float(hit.score)) for hit in hits]

    def get_vector(self, article_id: int) -> np.ndarray | None:
        """Lấy lại vector đã lưu của 1 bài báo theo id, trả None nếu không có."""
        points = self._client().retrieve(
            collection_name=self.collection_name,
            ids=[int(article_id)],
            with_vectors=True,
        )
        if not points:
            return None
        return np.asarray(points[0].vector, dtype=np.float32)


# Instance toàn cục duy nhất — dùng chung bởi embeddings.py và news_service.py.
vector_store = VectorStore()
