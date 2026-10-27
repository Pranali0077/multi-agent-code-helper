import React from "react";
import type { Message } from "../types";
import { formatExportMarkdown, downloadMarkdown } from "../lib/exportMarkdown";

interface ExportButtonProps {
  messages: Message[];
}

export const ExportButton: React.FC<ExportButtonProps> = ({ messages }) => {
  const hasAnswers = messages.some((m) => m.role === "assistant" && m.text);

  const handleExport = () => {
    const md = formatExportMarkdown(messages);
    downloadMarkdown("sample_questions.md", md);
  };

  return (
    <button
      type="button"
      onClick={handleExport}
      disabled={!hasAnswers}
      aria-label="Export chat to markdown"
      title={hasAnswers ? "Export conversation to sample_questions.md" : "No responses to export yet"}
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
    >
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
      </svg>
      Export
    </button>
  );
};
