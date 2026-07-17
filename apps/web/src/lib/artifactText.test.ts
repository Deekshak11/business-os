import { describe, expect, it } from "vitest";
import {
  cleanArtifactBody,
  prettifyIfRawJson,
  scrubArtifactText,
  unescapeLiteralEscapes,
} from "./artifactText";

describe("unescapeLiteralEscapes", () => {
  it("turns \\n into real newlines", () => {
    expect(unescapeLiteralEscapes("a\\nb\\nc")).toBe("a\nb\nc");
  });

  it("handles double-escaped sequences", () => {
    const once = unescapeLiteralEscapes("line1\\\\nline2");
    // after one full multi-pass we want real newlines
    expect(unescapeLiteralEscapes("Hook\\n\\nBody")).toContain("\n");
  });
});

describe("scrubArtifactText", () => {
  it("fixes the production quote-glue pattern from the screenshot", () => {
    const raw =
      '"\\n\\n"Testimonial Scripts (3)\\n"\\n\\n"Script 1: Pre-Shoot Prep\\n"\\nHey [Name] — excited.';
    const out = scrubArtifactText(raw);
    expect(out).not.toContain("\\n");
    expect(out).not.toMatch(/^"/);
    expect(out).toContain("Testimonial Scripts (3)");
    expect(out).toContain("Script 1: Pre-Shoot Prep");
    expect(out).toContain("Hey [Name]");
    // no dangling quote-only glue lines
    expect(out.split("\n").every((l) => l.trim() !== '"')).toBe(true);
  });

  it("extracts content from a full JSON blob", () => {
    const raw = JSON.stringify({
      summary: "ok",
      artifacts: [
        {
          title: "VSL Script",
          kind: "script",
          content: "## Hook\n\nStop losing clients.\n\n## CTA\n\nBook a call.",
          sources: ["x.md"],
        },
      ],
    });
    const out = scrubArtifactText(raw);
    expect(out).toContain("Stop losing clients");
    expect(out).not.toContain('"artifacts"');
    expect(out).not.toContain('"summary"');
  });

  it("leaves clean markdown alone", () => {
    const md = "## Hook\n\n**Bold** line\n\n1. One\n2. Two";
    expect(scrubArtifactText(md)).toBe(md);
  });

  it("does not destroy fenced JSON code blocks", () => {
    const md = "Setup:\n\n```json\n{\"nodes\": []}\n```\n\nDone.";
    const out = scrubArtifactText(md);
    expect(out).toContain("```json");
    expect(out).toContain('"nodes"');
  });
});

describe("prettifyIfRawJson", () => {
  it("pulls multiple content fields", () => {
    const raw =
      '{"artifacts":[{"title":"A","kind":"x","content":"Body A"},{"title":"B","kind":"y","content":"Body B"}]}';
    const out = prettifyIfRawJson(raw);
    expect(out).toContain("Body A");
    expect(out).toContain("Body B");
  });
});

describe("cleanArtifactBody", () => {
  it("strips duplicate title and sources dump", () => {
    const body =
      "# VSL Script\n\nHook here.\n\nSources: [\"foo.md\", \"bar.md\"]\n";
    const out = cleanArtifactBody("VSL Script", body);
    expect(out.startsWith("Hook here")).toBe(true);
    expect(out.toLowerCase()).not.toContain("sources:");
  });

  it("cleans the ugly screenshot blob into readable text", () => {
    const ugly =
      '"\\n\\n"Testimonial Scripts (3)\\n"\\n\\n"Script 1: Pre-Shoot Prep (Client Confidence Builder)\\n"\\nHey [Name] — excited about your free build!\n\n1. **The Before:** What was broken?\n2. **The After:** What\'s fixed now?';
    const out = cleanArtifactBody(
      "VSL Script (Free Build for Testimonial) + Testimonial Scripts",
      ugly,
    );
    expect(out).toContain("Testimonial Scripts (3)");
    expect(out).toContain("**The Before:**");
    expect(out).not.toContain("\\n");
    expect(out).not.toMatch(/^["']/);
  });
});
