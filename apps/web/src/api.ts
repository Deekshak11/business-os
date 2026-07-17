export type ChatMessage = {
  role: "user" | "assistant" | "system";
  content: string;
};

export type Citation = {
  name: string;
  file: string;
  why: string;
};

export type Plan = {
  version?: string;
  thread_id: string;
  business_context?: {
    industry?: string;
    offer?: string;
    headcount?: number | null;
    revenue_signals?: string;
    goals?: string;
    constraints_stated?: string[];
  };
  stage?: string;
  constraint?: string;
  strategy_summary?: string;
  frameworks_cited?: Citation[];
  action_steps?: { step: number; action: string; owner: string }[];
  deliverables?: {
    id?: string;
    type: string;
    title: string;
    spec?: string;
    acceptance?: string[];
  }[];
  recommended_route?: string;
  risks?: string[];
  questions_still_open?: string[];
};

export type ChatResponse = {
  thread_id: string;
  reply: string;
  plan?: Plan | null;
  awaiting_approval: boolean;
  status: string;
};

export type Artifact = {
  id: string;
  agent: string;
  title: string;
  kind: string;
  content: string;
  sources?: string[];
};

export type ExecuteResponse = {
  thread_id: string;
  status: string;
  route: string;
  summary: string;
  artifacts: Artifact[];
  agent_logs?: string[];
};

export type Health = {
  ok: boolean;
  version?: string;
  deepseek_configured?: boolean;
  llm_configured?: boolean;
  deepseek_model?: string;
  llm_model?: string;
  llm_provider?: string;
  host?: string;
};

/**
 * API base URL:
 * - Local dev: Vite proxies /api → 127.0.0.1:8000
 * - Production (Vercel): set VITE_API_URL to the Modal public URL
 */
const BASE = (import.meta.env.VITE_API_URL as string | undefined)?.replace(
  /\/$/,
  "",
) || "/api";

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

function networkErrorMessage(err: unknown): string {
  if (err instanceof DOMException && err.name === "AbortError") {
    return "Request timed out. The API may be cold-starting — try again.";
  }
  if (err instanceof TypeError) {
    // Browser surfaces CORS/network as "Failed to fetch"
    return (
      "Network error (Failed to fetch). Often a cold API start or temporary drop — " +
      "retrying usually works. If it keeps failing, the API host may be down."
    );
  }
  if (err instanceof Error) return err.message;
  return String(err);
}

type FetchJsonOpts = {
  retries?: number;
  timeoutMs?: number;
  retryDelayMs?: number;
};

/**
 * fetch with timeout + retries for Modal cold starts / flaky networks.
 */
async function fetchJson<T>(
  url: string,
  init: RequestInit,
  opts: FetchJsonOpts = {},
): Promise<T> {
  const retries = opts.retries ?? 2;
  const timeoutMs = opts.timeoutMs ?? 120_000;
  const retryDelayMs = opts.retryDelayMs ?? 1200;
  let lastErr: unknown;

  for (let attempt = 0; attempt <= retries; attempt++) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    try {
      const r = await fetch(url, { ...init, signal: ctrl.signal });
      clearTimeout(timer);

      if (!r.ok) {
        let detail = `Request failed: ${r.status}`;
        try {
          const j = await r.json();
          detail = j.detail || JSON.stringify(j);
        } catch {
          try {
            detail = (await r.text()).slice(0, 400) || detail;
          } catch {
            /* ignore */
          }
        }
        // Retry 502/503/504 (cold start / gateway)
        if ([502, 503, 504].includes(r.status) && attempt < retries) {
          await sleep(retryDelayMs * (attempt + 1));
          continue;
        }
        throw new Error(detail);
      }
      return (await r.json()) as T;
    } catch (err) {
      clearTimeout(timer);
      lastErr = err;
      // Don't retry structured API errors (4xx/5xx already handled)
      if (err instanceof Error && !/failed to fetch|network|abort|timed out/i.test(err.message) && ! (err instanceof TypeError) && !(err instanceof DOMException)) {
        // App-level Error from !r.ok
        if (!/502|503|504|timed out|Failed to fetch|Network error/i.test(err.message)) {
          throw err;
        }
      }
      if (attempt < retries) {
        await sleep(retryDelayMs * (attempt + 1));
        continue;
      }
    }
  }
  throw new Error(networkErrorMessage(lastErr));
}

export async function fetchHealth(): Promise<Health> {
  return fetchJson<Health>(`${BASE}/health`, { method: "GET" }, {
    retries: 2,
    timeoutMs: 45_000,
  });
}

export async function sendChat(
  message: string,
  threadId: string | null,
  history: ChatMessage[],
): Promise<ChatResponse> {
  return fetchJson<ChatResponse>(
    `${BASE}/chat`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        thread_id: threadId,
        history,
      }),
    },
    { retries: 2, timeoutMs: 150_000, retryDelayMs: 1500 },
  );
}

export async function runExecute(
  threadId: string,
  route: "copy" | "build" | "both",
  plan: Plan,
): Promise<ExecuteResponse> {
  // Specialists can take 2–4 minutes; allow one automatic retry on network blip
  return fetchJson<ExecuteResponse>(
    `${BASE}/execute`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        thread_id: threadId,
        route,
        plan,
      }),
    },
    { retries: 2, timeoutMs: 280_000, retryDelayMs: 2000 },
  );
}

/** Detect "try again / retry / redo execute" after a failed specialist run */
export function isExecuteRetryIntent(message: string): boolean {
  return /^\s*(try\s*again|retry|redo|run\s*again|execute\s*again|re-?run)\s*[.!]?\s*$/i.test(
    message.trim(),
  );
}

/** Detect mock/demo plan requests in the UI */
export function isMockPlanIntent(message: string): boolean {
  return /\b(mock|sample|demo)\b/i.test(message) &&
    /\b(plan|data|business|scenario)\b/i.test(message);
}
