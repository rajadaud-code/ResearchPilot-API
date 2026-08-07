# 🚀 ResearchPilot API — Autonomous Document Research Engine

An enterprise-grade, asynchronous backend engine built with **FastAPI**, **SQLAlchemy 2.0 (Async)**, **Passlib (bcrypt)**, **JWT Authentication**, **ChromaDB**, **LangGraph / LangChain**, **Celery**, and **Server-Sent Events (SSE)**.

Designed specifically for AI Engineers and Node.js/Express developers transitioning to production Python backend development.

---

## 🎯 Architecture Overview & Key Concepts

### 1. FastAPI Lifespan Context Manager (`@asynccontextmanager`)
Managed using Python's ASGI Lifespan protocol (`@asynccontextmanager`):
- Connects database tables and ChromaDB vector store clients at startup.
- Loads AI models into memory once and stores instances on `app.state`.
- Flushes DB connection pools and releases resources cleanly on shutdown.

### 2. JWT Bearer Authentication & OAuth2 Scheme
- User registration (`POST /api/v1/auth/register`) hashes passwords securely using salted `bcrypt` (`passlib`).
- User authentication (`POST /api/v1/auth/login`) issues signed JWT access tokens using HMAC-SHA256 (`python-jose`).
- Protected endpoints declare `current_user: User = Depends(get_current_user)` for declarative, auto-validated user resolution.

### 3. Authenticated SSE Streaming & Persistent Memory
- The streaming endpoint (`GET /api/v1/chat/stream`) requires JWT Bearer authentication.
- Incoming user queries are committed to PostgreSQL (`role="user"`) *before* streaming begins.
- Generated tokens stream real-time over SSE while accumulating in-memory.
- Upon completion, the synthesized answer is committed to PostgreSQL (`role="assistant"`).
- Chat turns are fetched via `GET /api/v1/chat/history` to provide conversational memory windows for LLM agent pipelines.

---

## 📁 Directory Structure

```
research_pilot/
├── app/
│   ├── api/
│   │   ├── dependencies.py          # OAuth2 scheme, get_current_user, DB sessions
│   │   ├── routes/              
│   │   │   ├── auth.py              # User registration & JWT login endpoints
│   │   │   ├── documents.py         # Vector search & document router
│   │   │   └── chat.py              # Authenticated SSE stream & history routes
│   │   └── websockets/
│   │       └── manager.py           # WebSocket connection manager
│   ├── core/
│   │   ├── config.py                # Pydantic v2 Settings (.env validation)
│   │   ├── security.py              # bcrypt hashing & JWT encode/decode
│   │   └── lifespan.py              # ASGI Lifespan (DB tables, ChromaDB & models)
│   ├── ai/                      
│   │   ├── agents/              
│   │   │   └── research_agent.py    # AsyncGenerator LangGraph agent simulator
│   │   ├── chains/                  # LangChain chains
│   │   ├── tools/                   # Agent custom tools
│   │   └── prompts.py               # Centralized system prompts
│   ├── services/                
│   │   ├── document_svc.py          # Document parsing & chunking service
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
│   │   └── tasks.py                 # Async background tasks (embeddings)
│   └── main.py                      # FastAPI app entry point & CORS
├── .env                             # Environment configuration
├── .env.example                     # Environment template
├── requirements.txt                 # Project dependencies
└── README.md                        # Project documentation
```

---

## 🛠️ Step-by-Step Setup Guide

### 1. Create and Activate Virtual Environment (`venv`)
```bash
cd research_pilot
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Development Server using Uvicorn
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Swagger Interactive API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Testing Phase 3 & Phase 4 Endpoints

### 1. Register a New User Account
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "researcher@example.com", "password": "SecurePassword123"}'
```

### 2. Authenticate & Obtain JWT Access Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=researcher@example.com&password=SecurePassword123"
```
*Copy the returned `access_token` string.*

### 3. Stream Protected AI Response via SSE
Pass the Bearer token in the `Authorization` header:

```bash
curl -N -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     "http://localhost:8000/api/v1/chat/stream?query=What+is+SQLAlchemy+2.0+async+ORM"
```

### 4. Fetch Persistent Chat History
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     "http://localhost:8000/api/v1/chat/history"
```
