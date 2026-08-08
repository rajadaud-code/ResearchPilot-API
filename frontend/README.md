# ⚡ ResearchPilot Frontend — Next.js 14 Dashboard

A sleek, responsive, cyberpunk-inspired glassmorphism web dashboard built with **React**, **Next.js 14 (App Router)**, **Tailwind CSS**, **Lucide Icons**, and **Framer Motion**.

Connects seamlessly to the **ResearchPilot API** FastAPI backend.

---

## ✨ Features

- **Futuristic Glassmorphism Aesthetic**: Dark slate backdrop (`#080c14`), translucent glass panels (`backdrop-blur`), glowing emerald/cyan neon accents, and smooth micro-animations.
- **Real-Time SSE AI Agent Stream**: Real-time token streaming with live LangGraph agent execution node chips (`🔍 Intent Analysis`, `📚 Vector Search`, `🤖 Response Synthesis`).
- **Persistent Memory Sidebar**: Displays conversation history loaded from PostgreSQL.
- **Non-Blocking Document Upload**: Drag-and-drop dropzone supporting PDF & TXT files with live progress bar connecting to Celery background task workers.
- **ChromaDB Vector Explorer**: High-dimensional semantic vector search with relevance percentage scores.
- **JWT Authentication Modal**: Built-in register and login modal storing JWT access tokens in `localStorage`.

---

## 🛠️ Step-by-Step Setup & Running Guide

### 1. Install Dependencies
Navigate to the `frontend/` directory:

```bash
cd frontend
npm install
```

### 2. Configure Environment Variables
Create a `.env.local` file (optional, defaults to `http://localhost:8000/api/v1`):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 3. Run Development Server
```bash
npm run dev
```

Open [http://localhost:3500](http://localhost:3500) in your browser to view the application.

---

## 📁 Directory Layout

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx             # Root layout with fonts & metadata
│   │   ├── page.tsx               # Main Dashboard App (Tabbed UI)
│   │   └── globals.css            # Custom CSS tokens & glassmorphism
│   ├── components/
│   │   ├── Navbar.tsx             # Brand Navbar & profile badge
│   │   ├── AuthModal.tsx          # JWT Auth register/login modal
│   │   ├── ChatSection.tsx        # Real-time SSE AI Agent Chat & Memory Sidebar
│   │   ├── DocumentUpload.tsx     # File Dropzone & Celery Task Progress
│   │   └── VectorSearch.tsx       # Vector Database Explorer
│   ├── lib/
│   │   └── api.ts                 # Fetch & SSE ReadableStream API client
│   └── types/
│       └── index.ts               # Shared TypeScript interfaces
├── package.json                   # Dependencies
├── tailwind.config.ts             # Tailwind design tokens
├── tsconfig.json                  # TypeScript config
└── README.md                      # Documentation
```
