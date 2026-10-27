import React from "react";
import type { Message } from "../types";
import { ExportButton } from "./ExportButton";

interface StatusBarProps {
  status: boolean;
  sessionId: string | null;
  messages: Message[];
}

export const StatusBar: React.FC<StatusBarProps> = ({ status, sessionId, messages }) => {
  return (
    <footer className="py-2.5 pb-3 px-4 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex items-center justify-between text-xs text-slate-700 dark:text-slate-200">
      {/* Backend connection status */}
      <div className="flex items-center gap-2">
        <span
          className={`w-2.5 h-2.5 rounded-full ${
            status
              ? "bg-emerald-500 shadow-xs shadow-emerald-500/50"
              : "bg-red-500 shadow-xs shadow-red-500/50"
          }`}
        />
        <span className="font-semibold text-slate-800 dark:text-slate-100">
          {status ? "Backend connected" : "Backend not reachable"}
        </span>
      </div>

      {/* Session ID & Export button */}
      <div className="flex items-center gap-4">
        <div className="text-slate-600 dark:text-slate-300">
          <span>Session: </span>
          <code className="font-mono text-slate-900 dark:text-slate-100 font-bold bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded">
            {sessionId ? sessionId.slice(0, 8) : "connecting..."}
          </code>
        </div>
        <ExportButton messages={messages} />
      </div>
    </footer>
  );
};
