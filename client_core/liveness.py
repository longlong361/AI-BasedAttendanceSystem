"""
Module: client_core.liveness
Nhiệm vụ: Phân tích các mốc khuôn mặt (Face Landmarks) thông qua MediaPipe để kiểm tra tính sống động (Liveness Detection):
          - Chống giả mạo ảnh bằng cách nghiêng điện thoại (Head Pose Angle <= 15 độ).
          - Phát hiện hành vi chớp mắt thật qua tỷ số co dãn mắt EAR (Eye Aspect Ratio).
"""

import math
from typing import List, Tuple, Any
import mediapipe as mp
from client_core.config import MODEL_PATH, ensure_model_downloaded

# Chỉ số các điểm mốc (landmarks) tương ứng với mắt trái và mắt phải theo chuẩn MediaPipe
LEFT_EYE_LANDMARKS = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_LANDMARKS = [362, 385, 387, 263, 373, 380]


class LivenessDetector:
    def __init__(self, model_path: str = MODEL_PATH):
        """
        Nhiệm vụ: Khởi tạo mô hình MediaPipe FaceLandmarker từ file task.
        Input:
            model_path (str): Đường dẫn đến file face_landmarker.task.
        Output:
            Không có (khởi tạo instance).
        """
        ensure_model_downloaded()
        base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
        options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=1,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False
        )
        self.landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(options)

    def detect_landmarks(self, rgb_frame: Any):
        """
        Nhiệm vụ: Trích xuất tọa độ các điểm mốc khuôn mặt từ khung hình RGB.
        Input:
            rgb_frame (np.ndarray): Khung hình đã chuyển sang hệ màu RGB.
        Output:
            Danh sách face_landmarks (hoặc None nếu không phát hiện khuôn mặt).
        """
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = self.landmarker.detect(mp_image)
        return detection_result.face_landmarks

    def check_head_tilt(self, face_landmarks: Any) -> Tuple[bool, float]:
        """
        Nhiệm vụ: Tính toán góc nghiêng của khuôn mặt (giữa mốc mắt phải [263] và mắt trái [33]).
                  Ngăn chặn hành vi dùng ảnh điện thoại lắc/nghiêng để qua mặt hệ thống.
        Input:
            face_landmarks: Tập hợp các điểm mốc của khuôn mặt được phát hiện.
        Output:
            Tuple[bool, float]: (is_head_straight, angle_degrees)
                - is_head_straight: True nếu góc nghiêng <= 15 độ, False nếu bị nghiêng quá mức.
                - angle_degrees: Góc nghiêng tính bằng độ.
        """
        dx = face_landmarks[263].x - face_landmarks[33].x
        dy = face_landmarks[263].y - face_landmarks[33].y
        angle = math.degrees(math.atan2(abs(dy), abs(dx)))
        is_straight = angle <= 15
        return is_straight, angle

    def calculate_ear(self, face_landmarks: Any, eye_indices: List[int], frame_width: int, frame_height: int) -> float:
        """
        Nhiệm vụ: Tính toán tỷ số co dãn mắt EAR (Eye Aspect Ratio) dựa trên khoảng cách Euclid.
        Input:
            face_landmarks: Mốc khuôn mặt từ MediaPipe.
            eye_indices (List[int]): Danh sách 6 chỉ số tương ứng với các điểm quanh mắt.
            frame_width (int): Chiều rộng khung hình (pixels).
            frame_height (int): Chiều cao khung hình (pixels).
        Output:
            float: Tỷ số EAR (mắt mở giá trị cao, mắt nhắm giá trị thấp).
        """
        pts = [(face_landmarks[idx].x * frame_width, face_landmarks[idx].y * frame_height) for idx in eye_indices]
        v1 = math.hypot(pts[1][0] - pts[5][0], pts[1][1] - pts[5][1])
        v2 = math.hypot(pts[2][0] - pts[4][0], pts[2][1] - pts[4][1])
        h = math.hypot(pts[0][0] - pts[3][0], pts[0][1] - pts[3][1])
        return (v1 + v2) / (2.0 * h) if h != 0 else 0.0

    def calculate_average_ear(self, face_landmarks: Any, frame_width: int, frame_height: int) -> float:
        """
        Nhiệm vụ: Tính trung bình cộng EAR của cả hai mắt (mắt trái và mắt phải).
        Input:
            face_landmarks: Mốc khuôn mặt.
            frame_width (int): Chiều rộng khung hình.
            frame_height (int): Chiều cao khung hình.
        Output:
            float: Giá trị trung bình EAR của cả 2 mắt.
        """
        left_ear = self.calculate_ear(face_landmarks, LEFT_EYE_LANDMARKS, frame_width, frame_height)
        right_ear = self.calculate_ear(face_landmarks, RIGHT_EYE_LANDMARKS, frame_width, frame_height)
        return (left_ear + right_ear) / 2.0
