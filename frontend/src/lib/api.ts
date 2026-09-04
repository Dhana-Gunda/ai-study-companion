export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Citation {
  episode: string;
  guest: string;
  timestamp: string;
  score: number;
}

export interface Artifact {
  id?: string;
  title: string;
  artifact_type: "markdown" | "html";
  content: string;
}

export interface Message {
  id?: string;
  role: "user" | "assistant" | "system";
  content: string;
  sources?: Citation[];
  artifacts?: Artifact[];
  created_at?: string;
}

export interface HealthData {
  status: string;
  database: { connected: boolean; mode: string };
  ollama: { connected: boolean; active_model?: string; available_models?: string[] };
  cloud_providers: {
    anthropic: { configured: boolean; model: string };
    openai: { configured: boolean; model: string };
  };
  indexed_chunks: number;
  version: string;
}

export async function fetchHealth(): Promise<HealthData> {
  const res = await fetch(`${API_BASE_URL}/api/health`);
  if (!res.ok) throw new Error("Failed to fetch health probe");
  return res.json();
}

export async function fetchSessions(): Promise<Session[]> {
  const res = await fetch(`${API_BASE_URL}/api/sessions`);
  if (!res.ok) throw new Error("Failed to fetch sessions");
  return res.json();
}

export async function createNewSession(title?: string): Promise<Session> {
  const res = await fetch(`${API_BASE_URL}/api/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: title || "New Conversation" }),
  });
  if (!res.ok) throw new Error("Failed to create session");
  return res.json();
}

export async function fetchSessionDetails(sessionId: string): Promise<Session & { messages: Message[] }> {
  const res = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`);
  if (!res.ok) throw new Error("Failed to load session details");
  return res.json();
}

export async function deleteSession(sessionId: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete session");
}
