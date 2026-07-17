/**
 * Lightweight Markdown → safe HTML for chat messages.
 * Escapes HTML first, then applies a subset of Markdown
 * (bold, italic, code, links, lists, headings, GFM tables, breaks).
 */

export function escapeHtml(raw: string): string {
  return raw
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatInline(escaped: string): string {
  let s = escaped;
  // fenced code already handled at block level; inline code
  s = s.replace(/`([^`\n]+)`/g, "<code>$1</code>");
  // bold **text** or __text__
  s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/__([^_]+)__/g, "<strong>$1</strong>");
  // italic *text* (after bold already applied)
  s = s.replace(/\*([^*\n]+)\*/g, "<em>$1</em>");
  s = s.replace(/(^|[^a-zA-Z0-9_])_([^_\n]+)_([^a-zA-Z0-9_]|$)/g, "$1<em>$2</em>$3");
  // links [label](url) — only http(s)
  s = s.replace(
    /\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>',
  );
  return s;
}

/** Split a GFM table row into cells (already HTML-escaped text). */
export function splitTableRow(line: string): string[] {
  let s = line.trim();
  if (s.startsWith("|")) s = s.slice(1);
  if (s.endsWith("|")) s = s.slice(0, -1);
  return s.split("|").map((c) => c.trim());
}

/** True for separator rows like |---|:---:|---:| or | --- | --- | */
export function isTableSeparator(line: string): boolean {
  const cells = splitTableRow(line);
  if (cells.length < 1) return false;
  return cells.every((c) => /^:?-{3,}:?$/.test(c.replace(/\s+/g, "")));
}

function looksLikeTableRow(line: string): boolean {
  const t = line.trim();
  if (!t.includes("|")) return false;
  // need at least one real pipe boundary (not only a lone | at end of prose)
  const cells = splitTableRow(t);
  return cells.length >= 2;
}

function renderTable(headerLine: string, bodyLines: string[]): string {
  const headers = splitTableRow(headerLine);
  const thead = `<thead><tr>${headers
    .map((h) => `<th>${formatInline(h)}</th>`)
    .join("")}</tr></thead>`;
  const rows = bodyLines
    .map((row) => {
      const cells = splitTableRow(row);
      // pad / trim to header width for ragged model output
      while (cells.length < headers.length) cells.push("");
      const tds = cells
        .slice(0, headers.length)
        .map((c) => `<td>${formatInline(c)}</td>`)
        .join("");
      return `<tr>${tds}</tr>`;
    })
    .join("");
  return `<div class="md-table-wrap"><table class="md-table">${thead}<tbody>${rows}</tbody></table></div>`;
}

/**
 * Convert Markdown string to safe HTML suitable for dangerouslySetInnerHTML.
 * Returns empty string for empty input.
 */
export function markdownToHtml(md: string): string {
  if (!md) return "";
  const escaped = escapeHtml(md);
  const lines = escaped.split(/\r?\n/);
  const out: string[] = [];
  let i = 0;
  let inUl = false;
  let inOl = false;
  let inCode = false;
  let codeBuf: string[] = [];

  const closeLists = () => {
    if (inUl) {
      out.push("</ul>");
      inUl = false;
    }
    if (inOl) {
      out.push("</ol>");
      inOl = false;
    }
  };

  while (i < lines.length) {
    const line = lines[i];

    // fenced code
    if (line.trim().startsWith("```")) {
      if (!inCode) {
        closeLists();
        inCode = true;
        codeBuf = [];
      } else {
        out.push(`<pre><code>${codeBuf.join("\n")}</code></pre>`);
        inCode = false;
        codeBuf = [];
      }
      i++;
      continue;
    }
    if (inCode) {
      codeBuf.push(line);
      i++;
      continue;
    }

    // GFM tables: header + separator + body rows
    if (
      looksLikeTableRow(line) &&
      i + 1 < lines.length &&
      isTableSeparator(lines[i + 1])
    ) {
      closeLists();
      const headerLine = line;
      i += 2; // skip header + separator
      const body: string[] = [];
      while (i < lines.length && looksLikeTableRow(lines[i]) && !isTableSeparator(lines[i])) {
        body.push(lines[i]);
        i++;
      }
      out.push(renderTable(headerLine, body));
      continue;
    }

    // headings
    const h = /^(#{1,3})\s+(.+)$/.exec(line);
    if (h) {
      closeLists();
      const level = h[1].length;
      out.push(`<h${level}>${formatInline(h[2])}</h${level}>`);
      i++;
      continue;
    }

    // unordered list
    const ul = /^[-*]\s+(.+)$/.exec(line);
    if (ul) {
      if (inOl) {
        out.push("</ol>");
        inOl = false;
      }
      if (!inUl) {
        out.push("<ul>");
        inUl = true;
      }
      out.push(`<li>${formatInline(ul[1])}</li>`);
      i++;
      continue;
    }

    // ordered list
    const ol = /^\d+\.\s+(.+)$/.exec(line);
    if (ol) {
      if (inUl) {
        out.push("</ul>");
        inUl = false;
      }
      if (!inOl) {
        out.push("<ol>");
        inOl = true;
      }
      out.push(`<li>${formatInline(ol[1])}</li>`);
      i++;
      continue;
    }

    // blank
    if (line.trim() === "") {
      closeLists();
      out.push("<br/>");
      i++;
      continue;
    }

    closeLists();
    out.push(`<p>${formatInline(line)}</p>`);
    i++;
  }

  if (inCode) {
    out.push(`<pre><code>${codeBuf.join("\n")}</code></pre>`);
  }
  closeLists();
  return out.join("\n");
}

/** True if markdownToHtml turned **bold** into a strong tag (for tests). */
export function hasRenderedBold(html: string): boolean {
  return /<strong>/.test(html) && !/\*\*[^*]+\*\*/.test(html);
}
