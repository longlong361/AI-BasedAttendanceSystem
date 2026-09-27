"""
Module: client_core.ui.enrollment_dialog
Nhiệm vụ: Cung cấp hộp thoại (Dialog Form) giao diện Tkinter để giáo viên nhập thông tin
          và đăng ký (enroll) học sinh mới kèm vector khuôn mặt chụp từ webcam.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Any
from client_core.recognizer import FaceRecognizer
from client_core.api_service import enroll_student_to_supabase


class EnrollmentDialog:
    def __init__(
        self,
        parent: tk.Tk,
        camera_capture: Any,
        recognizer: FaceRecognizer,
        log_callback: Callable[[str], None]
    ):
        """
        Nhiệm vụ: Khởi tạo và hiển thị form đăng ký học sinh mới.
        Input:
            parent (tk.Tk): Cửa sổ gốc của Tkinter.
            camera_capture (cv2.VideoCapture): Luồng camera hiện tại để chụp ảnh.
            recognizer (FaceRecognizer): Bộ trích xuất vector khuôn mặt.
            log_callback (Callable): Hàm ủy nhiệm để ghi log ra màn hình chính.
        Output:
            Không có (tạo cửa sổ dialog con).
        """
        self.camera_capture = camera_capture
        self.recognizer = recognizer
        self.log = log_callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Enroll Student")
        self.dialog.geometry("300x250")

        tk.Label(self.dialog, text="Student Code:").pack(pady=2)
        self.code_entry = tk.Entry(self.dialog)
        self.code_entry.pack(pady=2)

        tk.Label(self.dialog, text="Full Name:").pack(pady=2)
        self.name_entry = tk.Entry(self.dialog)
        self.name_entry.pack(pady=2)

        tk.Label(self.dialog, text="Class Name:").pack(pady=2)
        self.class_entry = tk.Entry(self.dialog)
        self.class_entry.pack(pady=2)

        tk.Label(self.dialog, text="School:").pack(pady=2)
        self.school_entry = tk.Entry(self.dialog)
        self.school_entry.pack(pady=2)

        tk.Button(
            self.dialog,
            text="Capture & Save",
            command=self.submit_enrollment,
            bg="blue",
            fg="white"
        ).pack(pady=15)

    def submit_enrollment(self):
        """
        Nhiệm vụ: Xử lý sự kiện nhấn nút 'Capture & Save':
                  - Kiểm tra tính đầy đủ của thông tin nhập vào.
                  - Đọc 1 frame mới nhất từ camera.
                  - Trích xuất vector và kiểm tra mặt thật với FasNet.
                  - Lưu vào bảng students trên Supabase qua REST API.
        Input: Không có (lấy từ các ô input và camera).
        Output: Hiển thị thông báo kết quả (messagebox) và đóng form nếu thành công.
        """
        student_code = self.code_entry.get().strip()
        name = self.name_entry.get().strip()
        class_name = self.class_entry.get().strip()
        school = self.school_entry.get().strip()

        if not all([student_code, name, class_name, school]):
            messagebox.showerror("Validation", "All fields are required.")
            return

        if not self.camera_capture or not self.camera_capture.isOpened():
            messagebox.showerror("Error", "Camera is not available.")
            return

        success, fresh_frame = self.camera_capture.read()
        if not success:
            messagebox.showerror("Error", "Could not capture frame from camera.")
            return

        self.log(f"Enrolling {name} to database...")

        try:
            results = self.recognizer.extract_features(fresh_frame)
            if not results or len(results) == 0:
                messagebox.showerror("Error", "No face detected in the captured frame. Try again.")
                return

            if not results[0].get("is_real", True):
                messagebox.showerror("Security Alert", "Fake face detected! Enrollment blocked.")
                return

            vector = results[0]["embedding"]
            is_success, response_msg = enroll_student_to_supabase(
                student_code=student_code,
                name=name,
                class_name=class_name,
                school=school,
                face_vector=vector
            )

            if is_success:
                self.log(f"Success: {name} enrolled in database.")
                self.dialog.destroy()
            else:
                self.log(f"Enrollment Error: {response_msg}")
                messagebox.showerror("API Error", f"Failed to save to Supabase: {response_msg}")

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
