"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "@/components/Navbar";
import { AuthModal } from "@/components/AuthModal";
import { ChatSection } from "@/components/ChatSection";
import { DocumentUpload } from "@/components/DocumentUpload";
import { VectorSearch } from "@/components/VectorSearch";
import { User } from "@/types";
import { fetchCurrentUser } from "@/lib/api";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"chat" | "upload" | "search">("chat");
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isAuthOpen, setIsAuthOpen] = useState(false);

  // Load JWT token from localStorage on mount
  useEffect(() => {
    const savedToken = localStorage.getItem("research_pilot_jwt");
    if (savedToken) {
      setToken(savedToken);
      fetchCurrentUser(savedToken)
        .then((profile) => setUser(profile))
        .catch(() => {
          localStorage.removeItem("research_pilot_jwt");
          setToken(null);
          setUser(null);
        });
    }
  }, []);

  const handleAuthSuccess = (newToken: string, newUser: User) => {
    localStorage.setItem("research_pilot_jwt", newToken);
    setToken(newToken);
    setUser(newUser);
  };

  const handleLogout = () => {
    localStorage.removeItem("research_pilot_jwt");
    setToken(null);
    setUser(null);
  };

  return (
    <div className="min-h-screen flex flex-col justify-between">
      <div>
        {/* Navigation Bar */}
        <Navbar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          user={user}
          onOpenAuth={() => setIsAuthOpen(true)}
          onLogout={handleLogout}
        />

        {/* Main Content Area */}
        <main className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
          {activeTab === "chat" && (
            <ChatSection
              token={token}
              onOpenAuth={() => setIsAuthOpen(true)}
            />
          )}

          {activeTab === "upload" && (
            <DocumentUpload
              token={token}
              onOpenAuth={() => setIsAuthOpen(true)}
            />
          )}

          {activeTab === "search" && (
            <VectorSearch
              token={token}
              onOpenAuth={() => setIsAuthOpen(true)}
            />
          )}
        </main>
      </div>

      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onSuccess={handleAuthSuccess}
      />

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-4 px-6 text-center text-xs text-slate-500 glass-panel mt-8">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>
            ResearchPilot API — Autonomous Document Research Engine
          </span>
          <div className="flex items-center space-x-3 text-[11px] font-mono">
            <span className="text-emerald-400">FastAPI</span>
            <span>•</span>
            <span className="text-cyan-400">LangGraph</span>
            <span>•</span>
            <span className="text-indigo-400">ChromaDB</span>
            <span>•</span>
            <span className="text-amber-400">Celery + Redis</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
