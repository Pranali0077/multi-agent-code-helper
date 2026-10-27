import React, { useRef, useEffect } from "react";
import type { Message } from "../types";
import { MessageBubble } from "./MessageBubble";
import { ChatInput } from "./ChatInput";
import { ExampleChips } from "./ExampleChips";

interface ChatPanelProps {
  messages: Message[];
  loading: boolean;
  selectedMessageId: string | null;
  onSend: (message: string) => void;
  onSelect: (id: string) => void;
  onRetry: (text: string) => void;
  onPickChip: (chip: string) => void;
  onOpenSidebar?: () => void;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  messages,
  loading,
  selectedMessageId,
  onSend,
  onSelect,
  onRetry,
  onPickChip,
  onOpenSidebar,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const isEmpty = messages.length === 0;

  return (
    <div className="flex-1 flex flex-col h-full bg-slate-50/50 dark:bg-slate-950/50 min-w-0">
      {/* Mobile top bar */}
      <div className="lg:hidden flex items-center justify-between p-3 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
        <button
          onClick={onOpenSidebar}
          aria-label="Open team sidebar"
          className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
          Multi-Agent Code Helper
        </span>
        <div className="w-7" />
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-6" aria-live="polite">
        <div className="max-w-3xl mx-auto">
          {isEmpty ? (
            <ExampleChips onPick={onPickChip} />
          ) : (
            <>
              {messages.map((m) => (
                <MessageBubble
                  key={m.id}
                  message={m}
                  selected={selectedMessageId === m.id}
                  onSelect={() => onSelect(m.id)}
                  onRetry={onRetry}
                />
              ))}
              <div ref={bottomRef} />
            </>
          )}
        </div>
      </div>

      {/* Chat input */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
        <div className="max-w-3xl mx-auto">
          <ChatInput disabled={loading} onSend={onSend} />
        </div>
      </div>
    </div>
  );
};
