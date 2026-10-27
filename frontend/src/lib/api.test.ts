import { describe, it, expect, vi, beforeEach } from "vitest";
import { checkHealth, createSession, sendChatMessage } from "./api";

describe("api.ts", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("maps 429 error to friendly message", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 429,
      json: async () => ({ detail: "Rate limit exceeded" }),
    });

    await expect(sendChatMessage("sess-1", "Hello")).rejects.toThrow(
      "Too many requests. Wait a minute and try again."
    );
  });

  it("maps network failure to friendly message", async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error("Failed to fetch"));

    await expect(sendChatMessage("sess-1", "Hello")).rejects.toThrow(
      "Cannot reach the backend. Is `uvicorn server:app --port 8000` running?"
    );
  });

  it("handles successful chat response", async () => {
    const mockChat = {
      answer: "The user class is here.",
      agent: "code_searcher",
      trace: [{ kind: "route", from: "coordinator", to: "code_searcher" }],
    };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockChat,
    });

    const res = await sendChatMessage("sess-1", "Where is the User class defined?");
    expect(res).toEqual(mockChat);
  });

  it("handles health check and session creation", async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ status: "ok", agents: 5 }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ session_id: "test-uuid" }),
      });

    const health = await checkHealth();
    expect(health.status).toBe("ok");
    expect(health.agents).toBe(5);

    const sessionId = await createSession();
    expect(sessionId).toBe("test-uuid");
  });
});
