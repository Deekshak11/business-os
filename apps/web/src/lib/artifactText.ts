/**
 * Clean specialist artifact bodies before display.
 * Mirrors backend scrub — handles literal \n, quote-glue, half-stripped JSON.
 */

/** Turn literal \\n / \\t / \\" into real characters. */
export function unescapeLiteralEscapes(text: string): string {
  if (!text) return "";
  let s = text;
  for (let pass = 0; pass < 3; pass++) {
    if (!s.includes("\\n") && !s.includes("\\t") && !s.includes('\\"') && !s.includes("\\u")) {
      break;
    }
    s = s
      .replace(/\\r\\n/g, "\n")
      .replace(/\\n/g, "\n")
      .replace(/\\r/g, "\n")
      .replace(/\\t/g, "\t")
      .replace(/\\"/g, '"')
      .replace(/\\'/g, "'")
      .replace(/\\u([0-9a-fA-F]{4})/g, (_, h) => {
        try {
          return String.fromCharCode(parseInt(h, 16));
        } catch {
          return _;
        }
      })
      .replace(/\\\\/g, "\\");
  }
  return s;
}

function looksLikeJsonBlob(text: string): boolean {
  const t = text.trim();
  return (
    t.startsWith("{") &&
    (t.includes('"artifacts"') || t.includes('"content"') || t.includes('"summary"'))
  );
}

/** Extract JSON string values for a field, respecting escapes. */
function extractJsonStringFields(text: string, field: string): string[] {
  const results: string[] = [];
  const re = new RegExp(`"${field}"\\s*:\\s*"`, "gi");
  let m: RegExpExecArray | null;
  while ((m = re.exec(text)) !== null) {
    const start = m.index + m[0].length - 1; // opening "
    let i = start + 1;
    let out = "";
    while (i < text.length) {
      const ch = text[i];
      if (ch === "\\") {
        const nxt = text[i + 1];
        if (nxt === undefined) break;
        const map: Record<string, string> = {
          n: "\n",
          t: "\t",
          r: "\r",
          '"': '"',
          "\\": "\\",
          "/": "/",
        };
        if (nxt in map) {
          out += map[nxt];
          i += 2;
          continue;
        }
        if (nxt === "u" && i + 5 < text.length) {
          const hex = text.slice(i + 2, i + 6);
          const code = parseInt(hex, 16);
          if (!Number.isNaN(code)) {
            out += String.fromCharCode(code);
            i += 6;
            continue;
          }
        }
        out += nxt;
        i += 2;
        continue;
      }
      if (ch === '"') {
        results.push(out);
        break;
      }
      out += ch;
      i++;
    }
  }
  return results;
}

/** If body is a raw JSON dump, prefer content fields / strip chrome. */
export function prettifyIfRawJson(content: string): string {
  const t = content.trim();
  if (!looksLikeJsonBlob(t) && !t.includes('"content"')) {
    return content;
  }

  const chunks = extractJsonStringFields(t, "content");
  if (chunks.length) {
    return chunks
      .map((c) => unescapeLiteralEscapes(c).trim())
      .filter(Boolean)
      .join("\n\n---\n\n");
  }

  let s = unescapeLiteralEscapes(t);
  s = s.replace(/^\s*\{[\s\S]*?"summary"\s*:\s*"/, "");
  s = s.replace(/"artifacts"\s*:\s*\[/gi, "\n");
  s = s.replace(/"title"\s*:\s*"[^"]*"\s*,?/gi, "\n");
  s = s.replace(/"kind"\s*:\s*"[^"]*"\s*,?/gi, "\n");
  s = s.replace(/"sources"\s*:\s*\[[^\]]*\]\s*,?/gi, "\n");
  s = s.replace(/"content"\s*:\s*"/gi, "\n");
  // Do NOT strip braces inside code — only outer-ish chrome already handled
  s = s.replace(/^[\{\[]+/, "").replace(/[\}\]]+$/, "");
  return s.trim() || content;
}

/**
 * Aggressive body scrub for quote-glue and half-stripped JSON.
 * Safe for already-clean markdown.
 */
export function scrubArtifactText(content: string): string {
  if (!content) return "";
  let s = unescapeLiteralEscapes(content).trim();

  if (looksLikeJsonBlob(s) || (s.includes('"content"') && s.includes('"title"'))) {
    const peeled = prettifyIfRawJson(s);
    if (peeled.trim()) s = peeled;
  }

  // Whole body wrapped in one pair of quotes
  if (
    s.length >= 2 &&
    ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'")))
  ) {
    const inner = s.slice(1, -1);
    if (inner.includes("\n") || inner.includes("\\n") || inner.length > 40) {
      s = unescapeLiteralEscapes(inner).trim();
    }
  }

  // Quote-glue between sections
  s = s.replace(/"\s*\\n\s*"/g, "\n\n");
  s = s.replace(/"\s*\n+\s*"/g, "\n\n");
  s = s.replace(/"\s*,\s*"/g, "\n\n");

  const lines = s.split("\n").map((line) => {
    const t = line.trim();
    if (
      t === '"' ||
      t === "'" ||
      t === '""' ||
      t === "''" ||
      t === "," ||
      t === "{" ||
      t === "}" ||
      t === "}," ||
      t === "[]" ||
      t === "],"
    ) {
      return "";
    }
    let line2 = line.replace(/^["']+\s*/, "").replace(/\s*["']+$/, "");
    line2 = line2.replace(
      /^\s*"(?:title|kind|content|summary|sources|agent|artifacts)"\s*:\s*"?/i,
      "",
    );
    return line2;
  });
  s = lines.join("\n");

  // Residual keys (outside fenced code)
  const parts = s.split(/(```[\s\S]*?```)/);
  s = parts
    .map((part, i) => {
      if (i % 2 === 1) return part;
      let p = part;
      p = p.replace(/"sources"\s*:\s*\[[^\]]*\]\s*,?/gi, "");
      p = p.replace(/"(?:title|kind|summary|agent)"\s*:\s*"[^"]*"\s*,?/gi, "");
      p = p.replace(/"content"\s*:\s*"/gi, "");
      p = p.replace(/"artifacts"\s*:\s*\[/gi, "\n");
      return p;
    })
    .join("");

  s = unescapeLiteralEscapes(s);
  s = s.replace(/\n{3,}/g, "\n\n").trim();
  s = s.replace(/^["']+|["']+$/g, "").trim();
  return s;
}

/** Strip a leading markdown/plain title that duplicates the card heading. */
export function stripDuplicateTitle(title: string, content: string): string {
  if (!title || !content) return content;
  const norm = (x: string) =>
    x
      .toLowerCase()
      .replace(/[*_#`]/g, "")
      .replace(/[^\w\s$]/g, "")
      .replace(/\s+/g, " ")
      .trim();
  const want = norm(title);
  if (!want) return content;

  const lines = content.replace(/^\uFEFF/, "").split(/\r?\n/);
  let i = 0;
  while (i < lines.length && !lines[i].trim()) i++;
  if (i >= lines.length) return content;

  const first = lines[i].trim();
  const headingText = first.replace(/^#{1,6}\s+/, "").trim();
  if (norm(headingText) === want || norm(first) === want) {
    i += 1;
    while (i < lines.length && !lines[i].trim()) i++;
    return lines.slice(i).join("\n");
  }
  return content;
}

/**
 * Remove inline "Sources: [...]" dumps — card already has a.sources list.
 */
export function stripInlineSourcesDump(content: string): string {
  if (!content) return content;
  let s = content;
  s = s.replace(
    /(?:^|\n)\s*(?:\*\*)?sources?(?:\*\*)?\s*:\s*\[[^\]]*\]\s*/gi,
    "\n",
  );
  s = s.replace(
    /(?:^|\n)\s*(?:\*\*)?sources?(?:\*\*)?\s*:?\s*\n(?:\s*[-*]\s+\S+\.md\s*\n?)+/gi,
    "\n",
  );
  s = s.replace(
    /(?:^|\n)\s*(?:\*\*)?sources?(?:\*\*)?\s*:\s*[^\n]*\.md[^\n]*/gi,
    "\n",
  );
  return s.replace(/\n{3,}/g, "\n\n").trimEnd();
}

/** Full clean pipeline for artifact bodies shown in UI / copy-to-clipboard. */
export function cleanArtifactBody(title: string, content: string): string {
  return stripInlineSourcesDump(
    stripDuplicateTitle(title, scrubArtifactText(content)),
  );
}
