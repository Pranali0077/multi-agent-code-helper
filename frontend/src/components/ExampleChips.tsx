import React from "react";
import { EXAMPLE_CHIPS } from "../data/agents";

interface ExampleChipsProps {
  onPick: (question: string) => void;
}

export const ExampleChips: React.FC<ExampleChipsProps> = ({ onPick }) => {
  return (
    <div className="flex flex-col items-center justify-center p-6 text-center max-w-xl mx-auto my-auto">
      <div className="w-12 h-12 rounded-2xl bg-blue-100 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center mb-4 shadow-xs">
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      </div>

      <h3 className="text-base font-semibold text-slate-800 dark:text-slate-100">
        How can the team help you today?
      </h3>
      <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 mb-6 max-w-md">
        Choose an example prompt below or type your own question about the codebase.
      </p>

      <div className="flex flex-wrap gap-2 justify-center">
        {EXAMPLE_CHIPS.map((chip) => (
          <button
            key={chip}
            type="button"
            onClick={() => onPick(chip)}
            className="px-3 py-1.5 rounded-full text-xs font-medium border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 hover:border-blue-500 dark:hover:border-blue-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50/50 dark:hover:bg-blue-950/30 transition-all shadow-2xs cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          >
            {chip}
          </button>
        ))}
      </div>
    </div>
  );
};
