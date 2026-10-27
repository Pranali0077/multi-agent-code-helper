import React from "react";
import { AgentCard } from "./AgentCard";
import { AGENTS } from "../data/agents";

interface TeamSidebarProps {
  activeAgent: string | null;
  onNewChat: () => void;
  onPickExample?: (example: string) => void;
  onCloseDrawer?: () => void;
}

export const TeamSidebar: React.FC<TeamSidebarProps> = ({
  activeAgent,
  onNewChat,
  onPickExample,
  onCloseDrawer,
}) => {
  return (
    <aside className="w-72 h-full flex flex-col bg-slate-50 dark:bg-slate-950 border-r border-slate-200 dark:border-slate-800 p-4 pt-4">
      {/* Sidebar header with top padding */}
      <div className="flex items-center justify-between pt-3 pb-3 mb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-sm font-bold tracking-tight text-slate-800 dark:text-slate-100">
            Agent Team
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">5 specialized ADK agents</p>
        </div>
        {onCloseDrawer && (
          <button
            onClick={onCloseDrawer}
            aria-label="Close sidebar"
            className="p-1 rounded text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 lg:hidden"
          >
            ✕
          </button>
        )}
      </div>

      <button
        onClick={onNewChat}
        className="w-full mb-4 py-2 px-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 text-sm font-medium transition-colors shadow-sm flex items-center justify-center gap-2"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        New Chat
      </button>

      <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
        {AGENTS.map((agent) => (
          <AgentCard
            key={agent.name}
            agent={agent}
            active={activeAgent === agent.name}
            onPickExample={onPickExample}
          />
        ))}
      </div>
    </aside>
  );
};
