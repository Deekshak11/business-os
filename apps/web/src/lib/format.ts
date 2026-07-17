/** Human-facing formatters for plan / pipeline UI */

const STAGE_NAMES: Record<string, string> = {
  "0": "Improvise",
  "1": "Monetize",
  "2": "Advertise",
  "3": "Stabilize",
  "4": "Prioritize",
  "5": "Productize",
  "6": "Optimize",
  "7": "Categorize",
  "8": "Specialize",
  "9": "Capitalize",
  unknown: "Unknown",
};

export function formatStage(stage?: string | null): string {
  if (stage == null || stage === "" || stage === "unknown") return "Not set";
  const name = STAGE_NAMES[String(stage)] || "";
  return name ? `Stage ${stage} · ${name}` : `Stage ${stage}`;
}

export function formatConstraint(c?: string | null): string {
  if (!c || c === "unknown") return "Not set";
  return c.charAt(0).toUpperCase() + c.slice(1);
}

export function formatRoute(r?: string | null): string | null {
  if (!r || r === "none") return null;
  if (r === "both") return "Copywriting + Builder";
  if (r === "copy") return "Copywriting Agent";
  if (r === "build") return "Builder Agent";
  return r;
}

export function isEmptyValue(v?: string | null): boolean {
  if (v == null) return true;
  const t = v.trim().toLowerCase();
  if (!t || t === "—" || t === "-") return true;
  if (t === "unknown" || t.startsWith("unknown")) return true;
  if (t.includes("no paid offer") || t.includes("not described")) return true;
  return false;
}

export function displayField(v?: string | null, fallback = "Not provided yet"): string {
  if (isEmptyValue(v)) return fallback;
  return v!.trim();
}
