/**
 * Hook: useAttendance
 * Nhiệm vụ: Đóng gói toàn bộ logic quản lý trạng thái điểm danh và tương tác API:
 *           - Kiểm tra xác thực token từ URL parameters hoặc hash.
 *           - Tự động polling danh sách học sinh từ backend mỗi 3 giây.
 *           - Thực hiện các thao tác: Reset trạng thái toàn bộ học sinh về 'absent' và Xóa học sinh.
 *           - Quản lý trạng thái thông báo Popup (Toast Notification).
 * Input: Không có.
 * Output:
 *   - studentList (Student[]): Danh sách học sinh cập nhật liên tục.
 *   - isAuthChecking (boolean): Cờ kiểm tra xác thực ban đầu.
 *   - toast ({ message, type } | null): Thông tin thông báo toast.
 *   - handleReset (function): Hàm gọi API reset điểm danh.
 *   - handleDelete (function): Hàm gọi API xóa học sinh.
 *   - fetchStudents (function): Hàm tải dữ liệu thủ công.
 */

'use client'

import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import { Student } from '@/types/student'

const API_STUDENT_LIST = '/api/students'

export function useAttendance() {
  const [studentList, setStudentList] = useState<Student[]>([])
  const [isAuthChecking, setIsAuthChecking] = useState(true)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  const showToast = useCallback((message: string, type: 'success' | 'error') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3000)
  }, [])

  // Kiểm tra access token từ query params hoặc hash URL khi mở trang
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    let tokenFromUrl = urlParams.get('access_token')

    if (!tokenFromUrl && window.location.hash.includes('access_token=')) {
      const hashParams = new URLSearchParams(window.location.hash.substring(1))
      tokenFromUrl = hashParams.get('access_token')
    }

    if (tokenFromUrl) {
      localStorage.setItem('access_token', tokenFromUrl)
      window.history.replaceState({}, document.title, window.location.pathname)
      setIsAuthChecking(false)
      return
    }

    setIsAuthChecking(false)
  }, [])

  const fetchStudents = useCallback(async (signal?: AbortSignal) => {
    try {
      const response = await axios.get<{ success: boolean; data: any[] }>(API_STUDENT_LIST, { signal })
      if (response.data.success && Array.isArray(response.data.data)) {
        const mappedData: Student[] = response.data.data.map((item: any) => ({
          id: item.student_code || item.id,
          name: item.name || 'Unknown',
          className: item.class_name || 'N/A',
          school: item.school || 'N/A',
          status: item.status || 'absent',
          initials: item.name ? item.name.substring(0, 2).toUpperCase() : '??',
        }))
        setStudentList(mappedData)
      }
    } catch (error) {
      if (!axios.isCancel(error)) console.error(error)
    }
  }, [])

  // Polling danh sách học sinh mỗi 3 giây
  useEffect(() => {
    if (isAuthChecking) return

    const abortController = new AbortController()
    fetchStudents(abortController.signal)

    const pollingInterval = setInterval(() => fetchStudents(), 3000)
    return () => {
      clearInterval(pollingInterval)
      abortController.abort()
    }
  }, [isAuthChecking, fetchStudents])

  const handleReset = async () => {
    try {
      const res = await axios.post('/api/students/reset')
      if (res.data.success) {
        showToast('All attendance records reset to absent.', 'success')
        fetchStudents()
      } else {
        showToast('Failed to reset attendance.', 'error')
      }
    } catch (error) {
      showToast('Error connecting to server.', 'error')
    }
  }

  const handleDelete = async (id: string) => {
    try {
      const res = await axios.delete(`/api/students/${id}`)
      if (res.data.success) {
        showToast('Student deleted successfully.', 'success')
        fetchStudents()
      } else {
        showToast('Failed to delete student.', 'error')
      }
    } catch (error) {
      showToast('Error connecting to server.', 'error')
    }
  }

  return {
    studentList,
    isAuthChecking,
    toast,
    handleReset,
    handleDelete,
    fetchStudents,
  }
}
