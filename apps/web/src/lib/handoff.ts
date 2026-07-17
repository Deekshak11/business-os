/** Clean handoff status for UI — never show internal thread IDs. */
export function formatHandoffNote(note: string | null | undefined): string {
  if (!note) return "";
  return note
    .split(/\r?\n/)
    .map((l) => l.trimEnd())
    .filter((l) => {
      const t = l.trim();
      if (!t) return false;
      // "Thread abc-uuid" or "thread: …"
      if (/^thread\b/i.test(t)) return false;
      if (/\bthread\s*[:=]?\s*[0-9a-f-]{8,}/i.test(t)) return false;
      // bare UUID line
      if (
        /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
          t,
        )
      ) {
        return false;
      }
      return true;
    })
    .join("\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}
