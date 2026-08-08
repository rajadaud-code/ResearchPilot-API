export interface User {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface ChatMessage {
  id?: number;
  user_id?: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
  node_step?: string;
  is_streaming?: boolean;
}

export interface DocumentUploadResponse {
  status: string;
  message: string;
  document_id: string;
  task_id: string;
  filename: string;
  size_bytes: number;
  status_url: string;
}

export interface TaskStatus {
  task_id: string;
  status: 'PENDING' | 'PROGRESS' | 'SUCCESS' | 'FAILURE' | 'REVOKED';
  result: {
    progress?: string;
    current_chunk?: number;
    total_chunks?: number;
    percent_complete?: number;
    file_name?: string;
    chunks_indexed?: number;
    error?: string;
    details?: string;
  };
}

export interface VectorSearchResultItem {
  id: string;
  score: number;
  content: string;
}

export interface VectorSearchResponse {
  status: string;
  query: string;
  results: VectorSearchResultItem[];
}
