import React from "react";
import type { AgentInfo } from "../types";

interface AgentCardProps {
  agent: AgentInfo;
  active: boolean;
  onPickExample?: (example: string) => void;
}

const DOT_COLORS: Record<string, string> = {
  slate: "bg-slate-400",
  blue: "bg-blue-500",
  green: "bg-emerald-500",
  purple: "bg-purple-500",
  amber: "bg-amber-500",
};

export const AgentCard: React.FC<AgentCardProps> = ({ agent, active, onPickExample }) => {
  const dotColor = DOT_COLORS[agent.color] || DOT_COLORS.slate;

  return (
    <div
      className={`relative p-3.5 rounded-xl border transition-all ${
        active
          ? "border-blue-500 ring-2 ring-blue-500/20 bg-blue-50/40 dark:bg-blue-950/20"
          : "border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 hover:border-slate-300 dark:hover:border-slate-700"
      }`}
    >
      <div className="flex items-start gap-2.5">
        <span className="relative flex h-2.5 w-2.5 mt-1.5 shrink-0">
          {active && (
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${dotColor}`} />
          )}
          <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${dotColor}`} />
        </span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-100 truncate">
              {agent.label}
            </h4>
            {active && (
              <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">
                Active
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">
            {agent.role}
          </p>
          {agent.example && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                if (onPickExample) {
                  onPickExample(agent.example!);
                }
              }}
              title={`Ask: "${agent.example}"`}
              className="mt-2 text-[11px] text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:underline text-left block truncate w-full cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue-500 rounded px-0.5 py-0.5 transition-colors"
            >
              Ex: "{agent.example}"
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
