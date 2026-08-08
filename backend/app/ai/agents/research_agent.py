"""
Autonomous LangGraph Multi-Agent Orchestrator.

===============================================================================
EXPRESS / NODE.JS VS. LANGGRAPH STATEGRAPH ORCHESTRATION
===============================================================================
In Node.js:
  - Agent loops are often coded imperatively using `while(true)` loops, manually calling
    OpenAI tool APIs until no `tool_calls` remain in the response object.

In Python / LangGraph:
  - LangGraph provides a cyclic graph structure (`StateGraph`) with state management,
    node execution, and declarative conditional branching.
  - State (`AgentState`) is shared across nodes. `Annotated[Sequence[BaseMessage], add_messages]`
    automatically appends new messages to the message history state without manual array concatenation.
  - `ToolNode` executes tool calls in parallel or sequence, returning `ToolMessage` instances.
  - `tools_condition` or a custom routing function evaluates whether to loop back to the agent node
    or transition to `END`.
===============================================================================
"""

import asyncio
import json
import logging
from typing import Annotated, Sequence, TypedDict, AsyncGenerator, List, Optional

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from app.ai.prompts import RESEARCH_AGENT_SYSTEM_PROMPT
from app.ai.tools.research_tools import RESEARCH_TOOLS

logger = logging.getLogger("research_pilot.agent")


class AgentState(TypedDict):
    """
    State schema for the LangGraph agent graph.
    `messages` uses `add_messages` reducer to automatically append new messages to state.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]


def create_agent_node():
    """
    Creates the main reasoning node function.
    In production:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2).bind_tools(RESEARCH_TOOLS)
        return lambda state: {"messages": [llm.invoke(state["messages"])]}
    """
    async def agent_node(state: AgentState) -> dict:
        messages = state["messages"]
        last_message = messages[-1]
        user_text = last_message.content if hasattr(last_message, "content") else str(last_message)
        
        logger.info(f"🤖 [LangGraph Node: Agent Reasoning] Processing turn with {len(messages)} state messages.")
        await asyncio.sleep(0.3)

        # Simulating autonomous tool selection logic for demonstration
        # If query mentions "document", "search", "vector", or "web", simulate a tool call step first
        has_tool_message = any(isinstance(m, ToolMessage) for m in messages)

        if not has_tool_message and any(k in user_text.lower() for k in ["document", "search", "vector", "pdf", "quantum"]):
            # Produce an AIMessage containing a tool call
            ai_msg = AIMessage(
                content="I need to consult the ChromaDB vector database index to retrieve relevant document context.",
                tool_calls=[{
                    "name": "chroma_vector_search_tool",
                    "args": {"query": user_text},
                    "id": "call_vector_db_001"
                }]
            )
            return {"messages": [ai_msg]}

        # If tools have executed or query is straightforward, return final answer
        final_answer = (
            f"Synthesized Research Answer for query: '{user_text}':\n\n"
            "1. **Architecture Specs**: The system uses FastAPI ASGI with SQLAlchemy 2.0 Async engine.\n"
            "2. **Agent State**: LangGraph StateGraph orchestrates cyclic tool calling and state updates.\n"
            "3. **Task Queue**: Heavy PDF vector ingestion is offloaded asynchronously to Redis & Celery workers."
        )
        return {"messages": [AIMessage(content=final_answer)]}

    return agent_node


def should_continue(state: AgentState) -> str:
    """
    Conditional edge function. Evaluates whether the agent produced tool calls.
    Returns "tools" to route to ToolNode, or END to finish execution.
    """
    messages = state["messages"]
    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        logger.info("🔀 [LangGraph Conditional Edge] Tool calls detected -> Routing to 'tools' node.")
        return "tools"
    
    logger.info("🏁 [LangGraph Conditional Edge] No tool calls remaining -> Routing to END.")
    return END


def build_research_graph():
    """
    Compiles the complete LangGraph StateGraph execution pipeline.
    """
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("agent", create_agent_node())
    workflow.add_node("tools", ToolNode(RESEARCH_TOOLS))

    # Add Edges
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    workflow.add_edge("tools", "agent")

    # Compile Graph
    compiled_graph = workflow.compile()
    return compiled_graph


# Pre-compiled global graph instance
research_graph = build_research_graph()


async def stream_research_agent_response(query: str) -> AsyncGenerator[str, None]:
    """
    Streams LangGraph agent execution step updates and LLM tokens in real time.

    Args:
        query (str): The research question submitted by the user.

    Yields:
        AsyncGenerator[str, None]: Token strings and step progress updates.
    """
    # Initialize graph state with SystemMessage and HumanMessage
    initial_state = {
        "messages": [
            SystemMessage(content=RESEARCH_AGENT_SYSTEM_PROMPT),
            HumanMessage(content=query)
        ]
    }

    # Step 1: Initial event notification
    yield f"🔍 [Agent Node: State Initialization] Starting research pipeline for: '{query}'...\n"
    await asyncio.sleep(0.3)

    # Run LangGraph streaming execution loop
    try:
        async for event in research_graph.astream(initial_state, stream_mode="updates"):
            for node_name, node_output in event.items():
                yield f"\n⚡ [LangGraph Executed Node: '{node_name}']\n"
                
                messages = node_output.get("messages", [])
                for msg in messages:
                    if isinstance(msg, AIMessage):
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            tool_name = msg.tool_calls[0]["name"]
                            yield f"🛠️ Requesting tool execution: '{tool_name}'...\n"
                        else:
                            # Stream content tokens incrementally
                            text_content = msg.content if isinstance(msg.content, str) else str(msg.content)
                            words = text_content.split(" ")
                            for i, word in enumerate(words):
                                token = word + (" " if i < len(words) - 1 else "")
                                yield token
                                await asyncio.sleep(0.03)
                    elif isinstance(msg, ToolMessage):
                        yield f"📊 Received tool context: {msg.content[:120]}...\n"

    except Exception as e:
        logger.error(f"❌ Error in LangGraph execution: {str(e)}", exc_info=True)
        yield f"\n⚠️ Error executing research agent graph: {str(e)}"
