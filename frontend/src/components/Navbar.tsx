"use client";

import React from "react";
import { User } from "@/types";
import { Cpu, Database, MessageSquare, Upload, User as UserIcon, LogOut, ShieldCheck } from "lucide-react";

interface NavbarProps {
  activeTab: "chat" | "upload" | "search";
  setActiveTab: (tab: "chat" | "upload" | "search") => void;
  user: User | null;
  onOpenAuth: () => void;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  user,
  onOpenAuth,
  onLogout,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Brand Logo */}
        <div className="flex items-center space-x-3">
          <div className="relative p-2.5 rounded-xl bg-gradient-to-tr from-emerald-500/20 to-cyan-500/20 border border-emerald-500/40 glow-emerald">
            <Cpu className="w-6 h-6 text-emerald-400 animate-pulse-slow" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold bg-gradient-to-r from-emerald-400 via-cyan-400 to-indigo-400 bg-clip-text text-transparent tracking-wide">
                ResearchPilot
              </h1>
              <span className="text-[10px] uppercase tracking-widest font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                v1.0 API
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium hidden sm:block">
              Autonomous Document Research & Vector Engine
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center space-x-1 glass-panel p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab("chat")}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === "chat"
                ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 shadow-lg shadow-emerald-500/10"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            <span>Research Agent</span>
          </button>

          <button
            onClick={() => setActiveTab("upload")}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === "upload"
                ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-lg shadow-cyan-500/10"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
            }`}
          >
            <Upload className="w-4 h-4" />
            <span>Document Ingestion</span>
          </button>

          <button
            onClick={() => setActiveTab("search")}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === "search"
                ? "bg-indigo-500/20 text-indigo-400 border border-indigo-500/40 shadow-lg shadow-indigo-500/10"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
            }`}
          >
            <Database className="w-4 h-4" />
            <span>Vector Explorer</span>
          </button>
        </nav>

        {/* User Auth Profile Badge */}
        <div className="flex items-center space-x-3">
          {/* API Health Status Indicator */}
          <div className="hidden lg:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900/80 border border-slate-800 text-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
            <span className="text-slate-300 font-medium">ASGI Engine: Online</span>
          </div>

          {user ? (
            <div className="flex items-center space-x-2 pl-2 border-l border-slate-800">
              <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-emerald-500/30">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-medium text-slate-200 truncate max-w-[130px]">
                  {user.email}
                </span>
              </div>
              <button
                onClick={onLogout}
                title="Logout Account"
                className="p-2 rounded-xl bg-slate-900/80 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 border border-slate-800 hover:border-rose-500/40 transition-all"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="glass-button flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold"
            >
              <UserIcon className="w-4 h-4" />
              <span>Sign In / Register</span>
            </button>
          )}
        </div>
      </div>

      {/* Mobile Tab Switcher */}
      <div className="flex md:hidden items-center justify-around mt-3 pt-3 border-t border-slate-800/80">
        <button
          onClick={() => setActiveTab("chat")}
          className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-medium ${
            activeTab === "chat" ? "bg-emerald-500/20 text-emerald-400" : "text-slate-400"
          }`}
        >
          <MessageSquare className="w-3.5 h-3.5" />
          <span>Research</span>
        </button>
        <button
          onClick={() => setActiveTab("upload")}
          className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-medium ${
            activeTab === "upload" ? "bg-cyan-500/20 text-cyan-400" : "text-slate-400"
          }`}
        >
          <Upload className="w-3.5 h-3.5" />
          <span>Ingest</span>
        </button>
        <button
          onClick={() => setActiveTab("search")}
          className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-medium ${
            activeTab === "search" ? "bg-indigo-500/20 text-indigo-400" : "text-slate-400"
          }`}
        >
          <Database className="w-3.5 h-3.5" />
          <span>Vector</span>
        </button>
      </div>
    </header>
  );
};
