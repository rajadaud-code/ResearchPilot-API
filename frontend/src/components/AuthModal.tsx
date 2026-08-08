"use client";

import React, { useState } from "react";
import { registerUser, loginUser, fetchCurrentUser } from "@/lib/api";
import { User } from "@/types";
import { X, Lock, Mail, KeyRound, ArrowRight, AlertCircle, CheckCircle2 } from "lucide-react";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (token: string, user: User) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setLoading(true);

    try {
      if (isRegister) {
        // Register user
        await registerUser(email, password);
        setMessage("Account created successfully! Logging you in...");
      }

      // Login user to retrieve JWT token
      const tokenData = await loginUser(email, password);
      const userProfile = await fetchCurrentUser(tokenData.access_token);

      onSuccess(tokenData.access_token, userProfile);
      onClose();
    } catch (err: any) {
      setError(err.message || "Authentication failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-md glass-panel p-6 sm:p-8 rounded-2xl border border-slate-700/80 shadow-2xl glow-emerald">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-200 rounded-xl hover:bg-slate-800/60 transition-all"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="text-center mb-6">
          <div className="inline-flex p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 mb-3">
            <Lock className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-bold text-slate-100">
            {isRegister ? "Create Research Pilot Account" : "Sign In to Research Pilot"}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            {isRegister
              ? "Access stateful AI agent streams and document indexing APIs"
              : "Enter your credentials to manage persistent sessions"}
          </p>
        </div>

        {/* Notifications */}
        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center space-x-2 text-xs text-rose-400">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {message && (
          <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center space-x-2 text-xs text-emerald-400">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{message}</span>
          </div>
        )}

        {/* Auth Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
              <input
                type="email"
                required
                placeholder="researcher@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-sm text-slate-100 focus:outline-none focus:border-emerald-500/80 focus:ring-1 focus:ring-emerald-500 transition-all placeholder:text-slate-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Password
            </label>
            <div className="relative">
              <KeyRound className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
              <input
                type="password"
                required
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-sm text-slate-100 focus:outline-none focus:border-emerald-500/80 focus:ring-1 focus:ring-emerald-500 transition-all placeholder:text-slate-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-slate-950 font-bold text-sm flex items-center justify-center space-x-2 transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-50"
          >
            <span>{loading ? "Processing..." : isRegister ? "Register Account" : "Sign In"}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Toggle Mode */}
        <div className="mt-6 text-center text-xs text-slate-400">
          {isRegister ? "Already have an account?" : "Don't have an account?"}{" "}
          <button
            onClick={() => {
              setIsRegister(!isRegister);
              setError(null);
            }}
            className="text-emerald-400 font-semibold hover:underline ml-1"
          >
            {isRegister ? "Sign In" : "Register Now"}
          </button>
        </div>

      </div>
    </div>
  );
};
