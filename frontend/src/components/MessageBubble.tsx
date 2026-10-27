import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import type { Message } from "../types";
import { AGENTS } from "../data/agents";
import { MermaidBlock } from "./MermaidBlock";

interface MessageBubbleProps {
  message: Message;
  selected?: boolean;
  onSelect?: () => void;
  onRetry?: (text: string) => void;
}

const AGENT_COLOR_MAP: Record<string, { bg: string; text: string; border: string }> = {
  coordinator: { bg: "bg-slate-100 dark:bg-slate-800", text: "text-slate-700 dark:text-slate-300", border: "border-slate-300 dark:border-slate-700" },
  code_searcher: { bg: "bg-blue-50 dark:bg-blue-950/40", text: "text-blue-700 dark:text-blue-300", border: "border-blue-300 dark:border-blue-800" },
  code_explainer: { bg: "bg-emerald-50 dark:bg-emerald-950/40", text: "text-emerald-700 dark:text-emerald-300", border: "border-emerald-300 dark:border-emerald-800" },
  architecture_mapper: { bg: "bg-purple-50 dark:bg-purple-950/40", text: "text-purple-700 dark:text-purple-300", border: "border-purple-300 dark:border-purple-800" },
  onboarding_guide: { bg: "bg-amber-50 dark:bg-amber-950/40", text: "text-amber-700 dark:text-amber-300", border: "border-amber-300 dark:border-amber-800" },
};

function tryParseMarkdownTable(text: string) {
  const lines = text.trim().split("\n").map((l) => l.trim()).filter(Boolean);
  if (lines.length >= 2 && lines.every((l) => l.startsWith("|") && l.endsWith("|"))) {
    const separatorLine = lines[1];
    if (/^\|[\s\-:|]+\|$/.test(separatorLine)) {
      const headers = lines[0].slice(1, -1).split("|").map((c) => c.trim());
      const rows = lines.slice(2).map((r) => r.slice(1, -1).split("|").map((c) => c.trim()));
      return { headers, rows };
    }
  }
  return null;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  selected,
  onSelect,
  onRetry,
}) => {
  const [copied, setCopied] = useState(false);
  const [showMobileTrace, setShowMobileTrace] = useState(false);
  const isUser = message.role === "user";

  const handleCopy = () => {
    navigator.clipboard.writeText(message.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (isUser) {
    return (
      <div className="flex justify-end my-3">
        <div className="max-w-2xl px-4 py-3 rounded-2xl bg-blue-600 text-white shadow-xs text-sm whitespace-pre-wrap leading-relaxed">
          {message.text}
        </div>
      </div>
    );
  }

  const agentMeta = AGENTS.find((a) => a.name === message.agent) || {
    name: message.agent || "coordinator",
    label: message.agent || "Coordinator",
    color: "slate",
  };

  const colors = AGENT_COLOR_MAP[agentMeta.name] || AGENT_COLOR_MAP.coordinator;

  return (
    <div
      onClick={onSelect}
      className={`group relative flex flex-col my-4 p-4 rounded-2xl border transition-all cursor-pointer ${
        selected
          ? "border-blue-500/80 ring-2 ring-blue-500/20 bg-slate-50/50 dark:bg-slate-900/60"
          : "border-slate-200/80 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-white dark:bg-slate-900"
      }`}
    >
      {/* Header: Agent badge + Actions */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${colors.bg} ${colors.text} ${colors.border}`}>
            <span className="w-1.5 h-1.5 rounded-full bg-current" />
            {agentMeta.label}
          </span>
          {message.trace && message.trace.length > 0 && (
            <span className="text-xs text-slate-400">
              • {message.trace.length} action{message.trace.length > 1 ? "s" : ""} taken
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {message.trace && message.trace.length > 0 && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                setShowMobileTrace(!showMobileTrace);
              }}
              aria-label="Toggle mobile trace"
              className="lg:hidden text-xs text-blue-600 dark:text-blue-400 hover:underline"
            >
              {showMobileTrace ? "Hide trace" : "Show trace"}
            </button>
          )}
          {message.text && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleCopy();
              }}
              type="button"
              aria-label="Copy response"
              className="opacity-0 group-hover:opacity-100 text-xs px-2 py-1 rounded text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-opacity flex items-center gap-1"
            >
              {copied ? (
                <span className="text-emerald-500 font-medium">Copied!</span>
              ) : (
                <span>Copy</span>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Body: Thinking, Error, or Markdown Content */}
      {message.error ? (
        <div className="text-sm text-red-600 dark:text-red-400 py-2">
          <p className="mb-2">{message.error}</p>
          {onRetry && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onRetry(message.text);
              }}
              type="button"
              className="px-3 py-1 text-xs font-medium rounded-lg bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 hover:bg-red-200 transition-colors"
            >
              Retry
            </button>
          )}
        </div>
      ) : !message.text ? (
        <div className="flex items-center gap-2 py-3 text-sm text-slate-400 animate-pulse">
          <span className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" />
          <span className="w-2 h-2 rounded-full bg-blue-500 animate-bounce [animation-delay:0.2s]" />
          <span className="w-2 h-2 rounded-full bg-blue-500 animate-bounce [animation-delay:0.4s]" />
          <span className="ml-1 text-xs">Analyzing codebase...</span>
        </div>
      ) : (
        <div className="markdown text-slate-800 dark:text-slate-200 overflow-x-auto">
          <ReactMarkdown
            rehypePlugins={[rehypeHighlight]}
            components={{
              a: ({ node, ...props }) => (
                <a {...props} target="_blank" rel="noreferrer" className="text-blue-500 underline hover:text-blue-600" />
              ),
              p: ({ node, children, ...props }) => {
                if (typeof children === "string") {
                  const tableData = tryParseMarkdownTable(children);
                  if (tableData) {
                    return (
                      <div className="overflow-x-auto my-3">
                        <table>
                          <thead>
                            <tr>
                              {tableData.headers.map((h, i) => (
                                <th key={i}>{h}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {tableData.rows.map((row, rIdx) => (
                              <tr key={rIdx}>
                                {row.map((cell, cIdx) => (
                                  <td key={cIdx}>{cell}</td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    );
                  }
                }
                return <p {...props}>{children}</p>;
              },
              pre: ({ children }: any) => <>{children}</>,
              code: ({ node, className, children, ...props }: any) => {
                const match = /language-(\w+)/.exec(className || "");
                const codeString = String(children).replace(/\n$/, "");

                // Check for mermaid diagram fence
                if (match && match[1] === "mermaid") {
                  return <MermaidBlock code={codeString} />;
                }

                // Inline code
                if (!match && !codeString.includes("\n")) {
                  return (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                }

                // Block code with copy button
                return (
                  <div className="relative group/code my-2">
                    <pre className="!mt-0 !mb-0 overflow-x-auto">
                      <code className={className} {...props}>
                        {children}
                      </code>
                    </pre>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigator.clipboard.writeText(codeString);
                      }}
                      className="absolute top-2 right-2 px-2 py-1 text-[10px] font-medium rounded bg-slate-800/80 text-slate-300 hover:text-white border border-slate-700 opacity-0 group-hover/code:opacity-100 transition-opacity"
                    >
                      Copy code
                    </button>
                  </div>
                );
              },
            }}
          >
            {message.text}
          </ReactMarkdown>
        </div>
      )}

      {/* Mobile inline collapsible trace */}
      {showMobileTrace && message.trace && message.trace.length > 0 && (
        <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-800 lg:hidden space-y-2">
          <div className="text-xs font-bold text-slate-700 dark:text-slate-300">
            Execution Steps ({message.trace.length})
          </div>
          {message.trace.map((step, idx) => (
            <div key={idx} className="p-2 rounded-lg bg-slate-50 dark:bg-slate-950 text-xs border border-slate-200 dark:border-slate-800">
              {step.kind === "route" && (
                <span>Route: <span className="font-mono">{step.from}</span> → <span className="font-mono font-bold text-blue-600">{step.to}</span></span>
              )}
              {step.kind === "tool_call" && (
                <div>
                  <span className="font-semibold text-amber-600 dark:text-amber-400">Tool: </span>
                  <span className="font-mono">{step.name}</span>
                </div>
              )}
              {step.kind === "tool_result" && (
                <div>
                  <span className="font-semibold text-emerald-600 dark:text-emerald-400">Result: </span>
                  <span className="font-mono text-slate-600 dark:text-slate-400 truncate block">{step.preview}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
