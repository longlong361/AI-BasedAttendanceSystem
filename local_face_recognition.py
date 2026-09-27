"""
Dự án: AI-Based Attendance System
File thực thi chính (Entry Point): local_face_recognition.py
Nhiệm vụ:
    Khởi chạy ứng dụng máy trạm AI Face Attendance trên nền tảng desktop Tkinter.
    File này đóng vai trò điểm kích hoạt chính (Entry Point), kết nối và điều phối các
    module trong thư mục client_core/ đã được chuẩn hóa theo kiến trúc phân tầng.
"""

import tkinter as tk
from client_core.ui.main_window import AttendanceApp

# Export AttendanceApp để tương thích ngược hoàn toàn nếu có module khác import
__all__ = ["AttendanceApp"]

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
