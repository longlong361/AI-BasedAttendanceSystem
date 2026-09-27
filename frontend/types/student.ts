/**
 * Module: frontend/types/student.ts
 * Nhiệm vụ: Khai báo cấu trúc kiểu dữ liệu của đối tượng học sinh (Student)
 *           dùng chung cho các components trong giao diện Dashboard.
 */

export type Student = {
  id: string
  name: string
  className: string
  school: string
  status: 'present' | 'absent'
  initials: string
}
