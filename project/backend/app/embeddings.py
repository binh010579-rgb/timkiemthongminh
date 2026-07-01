"""
Module embedding: chứa các hàm dùng chung để sinh embedding ngữ nghĩa cho
bài báo bằng SentenceTransformer (Qwen3 Embedding), cộng với lớp
`EmbeddingStore` dùng RIÊNG bởi server lúc runtime để embed câu query và
tìm kiếm trong Qdrant.

QUY TẮC BẮT BUỘC:
- CHỈ embedding `title + summary` (cột `tieu_de` + `summary`). TUYỆT ĐỐI
  KHÔNG đưa `content` (cột `noi_dung`) vào input của model.
- Vector embedding KHÔNG được giữ trong RAM dưới dạng numpy array và
  KHÔNG ghi ra file `.npy`/`.npz`. Toàn bộ vector sống trong Qdrant.
- Việc tìm kiếm (k-NN) hoàn toàn do Qdrant Search API đảm nhiệm — project
  KHÔNG tự viết cosine similarity, KHÔNG dùng numpy để brute-force search,
  KHÔNG dùng sklearn, KHÔNG dùng faiss, KHÔNG dùng reranker.

QUAN TRỌNG — tách trách nhiệm sau refactor:
- Việc SINH HÀNG LOẠT embedding cho toàn bộ dữ liệu + upsert vào Qdrant
  KHÔNG còn diễn ra tự động khi server khởi động. Việc đó là trách nhiệm
  DUY NHẤT của script độc lập `backend/build_vectors.py` (chạy thủ công,
  trước hoặc bất cứ khi nào dữ liệu CSV thay đổi).
- Khi server khởi động (`app/main.py`), `EmbeddingStore` CHỈ load model
  (để có thể embed query khi client gọi `/search`) và kết nối tới Qdrant
  collection đã có sẵn (do `build_vectors.py` tạo) — KHÔNG encode lại
  toàn bộ dữ liệu.
"""

from __future__ import annotations

import hashlib
import json
import os
import time

import numpy as np
import pandas as pd

from app.config import (
    EMBEDDING_BATCH_SIZE,
    EMBEDDING_MAX_SEQ_LENGTH,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_QUERY_TASK_DESCRIPTION,
    EMBEDDING_STATE_PATH,
)
from app.vector_store import vector_store


def _safe_str(value) -> str:
    """Chuyển giá trị (có thể là None/NaN) thành chuỗi an toàn để ghép embedding."""
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return str(value)


def build_embedding_text(row: pd.Series) -> str:
    """
    Ghép title + summary thành 1 chuỗi văn bản dùng làm input cho model
    embedding.

    CHỈ DÙNG ĐÚNG 2 CỘT `tieu_de` và `summary`. KHÔNG được thêm `noi_dung`
    (content) vào đây dù DataFrame có cột đó.

    LƯU Ý: đây là văn bản TÀI LIỆU (document) — theo đúng cách Qwen3
    Embedding được huấn luyện, tài liệu KHÔNG cần (và không nên) có
    instruction prefix. Chỉ CÂU QUERY của người dùng mới cần
    `build_query_instruct_text()` bên dưới.
    """
    title = _safe_str(row.get("tieu_de"))
    summary = _safe_str(row.get("summary"))
    return f"{title}\n{summary}".strip()


def build_query_instruct_text(query: str) -> str:
    """
    Bọc câu query của người dùng trong instruction prompt theo đúng format
    mà Qwen3-Embedding yêu cầu cho tác vụ truy hồi (retrieval):

        "Instruct: {mô tả task}\nQuery:{câu hỏi}"

    QUAN TRỌNG: Qwen3-Embedding là model bất đối xứng — tài liệu (xem
    `build_embedding_text`) KHÔNG có prefix này, chỉ query mới có. Thiếu
    bước này không gây lỗi (model vẫn chạy, vẫn ra vector), nhưng độ chính
    xác truy hồi giảm rõ rệt vì vector query không còn nằm đúng "vùng
    không gian" mà model được huấn luyện để so khớp với vector tài liệu.

    Tự dựng chuỗi này (thay vì dựa vào `model.prompts["query"]` nội bộ của
    sentence-transformers) để không phụ thuộc vào việc file cấu hình
    prompt của model có được tải đúng hay không (ví dụ khi dùng bản model
    tải thủ công / mirror nội bộ / cache cũ).
    """
    return f"Instruct: {EMBEDDING_QUERY_TASK_DESCRIPTION}\nQuery:{query}"


def build_payload(row: pd.Series, has_category: bool) -> dict:
    """
    Payload lưu kèm mỗi vector trong Qdrant — chỉ để tham khảo/lọc, KHÔNG
    dùng để search. Gồm: id, title, summary, category (nếu có), publish_date.
    """
    return {
        "id": int(row["id"]),
        "title": _safe_str(row.get("tieu_de")) or None,
        "summary": _safe_str(row.get("summary")) or None,
        "category": (_safe_str(row.get("category")) or None) if has_category else None,
        "publish_date": _safe_str(row.get("ngay_dang")) or None,
    }


def texts_hash(texts: list[str], model_name: str) -> str:
    """
    Hash nội dung toàn bộ text + tên model — dùng để biết dữ liệu/model có
    đổi so với lần encode trước hay không, từ đó quyết định
    `build_vectors.py` có cần encode lại (tốn thời gian) hay có thể bỏ qua.
    """
    hasher = hashlib.sha256()
    hasher.update(model_name.encode("utf-8"))
    for t in texts:
        hasher.update(t.encode("utf-8"))
        hasher.update(b"\x00")
    return hasher.hexdigest()


def load_state() -> dict | None:
    """Đọc file trạng thái nhỏ (JSON, không chứa vector). Trả None nếu chưa
    có hoặc đọc lỗi (ép encode lại từ đầu cho an toàn)."""
    if not os.path.exists(EMBEDDING_STATE_PATH):
        return None
    try:
        with open(EMBEDDING_STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        print(f"[embeddings] Không đọc được state ({exc}) — sẽ encode lại từ đầu.")
        return None


def save_state(hash_value: str, count: int, dim: int) -> None:
    os.makedirs(os.path.dirname(EMBEDDING_STATE_PATH), exist_ok=True)
    with open(EMBEDDING_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump({"texts_hash": hash_value, "count": count, "dim": dim}, f)


def load_embedding_model(model_name: str = EMBEDDING_MODEL_NAME):
    """
    Load SentenceTransformer (Qwen3 Embedding) MỘT LẦN. Dùng chung bởi:
    - `EmbeddingStore` (runtime, chỉ để embed query)
    - `build_vectors.py` (script bulk-encode toàn bộ dữ liệu)
    """
    import torch
    from sentence_transformers import SentenceTransformer

    # Chọn device tường minh + log ra, để biết chắc model có chạy trên
    # GPU hay không (chạy "ngầm" trên CPU mà không biết là nguyên nhân
    # phổ biến nhất khiến encode() trông như bị treo).
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[embeddings] Đang load model '{model_name}' trên device='{device}'...")
    model = SentenceTransformer(model_name, device=device)

    old_len = model.max_seq_length
    model.max_seq_length = EMBEDDING_MAX_SEQ_LENGTH
    print(f"[embeddings] max_seq_length: {old_len} -> {EMBEDDING_MAX_SEQ_LENGTH}")
    return model


def encode_and_upsert(
    model,
    ids: list[int],
    texts: list[str],
    payloads: list[dict],
    batch_size: int = EMBEDDING_BATCH_SIZE,
) -> int:
    """
    Encode `texts` theo batch (log rõ trước/sau mỗi batch) rồi upsert thẳng
    vào Qdrant (recreate collection trước để đảm bảo dữ liệu cũ — nếu có —
    không bị lẫn với lần encode mới). KHÔNG giữ vector trong RAM lâu dài,
    KHÔNG ghi ra .npy/.npz. Trả về số chiều (dim) của vector.

    Dùng bởi `build_vectors.py`.
    """
    total = len(texts)
    print(
        f"[embeddings] Bắt đầu encode {total} bài báo (title+summary), "
        f"batch_size={batch_size}..."
    )

    all_vectors: list[np.ndarray] = []
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        batch_texts = texts[start:end]
        t0 = time.time()
        print(f"[embeddings] -> Encode batch [{start}:{end}] / {total} ...", flush=True)

        batch_vectors = model.encode(
            batch_texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,  # chuẩn hoá L2 -> khớp với distance=COSINE trong Qdrant
            convert_to_numpy=True,
        )

        elapsed = time.time() - t0
        print(
            f"[embeddings] <- Xong batch [{start}:{end}] / {total} "
            f"({elapsed:.2f}s, {len(batch_texts) / max(elapsed, 1e-6):.2f} bài/s)",
            flush=True,
        )
        all_vectors.append(batch_vectors)

    vectors = np.concatenate(all_vectors, axis=0).astype(np.float32)
    dim = vectors.shape[1]

    vector_store.connect()
    vector_store.recreate_collection(vector_size=dim)
    vector_store.upsert(ids=ids, vectors=vectors, payloads=payloads)

    print(f"[embeddings] Đã upsert {total} vector (dim={dim}) vào Qdrant.")
    return dim


class EmbeddingStore:
    """
    Singleton dùng RIÊNG bởi server lúc runtime (xem `app/main.py`):
    - Load model SentenceTransformer (Qwen3 Embedding) MỘT LẦN khi server
      khởi động — chỉ để có thể `embed_query()` cho mỗi request `/search`.
    - Uỷ quyền tìm kiếm k-NN cho Qdrant (`search()`) — không tự tính cosine.

    KHÔNG bulk-encode dữ liệu, KHÔNG giữ vector trong RAM. Toàn bộ vector
    của bài báo do `build_vectors.py` sinh ra và lưu sẵn trong Qdrant từ
    trước; class này chỉ kết nối tới collection đã có sẵn đó.
    """

    def __init__(self) -> None:
        self.model = None
        self.dim: int | None = None
        self.loaded: bool = False

    def load(self, model_name: str = EMBEDDING_MODEL_NAME) -> None:
        """
        Load model (cho `embed_query`) + kết nối Qdrant. Gọi MỘT LẦN khi
        server khởi động. KHÔNG đọc CSV, KHÔNG encode hàng loạt — nếu
        collection rỗng/chưa tồn tại, chỉ log cảnh báo nhắc chạy
        `python build_vectors.py`, không raise lỗi (server vẫn khởi động
        bình thường, các endpoint danh sách/tìm-kiếm-từ-khoá khác không bị
        ảnh hưởng; `/search` chỉ đơn giản trả về rỗng cho tới khi có vector).
        """
        self.model = load_embedding_model(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()

        vector_store.connect()
        vector_store.ensure_collection(vector_size=self.dim)
        count = vector_store.count()
        if count == 0:
            print(
                "[embeddings] CẢNH BÁO: Qdrant collection chưa có vector nào. "
                "Chạy `python build_vectors.py` (trong thư mục backend/) để "
                "sinh embedding cho toàn bộ dữ liệu trước khi dùng /search."
            )
        else:
            print(f"[embeddings] Qdrant đã có {count} vector (dim={self.dim}) sẵn sàng tìm kiếm.")

        self.loaded = True

    def ensure_loaded(self) -> None:
        if not self.loaded or self.model is None:
            raise RuntimeError(
                "Embedding chưa sẵn sàng. EmbeddingStore.load() phải được gọi "
                "khi server khởi động."
            )

    def embed_query(self, text: str) -> np.ndarray:
        """
        Sinh embedding cho 1 câu truy vấn (search query), dùng lại đúng
        model đã được load sẵn ở `load()` — KHÔNG load lại model.

        QUAN TRỌNG: câu query được bọc qua `build_query_instruct_text()`
        trước khi encode (xem docstring hàm đó) — đây là điểm khác biệt
        BẮT BUỘC so với cách embed tài liệu (`build_embedding_text`,
        không có instruction). Model Qwen3-Embedding là model bất đối
        xứng: bỏ bước này không lỗi nhưng độ chính xác truy hồi giảm hẳn.
        """
        self.ensure_loaded()
        instructed_text = build_query_instruct_text(text)
        vector = self.model.encode(
            [instructed_text],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return np.asarray(vector[0], dtype=np.float32)

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int,
        score_threshold: float | None = None,
    ) -> list[tuple[int, float]]:
        """
        Tìm top_k bài báo gần nhất với `query_vector`. Uỷ quyền hoàn toàn
        cho Qdrant (collection tạo với distance=COSINE). Không có phép
        tính cosine thủ công nào ở tầng này hoặc tầng gọi.

        Trả về list[(article_id, score)] đã sắp xếp giảm dần theo score.
        """
        self.ensure_loaded()
        return vector_store.search(query_vector, top_k=top_k, score_threshold=score_threshold)

    def get_vector(self, article_id: int) -> np.ndarray | None:
        """Lấy lại vector embedding của 1 bài báo theo id, đọc trực tiếp từ Qdrant."""
        self.ensure_loaded()
        return vector_store.get_vector(article_id)

    def summary(self) -> tuple[int, int]:
        """Trả (số bài đã có embedding, số chiều vector) — dùng để log ở main.py."""
        self.ensure_loaded()
        return vector_store.count(), (self.dim or 0)


# Instance toàn cục duy nhất — được load (chỉ load model + connect) trong
# main.py (lifespan).
embedding_store = EmbeddingStore()
