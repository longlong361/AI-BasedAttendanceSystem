/**
 * Component: AttendanceTable
 * Nhiệm vụ: Bảng danh sách học sinh theo thời gian thực:
 *           - Cho phép tìm kiếm nhanh theo Tên hoặc Lớp học.
 *           - Cung cấp nút 'Reset All' để đặt lại trạng thái toàn bộ học sinh về 'absent'.
 *           - Cung cấp nút xóa từng học sinh khỏi cơ sở dữ liệu.
 * Input:
 *   - studentList (Student[]): Mảng danh sách học sinh đã được đồng bộ từ backend.
 *   - onReset (function): Hàm kích hoạt reset trạng thái điểm danh.
 *   - onDelete (function): Hàm kích hoạt xóa học sinh theo ID.
 * Output: JSX render bảng điểm danh chuẩn responsive, có thanh cuộn ngang khi màn hình nhỏ.
 */

'use client'

import React, { useState, useMemo } from 'react'
import { Search, RotateCcw, Trash2 } from 'lucide-react'
import { Student } from '@/types/student'

interface AttendanceTableProps {
  studentList: Student[]
  onReset: () => Promise<void> | void
  onDelete: (id: string) => Promise<void> | void
}

export function AttendanceTable({ studentList, onReset, onDelete }: AttendanceTableProps) {
  const [query, setQuery] = useState('')
  const [isResetting, setIsResetting] = useState(false)

  const filteredStudents = useMemo(
    () =>
      studentList.filter((student) =>
        `${student.name} ${student.className}`.toLowerCase().includes(query.toLowerCase())
      ),
    [studentList, query]
  )

  const handleReset = async () => {
    setIsResetting(true)
    await onReset()
    setIsResetting(false)
  }

  return (
    <section className="overflow-hidden rounded-xl border border-border/70 bg-card/60 backdrop-blur-md">
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-border/70 px-4 py-3">
        <div>
          <h2 className="text-sm font-semibold">Attendance overview</h2>
          <p className="mt-1 text-xs text-muted-foreground">Today&apos;s attendance</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search
              size={14}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
            />
            <input
              className="focus-ring w-52 rounded-md border border-input bg-background/70 py-2 pl-8 pr-3 text-xs outline-none placeholder:text-muted-foreground"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search students"
              aria-label="Search students"
            />
          </div>
          <button
            onClick={handleReset}
            disabled={isResetting}
            className="focus-ring flex items-center gap-2 rounded-md bg-secondary px-3 py-2 text-xs font-medium text-secondary-foreground hover:bg-secondary/80 disabled:opacity-50"
          >
            <RotateCcw size={13} className={isResetting ? 'animate-spin' : ''} />{' '}
            {isResetting ? 'Resetting...' : 'Reset All'}
          </button>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[680px] text-left">
          <thead>
            <tr className="border-b border-border text-[10px] uppercase tracking-wider text-muted-foreground">
              <th className="px-4 py-3 font-medium">No.</th>
              <th className="px-2 py-3 font-medium">Student</th>
              <th className="px-2 py-3 font-medium">Class</th>
              <th className="px-2 py-3 font-medium">School</th>
              <th className="px-4 py-3 text-right font-medium">Status</th>
              <th className="px-4 py-3 text-right font-medium">Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredStudents.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-sm text-muted-foreground">
                  No students found.
                </td>
              </tr>
            ) : (
              filteredStudents.map(({ id, name, className, school, status, initials }) => (
                <tr key={id} className="table-row-hover border-b border-border/70 last:border-0">
                  <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{id}</td>
                  <td className="px-2 py-3">
                    <div className="flex items-center gap-3">
                      <div className="flex size-7 items-center justify-center rounded-full bg-muted text-[10px] font-medium text-muted-foreground">
                        {initials}
                      </div>
                      <span className="text-sm">{name}</span>
                    </div>
                  </td>
                  <td className="px-2 py-3 font-mono text-xs text-muted-foreground">{className}</td>
                  <td className="px-2 py-3 text-xs text-muted-foreground">{school}</td>
                  <td className="px-4 py-3 text-right">
                    <span
                      className={`inline-flex rounded-full px-2 py-1 text-[11px] font-medium ${
                        status === 'present' ? 'status-present' : 'status-absent'
                      }`}
                    >
                      {status === 'present' ? 'Present' : 'Absent'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => {
                        if (window.confirm(`Are you sure you want to delete ${name}?`)) onDelete(id)
                      }}
                      className="p-1.5 text-muted-foreground hover:text-rose-500 rounded-md hover:bg-muted"
                    >
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}
