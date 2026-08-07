"""
LangChain / LangGraph Autonomous Research Tools.

===============================================================================
LANGGRAPH CUSTOM TOOLS PARADIGM
===============================================================================
In LangGraph:
  - Tools are functions decorated with `@tool` from `langchain_core.tools`.
  - The function's docstring and type hints are automatically extracted to construct
    OpenAI / Anthropic JSON Schema tool definitions.
  - When the LLM decides to call a tool, LangGraph's `ToolNode` executes the function,
    captures its return value, and appends a `ToolMessage` back into the conversation state.
===============================================================================
"""

import logging
from langchain_core.tools import tool

logger = logging.getLogger("research_pilot.tools")


@tool
def chroma_vector_search_tool(query: str) -> str:
    """
    Search the ChromaDB vector database index for relevant document passages and context.

    Args:
        query: The semantic search query or keyword phrase to locate in indexed documents.

    Returns:
        str: Formatted context retrieved from top vector embedding matches.
    """
    logger.info(f"🛠️ [Tool Executed: Chroma Vector Search] Query: '{query}'")
    # In production, query the ChromaDB vector collection instance
    return (
        f"[Vector DB Context for '{query}']:\n"
        "• Document 'quantum_arch_2026.pdf' (Chunk 4, Similarity 0.94): "
        "The ResearchPilot engine utilizes an event-driven ASGI execution graph with sub-100ms first-token latency.\n"
        "• Document 'fastapi_orm_spec.pdf' (Chunk 12, Similarity 0.89): "
        "SQLAlchemy 2.0 async sessions run on asyncpg driver, managing pools cleanly inside FastAPI dependencies."
    )


@tool
def web_search_tool(query: str) -> str:
    """
    Perform a web search to gather real-time external facts, recent documentation, or web evidence.

    Args:
        query: The search query to submit to the web search engine.

    Returns:
        str: Search results summary from authoritative online sources.
    """
    logger.info(f"🛠️ [Tool Executed: Web Search] Query: '{query}'")
    # In production, call DuckDuckGo, Tavily, or Google Custom Search API
    return (
        f"[Web Search Results for '{query}']:\n"
        "• Source: https://docs.fastapi.tiangolo.com/ - FastAPI documentation highlights native "
        "Server-Sent Events (SSE) streaming capabilities using Starlette StreamingResponse.\n"
        "• Source: https://python.langchain.com/ - LangGraph enables stateful multi-agent control loops "
        "with cycle detection, conditional branching, and streaming event listeners."
    )


# List of available research tools for binding to LLM agent graph
RESEARCH_TOOLS = [chroma_vector_search_tool, web_search_tool]
