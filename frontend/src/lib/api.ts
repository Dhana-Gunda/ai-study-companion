export const API_BASE_URL = credentialsBaseUrl();

function credentialsBaseUrl(): string {
  if (typeof window !== "undefined") {
    return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
  }
  return process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
}

function getAuthToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("token") || sessionStorage.getItem("token");
  }
  return null;
}

export function setAuthToken(token: string, remember: boolean = true) {
  if (typeof window !== "undefined") {
    if (remember) {
      localStorage.setItem("token", token);
    } else {
      sessionStorage.setItem("token", token);
    }
  }
}

export function clearAuthToken() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("token");
    sessionStorage.removeItem("token");
  }
}

async function authFetch(endpoint: string, options: RequestInit = {}): Promise<Response> {
  const token = getAuthToken();
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const url = endpoint.startsWith("http") ? endpoint : `${API_BASE_URL}${endpoint}`;
  return fetch(url, { ...options, headers });
}

// -------------------------------------------------------------
// Health Check
// -------------------------------------------------------------
export interface HealthCheckResponse {
  status: "healthy" | "degraded" | "unhealthy";
  timestamp: string;
  latency_ms: number;
  services: {
    database: {
      status: string;
      dialect?: string;
      pgvector_enabled?: boolean;
      fallback_mode?: boolean;
      error?: string;
    };
    redis: {
      status: string;
      ping?: boolean;
      url?: string;
    };
    ai_providers: {
      openai: { configured: boolean; model: string };
      anthropic: { configured: boolean; model: string };
      default_provider: string;
    };
  };
  environment: string;
  version: string;
}

export async function checkBackendHealth(): Promise<HealthCheckResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/health`, { cache: "no-store" });
    return await res.json();
  } catch (err: any) {
    return {
      status: "unhealthy",
      timestamp: new Date().toISOString(),
      latency_ms: 0,
      services: {
        database: { status: "disconnected", error: err.message },
        redis: { status: "disconnected" },
        ai_providers: {
          openai: { configured: false, model: "unknown" },
          anthropic: { configured: false, model: "unknown" },
          default_provider: "unknown",
        },
      },
      environment: "unknown",
      version: "unknown",
    };
  }
}

// -------------------------------------------------------------
// Auth APIs
// -------------------------------------------------------------
export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export async function loginUser(email: string, password: string): Promise<AuthResponse> {
  const res = await authFetch("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Login failed" }));
    throw new Error(err.detail || "Invalid email or password");
  }
  const data: AuthResponse = await res.json();
  setAuthToken(data.access_token);
  return data;
}

export async function registerUser(email: string, password: string, name: string): Promise<AuthResponse> {
  const res = await authFetch("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, name }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Registration failed" }));
    throw new Error(err.detail || "Registration failed");
  }
  const data: AuthResponse = await res.json();
  setAuthToken(data.access_token);
  return data;
}

export async function getCurrentUser(): Promise<User | null> {
  const token = getAuthToken();
  if (!token) return null;
  const res = await authFetch("/api/v1/auth/me");
  if (!res.ok) {
    clearAuthToken();
    return null;
  }
  return await res.json();
}

// -------------------------------------------------------------
// Spaces APIs
// -------------------------------------------------------------
export interface Space {
  id: string;
  name: string;
  description?: string;
  user_id: string;
  projects_count: number;
  created_at: string;
  updated_at: string;
}

export async function getSpaces(): Promise<Space[]> {
  const res = await authFetch("/api/v1/spaces");
  if (!res.ok) throw new Error("Failed to load learning spaces");
  return await res.json();
}

export async function createSpace(name: string, description?: string): Promise<Space> {
  const res = await authFetch("/api/v1/spaces", {
    method: "POST",
    body: JSON.stringify({ name, description }),
  });
  if (!res.ok) throw new Error("Failed to create space");
  return await res.json();
}

export async function deleteSpace(spaceId: string): Promise<void> {
  const res = await authFetch(`/api/v1/spaces/${spaceId}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete space");
}

// -------------------------------------------------------------
// Projects APIs
// -------------------------------------------------------------
export interface Project {
  id: string;
  space_id: string;
  user_id: string;
  name: string;
  description?: string;
  learning_goal: string;
  created_at: string;
  updated_at: string;
  materials_count: number;
  concepts_count: number;
}

export interface ProjectDashboard {
  project: Project;
  overall_mastery_percentage: number;
  materials_count: number;
  concepts_count: number;
  weak_concepts: Array<{
    concept_id: string;
    name: string;
    score: number;
    trend: string;
    confidence: number;
  }>;
  recent_events: Array<{
    id: string;
    event_type: string;
    payload: any;
    created_at: string;
  }>;
  active_recommendation?: {
    id: string;
    action_type: string;
    headline: string;
    description: string;
    cta_label: string;
    status: string;
  };
  learning_context: any;
}

export async function getAllProjects(): Promise<Project[]> {
  const res = await authFetch("/api/v1/projects");
  if (!res.ok) throw new Error("Failed to load projects");
  return await res.json();
}

export async function getSpaceProjects(spaceId: string): Promise<Project[]> {
  const res = await authFetch(`/api/v1/spaces/${spaceId}/projects`);
  if (!res.ok) throw new Error("Failed to load space projects");
  return await res.json();
}

export async function createProject(spaceId: string, name: string, learningGoal: string, description?: string): Promise<Project> {
  const res = await authFetch(`/api/v1/spaces/${spaceId}/projects`, {
    method: "POST",
    body: JSON.stringify({ name, learning_goal: learningGoal, description }),
  });
  if (!res.ok) throw new Error("Failed to create project");
  return await res.json();
}

export async function getProjectDashboard(projectId: string): Promise<ProjectDashboard> {
  const res = await authFetch(`/api/v1/projects/${projectId}/dashboard`);
  if (!res.ok) throw new Error("Failed to load project dashboard");
  return await res.json();
}

// -------------------------------------------------------------
// Materials APIs
// -------------------------------------------------------------
export interface Material {
  id: string;
  project_id: string;
  filename: string;
  file_size_bytes: number;
  status: "QUEUED" | "PROCESSING" | "READY" | "FAILED";
  page_count: number;
  error_message?: string;
  created_at: string;
}

export async function getProjectMaterials(projectId: string): Promise<Material[]> {
  const res = await authFetch(`/api/v1/projects/${projectId}/materials`);
  if (!res.ok) throw new Error("Failed to load project materials");
  return await res.json();
}

export async function uploadMaterial(projectId: string, file: File): Promise<Material> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await authFetch(`/api/v1/projects/${projectId}/materials/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Failed to upload document");
  }
  return await res.json();
}

export async function getMaterialStatus(projectId: string, materialId: string): Promise<any> {
  const res = await authFetch(`/api/v1/projects/${projectId}/materials/${materialId}/status`);
  if (!res.ok) throw new Error("Failed to check material status");
  return await res.json();
}

// -------------------------------------------------------------
// AI Tutor & Citations SSE Streaming
// -------------------------------------------------------------
export interface Citation {
  chunk_id?: string;
  filename: string;
  page_number: number;
  similarity?: number;
}

export interface Conversation {
  id: string;
  project_id: string;
  title: string;
  created_at: string;
  messages: Array<{
    id: string;
    role: "user" | "assistant";
    content: string;
    sources?: Citation[];
    created_at: string;
  }>;
}

export async function getConversations(projectId: string): Promise<Conversation[]> {
  const res = await authFetch(`/api/v1/projects/${projectId}/conversations`);
  if (!res.ok) throw new Error("Failed to load conversations");
  return await res.json();
}

export async function streamTutorChat(
  projectId: string,
  message: string,
  conversationId: string | null,
  onToken: (token: string) => void,
  onDone: (data: { conversation_id: string; citations: Citation[]; refused?: boolean }) => void,
  onError: (err: Error) => void
) {
  try {
    const token = getAuthToken();
    const response = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}/tutor/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });

    if (!response.ok) {
      throw new Error(`Chat error: HTTP ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error("No response stream reader available");

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const jsonStr = line.slice(6).trim();
          if (!jsonStr) continue;
          try {
            const parsed = JSON.parse(jsonStr);
            if (parsed.token) {
              onToken(parsed.token);
            }
            if (parsed.done) {
              onDone(parsed);
            }
          } catch (e) {
            console.error("Error parsing SSE data line", e);
          }
        }
      }
    }
  } catch (err: any) {
    onError(err);
  }
}

// -------------------------------------------------------------
// Adaptive Quizzes & Mastery APIs
// -------------------------------------------------------------
export interface QuizQuestion {
  id: string;
  session_id: string;
  concept_id?: string;
  question_type: "MCQ" | "OPEN_ENDED";
  prompt: string;
  options?: string[];
  user_answer?: string;
  score?: number;
  feedback?: string;
}

export interface QuizSession {
  id: string;
  project_id: string;
  status: "IN_PROGRESS" | "COMPLETED";
  score?: number;
  created_at: string;
  completed_at?: string;
  questions: QuizQuestion[];
}

export async function startQuiz(projectId: string, count: number = 3): Promise<QuizSession> {
  const res = await authFetch(`/api/v1/projects/${projectId}/quizzes/start`, {
    method: "POST",
    body: JSON.stringify({ question_count: count }),
  });
  if (!res.ok) throw new Error("Failed to start quiz session");
  return await res.json();
}

export async function getQuiz(sessionId: string): Promise<QuizSession> {
  const res = await authFetch(`/api/v1/quizzes/${sessionId}`);
  if (!res.ok) throw new Error("Failed to fetch quiz");
  return await res.json();
}

export async function submitQuizAnswer(sessionId: string, questionId: string, answer: string): Promise<any> {
  const res = await authFetch(`/api/v1/quizzes/${sessionId}/questions/${questionId}/answer`, {
    method: "POST",
    body: JSON.stringify({ user_answer: answer }),
  });
  if (!res.ok) throw new Error("Failed to submit answer");
  return await res.json();
}

export async function completeQuiz(sessionId: string): Promise<QuizSession> {
  const res = await authFetch(`/api/v1/quizzes/${sessionId}/complete`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to complete quiz");
  return await res.json();
}

export interface ConceptMastery {
  concept_id: string;
  name: string;
  description?: string;
  mastery_score: number;
  confidence_level: number;
  trend: "IMPROVING" | "STABLE" | "ATTENTION";
  last_assessed_at?: string;
}

export async function getProjectMastery(projectId: string): Promise<ConceptMastery[]> {
  const res = await authFetch(`/api/v1/projects/${projectId}/mastery`);
  if (!res.ok) throw new Error("Failed to load concept mastery");
  return await res.json();
}

export async function getMasteryHistory(projectId: string): Promise<any[]> {
  const res = await authFetch(`/api/v1/projects/${projectId}/mastery/history`);
  if (!res.ok) throw new Error("Failed to load mastery historical curve");
  return await res.json();
}

export async function getRecommendations(projectId: string): Promise<any[]> {
  const res = await authFetch(`/api/v1/projects/${projectId}/recommendations`);
  if (!res.ok) throw new Error("Failed to load recommendations");
  return await res.json();
}

// -------------------------------------------------------------
// Admin & Observability APIs
// -------------------------------------------------------------
export async function getAdminUsers(): Promise<any[]> {
  const res = await authFetch("/api/v1/admin/users");
  if (!res.ok) throw new Error("Admin access required");
  return await res.json();
}

export async function getAdminAIMetrics(): Promise<any> {
  const res = await authFetch("/api/v1/admin/ai-metrics");
  if (!res.ok) throw new Error("Admin access required");
  return await res.json();
}

export async function getAdminHealth(): Promise<any> {
  const res = await authFetch("/api/v1/admin/health");
  if (!res.ok) throw new Error("Admin access required");
  return await res.json();
}
