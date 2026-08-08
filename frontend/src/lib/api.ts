import { AuthToken, User, ChatMessage, DocumentUploadResponse, TaskStatus, VectorSearchResponse } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

/**
 * Helper to add Bearer authorization header if token exists
 */
function getHeaders(token?: string | null, isJson = true): HeadersInit {
  const headers: Record<string, string> = {};
  if (isJson) {
    headers["Content-Type"] = "application/json";
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

/**
 * Register new user
 */
export async function registerUser(email: string, password: string): Promise<User> {
  const res = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || "Registration failed.");
  }

  return res.json();
}

/**
 * Login user and receive JWT access token
 */
export async function loginUser(email: string, password: string): Promise<AuthToken> {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData.toString(),
  });

  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || "Login failed. Invalid credentials.");
  }

  return res.json();
}

/**
 * Fetch current user profile details
 */
export async function fetchCurrentUser(token: string): Promise<User> {
  const res = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: getHeaders(token),
  });

  if (!res.ok) {
    throw new Error("Failed to fetch user profile.");
  }

  return res.json();
}

/**
 * Fetch user persistent chat history
 */
export async function fetchChatHistory(token: string): Promise<ChatMessage[]> {
  const res = await fetch(`${API_BASE_URL}/chat/history?limit=50`, {
    headers: getHeaders(token),
  });

  if (!res.ok) {
    throw new Error("Failed to load chat history.");
  }

  return res.json();
}

/**
 * Upload document for asynchronous Celery ingestion
 */
export async function uploadDocument(file: File, token: string): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: "POST",
    headers: getHeaders(token, false),
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || "Document upload failed.");
  }

  return res.json();
}

/**
 * Fetch task execution status from Redis
 */
export async function fetchTaskStatus(taskId: string, token: string): Promise<TaskStatus> {
  const res = await fetch(`${API_BASE_URL}/documents/tasks/${taskId}`, {
    headers: getHeaders(token),
  });

  if (!res.ok) {
    throw new Error("Failed to query task status.");
  }

  return res.json();
}

/**
 * Query ChromaDB vector search
 */
export async function searchVectorDatabase(query: string, token: string): Promise<VectorSearchResponse> {
  const encodedQuery = encodeURIComponent(query);
  const res = await fetch(`${API_BASE_URL}/documents/search?query=${encodedQuery}`, {
    headers: getHeaders(token),
  });

  if (!res.ok) {
    throw new Error("Vector search request failed.");
  }

  return res.json();
}

/**
 * Stream real-time Server-Sent Events (SSE) AI Agent tokens
 */
export async function streamChatAgent(
  query: string,
  token: string,
  onToken: (token: string) => void,
  onEnd: () => void,
  onError: (error: string) => void
): Promise<AbortController> {
  const controller = new AbortController();
  const encodedQuery = encodeURIComponent(query);
  const url = `${API_BASE_URL}/chat/stream?query=${encodedQuery}`;

  try {
    const response = await fetch(url, {
      method: "GET",
      headers: getHeaders(token),
      signal: controller.signal,
    });

    if (!response.ok) {
      if (response.status === 429) {
        throw new Error("Rate limit exceeded. Please wait 1 minute before sending another query.");
      }
      throw new Error(`HTTP Error ${response.status}: Failed to establish SSE stream.`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder("utf-8");

    if (!reader) {
      throw new Error("ReadableStream is not supported by browser.");
    }

    let buffer = "";

    // Asynchronously read response stream chunks
    (async () => {
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n\n");

          // Process complete SSE frames
          buffer = lines.pop() || "";

          for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith("data: ")) {
              const dataStr = trimmed.slice(6);
              try {
                const parsed = JSON.parse(dataStr);
                if (parsed.token) {
                  onToken(parsed.token);
                } else if (parsed.type === "end") {
                  onEnd();
                } else if (parsed.type === "error") {
                  onError(parsed.message || "Streaming error.");
                }
              } catch {
                // If payload is plain text
                onToken(dataStr);
              }
            }
          }
        }
        onEnd();
      } catch (err: any) {
        if (err.name !== "AbortError") {
          onError(err.message || "Streaming interrupted.");
        }
      }
    })();

  } catch (err: any) {
    onError(err.message || "Failed to connect to streaming API.");
  }

  return controller;
}
