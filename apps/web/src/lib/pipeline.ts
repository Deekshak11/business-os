/**
 * Pipeline step model: strategy → execution.
 * Pure helpers for UI step selection (unit-testable).
 */

export type PipelineStepId =
  | "context"
  | "strategy"
  | "plan"
  | "approve"
  | "execute"
  | "done";

export type PipelineStep = {
  id: PipelineStepId;
  label: string;
  short: string;
  description: string;
};

export const PIPELINE_STEPS: PipelineStep[] = [
  {
    id: "context",
    label: "Context",
    short: "01",
    description: "Business signals — stage, offer, constraint (Chat).",
  },
  {
    id: "strategy",
    label: "Strategy",
    short: "02",
    description: "Scaling-stage diagnosis; playbooks only amplify (Chat).",
  },
  {
    id: "plan",
    label: "Plan",
    short: "03",
    description: "Structured plan with citations and deliverables (Plan).",
  },
  {
    id: "approve",
    label: "Approve",
    short: "04",
    description: "You route to Copywriting and/or Builder (Plan).",
  },
  {
    id: "execute",
    label: "Execute",
    short: "05",
    description: "Specialists run the approved handoff (Agents).",
  },
  {
    id: "done",
    label: "Done",
    short: "06",
    description: "Paste-ready deliverables ready (Outputs).",
  },
];

export type SessionFlags = {
  /** Backend status string: chatting | plan_ready | error | executing | done */
  status: string;
  awaitingApproval: boolean;
  hasUserMessage: boolean;
  hasPlan: boolean;
  hasExecution: boolean;
  executionComplete?: boolean;
};

/**
 * Map session flags → current pipeline step id.
 */
export function selectPipelineStep(flags: SessionFlags): PipelineStepId {
  if (flags.executionComplete || flags.status === "done") return "done";
  if (flags.hasExecution || flags.status === "executing") return "execute";
  if (flags.awaitingApproval) return "approve";
  if (flags.status === "plan_ready" || (flags.hasPlan && flags.status !== "chatting"))
    return "plan";
  if (flags.hasUserMessage || flags.status === "chatting") {
    // If we have a plan but still chatting, prefer plan when summary exists
    if (flags.hasPlan && flags.awaitingApproval) return "approve";
    if (flags.hasPlan && flags.status === "plan_ready") return "plan";
    if (flags.hasUserMessage) return "strategy";
  }
  return "context";
}

export function stepIndex(id: PipelineStepId): number {
  return PIPELINE_STEPS.findIndex((s) => s.id === id);
}

export function isStepDone(current: PipelineStepId, step: PipelineStepId): boolean {
  return stepIndex(step) < stepIndex(current);
}

export function isStepActive(current: PipelineStepId, step: PipelineStepId): boolean {
  return current === step;
}

/** Nav view ids used by the shell */
export type AppView = "chat" | "pipeline" | "plan" | "agents" | "outputs";

/**
 * When plan becomes ready / approval needed, suggest which view to focus.
 */
export function suggestedViewForStep(step: PipelineStepId): AppView {
  switch (step) {
    case "context":
    case "strategy":
      return "chat";
    case "plan":
    case "approve":
      return "plan";
    case "execute":
      return "pipeline";
    case "done":
      return "outputs";
    default:
      return "chat";
  }
}

export type PlanNavSignals = {
  /** API awaiting_approval */
  awaitingApproval: boolean;
  /** API status string */
  status: string;
  /** Assistant reply text */
  reply: string;
  /** Usable plan body (summary + steps/deliverables) */
  meatyPlan: boolean;
  /** Any plan object present (including synthetic) */
  hasPlan: boolean;
  /** Latest user message (this turn) */
  userMessage?: string;
};

/**
 * Should we auto-open the Plan view after this chat response?
 * Call once per response; pair with a session ref so it only navigates the first time.
 */
export function shouldAutoOpenPlan(s: PlanNavSignals): boolean {
  if (!s.hasPlan) return false;

  // Hard flags from API — always open
  if (s.awaitingApproval) return true;
  if (s.status === "plan_ready") return true;

  const reply = s.reply || "";
  if (/plan\s*locked/i.test(reply)) return true;
  if (/open\s+\*?\*?plan\*?\*?/i.test(reply)) return true;
  if (/ready\s+to\s+approve|route\s+to\s+(copy|builder)/i.test(reply)) return true;

  const user = s.userMessage || "";
  const userAskedForPlan =
    /\b((mock|sample|demo)\s+(plan|data)|generate\s+(a\s+)?(mock\s+|sample\s+|demo\s+)?plan|(show|create|write|draft|give|make)\s+(me\s+)?(a\s+)?(the\s+)?(full\s+|execution\s+|mock\s+|sample\s+)?plan|lock\s+(the\s+)?plan|show\s+me\s+the\s+plan)\b/i.test(
      user,
    );

  // Explicit plan / mock request + any usable plan body → open Plan
  if (userAskedForPlan && s.meatyPlan) return true;
  // Even thinner body: summary alone after explicit ask
  if (userAskedForPlan && s.hasPlan) return true;

  // Full execution plan written in the reply
  if (s.meatyPlan && /\b(execution plan|action steps|deliverables|14-?day|stage\s*\d)\b/i.test(reply)) {
    return true;
  }

  // Meaty plan with a real route is always reviewable
  if (s.meatyPlan) return true;

  return false;
}
