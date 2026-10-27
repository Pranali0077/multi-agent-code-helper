import React from "react";

interface ErrorBannerProps {
  message: string;
  onDismiss: () => void;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({ message, onDismiss }) => {
  return (
    <div
      role="alert"
      className="px-4 py-2.5 bg-red-50 dark:bg-red-950/40 border-b border-red-200 dark:border-red-900/50 text-red-700 dark:text-red-300 text-xs flex items-center justify-between shadow-2xs transition-all"
    >
      <div className="flex items-center gap-2">
        <svg className="w-4 h-4 text-red-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <span className="font-medium">{message}</span>
      </div>
      <button
        onClick={onDismiss}
        type="button"
        aria-label="Dismiss error banner"
        className="ml-4 p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/40 text-red-500 hover:text-red-700 dark:hover:text-red-200 cursor-pointer"
      >
        ✕
      </button>
    </div>
  );
};
