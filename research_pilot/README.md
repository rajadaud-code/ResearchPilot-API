# 🚀 ResearchPilot API — Autonomous Document Research Engine

An enterprise-grade, asynchronous backend engine built with **FastAPI**, **SQLAlchemy 2.0 (Async)**, **JWT Auth**, **LangGraph Multi-Agent Orchestrator**, **ChromaDB**, **Celery + Redis Task Queue**, and **Server-Sent Events (SSE)**.

Designed specifically for AI Engineers and Node.js/Express developers transitioning to production Python backend development.

---

## 🎯 Architecture Overview & Key Concepts

### 1. LangGraph Multi-Agent StateGraph Orchestrator (Phase 5)
- **AgentState**: Uses `Annotated[Sequence[BaseMessage], add_messages]` to automatically append chat turns and tool outputs to the state reducer.
- **Custom Tools**: `@tool` decorated functions (`chroma_vector_search_tool`, `web_search_tool`) for retrieving document vector context and web facts.
- **ToolNode**: Evaluates tool calls emitted by the agent node and appends `ToolMessage` instances back into the state graph.
- **Conditional Edges**: `should_continue` dynamically routes execution between tool nodes and `END` based on LLM output.
- **Token Streaming**: `stream_research_agent_response` streams execution node events and LLM tokens real-time over SSE.

### 2. Asynchronous Document Ingestion with Celery & Redis (Phase 6)
- **Non-blocking Upload**: `POST /api/v1/documents/upload` streams file bytes, dispatches a Celery task (`process_document_task.delay()`), and returns `202 Accepted` immediately.
- **Worker Execution**: Dedicated Celery worker processes extract PDF text (`pypdf`), split text into semantic chunks (`RecursiveCharacterTextSplitter`), generate dense vector embeddings, and populate ChromaDB without blocking the FastAPI event loop.
- **Task Status Polling**: `GET /api/v1/documents/tasks/{task_id}` queries Redis for ingestion progress (`PENDING`, `PROGRESS`, `SUCCESS`, `FAILURE`).

---

## 📁 Directory Structure

```
research_pilot/
├── app/
│   ├── api/
│   │   ├── dependencies.py          # OAuth2 scheme, get_current_user, DB sessions
│   │   ├── routes/              
│   │   │   ├── auth.py              # User registration & JWT login endpoints
│   │   │   ├── documents.py         # Asynchronous document upload & task status routes
│   │   │   └── chat.py              # Authenticated SSE stream & history routes
│   │   └── websockets/
│   │       └── manager.py           # WebSocket connection manager
│   ├── core/
│   │   ├── config.py                # Pydantic v2 Settings (.env validation)
│   │   ├── security.py              # bcrypt hashing & JWT encode/decode
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
├── requirements.txt                 # Project dependencies
└── README.md                        # Project documentation
```

---

## 🛠️ Step-by-Step Setup Guide

### 1. Activate Virtual Environment & Install Dependencies
```bash
cd research_pilot
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

### 2. Start Redis & Celery Worker Process
In a dedicated terminal window:
```bash
celery -A app.worker.celery_app worker --loglevel=info
```

### 3. Start FastAPI Uvicorn Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Testing Phase 5 & Phase 6 Endpoints

### 1. Register User & Obtain JWT Access Token
```bash
# Register
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "researcher@example.com", "password": "SecurePassword123"}'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=researcher@example.com&password=SecurePassword123"
```

### 2. Upload Document for Asynchronous Ingestion (HTTP 202 Accepted)
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -F "file=@/path/to/sample_paper.pdf"
```

Response:
```json
{
  "status": "ACCEPTED",
  "message": "File upload received. Document ingestion task dispatched to background worker queue.",
  "document_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "task_id": "f83a21d9-3e54-482a-a92c-e2f416551b9e",
  "status_url": "/api/v1/documents/tasks/f83a21d9-3e54-482a-a92c-e2f416551b9e"
}
```

### 3. Poll Background Task Ingestion Status
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     "http://localhost:8000/api/v1/documents/tasks/f83a21d9-3e54-482a-a92c-e2f416551b9e"
```

### 4. Stream LangGraph Multi-Agent AI Research Tokens via SSE
```bash
curl -N -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     "http://localhost:8000/api/v1/chat/stream?query=Search+documents+for+quantum+architecture"
```
