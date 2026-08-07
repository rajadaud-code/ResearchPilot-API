# 🚀 ResearchPilot API — Autonomous Document Research Engine

An enterprise-grade, asynchronous backend engine built with **FastAPI**, **SQLAlchemy 2.0 (Async)**, **JWT Auth**, **SlowAPI Rate Limiting**, **LangGraph Multi-Agent Orchestrator**, **ChromaDB**, **Celery + Redis Task Queue**, **WebSockets**, **Gunicorn/Uvicorn Workers**, and **Docker Compose**.

Designed specifically for AI Engineers and Node.js/Express developers transitioning to production Python backend development.

---

## 🎯 Architecture Overview & Production Concepts

### 1. Gunicorn Process Management with Uvicorn ASGI Workers (Phase 7)
Running Uvicorn alone limits execution to a single event-loop process.
In production Docker containers:
- **Gunicorn** acts as the process manager handling worker process lifecycles, graceful restarts, and OS signals (SIGTERM).
- `uvicorn.workers.UvicornWorker` runs high-performance async Uvicorn worker instances.
- Command: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000`.

### 2. API Security & Rate Limiting (`slowapi`)
- Protected streaming endpoint (`GET /api/v1/chat/stream`) is decorated with `@limiter.limit("10/minute")`.
- Prevents API credit drain attacks and denial-of-service attempts by returning HTTP 429 Too Many Requests when request quotas are exceeded.

### 3. Real-Time WebSockets Progress Stream
- Endpoint: `ws://localhost:8000/api/v1/ws/task-updates/{task_id}`.
- ConnectionManager maintains active socket maps grouped by `task_id`.
- Pushes Celery document chunking and vector indexing progress updates to the frontend in real time.

---

## 📁 Complete Directory Structure

```
research_pilot/
├── app/
│   ├── api/
│   │   ├── dependencies.py          # OAuth2 scheme, get_current_user, DB sessions
│   │   ├── routes/              
│   │   │   ├── auth.py              # User registration & JWT login endpoints
│   │   │   ├── documents.py         # Asynchronous document upload & task status routes
│   │   │   ├── chat.py              # Authenticated & rate-limited SSE stream route
│   │   │   └── websockets.py        # Real-time WebSocket task progress route
│   │   └── websockets/
│   │       └── manager.py           # Task-specific WebSocket connection manager
│   ├── core/
│   │   ├── config.py                # Pydantic v2 Settings (.env validation)
│   │   ├── security.py              # bcrypt hashing & JWT encode/decode
│   │   ├── rate_limit.py            # SlowAPI rate limiting configuration
│   │   └── lifespan.py              # ASGI Lifespan (DB tables, ChromaDB & models)
│   ├── ai/                      
│   │   ├── agents/              
│   │   │   └── research_agent.py    # LangGraph StateGraph & ToolNode agent
│   │   ├── chains/                  # LangChain chains
│   │   ├── tools/                   
│   │   │   └── research_tools.py    # Custom @tool functions (ChromaDB & Web Search)
│   │   └── prompts.py               # Centralized system prompts
│   ├── services/                
│   │   ├── document_svc.py          # Document extraction & chunking service
│   │   └── ai_svc.py                # Persistent chat history service methods
│   ├── models/                      
│   │   ├── base.py                  # SQLAlchemy 2.0 DeclarativeBase
│   │   ├── user.py                  # User ORM model
│   │   └── chat.py                  # ChatMessage ORM model
│   ├── schemas/                     
│   │   ├── user_schema.py           # User & Token Pydantic schemas
│   │   └── chat_schema.py           # Chat & Stream Pydantic schemas
│   ├── worker/                  
│   │   ├── celery_app.py            # Celery task queue configuration
│   │   └── tasks.py                 # Celery PDF extraction & embedding task
│   └── main.py                      # FastAPI app entry point & CORS
├── .env                             # Environment configuration
├── .env.example                     # Environment template
├── Dockerfile                       # Multi-stage production Gunicorn/Uvicorn image
├── docker-compose.yml               # Orchestration for web, postgres, redis, celery
├── requirements.txt                 # Project dependencies
└── README.md                        # Project documentation
```

---

## 🛠️ Step-by-Step Production Deployment Guide (Docker)

### 1. Build and Launch full Multi-Container Stack
Run the entire production stack (`web`, `postgres`, `redis`, `celery_worker`) using Docker Compose:

```bash
cd research_pilot
docker compose up --build -d
```

### 2. Scale Celery Workers Independently
Scale background worker processes up to handle heavy PDF ingestion queues:

```bash
docker compose up -d --scale celery_worker=3
```

### 3. Check Container Health & Logs
```bash
docker compose ps
docker compose logs -f web
```

---

## 🧪 Testing Phase 7 Features

### 1. Test Rate Limiting (HTTP 429)
Send 11 rapid requests to `/api/v1/chat/stream`:
```bash
for i in {1..11}; do
  curl -i -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
       "http://localhost:8000/api/v1/chat/stream?query=Test+query+$i"
done
```
*The 11th request will return `HTTP/1.1 429 Too Many Requests`.*

### 2. Test Real-Time Task Updates over WebSocket
In JavaScript / Browser console:
```javascript
const taskId = "YOUR_CELERY_TASK_ID";
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/task-updates/${taskId}`);

ws.onopen = () => console.log("🟢 Connected to Task WebSocket Stream");
ws.onmessage = (event) => console.log("📡 Progress Update:", JSON.parse(event.data));
ws.onclose = () => console.log("🔴 Socket Closed");
```
