"""
Module chịu trách nhiệm DUY NHẤT cho việc đọc file CSV và giữ dữ liệu
trong bộ nhớ (RAM) trong suốt vòng đời của server.

Nguyên tắc:
- pd.read_csv() chỉ được gọi MỘT LẦN, tại thời điểm server khởi động
  (xem `main.py`, hàm `lifespan`).
- Sau khi nạp xong, dữ liệu nằm trong `NewsStore.df` (một DataFrame
  trong RAM). Mọi request sau đó chỉ thao tác trên DataFrame có sẵn
  này, KHÔNG đọc lại file CSV.
- Không dùng database — CSV là nguồn dữ liệu duy nhất.
"""

import os
import pandas as pd

from app.config import CSV_PATH

# Các cột bắt buộc phải có trong CSV để hệ thống hoạt động đúng.
REQUIRED_COLUMNS = ["nguon", "tieu_de", "ngay_dang", "tac_gia", "summary", "so_binh_luan", "link"]


class NewsStore:
    """
    Singleton đơn giản giữ DataFrame tin tức trong RAM.

    Instance duy nhất được tạo và nạp dữ liệu trong `lifespan` của
    FastAPI app (xem main.py), sau đó được inject vào các router
    thông qua `app.state.news_store`.
    """

    def __init__(self) -> None:
        self.df: pd.DataFrame | None = None
        self.loaded: bool = False

    def load(self, csv_path: str = CSV_PATH) -> None:
        """Đọc CSV từ đĩa và chuẩn hoá dữ liệu. Chỉ nên gọi 1 lần."""
        if not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"Không tìm thấy file CSV tại: {csv_path}. "
                "Hãy đảm bảo file dữ liệu đã được đặt đúng vị trí backend/data/."
            )

        df = pd.read_csv(csv_path)

        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(f"File CSV thiếu các cột bắt buộc: {missing}")

        # Sinh cột id ổn định, tăng dần theo thứ tự dòng trong CSV.
        df = df.reset_index(drop=True)
        df.insert(0, "id", df.index + 1)

        # Chuẩn hoá kiểu dữ liệu / giá trị rỗng:
        # - Thay NaN/NaT bằng None để khi serialize JSON ra null, không phải "NaN".
        # - Ép comments về kiểu số nguyên (nullable Int64) cho gọn.
        # Một số giá trị trong CSV không phải số nguyên (ví dụ do làm tròn/scale
        # ở bước tiền xử lý trước đó), nên làm tròn trước khi ép kiểu Int64.
        df["so_binh_luan"] = pd.to_numeric(df["so_binh_luan"], errors="coerce").round().astype("Int64")

        text_cols = ["nguon", "tieu_de", "ngay_dang", "tac_gia", "summary", "link", "noi_dung"]
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].where(df[col].notna(), None)

        # Cột tạo sẵn cho tìm kiếm không phân biệt hoa/thường, không dấu
        # (tính một lần khi load, tránh tính lại mỗi request tìm kiếm).
        df["_search_blob"] = (
            df["tieu_de"].fillna("") + " " + df["summary"].fillna("")
        ).map(_strip_accents_lower)

        self.df = df
        self.loaded = True

    def ensure_loaded(self) -> pd.DataFrame:
        if not self.loaded or self.df is None:
            raise RuntimeError(
                "Dữ liệu tin tức chưa được nạp. NewsStore.load() phải được gọi "
                "khi server khởi động trước khi xử lý request."
            )
        return self.df


def _strip_accents_lower(text: str) -> str:
    """Chuẩn hoá chuỗi tiếng Việt: bỏ dấu, chữ thường, dùng để so khớp tìm kiếm."""
    import unicodedata

    normalized = unicodedata.normalize("NFD", text)
    no_accents = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    return no_accents.lower()


# Instance toàn cục duy nhất — được nạp dữ liệu trong main.py (lifespan).
news_store = NewsStore()
