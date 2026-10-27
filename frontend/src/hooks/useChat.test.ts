import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { useChat } from "./useChat";
import * as api from "../lib/api";

describe("useChat", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("send appends user message then assistant message on success", async () => {
    vi.spyOn(api, "checkHealth").mockResolvedValue({ status: "ok", agents: 5 });
    vi.spyOn(api, "createSession").mockResolvedValue("mock-session-123");
    vi.spyOn(api, "sendChatMessage").mockResolvedValue({
      answer: "User class found at models/user.py",
      agent: "code_searcher",
      trace: [{ kind: "route", from: "coordinator", to: "code_searcher" }],
    });

    const { result } = renderHook(() => useChat());

    await waitFor(() => {
      expect(result.current.sessionId).toBe("mock-session-123");
    });

    await act(async () => {
      await result.current.send("Where is the User class defined?");
    });

    expect(result.current.messages.length).toBe(2);
    expect(result.current.messages[0].role).toBe("user");
    expect(result.current.messages[0].text).toBe("Where is the User class defined?");
    expect(result.current.messages[1].role).toBe("assistant");
    expect(result.current.messages[1].text).toBe("User class found at models/user.py");
    expect(result.current.messages[1].agent).toBe("code_searcher");
    expect(result.current.activeAgent).toBe("code_searcher");
  });

  it("error keeps the user message and attaches error to assistant message", async () => {
    vi.spyOn(api, "checkHealth").mockResolvedValue({ status: "ok", agents: 5 });
    vi.spyOn(api, "createSession").mockResolvedValue("mock-session-123");
    vi.spyOn(api, "sendChatMessage").mockRejectedValue(
      new api.ApiError("Too many requests. Wait a minute and try again.", 429)
    );

    const { result } = renderHook(() => useChat());

    await waitFor(() => {
      expect(result.current.sessionId).toBe("mock-session-123");
    });

    await act(async () => {
      await result.current.send("Where is the User class defined?");
    });

    expect(result.current.messages.length).toBe(2);
    expect(result.current.messages[0].role).toBe("user");
    expect(result.current.messages[0].text).toBe("Where is the User class defined?");
    expect(result.current.messages[1].role).toBe("assistant");
    expect(result.current.messages[1].error).toBe("Too many requests. Wait a minute and try again.");
    expect(result.current.error).toBe("Too many requests. Wait a minute and try again.");
  });
});
