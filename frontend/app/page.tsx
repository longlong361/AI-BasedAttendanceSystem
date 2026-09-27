'use client'

import { useMemo, useState, useEffect } from 'react'
import { BookOpen, CalendarDays, Check, ChevronDown, Code2, Copy, LayoutDashboard, LogOut, MoreHorizontal, Search, Users, Wifi, X, Trash2, RotateCcw } from 'lucide-react'
import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from 'recharts'
import { ChartContainer, ChartTooltip, ChartTooltipContent, type ChartConfig } from '@/components/ui/chart'
import axios from 'axios'

const API_STUDENT_LIST = '/api/students'

type Student = {
  id: string
  name: string
  className: string
  school: string
  status: 'present' | 'absent'
  initials: string
}

const trendData = [
  { day: 'Mon', present: 38, absent: 7 }, { day: 'Tue', present: 41, absent: 4 }, { day: 'Wed', present: 39, absent: 6 }, { day: 'Thu', present: 43, absent: 2 }, { day: 'Fri', present: 40, absent: 5 }, { day: 'Sat', present: 42, absent: 3 }, { day: 'Sun', present: 40, absent: 5 },
]
const chartConfig = { present: { label: 'Present', color: 'var(--chart-1)' }, absent: { label: 'Absent', color: 'var(--chart-2)' } } satisfies ChartConfig
const navItems = [{ label: 'Overview', icon: LayoutDashboard }, { label: 'Installation Guide', icon: BookOpen }]

function Sidebar({ active, onChange }: { active: string; onChange: (value: string) => void }) {
  return <aside className="fixed inset-y-0 left-0 z-10 flex w-60 flex-col border-r border-border/70 bg-sidebar/80 px-3 py-4 backdrop-blur-md max-md:relative max-md:w-full max-md:flex-row max-md:items-center max-md:justify-between max-md:border-b max-md:border-r-0"><div className="space-y-8"><div className="flex items-center gap-3 px-3 py-2"><div className="flex size-7 items-center justify-center rounded-md bg-primary text-xs font-bold text-primary-foreground">A</div><span className="text-sm font-semibold tracking-tight">AI Attendance</span></div><nav aria-label="Main navigation" className="space-y-1">{navItems.map(({ label, icon: Icon }) => <button key={label} type="button" onClick={() => onChange(label)} className={`focus-ring flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm ${active === label ? 'bg-muted text-foreground' : 'text-muted-foreground hover:bg-muted/60 hover:text-foreground'}`}><Icon size={16} strokeWidth={1.8} /><span className="max-md:hidden">{label}</span></button>)}</nav></div><div className="space-y-3 max-md:flex max-md:items-center max-md:gap-3 max-md:space-y-0"><div className="flex items-center gap-3 rounded-md px-3 py-2 max-md:hidden"><div className="flex size-7 items-center justify-center rounded-full bg-muted text-[10px] font-semibold">NL</div><div className="min-w-0"><p className="truncate text-xs font-medium">Nguyễn Linh</p><p className="truncate text-[11px] text-muted-foreground">Administrator</p></div><MoreHorizontal className="ml-auto text-muted-foreground" size={15} /></div><button type="button" className="focus-ring flex items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground hover:text-foreground"><LogOut size={16} /><span className="max-md:hidden">Log out</span></button></div></aside>
}

function Metric({ label, value, detail, icon: Icon, accent }: { label: string; value: string; detail: string; icon: typeof Users; accent: 'cyan' | 'violet' | 'rose' }) {
  const accentClass = { cyan: 'before:bg-chart-1', violet: 'before:bg-chart-2', rose: 'before:bg-chart-3' }[accent]
  return <div className={`metric-card relative overflow-hidden rounded-xl border border-border/70 bg-card/65 p-4 backdrop-blur-md before:absolute before:inset-x-0 before:top-0 before:h-px ${accentClass}`}><div className="flex items-center justify-between"><p className="text-xs text-muted-foreground">{label}</p><Icon size={16} className="text-muted-foreground" /></div><p className="mt-3 text-2xl font-semibold tracking-tight">{value}</p><p className="mt-2 text-xs text-muted-foreground">{detail}</p></div>
}

function AttendanceChart() {
  return <section className="mb-5 rounded-xl border border-border/70 bg-card/60 p-5 backdrop-blur-md"><div className="flex flex-wrap items-start justify-between gap-4"><div><p className="text-xs font-medium text-primary">Weekly performance</p><h2 className="mt-1 text-lg font-semibold tracking-tight">Attendance trends over the last 7 days</h2><p className="mt-1 text-xs text-muted-foreground">Daily attendance activity across all classes</p></div><div className="flex items-center gap-4 pt-1 text-xs text-muted-foreground"><span className="flex items-center gap-2"><span className="size-2 rounded-full bg-chart-1" />Present</span><span className="flex items-center gap-2"><span className="size-2 rounded-full bg-chart-2" />Absent</span></div></div><ChartContainer config={chartConfig} className="mt-6 h-[260px] w-full"><AreaChart accessibilityLayer data={trendData} margin={{ left: -18, right: 8, top: 8 }}><defs><linearGradient id="presentFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="var(--color-present)" stopOpacity={0.3} /><stop offset="100%" stopColor="var(--color-present)" stopOpacity={0.02} /></linearGradient></defs><CartesianGrid vertical={false} stroke="var(--border)" strokeDasharray="3 3" /><XAxis dataKey="day" tickLine={false} axisLine={false} tickMargin={10} /><YAxis tickLine={false} axisLine={false} tickMargin={10} domain={[0, 45]} /><ChartTooltip cursor={false} content={<ChartTooltipContent indicator="line" />} /><Area type="monotone" dataKey="present" stroke="var(--color-present)" strokeWidth={2} fill="url(#presentFill)" dot={{ r: 3, fill: 'var(--color-present)', strokeWidth: 0 }} activeDot={{ r: 5 }} /><Area type="monotone" dataKey="absent" stroke="var(--color-absent)" strokeWidth={1.5} fill="transparent" strokeDasharray="4 4" /></AreaChart></ChartContainer></section>
}

function AttendanceTable({ studentList, onReset, onDelete }: { studentList: Student[], onReset: () => void, onDelete: (id: string) => void }) {
  const [query, setQuery] = useState('')
  const [isResetting, setIsResetting] = useState(false)

  const filteredStudents = useMemo(
    () => studentList.filter((student) => `${student.name} ${student.className}`.toLowerCase().includes(query.toLowerCase())),
    [studentList, query]
  )

  const handleReset = async () => {
    setIsResetting(true)
    await onReset()
    setIsResetting(false)
  }

  return <section className="overflow-hidden rounded-xl border border-border/70 bg-card/60 backdrop-blur-md"><div className="flex flex-wrap items-center justify-between gap-4 border-b border-border/70 px-4 py-3"><div><h2 className="text-sm font-semibold">Attendance overview</h2><p className="mt-1 text-xs text-muted-foreground">Today&apos;s attendance</p></div><div className="flex items-center gap-3"><div className="relative"><Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" /><input className="focus-ring w-52 rounded-md border border-input bg-background/70 py-2 pl-8 pr-3 text-xs outline-none placeholder:text-muted-foreground" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search students" aria-label="Search students" /></div><button onClick={handleReset} disabled={isResetting} className="focus-ring flex items-center gap-2 rounded-md bg-secondary px-3 py-2 text-xs font-medium text-secondary-foreground hover:bg-secondary/80 disabled:opacity-50"><RotateCcw size={13} className={isResetting ? "animate-spin" : ""} /> {isResetting ? "Resetting..." : "Reset All"}</button></div></div><div className="overflow-x-auto"><table className="w-full min-w-[680px] text-left"><thead><tr className="border-b border-border text-[10px] uppercase tracking-wider text-muted-foreground"><th className="px-4 py-3 font-medium">No.</th><th className="px-2 py-3 font-medium">Student</th><th className="px-2 py-3 font-medium">Class</th><th className="px-2 py-3 font-medium">School</th><th className="px-4 py-3 text-right font-medium">Status</th><th className="px-4 py-3 text-right font-medium">Action</th></tr></thead><tbody>{filteredStudents.length === 0 ? <tr><td colSpan={6} className="px-4 py-8 text-center text-sm text-muted-foreground">No students found.</td></tr> : filteredStudents.map(({ id, name, className, school, status, initials }) => <tr key={id} className="table-row-hover border-b border-border/70 last:border-0"><td className="px-4 py-3 font-mono text-xs text-muted-foreground">{id}</td><td className="px-2 py-3"><div className="flex items-center gap-3"><div className="flex size-7 items-center justify-center rounded-full bg-muted text-[10px] font-medium text-muted-foreground">{initials}</div><span className="text-sm">{name}</span></div></td><td className="px-2 py-3 font-mono text-xs text-muted-foreground">{className}</td><td className="px-2 py-3 text-xs text-muted-foreground">{school}</td><td className="px-4 py-3 text-right"><span className={`inline-flex rounded-full px-2 py-1 text-[11px] font-medium ${status === 'present' ? 'status-present' : 'status-absent'}`}>{status === 'present' ? 'Present' : 'Absent'}</span></td><td className="px-4 py-3 text-right"><button onClick={() => { if(window.confirm(`Are you sure you want to delete ${name}?`)) onDelete(id); }} className="p-1.5 text-muted-foreground hover:text-rose-500 rounded-md hover:bg-muted"><Trash2 size={14} /></button></td></tr>)}</tbody></table></div></section>
}

function SetupView() {
  const [copied, setCopied] = useState(false)
  const copyKey = async () => { await navigator.clipboard?.writeText('sk_live_ai_attendance_demo_key_83b2'); setCopied(true); window.setTimeout(() => setCopied(false), 1800) }
  return <div className="space-y-6"><div><p className="text-xs font-medium text-primary">Developer center</p><h1 className="mt-2 text-2xl font-semibold tracking-tight">Local AI Setup</h1><p className="mt-2 max-w-xl text-sm leading-6 text-muted-foreground">Connect your camera to AI Attendance with a Python script running locally.</p></div><div className="grid gap-4 lg:grid-cols-[1.35fr_.65fr]"><div className="rounded-xl border border-border/70 bg-card/60 p-5 backdrop-blur-md"><div className="flex items-center gap-3"><Code2 size={17} className="text-muted-foreground" /><div><h2 className="text-sm font-semibold">API credentials</h2><p className="text-xs text-muted-foreground">Use this key in your local environment</p></div></div><div className="mt-5 flex items-center gap-2 rounded-md border border-input bg-background/70 p-2 pl-3"><code className="min-w-0 flex-1 truncate font-mono text-xs text-muted-foreground">sk_live_ai_attendance_••••••••••••••••</code><button type="button" onClick={copyKey} className="focus-ring rounded-md bg-primary px-3 py-2 text-xs font-medium text-primary-foreground hover:bg-primary/90"><Copy size={13} className="mr-2 inline" />{copied ? 'Copied' : 'Copy key'}</button></div><p className="mt-3 flex items-center gap-2 text-xs text-muted-foreground"><Wifi size={13} className="text-emerald-400" /> Key is active and ready to use</p></div><div className="rounded-xl border border-border/70 bg-card/60 p-5 backdrop-blur-md"><div className="flex items-center justify-between"><p className="text-xs text-muted-foreground">System status</p><span className="flex items-center gap-2 text-xs text-emerald-400"><span className="size-1.5 animate-pulse rounded-full bg-emerald-400" />Online</span></div><p className="mt-8 text-3xl font-semibold tracking-tight">98.7%</p><p className="mt-1 text-xs text-muted-foreground">recognition accuracy</p></div></div></div>
}

export default function Page() {
  const [active, setActive] = useState('Overview')
  const [studentList, setStudentList] = useState<Student[]>([])
  const [isAuthChecking, setIsAuthChecking] = useState(true)
  const [toast, setToast] = useState<{message: string, type: 'success' | 'error'} | null>(null)

  const showToast = (message: string, type: 'success' | 'error') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3000)
  }

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    let tokenFromUrl = urlParams.get('access_token');
    
    if (!tokenFromUrl && window.location.hash.includes('access_token=')) {
      const hashParams = new URLSearchParams(window.location.hash.substring(1));
      tokenFromUrl = hashParams.get('access_token');
    }

    if (tokenFromUrl) {
      localStorage.setItem('access_token', tokenFromUrl);
      window.history.replaceState({}, document.title, window.location.pathname);
      setIsAuthChecking(false);
      return;
    }

    setIsAuthChecking(false); 
  }, []);

  const fetchStudents = async (signal?: AbortSignal) => {
    try {
      const response = await axios.get<{success: boolean, data: any[]}>(API_STUDENT_LIST, { signal })
      if (response.data.success && Array.isArray(response.data.data)) {
        const mappedData = response.data.data.map((item: any) => ({
          id: item.student_code || item.id,
          name: item.name || 'Unknown',
          className: item.class_name || 'N/A',
          school: item.school || 'N/A',
          status: item.status || 'absent',
          initials: item.name ? item.name.substring(0, 2).toUpperCase() : '??'
        }));
        setStudentList(mappedData)
      }
    } catch (error) {
      if (!axios.isCancel(error)) console.error(error)
    }
  }

  useEffect(() => {
    if (isAuthChecking) return;

    const abortController = new AbortController()
    fetchStudents(abortController.signal)
    
    const pollingInterval = setInterval(() => fetchStudents(), 3000)
    return () => { clearInterval(pollingInterval); abortController.abort() }
  }, [isAuthChecking])

  const handleReset = async () => {
    try {
      const res = await axios.post('/api/students/reset')
      if (res.data.success) {
        showToast("All attendance records reset to absent.", "success")
        fetchStudents()
      } else {
        showToast("Failed to reset attendance.", "error")
      }
    } catch (error) {
      showToast("Error connecting to server.", "error")
    }
  }

  const handleDelete = async (id: string) => {
    try {
      const res = await axios.delete(`/api/students/${id}`)
      if (res.data.success) {
        showToast("Student deleted successfully.", "success")
        fetchStudents()
      } else {
        showToast("Failed to delete student.", "error")
      }
    } catch (error) {
      showToast("Error connecting to server.", "error")
    }
  }

  if (isAuthChecking) return <div className="flex h-screen items-center justify-center text-sm text-muted-foreground">Authenticating...</div>

  const totalStudents = studentList.length;
  const presentToday = studentList.filter(s => s.status === 'present').length;
  const absentToday = totalStudents - presentToday;
  const presentRate = totalStudents > 0 ? ((presentToday / totalStudents) * 100).toFixed(1) : '0.0';
  const absentRate = totalStudents > 0 ? ((absentToday / totalStudents) * 100).toFixed(1) : '0.0';

  const date = new Intl.DateTimeFormat('en-US', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }).format(new Date())
  
  return (
    <main className="mesh-background min-h-screen relative">
      <Sidebar active={active} onChange={setActive} />
      <div className="ml-60 min-h-screen max-md:ml-0">
        <div className="mx-auto max-w-6xl px-8 py-8 max-md:px-4">
          <header className="mb-8 flex items-start justify-between gap-4">
            <div>
              <p className="text-xs text-muted-foreground">{date}</p>
              <h1 className="mt-2 text-2xl font-semibold tracking-tight">Good morning, Linh</h1>
              <p className="mt-1 text-sm text-muted-foreground">Here&apos;s your attendance intelligence for today.</p>
            </div>
            <button type="button" className="focus-ring hidden items-center gap-2 rounded-md border border-border px-3 py-2 text-xs text-muted-foreground hover:bg-muted md:flex">
              <CalendarDays size={14} /> Today <ChevronDown size={13} />
            </button>
          </header>
          {active === 'Overview' ? (
            <>
              <div className="mb-5 grid gap-3 sm:grid-cols-3">
                <Metric label="Total students" value={totalStudents.toString()} detail={`Across the system`} icon={Users} accent="cyan" />
                <Metric label="Present today" value={presentToday.toString()} detail={`${presentRate}% attendance rate`} icon={Check} accent="violet" />
                <Metric label="Absent today" value={absentToday.toString()} detail={`${absentRate}% of total`} icon={X} accent="rose" />
              </div>
              <AttendanceChart />
              <AttendanceTable studentList={studentList} onReset={handleReset} onDelete={handleDelete} />
            </>
          ) : <SetupView />}
        </div>
      </div>
      
      {/* Toast Notification */}
      {toast && (
        <div className={`fixed bottom-6 right-6 z-50 flex items-center gap-2 rounded-lg px-4 py-3 shadow-lg backdrop-blur-md border animate-in slide-in-from-bottom-5 fade-in duration-300 ${toast.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500' : 'bg-rose-500/10 border-rose-500/20 text-rose-500'}`}>
          {toast.type === 'success' ? <Check size={16} /> : <X size={16} />}
          <p className="text-sm font-medium">{toast.message}</p>
        </div>
      )}
    </main>
  )
}
