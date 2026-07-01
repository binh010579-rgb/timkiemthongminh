"""
Script độc lập: đọc toàn bộ dữ liệu tin tức từ CSV, sinh embedding cho
title+summary bằng SentenceTransformer (Qwen3 Embedding), rồi upload toàn
bộ vector lên Qdrant.

Đây là nơi DUY NHẤT trong project thực hiện việc bulk-encode dữ liệu —
server FastAPI (`app/main.py`) khi khởi động KHÔNG tự encode lại, nó chỉ
kết nối tới collection mà script này đã tạo sẵn.

Khi nào cần chạy:
- Trước khi chạy server lần đầu (collection Qdrant đang rỗng).
- Mỗi khi `backend/data/cleaned_news.csv` được cập nhật (dữ liệu mới/khác).
- Script tự động bỏ qua việc encode lại nếu dữ liệu + model KHÔNG đổi so
  với lần chạy trước (so khớp qua hash lưu tại
  `backend/data/embedding_state.json`) — dùng `--force` để ép encode lại
  dù không có gì thay đổi.

Cách chạy (từ thư mục backend/, sau khi `pip install -r requirements.txt`
và đã có Qdrant đang chạy, ví dụ `docker run -p 6333:6333 qdrant/qdrant`):

    python build_vectors.py
    python build_vectors.py --force   # ép encode lại toàn bộ

QUY TẮC: CHỈ embed title (`tieu_de`) + summary (`summary`). KHÔNG bao giờ
đưa content (`noi_dung`) vào input embedding.
"""

from __future__ import annotations

import argparse

from app.data_loader import NewsStore
from app.embeddings import (
    build_embedding_text,
    build_payload,
    encode_and_upsert,
    load_embedding_model,
    load_state,
    save_state,
    texts_hash,
)
from app.config import EMBEDDING_BATCH_SIZE, EMBEDDING_MODEL_NAME
from app.vector_store import vector_store


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Đọc CSV, embedding title+summary, upload lên Qdrant."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ép encode lại toàn bộ dữ liệu dù hash không đổi.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=EMBEDDING_BATCH_SIZE,
        help=f"Batch size khi encode (mặc định: {EMBEDDING_BATCH_SIZE}).",
    )
    args = parser.parse_args()

    # 1. Đọc toàn bộ dữ liệu từ CSV (cùng cách load.py dùng cho server).
    print("[build_vectors] Đang đọc dữ liệu từ CSV...")
    news_store = NewsStore()
    news_store.load()
    df = news_store.df
    print(f"[build_vectors] Đã đọc {len(df)} bài báo.")

    # 2. Chuẩn bị text (title+summary) + payload cho từng bài báo.
    texts = [build_embedding_text(row) for _, row in df.iterrows()]
    ids = df["id"].tolist()
    has_category = "category" in df.columns
    payloads = [build_payload(row, has_category) for _, row in df.iterrows()]

    empty_count = sum(1 for t in texts if t == "")
    if empty_count:
        print(
            f"[build_vectors] Cảnh báo: {empty_count} bài báo có title+summary "
            "rỗng — vẫn encode bình thường."
        )

    # 3. Kiểm tra xem dữ liệu/model có đổi so với lần chạy trước không, để
    #    tránh encode lại không cần thiết (rất tốn thời gian).
    hash_value = texts_hash(texts, EMBEDDING_MODEL_NAME)
    state = load_state()
    vector_store.connect()
    qdrant_count = vector_store.count()

    data_unchanged = (
        not args.force
        and state is not None
        and state.get("texts_hash") == hash_value
        and state.get("count") == len(texts)
        and qdrant_count == len(texts)
    )

    if data_unchanged:
        print(
            "[build_vectors] Dữ liệu + model không đổi và Qdrant đã có đủ "
            f"{qdrant_count} vector — bỏ qua encode. Dùng --force để ép chạy lại."
        )
        return

    # 4. Load model + encode + upsert lên Qdrant.
    model = load_embedding_model(EMBEDDING_MODEL_NAME)
    dim = encode_and_upsert(model, ids, texts, payloads, batch_size=args.batch_size)
    save_state(hash_value, count=len(texts), dim=dim)

    print(
        f"[build_vectors] Hoàn tất: {len(texts)} bài báo, dim={dim}, "
        f"collection='{vector_store.collection_name}'."
    )


if __name__ == "__main__":
    main()
