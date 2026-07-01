"""
Wrapper mỏng để có thể chạy server bằng đúng lệnh:

    uvicorn main:app --reload --port 8000

(chạy từ thư mục `backend/`). FastAPI app thật sự được định nghĩa ở
`app/main.py` — file này chỉ re-export biến `app` ra module gốc.
"""

from app.main import app

__all__ = ["app"]
