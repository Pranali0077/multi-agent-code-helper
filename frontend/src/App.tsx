import { useState, useEffect } from "react";
import { useChat } from "./hooks/useChat";
import { useHealth } from "./hooks/useHealth";
import { TeamSidebar } from "./components/TeamSidebar";
import { ChatPanel } from "./components/ChatPanel";
import { TracePanel } from "./components/TracePanel";
import { StatusBar } from "./components/StatusBar";
import { ErrorBanner } from "./components/ErrorBanner";

export function App() {
  const {
    messages,
    loading,
    sessionId,
    activeAgent,
    selectedMessageId,
    setSelectedMessageId,
    error,
    setError,
    send,
    retry,
    newChat,
  } = useChat();

  const isHealthy = useHealth(15000);
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Close drawer on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && drawerOpen) {
        setDrawerOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [drawerOpen]);

  const handlePickChip = (chip: string) => {
    send(chip);
  };

  // Find the selected message for trace panel
  const selectedMessage = messages.find((m) => m.id === selectedMessageId);
  const selectedTrace = selectedMessage?.trace;

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-100 dark:bg-slate-950 text-slate-800 dark:text-slate-100 font-sans">
      {/* Desktop Sidebar (Left) */}
      <div className="hidden lg:block h-full shrink-0">
        <TeamSidebar
          activeAgent={activeAgent}
          onNewChat={newChat}
          onPickExample={handlePickChip}
        />
      </div>

      {/* Mobile Drawer */}
      {drawerOpen && (
        <div className="fixed inset-0 z-50 flex lg:hidden">
          <div
            className="fixed inset-0 bg-black/40 backdrop-blur-xs transition-opacity"
            onClick={() => setDrawerOpen(false)}
            aria-hidden="true"
          />
          <div
            role="dialog"
            aria-modal="true"
            aria-label="Team Sidebar Drawer"
            className="relative z-10 h-full w-72 shadow-2xl bg-white dark:bg-slate-950"
          >
            <TeamSidebar
              activeAgent={activeAgent}
              onNewChat={() => {
                newChat();
                setDrawerOpen(false);
              }}
              onPickExample={(chip) => {
                handlePickChip(chip);
                setDrawerOpen(false);
              }}
              onCloseDrawer={() => setDrawerOpen(false)}
            />
          </div>
        </div>
      )}

      {/* Main Content: Chat Center + Status Bar */}
      <main className="flex-1 flex flex-col h-full min-w-0">
        {/* Error Notification Banner if any */}
        {error && (
          <ErrorBanner message={error} onDismiss={() => setError(null)} />
        )}

        {/* Center: Chat + Right Trace Panel (Desktop) */}
        <div className="flex-1 flex min-h-0 overflow-hidden">
          <ChatPanel
            messages={messages}
            loading={loading}
            selectedMessageId={selectedMessageId}
            onSend={send}
            onSelect={(id) => setSelectedMessageId(id)}
            onRetry={retry}
            onPickChip={handlePickChip}
            onOpenSidebar={() => setDrawerOpen(true)}
          />

          {/* Desktop Right Trace Panel */}
          <div className="hidden lg:block h-full shrink-0">
            <TracePanel
              trace={selectedTrace}
              onClose={() => setSelectedMessageId(null)}
            />
          </div>
        </div>

        {/* Bottom Status Bar */}
        <StatusBar
          status={isHealthy}
          sessionId={sessionId}
          messages={messages}
        />
      </main>
    </div>
  );
}

export default App;
