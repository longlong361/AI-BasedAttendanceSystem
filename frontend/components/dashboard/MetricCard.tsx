/**
 * Component: MetricCard
 * Nhiệm vụ: Hiển thị một thẻ chỉ số thống kê (Tổng học sinh, Đã có mặt, Vắng mặt).
 * Input:
 *   - label (string): Tiêu đề chỉ số (ví dụ: 'Total students').
 *   - value (string): Giá trị định lượng (ví dụ: '45').
 *   - detail (string): Mô tả phụ hoặc tỷ lệ phần trăm (ví dụ: '95.5% attendance rate').
 *   - icon (LucideIcon): Icon biểu diễn chỉ số.
 *   - accent ('cyan' | 'violet' | 'rose'): Tông màu viền trên của thẻ card.
 * Output: JSX render thẻ Card với phong cách giao diện hiện đại (backdrop blur, gradient line).
 */

import React from 'react'
import { LucideIcon } from 'lucide-react'

interface MetricCardProps {
  label: string
  value: string
  detail: string
  icon: LucideIcon
  accent: 'cyan' | 'violet' | 'rose'
}

export function MetricCard({ label, value, detail, icon: Icon, accent }: MetricCardProps) {
  const accentClass = {
    cyan: 'before:bg-chart-1',
    violet: 'before:bg-chart-2',
    rose: 'before:bg-chart-3',
  }[accent]

  return (
    <div
      className={`metric-card relative overflow-hidden rounded-xl border border-border/70 bg-card/65 p-4 backdrop-blur-md before:absolute before:inset-x-0 before:top-0 before:h-px ${accentClass}`}
    >
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">{label}</p>
        <Icon size={16} className="text-muted-foreground" />
      </div>
      <p className="mt-3 text-2xl font-semibold tracking-tight">{value}</p>
      <p className="mt-2 text-xs text-muted-foreground">{detail}</p>
    </div>
  )
}
