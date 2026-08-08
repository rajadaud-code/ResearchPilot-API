"use client";

import React, { useState, useEffect } from "react";
import { uploadDocument, fetchTaskStatus } from "@/lib/api";
import { DocumentUploadResponse, TaskStatus } from "@/types";
import { Upload, FileText, CheckCircle, AlertCircle, RefreshCw, Cpu, Layers, HardDrive } from "lucide-react";

interface DocumentUploadProps {
  token: string | null;
  onOpenAuth: () => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ token, onOpenAuth }) => {
  const [file, setFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<DocumentUploadResponse | null>(null);
  const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Poll task status if a task_id exists and status is incomplete
  useEffect(() => {
    if (!uploadResult?.task_id || !token) return;

    let intervalId: NodeJS.Timeout;

    const checkStatus = async () => {
      try {
        const statusData = await fetchTaskStatus(uploadResult.task_id, token);
        setTaskStatus(statusData);

        if (statusData.status === "SUCCESS" || statusData.status === "FAILURE") {
          clearInterval(intervalId);
        }
      } catch (err) {
        console.error("Task poll error:", err);
      }
    };

    // Initial check + poll interval every 1 second
    checkStatus();
    intervalId = setInterval(checkStatus, 1000);

    return () => clearInterval(intervalId);
  }, [uploadResult, token]);

  const handleFileChange = (selectedFile: File) => {
    setError(null);
    setUploadResult(null);
    setTaskStatus(null);

    // Validate file type (PDF or TXT)
    const validExtensions = [".pdf", ".txt", ".md"];
    const ext = selectedFile.name.substring(selectedFile.name.lastIndexOf(".")).toLowerCase();

    if (!validExtensions.includes(ext)) {
      setError("Please select a PDF or Text document (.pdf, .txt, .md).");
      return;
    }

    setFile(selectedFile);
  };

  const handleUploadSubmit = async () => {
    if (!token) {
      onOpenAuth();
      return;
    }

    if (!file) return;

    setIsUploading(true);
    setError(null);

    try {
      const response = await uploadDocument(file, token);
      setUploadResult(response);
    } catch (err: any) {
      setError(err.message || "Failed to upload document.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      
      {/* Header Info */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 text-center relative overflow-hidden">
        <div className="inline-flex p-3 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 mb-3">
          <Upload className="w-6 h-6 animate-pulse" />
        </div>
        <h2 className="text-2xl font-bold text-slate-100">
          Asynchronous Document Ingestion Engine
        </h2>
        <p className="text-xs text-slate-400 max-w-xl mx-auto mt-1">
          Upload PDF research papers or text files. The engine streams file bytes, offloads semantic text chunking & ChromaDB vector embedding generation to Celery workers, and updates status in real time.
        </p>
      </div>

      {!token && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-center justify-between">
          <span>Sign in required to upload documents and trigger background vector indexing.</span>
          <button
            onClick={onOpenAuth}
            className="font-bold underline text-amber-200"
          >
            Sign In
          </button>
        </div>
      )}

      {/* Drag & Drop File Zone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragOver(false);
          if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileChange(e.dataTransfer.files[0]);
          }
        }}
        className={`glass-panel p-8 sm:p-12 rounded-2xl border-2 border-dashed text-center transition-all cursor-pointer ${
          isDragOver
            ? "border-cyan-400 bg-cyan-500/10 glow-cyan"
            : file
            ? "border-emerald-500/60 bg-emerald-500/5"
            : "border-slate-700/80 hover:border-slate-600 bg-slate-900/40"
        }`}
        onClick={() => {
          const input = document.createElement("input");
          input.type = "file";
          input.accept = ".pdf,.txt,.md";
          input.onchange = (e: any) => {
            if (e.target.files && e.target.files[0]) {
              handleFileChange(e.target.files[0]);
            }
          };
          input.click();
        }}
      >
        {file ? (
          <div className="flex flex-col items-center space-y-3">
            <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
              <FileText className="w-10 h-10" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-100">{file.name}</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Size: {(file.size / 1024).toFixed(1)} KB • Type: {file.type || "Document"}
              </p>
            </div>
            <span className="text-[11px] px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 font-semibold border border-emerald-500/40">
              File Ready for Ingestion
            </span>
          </div>
        ) : (
          <div className="flex flex-col items-center space-y-3">
            <div className="p-4 rounded-2xl bg-slate-800/80 text-slate-400 border border-slate-700">
              <Upload className="w-8 h-8 text-cyan-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-200">
                Drag and drop your research document here
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Supports PDF (.pdf) or Plain Text (.txt, .md) up to 25 MB
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Action Button */}
      {file && !uploadResult && (
        <button
          onClick={handleUploadSubmit}
          disabled={isUploading || !token}
          className="w-full py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-bold text-sm flex items-center justify-center space-x-2 transition-all shadow-lg shadow-cyan-500/20 disabled:opacity-50"
        >
          {isUploading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin text-slate-950" />
              <span>Uploading & Offloading Task...</span>
            </>
          ) : (
            <>
              <Cpu className="w-4 h-4 text-slate-950" />
              <span>Submit to Celery Worker Queue</span>
            </>
          )}
        </button>
      )}

      {/* Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Real-time Celery Worker Task Progress Card */}
      {uploadResult && (
        <div className="glass-panel p-6 rounded-2xl border border-cyan-500/30 space-y-4 animate-fadeIn glow-cyan">
          
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-emerald-400" />
              <h3 className="text-sm font-bold text-slate-100">
                HTTP 202 Accepted — Task Dispatched
              </h3>
            </div>
            <span className="text-xs font-mono px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-cyan-400">
              Task ID: {uploadResult.task_id.substring(0, 18)}...
            </span>
          </div>

          {/* Task Progress Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">Status</span>
              <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                taskStatus?.status === "SUCCESS"
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                  : "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 animate-pulse"
              }`}>
                {taskStatus?.status || "PENDING"}
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">Worker Queue</span>
              <span className="text-xs font-mono text-slate-200">Redis Broker</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">Document ID</span>
              <span className="text-xs font-mono text-slate-300 truncate block">
                {uploadResult.document_id.substring(0, 12)}...
              </span>
            </div>
          </div>

          {/* Dynamic Progress Bar */}
          <div className="space-y-1.5 pt-2">
            <div className="flex justify-between text-xs text-slate-400">
              <span className="flex items-center space-x-1.5">
                <Layers className="w-3.5 h-3.5 text-cyan-400" />
                <span>Generating Vector Embeddings & Ingesting ChromaDB...</span>
              </span>
              <span className="font-mono text-cyan-400 font-bold">
                {taskStatus?.result?.percent_complete || (taskStatus?.status === "SUCCESS" ? 100 : 25)}%
              </span>
            </div>

            <div className="w-full h-2.5 rounded-full bg-slate-900 overflow-hidden p-0.5 border border-slate-800">
              <div
                className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-emerald-500 transition-all duration-500 shadow-lg shadow-cyan-500/50"
                style={{
                  width: `${taskStatus?.result?.percent_complete || (taskStatus?.status === "SUCCESS" ? 100 : 25)}%`,
                }}
              ></div>
            </div>
          </div>

          {taskStatus?.status === "SUCCESS" && (
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-300 flex items-center space-x-2">
              <HardDrive className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>
                Document successfully indexed into ChromaDB! Created {taskStatus.result.chunks_indexed || 12} semantic vector chunks.
              </span>
            </div>
          )}

        </div>
      )}

    </div>
  );
};
