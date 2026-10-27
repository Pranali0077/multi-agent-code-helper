import { describe, it, expect } from "vitest";
import { formatExportMarkdown } from "./exportMarkdown";
import type { Message } from "../types";

describe("exportMarkdown", () => {
  it("given messages, output contains question, agent, and answer", () => {
    const messages: Message[] = [
      {
        id: "msg-1",
        role: "user",
        text: "Where is the search done?",
      },
      {
        id: "msg-2",
        role: "assistant",
        agent: "code_searcher",
        text: "The search is implemented in `search.py` using Pinecone.",
        trace: [
          { kind: "tool_call", agent: "code_searcher", name: "search_codebase", args: { query: "search" } },
        ],
      },
    ];

    const result = formatExportMarkdown(messages);
    expect(result).toContain("Where is the search done?");
    expect(result).toContain("code_searcher");
    expect(result).toContain("The search is implemented in `search.py` using Pinecone.");
    expect(result).toContain("search_codebase");
  });
});
