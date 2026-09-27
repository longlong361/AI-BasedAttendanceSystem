"""
Module: client_core.ui.main_window
Nhiệm vụ: Cửa sổ giao diện chính của ứng dụng AI Face Attendance (Tkinter GUI):
          - Quản lý tương tác người dùng: Chọn camera, bật/tắt camera, mở popup đăng ký học sinh.
          - Vòng lặp cập nhật video thời gian thực (update_video_frame, chu kỳ 30ms).
          - Điều phối luồng xử lý: MediaPipe Liveness Detection -> DeepFace Recognition -> API Điểm danh.
          - Hiển thị phản hồi thị giác: Khung viền nhận diện (Bounding box), tên học sinh, cảnh báo khuôn mặt giả.
"""

import time
import threading
import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from client_core.config import COOLDOWN_SECONDS
from client_core.camera import detect_available_cameras, open_camera
from client_core.liveness import LivenessDetector
from client_core.recognizer import FaceRecognizer
from client_core.api_service import send_attendance_vector
from client_core.ui.enrollment_dialog import EnrollmentDialog


class AttendanceApp:
    def __init__(self, root: tk.Tk):
        """
        Nhiệm vụ: Khởi tạo toàn bộ giao diện và các module xử lý AI cho ứng dụng.
        Input:
            root (tk.Tk): Cửa sổ gốc Tkinter.
        Output:
            Không có (khởi tạo app instance).
        """
        self.root = root
        self.root.title("AI Face Attendance System")

        self.camera_capture = None
        self.is_camera_running = False
        self.last_recognition_timestamps = {}
        self.is_processing_frame = False
        self.detected_faces = []

        # Khởi tạo các module nghiệp vụ AI độc lập
        self.liveness_detector = LivenessDetector()
        self.recognizer = FaceRecognizer()

        self.liveness_passed = False
        self.eyes_were_open = False
        self.last_face_time = 0

        self._setup_ui()
        self._detect_available_cameras()

    def _setup_ui(self):
        """
        Nhiệm vụ: Dựng các phần tử giao diện Tkinter (Labels, Combobox, Buttons, Canvas, Text Log).
        Input / Output: Không có.
        """
        self.camera_label = tk.Label(self.root, text="Select Camera:")
        self.camera_label.pack(pady=5)

        self.camera_selector = ttk.Combobox(self.root)
        self.camera_selector.pack(pady=5)

        self.toggle_camera_button = tk.Button(
            self.root,
            text="Start Camera",
            command=self.toggle_camera,
            width=20
        )
        self.toggle_camera_button.pack(pady=5)

        self.enroll_button = tk.Button(
            self.root,
            text="Enroll New Student",
            command=self.open_enrollment_dialog,
            width=20,
            state=tk.DISABLED
        )
        self.enroll_button.pack(pady=5)

        self.video_display = tk.Label(self.root)
        self.video_display.pack(pady=5)

        self.log_output = tk.Text(self.root, height=12, width=60)
        self.log_output.pack(pady=5)

    def _detect_available_cameras(self):
        """
        Nhiệm vụ: Tìm kiếm các camera kết nối với máy tính và đưa danh sách vào Combobox.
        Input / Output: Không có.
        """
        self.log("Scanning for available cameras...")
        available_cameras = detect_available_cameras(max_to_test=5)

        if available_cameras:
            self.camera_selector['values'] = available_cameras
            self.camera_selector.current(0)
            self.log(f"Found cameras: {available_cameras}")
        else:
            self.log("No cameras found")

    def log(self, message: str):
        """
        Nhiệm vụ: Ghi thông báo ra khung Text log trên giao diện và in ra console.
        Input:
            message (str): Chuỗi nội dung cần ghi log.
        Output: Không có.
        """
        self.log_output.insert(tk.END, message + "\n")
        self.log_output.see(tk.END)
        print(message)

    def toggle_camera(self):
        """
        Nhiệm vụ: Bật hoặc tắt luồng nhận diện camera khi người dùng nhấn nút 'Start Camera' / 'Stop Camera'.
        Input / Output: Không có.
        """
        if self.is_camera_running:
            self.is_camera_running = False
            self.toggle_camera_button.config(text="Start Camera")
            self.enroll_button.config(state=tk.DISABLED)
            if self.camera_capture:
                self.camera_capture.release()
            self.video_display.config(image='')
            self.liveness_passed = False
            self.log("Camera stopped.")
        else:
            selected_camera = self.camera_selector.get()
            self.camera_capture = open_camera(selected_camera)

            if not self.camera_capture.isOpened():
                self.log("Error: Cannot open the selected camera.")
                return

            self.is_camera_running = True
            self.toggle_camera_button.config(text="Stop Camera")
            self.enroll_button.config(state=tk.NORMAL)
            self.log("Camera started. Looking for faces...")
            self.update_video_frame()

    def update_video_frame(self):
        """
        Nhiệm vụ: Vòng lặp đọc khung hình từ camera (khoảng 30ms/lần):
                  - Đọc frame và chuyển đổi sang RGB.
                  - Phát hiện mốc khuôn mặt với MediaPipe.
                  - Kiểm tra góc nghiêng mặt (chống giả mạo ảnh nghiêng).
                  - Kiểm tra nhịp chớp mắt (EAR) để xác nhận người thật (Liveness Detection).
                  - Nếu hợp lệ: Kích hoạt luồng nhận diện DeepFace (chạy đa luồng ngầm).
                  - Vẽ các khung nhận diện và cập nhật hình ảnh lên màn hình Tkinter.
        Input / Output: Không có.
        """
        if not self.is_camera_running:
            return

        success, frame = self.camera_capture.read()
        if success:
            frame_height, frame_width, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            landmarks_list = self.liveness_detector.detect_landmarks(rgb_frame)

            if landmarks_list:
                self.last_face_time = time.time()

                for face_landmarks in landmarks_list:
                    # Ngăn chặn hành vi dùng ảnh điện thoại lắc/nghiêng
                    is_straight, _ = self.liveness_detector.check_head_tilt(face_landmarks)
                    if not is_straight:
                        cv2.putText(frame, "Keep your head straight!", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                        self.eyes_were_open = False
                        self.liveness_passed = False
                        self.detected_faces = []
                        break

                if not self.liveness_passed:
                    for face_landmarks in landmarks_list:
                        avg_ear = self.liveness_detector.calculate_average_ear(face_landmarks, frame_width, frame_height)

                        if avg_ear > 0.25:
                            self.eyes_were_open = True
                        elif avg_ear < 0.2 and getattr(self, 'eyes_were_open', False):
                            self.liveness_passed = True
                            break

                if self.liveness_passed:
                    cv2.putText(frame, "Liveness Passed!", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    if not self.is_processing_frame:
                        self.is_processing_frame = True
                        threading.Thread(target=self.recognize_faces, args=(frame.copy(),), daemon=True).start()
                else:
                    cv2.putText(frame, "Please blink your eyes...", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            else:
                if time.time() - getattr(self, 'last_face_time', 0) > 1.0:
                    self.liveness_passed = False
                    self.eyes_were_open = False
                    self.detected_faces = []

            # Giữ lại các hộp khuôn mặt được cập nhật trong vòng 2 giây gần nhất
            current_time = time.time()
            self.detected_faces = [face for face in self.detected_faces if current_time - face['timestamp'] < 2]

            for face in self.detected_faces:
                color = (0, 0, 255) if face.get('is_fake', False) else (0, 255, 0)
                cv2.rectangle(frame, (face['x'], face['y']), (face['x'] + face['width'], face['y'] + face['height']), color, 2)
                cv2.putText(frame, face['name'], (face['x'], face['y'] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            rgb_frame_ui = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_obj = Image.fromarray(rgb_frame_ui)
            tk_image = ImageTk.PhotoImage(image=image_obj)

            self.video_display.imgtk = tk_image
            self.video_display.configure(image=tk_image)

        self.root.after(30, self.update_video_frame)

    def recognize_faces(self, frame):
        """
        Nhiệm vụ: Chạy trong luồng ngầm (daemon thread) để nhận diện khuôn mặt và điểm danh:
                  - Dùng DeepFace (Facenet512 + FasNet Anti-spoofing).
                  - Nếu phát hiện mặt giả: Báo động và chặn.
                  - Nếu là mặt thật: Gửi vector trích xuất sang Next.js backend để đối sánh qua Supabase.
                  - Cập nhật bounding box và trạng thái điểm danh lên UI (có áp dụng cooldown).
        Input:
            frame (np.ndarray): Bản sao khung hình chụp tại thời điểm vượt qua liveness.
        Output: Không có.
        """
        try:
            results = self.recognizer.extract_features(frame)
            if not results:
                return

            current_time = time.time()

            for result in results:
                if not result.get("is_real", True):
                    self.root.after(0, self.log, "Security Alert: Fake face (spoofing) detected and blocked!")
                    self.liveness_passed = False
                    self.eyes_were_open = False
                    facial_area = result["facial_area"]
                    self.detected_faces = [{
                        'name': 'FAKE FACE BLOCKED!',
                        'x': facial_area["x"],
                        'y': facial_area["y"],
                        'width': facial_area["w"],
                        'height': facial_area["h"],
                        'timestamp': current_time,
                        'is_fake': True
                    }]
                    continue

                embedding_vector = result["embedding"]
                print(f"[Debug] Extracted Face Vector (Length {len(embedding_vector)}): {embedding_vector}")
                self.root.after(0, self.log, f"Scanned vector starts with: {str(embedding_vector[:5])}...")

                facial_area = result["facial_area"]
                x = facial_area["x"]
                y = facial_area["y"]
                width = facial_area["w"]
                height = facial_area["h"]

                self.detected_faces = [{
                    'name': 'Analyzing...',
                    'x': x,
                    'y': y,
                    'width': width,
                    'height': height,
                    'timestamp': current_time
                }]

                success, student_info = send_attendance_vector(embedding_vector)
                if success and student_info:
                    student_id = student_info.get("student_code") or student_info.get("id", "Unknown")
                    student_name = student_info.get("name", student_id)

                    self.detected_faces = [{
                        'name': student_name,
                        'x': x,
                        'y': y,
                        'width': width,
                        'height': height,
                        'timestamp': current_time
                    }]

                    # Cooldown tránh lặp log điểm danh liên tục
                    last_time = self.last_recognition_timestamps.get(student_id, 0)
                    if (current_time - last_time) > COOLDOWN_SECONDS:
                        self.last_recognition_timestamps[student_id] = current_time
                        self.root.after(0, self.log, f"Attendance marked for: {student_name} ({student_id})")

                        self.liveness_passed = False
                        self.eyes_were_open = False

        except Exception as error:
            print(f"[Debug] DeepFace Error: {error}")
        finally:
            self.is_processing_frame = False

    def open_enrollment_dialog(self):
        """
        Nhiệm vụ: Mở popup giao diện đăng ký học sinh mới nếu camera đang hoạt động.
        Input / Output: Không có.
        """
        if not self.is_camera_running:
            return
        EnrollmentDialog(
            parent=self.root,
            camera_capture=self.camera_capture,
            recognizer=self.recognizer,
            log_callback=self.log
        )
