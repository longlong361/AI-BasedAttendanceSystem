"""
Module: client_core.api_service
Nhiệm vụ: Phụ trách giao tiếp mạng HTTP:
          - Gửi vector khuôn mặt tới Next.js API để đối sánh và điểm danh.
          - Gửi thông tin đăng ký học sinh mới trực tiếp lên Supabase Database.
"""

from typing import List, Dict, Any, Tuple, Optional
import requests
from client_core.config import API_UPDATE_STATUS, SUPABASE_URL, SUPABASE_KEY


def send_attendance_vector(vector: List[float], timeout: int = 5) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Nhiệm vụ: Gửi vector đặc trưng khuôn mặt sang Next.js backend để đối chiếu với cơ sở dữ liệu.
    Input:
        vector (List[float]): Vector 512 chiều biểu diễn khuôn mặt.
        timeout (int): Thời gian chờ tối đa cho request (giây), mặc định 5.
    Output:
        Tuple[bool, Optional[Dict[str, Any]]]:
            - bool: True nếu điểm danh thành công (status 200 và success=True).
            - dict: Thông tin học sinh nhận diện được (gồm student_code, name, class_name,...), hoặc None nếu thất bại.
    """
    try:
        response = requests.post(API_UPDATE_STATUS, json={"vector": vector}, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return True, data.get("student", {})
        return False, None
    except requests.exceptions.RequestException:
        return False, None


def enroll_student_to_supabase(
    student_code: str,
    name: str,
    class_name: str,
    school: str,
    face_vector: List[float],
    timeout: int = 10
) -> Tuple[bool, str]:
    """
    Nhiệm vụ: Ghi danh học sinh mới kèm vector khuôn mặt vào bảng students trên Supabase REST API.
    Input:
        student_code (str): Mã số học sinh.
        name (str): Họ và tên học sinh.
        class_name (str): Lớp học.
        school (str): Tên trường học.
        face_vector (List[float]): Vector đặc trưng 512 chiều trích xuất từ camera.
        timeout (int): Thời gian chờ request (giây), mặc định 10.
    Output:
        Tuple[bool, str]:
            - bool: True nếu thêm thành công (mã trạng thái 200 hoặc 201).
            - str: Chuỗi thông báo thành công hoặc nội dung lỗi từ Supabase API.
    """
    payload = {
        "student_code": student_code,
        "name": name,
        "class_name": class_name,
        "school": school,
        "status": "absent",
        "face_vector": face_vector
    }
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    try:
        response = requests.post(SUPABASE_URL, headers=headers, json=payload, timeout=timeout)
        if response.status_code in [200, 201]:
            return True, "Enrolled successfully"
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)
