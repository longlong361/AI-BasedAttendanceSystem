"""
Module: client_core.camera
Nhiệm vụ: Quản lý thiết bị ghi hình (Webcam), dò tìm các camera khả dụng và khởi tạo đối tượng VideoCapture.
"""

import cv2
from typing import List, Union


def detect_available_cameras(max_to_test: int = 5) -> List[str]:
    """
    Nhiệm vụ: Quét các chỉ số camera (từ 0 đến max_to_test - 1) để tìm các thiết bị đang hoạt động.
              Lưu ý: Không dùng cv2.CAP_DSHOW vì có thể gây hiện tượng rách hình (artifacting) với virtual camera (như DroidCam).
    Input:
        max_to_test (int): Số lượng cổng camera tối đa cần kiểm tra (mặc định là 5).
    Output:
        List[str]: Danh sách các chỉ số camera hợp lệ dưới dạng chuỗi, ví dụ: ['0', '1'].
    """
    available_cameras = []
    for camera_index in range(max_to_test):
        capture = cv2.VideoCapture(camera_index)
        if capture.isOpened():
            available_cameras.append(str(camera_index))
            capture.release()
    return available_cameras


def open_camera(camera_index: Union[int, str]) -> cv2.VideoCapture:
    """
    Nhiệm vụ: Khởi tạo kết nối đến camera được chỉ định.
    Input:
        camera_index (Union[int, str]): Chỉ số camera (ví dụ: 0 hoặc '0').
    Output:
        cv2.VideoCapture: Đối tượng luồng camera từ OpenCV.
    """
    idx = int(camera_index) if str(camera_index).isdigit() else camera_index
    return cv2.VideoCapture(idx)
