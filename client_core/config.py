"""
Module: client_core.config
Nhiệm vụ: Quản lý toàn bộ cấu hình, hằng số hệ thống, đường dẫn file mô hình và API endpoints.
"""

import os
import urllib.request

# Đường dẫn file model MediaPipe Face Landmarker
MODEL_PATH = "face_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"

# Endpoint API Next.js cục bộ để gửi kết quả điểm danh
API_UPDATE_STATUS = "http://localhost:3000/api/attendance"

# Thời gian chờ (giây) giữa các lần điểm danh của cùng một học sinh để tránh spam log
COOLDOWN_SECONDS = 5

# Cấu hình Supabase REST API dùng cho tính năng ghi danh (Enrollment)
SUPABASE_URL = "https://bkzprvmspptbqitcuktg.supabase.co/rest/v1/students"
SUPABASE_KEY = "sb_publishable_otwaSx22jr_AJf_VQtL4jQ_szQr0wYI"


def ensure_model_downloaded():
    """
    Nhiệm vụ: Kiểm tra xem file model MediaPipe FaceLandmarker đã tồn tại ở local chưa,
              nếu chưa có thì tự động tải về từ Google Cloud Storage.
    Input: Không có.
    Output: bool - True nếu file đã sẵn sàng, False nếu tải thất bại.
    """
    if not os.path.exists(MODEL_PATH):
        print("Downloading FaceLandmarker model...")
        try:
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            print("Download complete.")
            return True
        except Exception as e:
            print(f"Error downloading model: {e}")
            return False
    return True
