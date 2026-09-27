/**
 * Component: SetupView
 * Nhiệm vụ: Hiển thị màn hình hướng dẫn cài đặt Local AI Setup (Developer Center):
 *           - Cho phép giáo viên / kỹ thuật viên sao chép API Key để đưa vào script Python.
 *           - Hiển thị trạng thái hoạt động trực tuyến (Online) và độ chính xác nhận diện.
 * Input / Output: Không có.
 */

'use client'

import React, { useState } from 'react'
import { Code2, Copy, Wifi } from 'lucide-react'

export function SetupView() {
  const [copied, setCopied] = useState(false)

  const copyKey = async () => {
    await navigator.clipboard?.writeText('sk_live_ai_attendance_demo_key_83b2')
    setCopied(true)
    window.setTimeout(() => setCopied(false), 1800)
  }

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-medium text-primary">Developer center</p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight">Local AI Setup</h1>
        <p className="mt-2 max-w-xl text-sm leading-6 text-muted-foreground">
          Connect your camera to AI Attendance with a Python script running locally.
        </p>
      </div>
      <div className="grid gap-4 lg:grid-cols-[1.35fr_.65fr]">
        <div className="rounded-xl border border-border/70 bg-card/60 p-5 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <Code2 size={17} className="text-muted-foreground" />
            <div>
              <h2 className="text-sm font-semibold">API credentials</h2>
              <p className="text-xs text-muted-foreground">Use this key in your local environment</p>
            </div>
          </div>
          <div className="mt-5 flex items-center gap-2 rounded-md border border-input bg-background/70 p-2 pl-3">
            <code className="min-w-0 flex-1 truncate font-mono text-xs text-muted-foreground">
              sk_live_ai_attendance_••••••••••••••••
            </code>
            <button
              type="button"
              onClick={copyKey}
              className="focus-ring rounded-md bg-primary px-3 py-2 text-xs font-medium text-primary-foreground hover:bg-primary/90"
            >
              <Copy size={13} className="mr-2 inline" />
              {copied ? 'Copied' : 'Copy key'}
            </button>
          </div>
          <p className="mt-3 flex items-center gap-2 text-xs text-muted-foreground">
            <Wifi size={13} className="text-emerald-400" /> Key is active and ready to use
          </p>
        </div>
        <div className="rounded-xl border border-border/70 bg-card/60 p-5 backdrop-blur-md">
          <div className="flex items-center justify-between">
            <p className="text-xs text-muted-foreground">System status</p>
            <span className="flex items-center gap-2 text-xs text-emerald-400">
              <span className="size-1.5 animate-pulse rounded-full bg-emerald-400" />
              Online
            </span>
          </div>
          <p className="mt-8 text-3xl font-semibold tracking-tight">98.7%</p>
          <p className="mt-1 text-xs text-muted-foreground">recognition accuracy</p>
        </div>
      </div>
    </div>
  )
}
