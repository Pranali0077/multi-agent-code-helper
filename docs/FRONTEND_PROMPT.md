Build only the frontend of the "Multi-Agent Code Helper" in the `frontend/` folder, using @docs/frontend.md as the single source of truth (backend contract is in section 2; do not change it). Use @docs/structure.md for where the frontend sits in the repo.

Read frontend.md fully first, then follow its section 10 build order step by step. Check each gate before moving on.

Rules:
- React + Vite + TypeScript + Tailwind. Libraries allowed: react-markdown, rehype-highlight, highlight.js, mermaid, vitest, @testing-library/react. Nothing else.
- Talk to the backend only through /api/health, /api/sessions, /api/chat via the Vite proxy to http://localhost:8000.
- Show: 5-agent sidebar with the answering agent highlighted, chat with markdown + code + rendered Mermaid diagrams, tool-trace panel, example question chips, status bar, retry on error, export to sample_questions.md.
- Responsive to 360px, light/dark mode, keyboard accessible. No localStorage.
- Keep the code small and easy to explain. No extra features, no state libraries, no UI kits.
- If the backend is not running yet, mock /api with a small local mock (MSW or a tiny Vite plugin) using the same contract so every gate can still be checked, and say so.
- After each step give a 2-line status and how to see it.

Start with step 1.
