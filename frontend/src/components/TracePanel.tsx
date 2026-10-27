import React, { useState } from "react";
import type { TraceStep } from "../types";

interface TracePanelProps {
  trace?: TraceStep[];
  onClose?: () => void;
}

export const TracePanel: React.FC<TracePanelProps> = ({ trace, onClose }) => {
  const [expandedResults, setExpandedResults] = useState<Record<number, boolean>>({});

  const toggleExpand = (index: number) => {
    setExpandedResults((prev) => ({ ...prev, [index]: !prev[index] }));
  };

  return (
    <aside className="w-80 h-full flex flex-col bg-slate-50 dark:bg-slate-950 border-l border-slate-200 dark:border-slate-800 p-4 pt-4">
      {/* Header */}
      <div className="flex items-center justify-between pt-3 pb-3 mb-3 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-bold tracking-tight text-slate-800 dark:text-slate-100">
            Execution Trace
          </h2>
          {trace && trace.length > 0 && (
            <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
              {trace.length} step{trace.length > 1 ? "s" : ""}
            </span>
          )}
        </div>
        {onClose && (
          <button
            onClick={onClose}
            aria-label="Close trace panel"
            className="p-1 rounded text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
          >
            ✕
          </button>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {!trace || trace.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-center text-xs text-slate-400 p-4">
            <svg className="w-8 h-8 mb-2 text-slate-300 dark:text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="font-medium text-slate-500 dark:text-slate-400">No trace available</p>
            <p className="mt-1">Select an assistant response to view its routing and tool steps.</p>
          </div>
        ) : (
          trace.map((step, idx) => {
            if (step.kind === "route") {
              return (
                <div
                  key={idx}
                  className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs"
                >
                  <div className="flex items-center gap-2 text-xs font-semibold text-slate-700 dark:text-slate-200">
                    <span className="p-1 rounded bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400">
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                      </svg>
                    </span>
                    <span>Route</span>
                  </div>
                  <div className="mt-2 text-xs flex items-center gap-1.5 flex-wrap">
                    <span className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 font-mono text-slate-700 dark:text-slate-300">
                      {step.from}
                    </span>
                    <span className="text-slate-400">→</span>
                    <span className="px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-950 font-mono text-blue-700 dark:text-blue-300 font-medium">
                      {step.to}
                    </span>
                  </div>
                </div>
              );
            }

            if (step.kind === "tool_call") {
              const formattedArgs = typeof step.args === "object" ? JSON.stringify(step.args, null, 2) : String(step.args);
              return (
                <div
                  key={idx}
                  className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs"
                >
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-700 dark:text-slate-200">
                    <div className="flex items-center gap-2">
                      <span className="p-1 rounded bg-amber-100 dark:bg-amber-900/50 text-amber-600 dark:text-amber-400">
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                      </span>
                      <span>Tool Call</span>
                    </div>
                    <span className="text-[10px] text-slate-400 font-mono">{step.agent}</span>
                  </div>
                  <div className="mt-2 text-xs font-mono font-medium text-slate-800 dark:text-slate-200">
                    {step.name}
                  </div>
                  {step.args !== undefined && (
                    <pre className="mt-1.5 p-2 rounded bg-slate-100 dark:bg-slate-800/80 text-[11px] font-mono text-slate-700 dark:text-slate-300 overflow-x-auto max-h-36">
                      {formattedArgs}
                    </pre>
                  )}
                </div>
              );
            }

            if (step.kind === "tool_result") {
              const isExpanded = !!expandedResults[idx];
              const previewText = step.preview || "";
              const shouldTruncate = previewText.length > 120;
              const displayText = shouldTruncate && !isExpanded ? previewText.slice(0, 120) + "..." : previewText;

              return (
                <div
                  key={idx}
                  className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs"
                >
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-700 dark:text-slate-200">
                    <div className="flex items-center gap-2">
                      <span className="p-1 rounded bg-emerald-100 dark:bg-emerald-900/50 text-emerald-600 dark:text-emerald-400">
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </span>
                      <span>Tool Result</span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-400">{step.name}</span>
                  </div>
                  <div className="mt-2 p-2 rounded bg-slate-100 dark:bg-slate-800/80 text-[11px] font-mono text-slate-600 dark:text-slate-300 whitespace-pre-wrap break-words max-h-48 overflow-y-auto">
                    {displayText}
                  </div>
                  {shouldTruncate && (
                    <button
                      type="button"
                      onClick={() => toggleExpand(idx)}
                      className="mt-1 text-[11px] text-blue-600 dark:text-blue-400 hover:underline cursor-pointer"
                    >
                      {isExpanded ? "Show less" : "Show full"}
                    </button>
                  )}
                </div>
              );
            }

            return null;
          })
        )}
      </div>
    </aside>
  );
};
