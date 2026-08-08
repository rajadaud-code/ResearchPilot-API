"use client";

import React, { useState } from "react";
import { searchVectorDatabase } from "@/lib/api";
import { VectorSearchResultItem } from "@/types";
import { Database, Search, Sparkles, Layers, CheckCircle2, AlertCircle } from "lucide-react";

interface VectorSearchProps {
  token: string | null;
  onOpenAuth: () => void;
}

export const VectorSearch: React.FC<VectorSearchProps> = ({ token, onOpenAuth }) => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<VectorSearchResultItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    if (!token) {
      onOpenAuth();
      return;
    }

    if (!query.trim() || loading) return;

    setLoading(true);
    setError(null);

    try {
      const response = await searchVectorDatabase(query, token);
      setResults(response.results || []);
    } catch (err: any) {
      setError(err.message || "Vector search failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      
      {/* Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 text-center relative overflow-hidden">
        <div className="inline-flex p-3 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 mb-3">
          <Database className="w-6 h-6 animate-pulse" />
        </div>
        <h2 className="text-2xl font-bold text-slate-100">
          ChromaDB Semantic Vector Explorer
        </h2>
        <p className="text-xs text-slate-400 max-w-xl mx-auto mt-1">
          Perform high-dimensional cosine similarity searches against indexed document chunks stored in the ChromaDB vector database.
        </p>
      </div>

      {!token && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-center justify-between">
          <span>Sign in required to perform vector database searches.</span>
          <button
            onClick={onOpenAuth}
            className="font-bold underline text-amber-200"
          >
            Sign In
          </button>
        </div>
      )}

      {/* Search Input Bar */}
      <form onSubmit={handleSearch} className="glass-panel p-2 rounded-2xl border border-slate-800 flex items-center">
        <div className="relative flex-1 flex items-center">
          <Search className="absolute left-4 w-5 h-5 text-slate-400" />
          <input
            type="text"
            placeholder="Search vector database (e.g. 'FastAPI async engine architecture')..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={!token || loading}
            className="w-full pl-12 pr-4 py-3 bg-transparent text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none disabled:opacity-50"
          />
        </div>

        <button
          type="submit"
          disabled={!token || !query.trim() || loading}
          className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-cyan-500 hover:from-indigo-400 hover:to-cyan-400 text-slate-950 font-bold text-xs flex items-center space-x-2 transition-all disabled:opacity-30 shadow-lg shadow-indigo-500/20"
        >
          {loading ? (
            <span>Querying...</span>
          ) : (
            <>
              <Sparkles className="w-4 h-4 text-slate-950" />
              <span>Search Vectors</span>
            </>
          )}
        </button>
      </form>

      {/* Error Notice */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Vector Results Display */}
      <div className="space-y-3">
        {results.length > 0 && (
          <div className="flex items-center justify-between text-xs text-slate-400 px-1">
            <span>Retrieved Top Similarity Matches</span>
            <span className="font-mono text-indigo-400 font-semibold">{results.length} chunks</span>
          </div>
        )}

        {results.map((item, idx) => (
          <div
            key={idx}
            className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-indigo-500/40 transition-all space-y-2 group"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Layers className="w-4 h-4 text-indigo-400" />
                <span className="text-xs font-mono font-bold text-slate-200">
                  Chunk ID: {item.id}
                </span>
              </div>
              <span className="text-[11px] font-mono font-bold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                Similarity: {(item.score * 100).toFixed(1)}%
              </span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed font-mono bg-slate-950/60 p-3 rounded-xl border border-slate-800">
              "{item.content}"
            </p>
          </div>
        ))}
      </div>

    </div>
  );
};
