import { useState, useEffect, useCallback } from "react";
import type { Message } from "../types";
import { checkHealth, createSession, sendChatMessage, ApiError } from "../lib/api";

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [selectedMessageId, setSelectedMessageId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [backendHealthy, setBackendHealthy] = useState<boolean>(false);

  const initSession = useCallback(async () => {
    try {
      setError(null);
      await checkHealth();
      setBackendHealthy(true);
      const newId = await createSession();
      setSessionId(newId);
      setMessages([]);
      setActiveAgent(null);
      setSelectedMessageId(null);
    } catch (err: unknown) {
      setBackendHealthy(false);
      const msg = err instanceof ApiError ? err.message : "Cannot initialize session";
      setError(msg);
    }
  }, []);

  useEffect(() => {
    initSession();
  }, [initSession]);

  const send = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || loading) return;

      let currentSession = sessionId;
      if (!currentSession) {
        try {
          currentSession = await createSession();
          setSessionId(currentSession);
        } catch (err: unknown) {
          const msg = err instanceof ApiError ? err.message : "Failed to create session";
          setError(msg);
          return;
        }
      }

      const userMsgId = "user-" + Date.now() + "-" + Math.random().toString(36).substring(2, 7);
      const assistantMsgId = "asst-" + Date.now() + "-" + Math.random().toString(36).substring(2, 7);

      const userMessage: Message = {
        id: userMsgId,
        role: "user",
        text: trimmed,
      };

      const placeholderMessage: Message = {
        id: assistantMsgId,
        role: "assistant",
        text: "",
      };

      setMessages((prev) => [...prev, userMessage, placeholderMessage]);
      setLoading(true);
      setError(null);
      // Briefly show coordinator as active while routing starts
      setActiveAgent("coordinator");

      try {
        const res = await sendChatMessage(currentSession, trimmed);
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMsgId
              ? {
                  ...m,
                  text: res.answer,
                  agent: res.agent,
                  trace: res.trace,
                }
              : m
          )
        );
        setActiveAgent(res.agent);
        setSelectedMessageId(assistantMsgId);
      } catch (err: unknown) {
        const errorText = err instanceof ApiError ? err.message : "An unexpected error occurred.";
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMsgId
              ? {
                  ...m,
                  error: errorText,
                }
              : m
          )
        );
        setError(errorText);
      } finally {
        setLoading(false);
      }
    },
    [sessionId, loading]
  );

  const retry = useCallback(
    (text: string) => {
      // Remove any trailing failed assistant message and resend
      setMessages((prev) => {
        if (prev.length > 0 && prev[prev.length - 1].role === "assistant" && prev[prev.length - 1].error) {
          return prev.slice(0, -1);
        }
        return prev;
      });
      send(text);
    },
    [send]
  );

  const newChat = useCallback(async () => {
    await initSession();
  }, [initSession]);

  return {
    messages,
    loading,
    sessionId,
    activeAgent,
    selectedMessageId,
    setSelectedMessageId,
    error,
    setError,
    backendHealthy,
    send,
    retry,
    newChat,
    initSession,
  };
}
