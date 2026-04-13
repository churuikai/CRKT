import { describe, it, expect } from "vitest";
import { renderMarkdown } from "../markdown";

describe("renderMarkdown", () => {
  it("renders basic markdown", () => {
    const html = renderMarkdown("**bold** and *italic*");
    expect(html).toContain("<strong>bold</strong>");
    expect(html).toContain("<em>italic</em>");
  });

  it("renders inline math", () => {
    const html = renderMarkdown("The formula $x^2$ is simple");
    expect(html).toContain("katex");
    expect(html).not.toContain("$x^2$");
  });

  it("renders block math", () => {
    const html = renderMarkdown("$$\\sum_{i=1}^n x_i$$");
    expect(html).toContain("katex");
    expect(html).toContain("katex-display");
  });

  it("handles empty input", () => {
    expect(renderMarkdown("")).toBe("");
  });

  it("preserves code blocks", () => {
    const html = renderMarkdown("```\ncode here\n```");
    expect(html).toContain("<code>");
  });
});
