"use client";

import React, { useState, useEffect, useRef } from "react";
import { ChatMessage } from "@/types";
import { fetchChatHistory, streamChatAgent } from "@/lib/api";
import { Send, Bot, User as UserIcon, Sparkles, Clock, AlertTriangle, Terminal, ShieldAlert, Cpu } from "lucide-react";

interface ChatSectionProps {
  token: string | null;
  onOpenAuth: () => void;
}

export const ChatSection: React.FC<ChatSectionProps> = ({ token, onOpenAuth }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuery, setInputQuery] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentNodeStep, setCurrentNodeStep] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const activeStreamController = useRef<AbortController | null>(null);

  // Auto-scroll to bottom of messages container
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentNodeStep]);

  // Load persistent chat history from PostgreSQL when token is set
  useEffect(() => {
    if (token) {
      fetchChatHistory(token)
        .then((history) => setMessages(history))
        .catch((err) => console.error("History load error:", err));
    }
  }, [token]);

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    if (!token) {
      onOpenAuth();
      return;
    }

    if (!inputQuery.trim() || isStreaming) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: inputQuery,
      timestamp: new Date().toISOString(),
    };

    const queryText = inputQuery;
    setInputQuery("");
    setErrorMessage(null);
    setMessages((prev) => [...prev, userMessage]);

    // Create placeholder assistant message for streaming tokens
    const assistantMessage: ChatMessage = {
      role: "assistant",
      content: "",
      timestamp: new Date().toISOString(),
      is_streaming: true,
    };

    setMessages((prev) => [...prev, assistantMessage]);
    setIsStreaming(true);
    setCurrentNodeStep("🔍 Initializing LangGraph Agent...");

    try {
      const controller = await streamChatAgent(
        queryText,
        token,
        (tokenChunk) => {
          // Check if token chunk is a node execution log step
          if (tokenChunk.includes("[LangGraph Executed Node") || tokenChunk.includes("Requesting tool")) {
            setCurrentNodeStep(tokenChunk.trim());
          } else {
            // Append content token to assistant message
            setMessages((prev) => {
              const updated = [...prev];
              const lastMsg = updated[updated.length - 1];
              if (lastMsg && lastMsg.role === "assistant") {
                lastMsg.content += tokenChunk;
              }
              return updated;
            });
          }
        },
        () => {
          // On Stream Completion
          setIsStreaming(false);
          setCurrentNodeStep(null);
          setMessages((prev) => {
            const updated = [...prev];
            const lastMsg = updated[updated.length - 1];
            if (lastMsg) lastMsg.is_streaming = false;
            return updated;
          });
        },
        (errorStr) => {
          // On Stream Error
          setIsStreaming(false);
          setCurrentNodeStep(null);
          setErrorMessage(errorStr);
        }
      );
      activeStreamController.current = controller;
    } catch (err: any) {
      setIsStreaming(false);
      setCurrentNodeStep(null);
      setErrorMessage(err.message || "Streaming failed.");
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-140px)] min-h-[550px]">
      
      {/* Sidebar: Persistent History */}
      <div className="lg:col-span-1 glass-panel rounded-2xl p-4 flex flex-col border border-slate-800 hidden lg:flex">
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800/80">
          <div className="flex items-center space-x-2 text-slate-200 font-semibold text-xs uppercase tracking-wider">
            <Clock className="w-4 h-4 text-emerald-400" />
            <span>Persistent Memory</span>
          </div>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
            {messages.length} messages
          </span>
        </div>

        <div className="flex-1 overflow-y-auto space-y-2 pr-1">
          {messages.length === 0 ? (
            <div className="text-center py-10 text-xs text-slate-500">
              No chat history recorded yet.
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                className={`p-2.5 rounded-xl border text-xs transition-all ${
                  msg.role === "user"
                    ? "bg-slate-900/60 border-slate-800 text-slate-300"
                    : "bg-emerald-500/5 border-emerald-500/20 text-emerald-200"
                }`}
              >
                <div className="flex items-center justify-between text-[10px] text-slate-500 mb-1">
                  <span className="font-semibold uppercase tracking-wider text-slate-400">
                    {msg.role}
                  </span>
                  {msg.timestamp && (
                    <span>{new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  )}
                </div>
                <p className="line-clamp-2 text-slate-300 font-medium">{msg.content}</p>
              </div>
            ))
          )}
        </div>

        {/* Rate limit warning box */}
        <div className="mt-3 p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-[11px] text-slate-400 flex items-start space-x-2">
          <ShieldAlert className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
          <span>Protected by SlowAPI rate limits (10 SSE queries / minute).</span>
        </div>
      </div>

      {/* Main Streaming Chat Console */}
      <div className="lg:col-span-3 glass-panel rounded-2xl p-4 sm:p-6 flex flex-col border border-slate-800/80 relative overflow-hidden">
        
        {/* Chat Console Header */}
        <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800/80">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-100 flex items-center space-x-2">
                <span>Autonomous LangGraph Research Agent</span>
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              </h2>
              <p className="text-xs text-slate-400">
                Multi-node tool execution graph & real-time SSE token stream
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-[10px] font-mono px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-cyan-400">
              Agent Model: gpt-4o-mini
            </span>
          </div>
        </div>

        {/* Live LangGraph Execution Step Banner */}
        {currentNodeStep && (
          <div className="mb-4 p-3 rounded-xl bg-gradient-to-r from-emerald-500/10 via-cyan-500/10 to-indigo-500/10 border border-emerald-500/30 flex items-center space-x-3 text-xs text-emerald-300 animate-pulse">
            <Terminal className="w-4 h-4 text-emerald-400 shrink-0" />
            <span className="font-mono font-medium truncate">{currentNodeStep}</span>
          </div>
        )}

        {/* Error Notification */}
        {errorMessage && (
          <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center space-x-2 text-xs text-rose-400">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Messages Stream Display */}
        <div className="flex-1 overflow-y-auto space-y-4 pr-2">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-400">
              <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 mb-4 glow-emerald">
                <Sparkles className="w-8 h-8 text-emerald-400 animate-pulse" />
              </div>
              <h3 className="text-lg font-bold text-slate-200">Start an Autonomous Research Pipeline</h3>
              <p className="text-xs text-slate-400 max-w-md mt-1 mb-6">
                Ask a research query to trigger the LangGraph multi-node agent. The agent will formulate a strategy, query ChromaDB vector index, call web tools, and stream tokens.
              </p>
              
              {/* Preset Sample Queries */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-lg">
                {[
                  "Explain quantum computing vector architecture",
                  "Search documents for FastAPI async ORM spec",
                  "What is ASGI lifespan state management?",
                  "Synthesize multi-agent research tools"
                ].map((sample, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setInputQuery(sample);
                    }}
                    className="p-2.5 text-left rounded-xl bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800 text-xs text-slate-300 transition-all hover:border-emerald-500/40"
                  >
                    "{sample}"
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex space-x-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.role === "assistant" && (
                  <div className="w-8 h-8 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0 mt-1">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`max-w-[85%] sm:max-w-[75%] p-4 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-gradient-to-r from-emerald-600 to-teal-600 text-slate-950 font-medium rounded-tr-none shadow-lg shadow-emerald-500/10"
                      : "glass-panel border border-slate-800 text-slate-200 rounded-tl-none"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                  {msg.is_streaming && (
                    <span className="inline-block w-2 h-4 ml-1 bg-emerald-400 animate-pulse"></span>
                  )}
                </div>

                {msg.role === "user" && (
                  <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0 mt-1">
                    <UserIcon className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSendMessage} className="mt-4 pt-3 border-t border-slate-800/80">
          {!token && (
            <div className="mb-2 p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-center justify-between">
              <span>Sign in required to stream research agent responses and persist chat history.</span>
              <button
                type="button"
                onClick={onOpenAuth}
                className="font-bold underline text-amber-200 ml-2"
              >
                Sign In
              </button>
            </div>
          )}

          <div className="relative flex items-center">
            <input
              type="text"
              placeholder={
                token
                  ? "Enter research question (e.g. 'Search documents for vector indexes')..."
                  : "Please sign in to start research chat..."
              }
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              disabled={!token || isStreaming}
              className="w-full pl-4 pr-12 py-3.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-sm text-slate-100 focus:outline-none focus:border-emerald-500/80 focus:ring-1 focus:ring-emerald-500 transition-all placeholder:text-slate-500 disabled:opacity-50"
            />

            <button
              type="submit"
              disabled={!token || !inputQuery.trim() || isStreaming}
              className="absolute right-2 p-2.5 rounded-lg bg-gradient-to-r from-emerald-500 to-cyan-500 text-slate-950 font-bold hover:from-emerald-400 hover:to-cyan-400 transition-all disabled:opacity-30 disabled:hover:from-emerald-500 shadow-md shadow-emerald-500/20"
            >
              {isStreaming ? (
                <Cpu className="w-4 h-4 animate-spin text-slate-950" />
              ) : (
                <Send className="w-4 h-4 text-slate-950" />
              )}
            </button>
          </div>
        </form>

      </div>
    </div>
  );
};
