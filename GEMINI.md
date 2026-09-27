# GEMINI PROJECT MEMORY: AI-Based Attendance System

## 1. Tech Stack
- **AI Desktop Client:** Python 3.10+, OpenCV, MediaPipe FaceLandmarker (`face_landmarker.task`), DeepFace (`Facenet512` + `mtcnn` + FasNet Anti-spoofing), Tkinter GUI, Requests.
- **Web Dashboard:** Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS, Recharts, Lucide Icons.
- **Database:** Supabase (PostgreSQL 17, `pgvector` extension với vector 512D, RPC `match_face`, PostgREST).

## 2. Folder Structure
```plaintext
AI-BasedAttendanceSystem/
├── client_core/                       # Python Desktop Client Modules
│   ├── config.py                      # Constants, URLs, Supabase keys, model download
│   ├── camera.py                      # VideoCapture & Camera scanner
│   ├── liveness.py                    # MediaPipe EAR (Eye Blink) & Head tilt angle
│   ├── recognizer.py                  # DeepFace Facenet512 + FasNet Anti-spoofing
│   ├── api_service.py                 # HTTP requests to Next.js API & Supabase
│   └── ui/
│       ├── main_window.py             # Tkinter Main Window & 30ms render loop
│       └── enrollment_dialog.py       # Tkinter Student Enrollment popup
├── frontend/                          # Next.js Management Web Dashboard
│   ├── app/
│   │   ├── api/attendance/route.ts    # POST: RPC match_face & update status
│   │   ├── api/students/route.ts       # GET: List students
│   │   ├── api/students/[id]/route.ts # DELETE: Remove student by student_code
│   │   ├── api/students/reset/route.ts# POST: Reset all students to absent
│   │   └── page.tsx                   # Main Dashboard Container Page (~130 lines)
│   ├── components/dashboard/          # Modular Dashboard Components
│   │   ├── Sidebar.tsx, MetricCard.tsx, AttendanceChart.tsx, AttendanceTable.tsx, SetupView.tsx
│   ├── hooks/useAttendance.ts         # State management, 3s Polling & API actions
│   ├── types/student.ts               # Student TypeScript definition
│   └── config/dashboard.ts            # Trend mock data, ChartConfig, NavItems
├── local_face_recognition.py          # Python Entry Point (launcher)
├── sqlscript.md                       # Supabase Database schema & match_face RPC
└── requirements.txt                   # Python dependencies
```

## 3. Data Flow
1. **Enrollment:** User inputs Student Code/Name/Class/School in Tkinter -> DeepFace extracts 512D vector & verifies liveness (FasNet) -> POST directly to Supabase `students` table (`status='absent'`).
2. **Attendance:** Camera captures frame -> MediaPipe verifies liveness (head tilt $\le 15^\circ$ + EAR blink) -> DeepFace extracts 512D vector -> POST to Next.js `/api/attendance` -> Next.js calls Supabase RPC `match_face` (threshold 0.5) -> Supabase updates `students.status = 'present'` -> Client receives student info & displays green bounding box with 5s cooldown.
3. **Web Sync:** Next.js Dashboard polls `/api/students` every 3 seconds -> Updates metrics, trends & attendance table.

## 4. Core Rules (Bắt buộc tuân thủ)
1. **Root Cause First:** Mọi phản hồi phải giải thích nguyên nhân gốc rễ (Root Cause) bằng tiếng Việt trước khi sửa code (theo `.agents/rules/rootcause.md`).
2. **File Size Limit (< 200 lines):** Tuyệt đối không để bất kỳ file nào vượt quá 200 dòng. Khi thêm tính năng mới, bắt buộc phải tách module độc lập.
3. **Zero Regression & Style Preservation:** Giữ nguyên 100% phong cách code, giao diện, cấu trúc Tailwind, thuật toán AI và logic nghiệp vụ ban đầu.
