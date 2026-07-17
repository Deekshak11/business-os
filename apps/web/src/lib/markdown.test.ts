import { describe, expect, it } from "vitest";
import {
  escapeHtml,
  hasRenderedBold,
  markdownToHtml,
} from "./markdown";

describe("markdownToHtml (shipped helper)", () => {
  it("renders **bold** as strong, not literal stars", () => {
    const html = markdownToHtml("Use the **Rule of 100** daily.");
    expect(html).toContain("<strong>Rule of 100</strong>");
    expect(html).not.toContain("**Rule of 100**");
    expect(hasRenderedBold(html)).toBe(true);
  });

  it("escapes raw HTML injection", () => {
    const html = markdownToHtml('Hello <script>alert(1)</script> **x**');
    expect(html).not.toContain("<script>");
    expect(html).toContain("&lt;script&gt;");
    expect(html).toContain("<strong>x</strong>");
  });

  it("renders headings and lists", () => {
    const md = "## Diagnosis\n\n- first\n- second\n\n1. one";
    const html = markdownToHtml(md);
    expect(html).toContain("<h2>Diagnosis</h2>");
    expect(html).toContain("<ul>");
    expect(html).toContain("<li>first</li>");
    expect(html).toContain("<ol>");
  });

  it("escapeHtml is used as base (ampersand)", () => {
    expect(escapeHtml("a & b")).toBe("a &amp; b");
  });

  it("renders GFM tables as HTML table", () => {
    const md = [
      "| Tool | How it sharpens |",
      "|------|-----------------|",
      "| Core Four | YT every day |",
      "| **Lead Magnet** | Free build |",
    ].join("\n");
    const html = markdownToHtml(md);
    expect(html).toContain('<table class="md-table">');
    expect(html).toContain("<th>");
    expect(html).toContain("Tool");
    expect(html).toContain("<td>");
    expect(html).toContain("Core Four");
    expect(html).toContain("<strong>Lead Magnet</strong>");
    expect(html).not.toContain("|------|");
  });
});
