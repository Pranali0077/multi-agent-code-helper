import type { TraceStep } from "../types";

export interface HealthResponse {
  status: string;
  agents: number;
}

export interface SessionResponse {
  session_id: string;
}

export interface ChatResponse {
  answer: string;
  agent: string;
  trace: TraceStep[];
}

export class ApiError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.status = status;
  }
}

async function fetchWithTimeout(url: string, options: RequestInit = {}, timeoutMs = 90000): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    return response;
  } catch (err: unknown) {
    if (err instanceof Error && err.name === "AbortError") {
      throw new ApiError("The request took too long. Try again.");
    }
    throw new ApiError("Cannot reach the backend. Is `uvicorn server:app --port 8000` running?");
  } finally {
    clearTimeout(id);
  }
}

export async function checkHealth(): Promise<HealthResponse> {
  const res = await fetchWithTimeout("/api/health", { method: "GET" }, 10000);
  if (!res.ok) {
    throw new ApiError(`Health check failed with status ${res.status}`, res.status);
  }
  return res.json();
}

export async function createSession(): Promise<string> {
  const res = await fetchWithTimeout("/api/sessions", { method: "POST" }, 15000);
  if (!res.ok) {
    throw new ApiError(`Failed to create session with status ${res.status}`, res.status);
  }
  const data: SessionResponse = await res.json();
  return data.session_id;
}

export async function sendChatMessage(sessionId: string, message: string): Promise<ChatResponse> {
  const res = await fetchWithTimeout(
    "/api/chat",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message }),
    },
    90000
  );

  if (!res.ok) {
    if (res.status === 429) {
      throw new ApiError("Too many requests. Wait a minute and try again.", 429);
    }
    let errorDetail = `Request failed (${res.status})`;
    try {
      const errJson = await res.json();
      if (errJson.detail) {
        errorDetail = typeof errJson.detail === "string" ? errJson.detail : JSON.stringify(errJson.detail);
      }
    } catch {
      // ignore json parse error on response
    }
    throw new ApiError(errorDetail, res.status);
  }

  return res.json();
}
