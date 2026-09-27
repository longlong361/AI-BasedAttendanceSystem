/**
 * Module: frontend/config/dashboard.ts
 * Nhiệm vụ: Quản lý các cấu hình tĩnh, dữ liệu mẫu biểu đồ và danh mục điều hướng Sidebar.
 */

import { BookOpen, LayoutDashboard } from 'lucide-react'
import type { ChartConfig } from '@/components/ui/chart'

// Dữ liệu mẫu biểu đồ xu hướng điểm danh trong 7 ngày
export const trendData = [
  { day: 'Mon', present: 38, absent: 7 },
  { day: 'Tue', present: 41, absent: 4 },
  { day: 'Wed', present: 39, absent: 6 },
  { day: 'Thu', present: 43, absent: 2 },
  { day: 'Fri', present: 40, absent: 5 },
  { day: 'Sat', present: 42, absent: 3 },
  { day: 'Sun', present: 40, absent: 5 },
]

// Cấu hình nhãn và biến màu CSS cho biểu đồ Recharts
export const chartConfig = {
  present: { label: 'Present', color: 'var(--chart-1)' },
  absent: { label: 'Absent', color: 'var(--chart-2)' },
} satisfies ChartConfig

// Danh sách các mục điều hướng trên thanh Sidebar
export const navItems = [
  { label: 'Overview', icon: LayoutDashboard },
  { label: 'Installation Guide', icon: BookOpen },
]
