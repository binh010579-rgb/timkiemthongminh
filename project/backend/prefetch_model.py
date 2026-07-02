from sentence_transformers import SentenceTransformer

from app.config import EMBEDDING_MODEL_NAME

if __name__ == "__main__":
    print(f"[prefetch_model] Đang tải trước model '{EMBEDDING_MODEL_NAME}'...")
    SentenceTransformer(EMBEDDING_MODEL_NAME)
    print("[prefetch_model] Tải xong, đã cache vào ~/.cache/huggingface.")
