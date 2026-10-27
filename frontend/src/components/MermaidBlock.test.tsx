import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MermaidBlock } from "./MermaidBlock";
import mermaid from "mermaid";

vi.mock("mermaid", () => ({
  default: {
    initialize: vi.fn(),
    render: vi.fn(),
  },
}));

describe("MermaidBlock", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders fallback with raw code when mermaid render throws", async () => {
    vi.mocked(mermaid.render).mockImplementation(() =>
      Promise.reject(new Error("Invalid syntax error"))
    );

    render(<MermaidBlock code="invalid mermaid code" />);

    const fallback = await screen.findByText(/Failed to render diagram/i, {}, { timeout: 3000 });
    expect(fallback).toBeDefined();
    const rawCode = await screen.findByText("invalid mermaid code");
    expect(rawCode).toBeDefined();
  });

  it("renders svg when mermaid render succeeds", async () => {
    vi.mocked(mermaid.render).mockImplementation(() =>
      Promise.resolve({
        svg: '<svg data-testid="mermaid-svg"><g>diagram</g></svg>',
        bindFunctions: undefined,
      })
    );

    render(<MermaidBlock code="graph TD; A-->B;" />);

    const svgElement = await screen.findByTestId("mermaid-svg");
    expect(svgElement).toBeDefined();
  });
});
