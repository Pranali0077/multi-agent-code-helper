import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MessageBubble } from "./MessageBubble";
import type { Message } from "../types";

vi.mock("./MermaidBlock", () => ({
  MermaidBlock: ({ code }: { code: string }) => (
    <div data-testid="mock-mermaid">{code}</div>
  ),
}));

describe("MessageBubble", () => {
  it("renders markdown headings and text", () => {
    const msg: Message = {
      id: "msg-1",
      role: "assistant",
      agent: "code_explainer",
      text: "### Explanation\nThis explains main.py.",
    };

    render(<MessageBubble message={msg} />);
    expect(screen.getByText("Explanation")).toBeDefined();
    expect(screen.getByText("This explains main.py.")).toBeDefined();
    expect(screen.getByText("Code Explainer")).toBeDefined();
  });

  it("renders mermaid fence as MermaidBlock component", async () => {
    const msg: Message = {
      id: "msg-2",
      role: "assistant",
      agent: "architecture_mapper",
      text: "```mermaid\ngraph TD\nA-->B\n```",
    };

    render(<MessageBubble message={msg} />);
    const mermaidEl = await screen.findByTestId("mock-mermaid");
    expect(mermaidEl).toBeDefined();
    expect(mermaidEl.textContent).toContain("graph TD");
  });
});
