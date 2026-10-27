import React, { useEffect, useState } from "react";
import mermaid from "mermaid";

interface MermaidBlockProps {
  code: string;
}

function initMermaid(isDark: boolean) {
  mermaid.initialize({
    startOnLoad: false,
    theme: isDark ? "dark" : "default",
    securityLevel: "loose",
    fontFamily: "system-ui, sans-serif",
  });
}

export const MermaidBlock: React.FC<MermaidBlockProps> = ({ code }) => {
  const [svg, setSvg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const idRef = React.useRef(`mermaid_${Math.random().toString(36).substring(2, 9)}`);
  const uniqueId = idRef.current;

  useEffect(() => {
    let isMounted = true;
    const isDark =
      (typeof document !== "undefined" && document.documentElement.classList.contains("dark")) ||
      (typeof window !== "undefined" && typeof window.matchMedia === "function" && window.matchMedia("(prefers-color-scheme: dark)").matches);

    initMermaid(isDark);

    const renderDiagram = async () => {
      try {
        setError(null);
        const res = await mermaid.render(uniqueId, code.trim());
        if (isMounted) {
          if (res && res.svg) {
            setSvg(res.svg);
          } else {
            throw new Error("No diagram SVG generated");
          }
        }
      } catch (err: unknown) {
        if (isMounted) {
          console.error("Mermaid parse error:", err);
          setError("Failed to render diagram. Falling back to raw Mermaid definition.");
          setSvg(null);
        }
      }
    };

    renderDiagram();

    return () => {
      isMounted = false;
      const el = document.getElementById(uniqueId);
      if (el) el.remove();
      const bindEl = document.getElementById("d" + uniqueId);
      if (bindEl) bindEl.remove();
    };
  }, [code]);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/90 shadow-xs overflow-hidden">
      <div className="flex items-center justify-between px-3 py-2 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/60 text-xs">
        <span className="font-semibold text-purple-600 dark:text-purple-400 flex items-center gap-1.5">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
          </svg>
          Architecture Diagram
        </span>
        <button
          onClick={handleCopy}
          type="button"
          aria-label="Copy mermaid definition"
          className="px-2 py-1 rounded text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors text-[11px] font-medium"
        >
          {copied ? "Copied Mermaid!" : "Copy mermaid"}
        </button>
      </div>

      <div className="p-4 overflow-x-auto flex justify-center">
        {error ? (
          <div className="w-full text-left">
            <div className="text-xs text-amber-600 dark:text-amber-400 mb-2 font-medium">
              ⚠️ {error}
            </div>
            <pre className="p-3 rounded-lg bg-slate-100 dark:bg-slate-950 font-mono text-xs text-slate-700 dark:text-slate-300 overflow-x-auto">
              {code}
            </pre>
          </div>
        ) : svg ? (
          <div
            className="w-full flex justify-center [&>svg]:max-w-full [&>svg]:h-auto"
            dangerouslySetInnerHTML={{ __html: svg }}
          />
        ) : (
          <div className="py-6 text-xs text-slate-400 animate-pulse">
            Rendering diagram...
          </div>
        )}
      </div>
    </div>
  );
};
