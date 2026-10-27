# Frontend Spec — Multi-Agent Code Helper

A single-page chat app for the backend in `implementation.md`. It shows who answered (which of the 5 agents), what they did (tool trace), and renders Mermaid architecture diagrams.

## 1. Stack
React 18, Vite, TypeScript, Tailwind CSS, `react-markdown`, `rehype-highlight` (+ `highlight.js` theme), `mermaid`. No router, no state library, no UI kit. Plain `fetch`.

## 2. Backend contract (do not change)
```
GET  /api/health          -> { "status": "ok", "agents": 5 }
POST /api/sessions        -> { "session_id": string }
POST /api/chat            <- { "session_id": string, "message": string }
                          -> { "answer": string (markdown), "agent": string, "trace": TraceStep[] }
```
```ts
type TraceStep =
  | { kind: "route"; from: string; to: string }
  | { kind: "tool_call"; agent: string; name: string; args: unknown }
  | { kind: "tool_result"; agent: string; name: string; preview: string };

type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
  agent?: string;
  trace?: TraceStep[];
  error?: string;
};
```
Vite dev proxy: `/api` -> `http://localhost:8000`.
Errors: HTTP 429 -> "Too many requests. Wait a minute and try again."; network failure -> "Cannot reach the backend. Is `uvicorn server:app --port 8000` running?"; any other -> show the status and message.

## 3. Agent data (`src/data/agents.ts`)
Names must match the backend exactly.

| name | label | role | color | example question |
|------|-------|------|-------|------------------|
| `coordinator` | Coordinator | Routes each question | slate | (none) |
| `code_searcher` | Code Searcher | Finds code with RAG | blue | Where is the User class defined? |
| `code_explainer` | Code Explainer | Explains files and functions | green | Explain what main.py does. |
| `architecture_mapper` | Architecture Mapper | Structure and Mermaid diagrams | purple | Show me the architecture diagram. |
| `onboarding_guide` | Onboarding Guide | Helps newcomers get started | amber | I am new. Where do I start? |

Each entry also has the one-line description used by the backend.

## 4. Layout
Desktop (>= 1024px): three regions.
```
┌───────────────┬──────────────────────────────┬────────────────┐
│ Team sidebar  │ Chat (messages + input)      │ Trace panel    │
│ 5 agent cards │ example chips (when empty)   │ for selected   │
│ New chat      │                              │ assistant msg  │
├───────────────┴──────────────────────────────┴────────────────┤
│ Status bar: backend status · session id · Export              │
└───────────────────────────────────────────────────────────────┘
```
Tablet/mobile (< 1024px): chat only. Sidebar opens as a left drawer (hamburger button); trace appears as a collapsible section under each assistant message instead of a right column. Must work at 360px width with no horizontal scroll.

## 5. Components

| Component | Props | Behavior |
|-----------|-------|----------|
| `App` | none | Holds `useChat()`; lays out regions; manages drawer and selected message |
| `TeamSidebar` | `activeAgent`, `onNewChat` | Lists 5 `AgentCard`s; "New chat" button |
| `AgentCard` | `agent`, `active` | Name, role, color dot; highlighted ring + subtle pulse when active; coordinator is highlighted briefly during routing |
| `ChatPanel` | `messages`, `loading`, `onSend`, `onSelect` | Scrollable list; auto-scroll to newest; empty state shows `ExampleChips` |
| `MessageBubble` | `message`, `selected`, `onSelect` | User: right aligned. Assistant: left aligned, agent badge (color + label), markdown body, "Show trace" toggle on mobile, copy button |
| `MermaidBlock` | `code` | Renders diagram; fallback to raw code with note on parse error; "Copy mermaid" button |
| `ChatInput` | `disabled`, `onSend` | Textarea; Enter sends, Shift+Enter newline; disabled while loading; max 2000 chars |
| `ExampleChips` | `onPick` | 4 chips from `agents.ts`; clicking sends immediately |
| `TracePanel` | `trace` | Ordered steps: route (arrow icon), tool call (wrench, name + compact args), tool result (preview truncated, expandable) |
| `StatusBar` | `status`, `sessionId`, `messages` | Green/red dot (polls `/api/health` every 15 s); short session id; `ExportButton` |
| `ExportButton` | `messages` | Downloads `sample_questions.md` |
| `ErrorBanner` | `message`, `onDismiss` | Dismissible, `role="alert"` |

## 6. Behavior details
- **Start:** call `health()`; then `newSession()`. If either fails, show the error banner and keep input disabled until health succeeds.
- **Send:** append user message; set `loading`; show a "thinking" assistant placeholder (animated dots); call `chat()`; replace placeholder with the answer, `agent`, `trace`; set `activeAgent = agent`; auto-select that message for the trace panel.
- **During loading:** input disabled; send button shows a spinner. Request timeout 90 s with `AbortController`; on timeout show "The request took too long. Try again."
- **Errors:** do not lose the user's message; show the error as an assistant error bubble with a "Retry" button that resends the same text.
- **New chat:** new session, clear messages, clear `activeAgent`, no confirmation needed.
- **Persistence:** none (memory only). Do not use localStorage.
- **Markdown:** GFM tables and lists, inline code, fenced code with syntax highlight and a copy button; links open in a new tab with `rel="noreferrer"`. Do not allow raw HTML.
- **Mermaid:** custom `code` renderer; when the fence language is `mermaid`, render `MermaidBlock`. Initialize mermaid once (`startOnLoad:false`), use a unique id per render, re-render when the color scheme changes.
- **Export format (`exportMarkdown.ts`):**
  ```
  # Code Helper — Sample Questions
  ## 1. <question>
  **Answered by:** `code_searcher`
  <answer markdown>
  ```
  One section per user/assistant pair. Include a short list of tools called under each answer.

## 7. Visual design
- Clean, developer-tool look. Light and dark via `prefers-color-scheme` (Tailwind `dark:` classes).
- Font: system UI for text, `ui-monospace` for code. Base 16px; chat max width ~720px.
- Agent colors used for badges, card dots, and trace icons: blue, green, purple, amber; coordinator slate.
- Rounded cards (`rounded-xl`), 1px borders, soft shadows only on the input and drawer.
- Motion: only the thinking dots, active-card ring, and drawer slide; respect `prefers-reduced-motion`.

## 8. Accessibility
Labels on all icon buttons; visible focus rings; chat list `aria-live="polite"`; contrast at least 4.5:1; full keyboard use (Tab order: sidebar, messages, input); drawer traps focus and closes on Escape.

## 9. File list
```
src/
  main.tsx  App.tsx  index.css  types.ts
  data/agents.ts
  lib/api.ts  lib/exportMarkdown.ts
  hooks/useChat.ts  hooks/useHealth.ts
  components/ChatPanel.tsx MessageBubble.tsx MermaidBlock.tsx ChatInput.tsx
             ExampleChips.tsx TeamSidebar.tsx AgentCard.tsx TracePanel.tsx
             StatusBar.tsx ExportButton.tsx ErrorBanner.tsx
```

## 10. Build order and gates
1. Scaffold Vite + Tailwind, proxy, `types.ts`, `agents.ts`.
2. `api.ts` + `useChat.ts`. **Gate:** with the backend running, a temporary button can create a session and get an answer in the console.
3. `ChatPanel`, `MessageBubble` (markdown), `ChatInput`. **Gate:** ask a question and see the formatted answer.
4. `TeamSidebar`, `AgentCard`, agent badge. **Gate:** the right card lights up for each of the 4 example questions.
5. `TracePanel`. **Gate:** route + tool steps appear for each answer.
6. `MermaidBlock`. **Gate:** "Show me the architecture diagram." renders a diagram; a broken diagram falls back to raw code.
7. `ExampleChips`, `StatusBar`, `ErrorBanner`, `ExportButton`, retry. **Gate:** stopping the backend shows "not reachable" and a friendly error; export downloads a valid file.
8. Responsive + dark mode + accessibility pass. **Gate:** works at 360px, no horizontal scroll, keyboard-only usable.

## 11. Tests (Vitest + Testing Library)
- `exportMarkdown`: given messages, output contains question, agent, answer.
- `api.ts` with mocked `fetch`: maps 429 and network errors to the friendly messages.
- `MessageBubble`: renders markdown and a ```mermaid fence as `MermaidBlock`.
- `MermaidBlock`: invalid code shows the fallback (mock `mermaid.render` to throw).
- `useChat`: send appends user message then assistant message; error keeps the user message.

## 12. Out of scope
Auth, streaming tokens, chat history storage, file upload, settings page, i18n.
