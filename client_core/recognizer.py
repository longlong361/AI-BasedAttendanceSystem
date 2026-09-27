"""
Module: client_core.recognizer
Nhiệm vụ: Trích xuất đặc trưng khuôn mặt (Embedding Vector 512 chiều) và kiểm tra mặt thật/giả
          sử dụng mô hình DeepFace (FaceNet512, backend MTCNN, tích hợp mạng FasNet Anti-Spoofing).
"""

from typing import List, Dict, Any, Optional
from deepface import DeepFace


class FaceRecognizer:
    def __init__(self, model_name: str = "Facenet512", detector_backend: str = "mtcnn"):
        """
        Nhiệm vụ: Khởi tạo cấu hình cho bộ nhận diện khuôn mặt.
        Input:
            model_name (str): Tên mô hình nhận diện (mặc định là 'Facenet512').
            detector_backend (str): Backend phát hiện khuôn mặt (mặc định là 'mtcnn').
        """
        self.model_name = model_name
        self.detector_backend = detector_backend

    def extract_features(self, frame) -> Optional[List[Dict[str, Any]]]:
        """
        Nhiệm vụ: Phát hiện khuôn mặt trong khung hình, kiểm tra tính xác thực (FasNet Anti-spoofing)
                  và trích xuất vector embedding 512 chiều.
        Input:
            frame (np.ndarray): Khung hình BGR từ camera.
        Output:
            Optional[List[Dict[str, Any]]]:
                - Danh sách các khuôn mặt phát hiện được, mỗi phần tử gồm:
                    - 'is_real' (bool): True nếu là người thật, False nếu là ảnh/màn hình giả mạo.
                    - 'embedding' (List[float]): Vector 512 chiều biểu diễn khuôn mặt.
                    - 'facial_area' (dict): Tọa độ vùng mặt (x, y, w, h).
                - Trả về None hoặc rỗng nếu không tìm thấy khuôn mặt (bắt lỗi ValueError từ DeepFace).
        """
        try:
            results = DeepFace.represent(
                img_path=frame,
                model_name=self.model_name,
                enforce_detection=True,
                detector_backend=self.detector_backend,
                anti_spoofing=True
            )
            return results
        except ValueError:
            # DeepFace bắn ra ValueError khi không phát hiện thấy khuôn mặt nào trong frame
            return None
        except Exception as error:
            print(f"[Debug] DeepFace Error: {error}")
            return None
