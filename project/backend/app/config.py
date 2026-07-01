"""
Cấu hình tập trung cho backend.

Mọi giá trị "cứng" (đường dẫn file, danh sách origin được phép gọi CORS...)
nên đặt ở đây để dễ chỉnh sửa mà không phải lục code logic.
"""

import os

# Thư mục gốc của backend (.../backend)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Đường dẫn tới file CSV chứa dữ liệu tin tức đã làm sạch.
# Đây là nguồn dữ liệu DUY NHẤT của hệ thống — không dùng database.
CSV_PATH = os.path.join(BASE_DIR, "data", "cleaned_news.csv")

# Các origin frontend được phép gọi API (Vite dev server mặc định: 5173).
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Giới hạn an toàn cho tham số phân trang để tránh client truyền limit quá lớn.
MAX_PAGE_LIMIT = 100
DEFAULT_PAGE_LIMIT = 10

# Model embedding dùng để sinh vector ngữ nghĩa cho mỗi bài báo.
# Có thể đổi sang bản lớn hơn (Qwen3-Embedding-4B / -8B) nếu máy đủ tài nguyên.
EMBEDDING_MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"

# Kích thước batch khi encode hàng loạt bài báo (tăng nếu có GPU mạnh).
# Lưu ý: nếu chạy trên CPU, batch lớn + chuỗi dài (xem EMBEDDING_MAX_SEQ_LENGTH)
# sẽ khiến mỗi batch mất rất lâu (trông giống như "bị treo" dù thực ra vẫn
# đang chạy). 16 là giá trị an toàn cho CPU; có thể tăng lên 32-64 nếu có GPU.
EMBEDDING_BATCH_SIZE = 16

# Số token tối đa cho mỗi văn bản khi encode. Từ bản refactor này, input
# embedding CHỈ gồm title+summary (không còn content) nên luôn ngắn — giá
# trị này chỉ còn vai trò giới hạn an toàn cho các summary bất thường dài,
# không còn ảnh hưởng nhiều tới tốc độ như khi còn embed content.
EMBEDDING_MAX_SEQ_LENGTH = 512

# Qwen3-Embedding là model BẤT ĐỐI XỨNG (asymmetric retrieval): tài liệu
# (title+summary của bài báo) được encode thẳng, KHÔNG kèm instruction —
# nhưng CÂU QUERY của người dùng PHẢI được bọc trong 1 prompt dạng
# "Instruct: {mô tả task}\nQuery:{câu hỏi}" thì model mới cho ra vector
# đúng không gian ngữ nghĩa để so khớp với vector tài liệu. Đây là yêu cầu
# chính thức từ nhà phát hành model (Qwen), không phải tuỳ chọn tối ưu —
# thiếu bước này khiến độ chính xác tìm kiếm giảm rõ rệt dù vẫn chạy được
# và không báo lỗi. Xem `app/embeddings.py::build_query_instruct_text()`.
EMBEDDING_QUERY_TASK_DESCRIPTION = (
    "Given a Vietnamese news search query, retrieve news articles "
    "(title and summary) that answer or are most relevant to the query"
)

# --- Qdrant (vector store lưu trữ + tìm kiếm embedding bài báo) ---
# Mặc định trỏ tới Qdrant chạy bằng:
#   docker run -p 6333:6333 qdrant/qdrant
# (hoặc `docker compose up` với docker-compose.yml đi kèm) — để project
# chạy được ngay sau 2 lệnh đó mà không cần cấu hình thêm gì.
#
# Set QDRANT_URL="" (rỗng) nếu muốn dùng chế độ embedded thay thế — Qdrant
# chạy in-process, tự lưu dữ liệu trên đĩa tại QDRANT_LOCAL_PATH, không
# cần cài đặt server riêng (tiện cho demo/máy đơn không có Docker).
_QDRANT_URL_RAW = os.environ.get("QDRANT_URL", "embedded")
QDRANT_URL = (
    "" if _QDRANT_URL_RAW.strip().lower() in ("", "embedded", "none", "local")
    else _QDRANT_URL_RAW
)
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY", "")
QDRANT_LOCAL_PATH = os.path.join(BASE_DIR, "data", "qdrant_local")
QDRANT_COLLECTION_NAME = "news_articles"

# File trạng thái nhỏ (JSON, KHÔNG chứa vector) dùng để biết embedding đã
# được sinh & đẩy vào Qdrant cho đúng bộ dữ liệu + model hiện tại hay chưa,
# tránh phải encode lại toàn bộ bài báo mỗi lần khởi động server nếu CSV và
# model không đổi. Thay thế cho file .npz cache (mảng vector) trước đây —
# file này chỉ lưu hash + vài số liệu thống kê, không lưu vector nào.
EMBEDDING_STATE_PATH = os.path.join(BASE_DIR, "data", "embedding_state.json")

# Số kết quả trả về cho client khi tìm kiếm ngữ nghĩa (POST /search).
# Search Pipeline: Query -> Embedding Query -> Qdrant Search -> Top K bài
# -> lấy content đầy đủ theo id từ database -> trả về API.
# Không có giai đoạn rerank / CrossEncoder nào sau Qdrant Search.
SEARCH_TOP_K = 5

# Ngưỡng điểm tương đồng cosine tối thiểu (0..1) để 1 kết quả được coi là
# "đủ liên quan" và trả về cho client. Nếu để None, Qdrant luôn trả đủ
# top-K dù không có bài nào thực sự liên quan tới câu query (vì Qdrant chỉ
# tìm điểm GẦN NHẤT, không biết thế nào là "đủ gần"), khiến những câu query
# lạc đề vẫn trả về kết quả trông như ngẫu nhiên.
#
# 0.35–0.45 là khoảng khởi điểm hợp lý cho Qwen3-Embedding với văn bản
# tiếng Việt ngắn (title+summary) khi đã dùng đúng query instruction ở
# trên — nên tinh chỉnh lại bằng cách thử vài câu query thật và xem điểm
# số trả về trước khi đưa vào production. Để None để tắt tính năng này
# (giữ nguyên hành vi trả đủ top-K như trước).
SEARCH_SCORE_THRESHOLD: float | None = None
