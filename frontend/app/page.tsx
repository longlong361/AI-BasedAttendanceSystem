/**
 * Page: Attendance Dashboard (Main Entry View)
 * Nhiệm vụ: Trang giao diện chính của hệ thống quản lý điểm danh thông minh AI:
 *           - Điều phối và hiển thị các module: Thanh điều hướng (Sidebar), các thẻ chỉ số (MetricCard),
 *             Biểu đồ xu hướng (AttendanceChart), Bảng danh sách (AttendanceTable) và Màn hình cài đặt (SetupView).
 *           - Sử dụng custom hook useAttendance để tự động đồng bộ hóa dữ liệu thời gian thực.
 * Input: Không có (Next.js App Router Page).
 * Output: JSX render toàn bộ Dashboard theo phong cách hiện đại (Mesh gradient background, Glassmorphism).
 */

'use client'

import { useState } from 'react'
import { CalendarDays, Check, ChevronDown, Users, X } from 'lucide-react'
import { Sidebar } from '@/components/dashboard/Sidebar'
import { MetricCard } from '@/components/dashboard/MetricCard'
import { AttendanceChart } from '@/components/dashboard/AttendanceChart'
import { AttendanceTable } from '@/components/dashboard/AttendanceTable'
import { SetupView } from '@/components/dashboard/SetupView'
import { useAttendance } from '@/hooks/useAttendance'

export default function Page() {
  const [active, setActive] = useState('Overview')
  const { studentList, isAuthChecking, toast, handleReset, handleDelete } = useAttendance()

  if (isAuthChecking) {
    return (
      <div className="flex h-screen items-center justify-center text-sm text-muted-foreground">
        Authenticating...
      </div>
    )
  }

  // Tính toán các chỉ số thống kê tổng hợp từ danh sách học sinh
  const totalStudents = studentList.length
  const presentToday = studentList.filter((s) => s.status === 'present').length
  const absentToday = totalStudents - presentToday
  const presentRate = totalStudents > 0 ? ((presentToday / totalStudents) * 100).toFixed(1) : '0.0'
  const absentRate = totalStudents > 0 ? ((absentToday / totalStudents) * 100).toFixed(1) : '0.0'

  const date = new Intl.DateTimeFormat('en-US', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(new Date())

  return (
    <main className="mesh-background min-h-screen relative">
      {/* Thanh điều hướng bên trái */}
      <Sidebar active={active} onChange={setActive} />

      <div className="ml-60 min-h-screen max-md:ml-0">
        <div className="mx-auto max-w-6xl px-8 py-8 max-md:px-4">
          {/* Header chào mừng và ngày tháng */}
          <header className="mb-8 flex items-start justify-between gap-4">
            <div>
              <p className="text-xs text-muted-foreground">{date}</p>
              <h1 className="mt-2 text-2xl font-semibold tracking-tight">Good morning, Linh</h1>
              <p className="mt-1 text-sm text-muted-foreground">
                Here&apos;s your attendance intelligence for today.
              </p>
            </div>
            <button
              type="button"
              className="focus-ring hidden items-center gap-2 rounded-md border border-border px-3 py-2 text-xs text-muted-foreground hover:bg-muted md:flex"
            >
              <CalendarDays size={14} /> Today <ChevronDown size={13} />
            </button>
          </header>

          {/* Nội dung chính theo tab được chọn */}
          {active === 'Overview' ? (
            <>
              {/* Thẻ chỉ số tổng hợp */}
              <div className="mb-5 grid gap-3 sm:grid-cols-3">
                <MetricCard
                  label="Total students"
                  value={totalStudents.toString()}
                  detail="Across the system"
                  icon={Users}
                  accent="cyan"
                />
                <MetricCard
                  label="Present today"
                  value={presentToday.toString()}
                  detail={`${presentRate}% attendance rate`}
                  icon={Check}
                  accent="violet"
                />
                <MetricCard
                  label="Absent today"
                  value={absentToday.toString()}
                  detail={`${absentRate}% of total`}
                  icon={X}
                  accent="rose"
                />
              </div>

              {/* Biểu đồ xu hướng điểm danh */}
              <AttendanceChart />

              {/* Bảng danh sách học sinh và thao tác */}
              <AttendanceTable
                studentList={studentList}
                onReset={handleReset}
                onDelete={handleDelete}
              />
            </>
          ) : (
            <SetupView />
          )}
        </div>
      </div>

      {/* Thông báo Toast dạng popup ở góc dưới màn hình */}
      {toast && (
        <div
          className={`fixed bottom-6 right-6 z-50 flex items-center gap-2 rounded-lg px-4 py-3 shadow-lg backdrop-blur-md border animate-in slide-in-from-bottom-5 fade-in duration-300 ${
            toast.type === 'success'
              ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500'
              : 'bg-rose-500/10 border-rose-500/20 text-rose-500'
          }`}
        >
          {toast.type === 'success' ? <Check size={16} /> : <X size={16} />}
          <p className="text-sm font-medium">{toast.message}</p>
        </div>
      )}
    </main>
  )
}
