/**
 * Component: Sidebar
 * Nhiệm vụ: Thanh điều hướng bên trái giao diện (hỗ trợ responsive mobile/desktop).
 * Input:
 *   - active (string): Tab đang được chọn ('Overview' hoặc 'Installation Guide').
 *   - onChange (function): Hàm callback nhận giá trị tab mới khi người dùng click chọn.
 * Output: JSX render thanh điều hướng, logo và thông tin tài khoản quản trị viên.
 */

'use client'

import React from 'react'
import { LogOut, MoreHorizontal } from 'lucide-react'
import { navItems } from '@/config/dashboard'

interface SidebarProps {
  active: string
  onChange: (value: string) => void
}

export function Sidebar({ active, onChange }: SidebarProps) {
  return (
    <aside className="fixed inset-y-0 left-0 z-10 flex w-60 flex-col border-r border-border/70 bg-sidebar/80 px-3 py-4 backdrop-blur-md max-md:relative max-md:w-full max-md:flex-row max-md:items-center max-md:justify-between max-md:border-b max-md:border-r-0">
      <div className="space-y-8">
        <div className="flex items-center gap-3 px-3 py-2">
          <div className="flex size-7 items-center justify-center rounded-md bg-primary text-xs font-bold text-primary-foreground">
            A
          </div>
          <span className="text-sm font-semibold tracking-tight">AI Attendance</span>
        </div>
        <nav aria-label="Main navigation" className="space-y-1">
          {navItems.map(({ label, icon: Icon }) => (
            <button
              key={label}
              type="button"
              onClick={() => onChange(label)}
              className={`focus-ring flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm ${
                active === label
                  ? 'bg-muted text-foreground'
                  : 'text-muted-foreground hover:bg-muted/60 hover:text-foreground'
              }`}
            >
              <Icon size={16} strokeWidth={1.8} />
              <span className="max-md:hidden">{label}</span>
            </button>
          ))}
        </nav>
      </div>
      <div className="space-y-3 max-md:flex max-md:items-center max-md:gap-3 max-md:space-y-0">
        <div className="flex items-center gap-3 rounded-md px-3 py-2 max-md:hidden">
          <div className="flex size-7 items-center justify-center rounded-full bg-muted text-[10px] font-semibold">
            NL
          </div>
          <div className="min-w-0">
            <p className="truncate text-xs font-medium">Nguyễn Linh</p>
            <p className="truncate text-[11px] text-muted-foreground">Administrator</p>
          </div>
          <MoreHorizontal className="ml-auto text-muted-foreground" size={15} />
        </div>
        <button
          type="button"
          className="focus-ring flex items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground hover:text-foreground"
        >
          <LogOut size={16} />
          <span className="max-md:hidden">Log out</span>
        </button>
      </div>
    </aside>
  )
}
