# 🚀 ResearchPilot API — Autonomous Document Research Engine

An enterprise-grade, asynchronous backend engine built with **FastAPI**, **SQLAlchemy 2.0 (Async)**, **ChromaDB**, **LangGraph / LangChain**, **Celery**, and **Server-Sent Events (SSE)**.

Designed specifically for AI Engineers and Node.js/Express developers transitioning to production Python backend development.

---

## 🎯 Architecture Overview & Key Concepts

### 1. FastAPI Lifespan Context Manager (`@asynccontextmanager`)
In legacy FastAPI (or Express.js setup callbacks), startup and shutdown events were handled via fragmented hooks (`@app.on_event("startup")`). In modern FastAPI, application state is managed using Python's ASGI Lifespan protocol (`@asynccontextmanager`).

```
               +-----------------------------------+
               |        Uvicorn ASGI Server        |
               +-----------------------------------+
                                 |
                     1. Enter Lifespan Context
                                 v
        +-------------------------------------------------+
        |  Startup Phase:                                 |
        |  - Connect ChromaDB client                       |
        |  - Load heavy LLM weights into memory           |
        |  - Initialize SQLAlchemy connection pool       |
        |  - Store instances on app.state                 |
        +-------------------------------------------------+
                                 |
                             2. yield
                                 v
        +-------------------------------------------------+
        |  Active Server Loop:                            |
        |  - Process HTTP GET/POST & SSE stream requests  |
        |  - Inject app.state dependencies into routes    |
        +-------------------------------------------------+
                                 |
                     3. Exit Lifespan Context (Shutdown)
                                 v
        +-------------------------------------------------+
        |  Teardown Phase:                                |
        |  - Flush DB connection pools                    |
        |  - Unload AI model memory                       |
        |  - Close vector store sockets                   |
        +-------------------------------------------------+
```

### 2. Server-Sent Events (SSE) Streaming for AI Agents
Standard REST API endpoints wait for the complete LLM response before returning a JSON payload, resulting in poor user experience and high initial latency (TTFT - Time To First Token).

Using `StreamingResponse` with an `AsyncGenerator`:
1. The AI Agent (`stream_research_agent_response`) yields execution steps and tokens incrementally as python `str` chunks.
2. The SSE route (`/api/v1/chat/stream`) wraps chunks in W3C compliant formatting: `data: {"token": "..."}\n\n`.
3. Client disconnects are checked per chunk using `await request.is_disconnected()`, ensuring background LLM calls are aborted immediately if a user navigates away.

---

## 📁 Directory Structure

```
research_pilot/
├── app/
│   ├── api/
│   │   ├── dependencies.py          # Dependency Injection (DB sessions, app.state)
│   │   ├── routes/              
│   │   │   ├── auth.py              # Authentication router stub
│   │   │   ├── documents.py         # Vector search & document router
│   │   │   └── chat.py              # SSE real-time streaming router
│   │   └── websockets/
│   │       └── manager.py           # WebSocket connection manager
│   ├── core/
│   │   ├── config.py                # Pydantic v2 Settings (.env validation)
│   │   ├── security.py              # JWT & hashing utilities
│   │   └── lifespan.py              # ASGI Lifespan (ChromaDB & model init)
│   ├── ai/                      
│   │   ├── agents/              
│   │   │   └── research_agent.py    # AsyncGenerator LangGraph agent simulator
│   │   ├── chains/                  # LangChain chains
│   │   ├── tools/                   # Agent custom tools
│   │   └── prompts.py               # Centralized system prompts
│   ├── services/                
│   │   ├── document_svc.py          # Document parsing & chunking service
│   │   └── ai_svc.py                # AI service abstraction layer
│   ├── models/                      # SQLAlchemy 2.0 ORM models
│   ├── schemas/                     # Pydantic validation schemas
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

### 1. Prerequisites
- Python 3.10+ installed
- PowerShell / Terminal

### 2. Create and Activate Virtual Environment (`venv`)
Navigate to the project root directory:

```bash
cd research_pilot
```

Create a virtual environment:
```bash
python -m venv venv
```

Activate the virtual environment:
- **Windows (PowerShell)**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Linux / macOS**:
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 5. Run Development Server using Uvicorn
Start the FastAPI server with live-reloading:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once running:
- **Swagger Interactive API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check Endpoint**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Testing SSE Real-Time Stream

To verify real-time Server-Sent Events token delivery in your terminal, run `curl` with the unbuffered flag (`-N` / `--no-buffer`):

```bash
curl -N "http://localhost:8000/api/v1/chat/stream?query=Explain+quantum+computing+architecture"
```

### Expected Real-Time Response Output:
```http
HTTP/1.1 200 OK
date: Fri, 07 Aug 2026 11:40:00 GMT
server: uvicorn
content-type: text/event-stream
cache-control: no-cache
connection: keep-alive
x-accel-buffering: no

data: {"token": "\ud83d\udd0d [Agent Node: Intent Analysis] Formulating research strategy for query: 'Explain quantum computing architecture'...\n", "type": "content"}

data: {"token": "\ud83d\udcda [Agent Node: Vector Search] Retrieving top relevant document chunks from ChromaDB index...\n", "type": "content"}

data: {"token": "\n\ud83e\udd16 [Agent Node: Response Synthesis] Answer:\n", "type": "content"}

data: {"token": "Based ", "type": "content"}

data: {"token": "on ", "type": "content"}

data: {"token": "retrieved ", "type": "content"}

data: {"token": "documentation...", "type": "content"}

event: end
data: {"type": "end", "status": "completed"}
```

---

## 💡 Key Architectural Takeaways for Express Developers

| Feature / Concept | Express / Node.js Paradigm | FastAPI / Python Paradigm |
| :--- | :--- | :--- |
| **Server Engine** | Node Event Loop (`http.createServer`) | ASGI / Uvicorn (`uvicorn app.main:app`) |
| **Lifecycle** | Manual `app.listen()` callbacks | `@asynccontextmanager` Lifespan protocol |
| **Validation & Env** | `dotenv` + `process.env` + Zod/Joi | `pydantic-settings` (`BaseSettings`) |
| **Request Context** | Mutating `req` (e.g. `req.db = pool`) | Declarative Dependency Injection `Depends(get_db)` |
| **Real-time Stream** | `res.writeHead()` + `res.write()` | `StreamingResponse` wrapping `AsyncGenerator` |
| **Task Offloading** | BullMQ / Bee-Queue + Redis | Celery + Redis Task Workers |
