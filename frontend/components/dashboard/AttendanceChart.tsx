/**
 * Component: AttendanceChart
 * Nhiệm vụ: Trực quan hóa xu hướng điểm danh trong 7 ngày gần nhất bằng biểu đồ diện tích (AreaChart).
 * Input: Không có (sử dụng dữ liệu tĩnh trendData và chartConfig cấu hình).
 * Output: JSX render biểu đồ AreaChart tương tác với Tooltip, đường nét mượt mà và dải màu gradient.
 */

'use client'

import React from 'react'
import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from 'recharts'
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart'
import { trendData, chartConfig } from '@/config/dashboard'

export function AttendanceChart() {
  return (
    <section className="mb-5 rounded-xl border border-border/70 bg-card/60 p-5 backdrop-blur-md">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-primary">Weekly performance</p>
          <h2 className="mt-1 text-lg font-semibold tracking-tight">
            Attendance trends over the last 7 days
          </h2>
          <p className="mt-1 text-xs text-muted-foreground">
            Daily attendance activity across all classes
          </p>
        </div>
        <div className="flex items-center gap-4 pt-1 text-xs text-muted-foreground">
          <span className="flex items-center gap-2">
            <span className="size-2 rounded-full bg-chart-1" />
            Present
          </span>
          <span className="flex items-center gap-2">
            <span className="size-2 rounded-full bg-chart-2" />
            Absent
          </span>
        </div>
      </div>
      <ChartContainer config={chartConfig} className="mt-6 h-[260px] w-full">
        <AreaChart accessibilityLayer data={trendData} margin={{ left: -18, right: 8, top: 8 }}>
          <defs>
            <linearGradient id="presentFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--color-present)" stopOpacity={0.3} />
              <stop offset="100%" stopColor="var(--color-present)" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid vertical={false} stroke="var(--border)" strokeDasharray="3 3" />
          <XAxis dataKey="day" tickLine={false} axisLine={false} tickMargin={10} />
          <YAxis tickLine={false} axisLine={false} tickMargin={10} domain={[0, 45]} />
          <ChartTooltip cursor={false} content={<ChartTooltipContent indicator="line" />} />
          <Area
            type="monotone"
            dataKey="present"
            stroke="var(--color-present)"
            strokeWidth={2}
            fill="url(#presentFill)"
            dot={{ r: 3, fill: 'var(--color-present)', strokeWidth: 0 }}
            activeDot={{ r: 5 }}
          />
          <Area
            type="monotone"
            dataKey="absent"
            stroke="var(--color-absent)"
            strokeWidth={1.5}
            fill="transparent"
            strokeDasharray="4 4"
          />
        </AreaChart>
      </ChartContainer>
    </section>
  )
}
