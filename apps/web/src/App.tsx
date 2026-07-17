import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import {
  Artifact,
  ChatMessage,
  ChatResponse,
  Plan,
  fetchHealth,
  isExecuteRetryIntent,
  runExecute,
  sendChat,
} from "./api";
import { AgentsView } from "./components/AgentsView";
import { ChatView, UiMessage } from "./components/ChatView";
import { OutputsView } from "./components/OutputsView";
import { PipelineView } from "./components/PipelineView";
import { PlanView } from "./components/PlanView";
import { Sidebar } from "./components/Sidebar";
import { cleanArtifactBody } from "./lib/artifactText";
import { formatHandoffNote } from "./lib/handoff";
import {
  AppView,
  PipelineStepId,
  PIPELINE_STEPS,
  selectPipelineStep,
  shouldAutoOpenPlan,
} from "./lib/pipeline";

function uid() {
  return Math.random().toString(36).slice(2, 10);
}

function routeLabel(route: "copy" | "build" | "both") {
  if (route === "copy") return "Copywriting Agent";
  if (route === "build") return "Builder Agent";
  return "Copywriting Agent + Builder Agent";
}

function artifactsToMarkdown(artifacts: Artifact[], summary: string): string {
  const parts = [
    `## Specialist outputs`,
    summary ? summary : "",
    "",
    ...artifacts.map((a) => {
      const who =
        a.agent === "copy"
          ? "Copywriting Agent"
          : a.agent === "build"
            ? "Builder Agent"
            : a.agent;
      const body = cleanArtifactBody(a.title, a.content);
      return `### ${a.title}\n*${who} · ${a.kind}*\n\n${body}`;
    }),
  ];
  return parts.filter(Boolean).join("\n\n");
}

const WELCOME =
  "I'm your **Business Strategist** — trained on Alex Hormozi's **$100M Offers**, **$100M Leads**, and Acquisition.com playbooks used across nine-figure portfolio companies.\n\nTell me what you sell and what's stuck (leads, offer, closes, cash). I'll diagnose the constraint and lock a plan for **Copy** / **Builder**.";

function makeWelcome(): UiMessage {
  return { id: "welcome", role: "assistant", content: WELCOME };
}

export default function App() {
  const [systemsLive, setSystemsLive] = useState(false);
  const [view, setView] = useState<AppView>("chat");
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [messages, setMessages] = useState<UiMessage[]>([makeWelcome()]);
  const [plan, setPlan] = useState<Plan | null>(null);
  const [status, setStatus] = useState("chatting");
  const [awaitingApproval, setAwaitingApproval] = useState(false);
  const [execNote, setExecNote] = useState<string | null>(null);
  const [executionComplete, setExecutionComplete] = useState(false);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [execSummary, setExecSummary] = useState<string | null>(null);
  const [activeRoute, setActiveRoute] = useState<
    "copy" | "build" | "both" | null
  >(null);
  const logRef = useRef<HTMLDivElement>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  /** Last specialist route so "try again" can re-run execute without re-planning */
  const lastRouteRef = useRef<"copy" | "build" | "both" | null>(null);
  const lastExecuteFailedRef = useRef(false);
  /** Fingerprint of last plan we auto-opened (re-open when a new plan arrives) */
  const lastOpenedPlanKeyRef = useRef<string>("");

  useEffect(() => {
    let cancelled = false;
    const tick = async () => {
      try {
        const h = await fetchHealth();
        if (!cancelled) {
          // Modal returns llm_configured; older local API used deepseek_configured
          const llmOn = !!(h.llm_configured ?? h.deepseek_configured);
          setSystemsLive(!!h.ok && llmOn);
        }
      } catch {
        if (!cancelled) setSystemsLive(false);
      }
    };
    tick();
    const id = setInterval(tick, 12000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  useEffect(() => {
    if (view !== "chat") return;
    const el = logRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, busy, executing, view]);

  const hasUserMessage = messages.some(
    (m) => m.role === "user" && m.id !== "welcome",
  );

  const currentStep: PipelineStepId = useMemo(
    () =>
      selectPipelineStep({
        status,
        awaitingApproval,
        hasUserMessage,
        hasPlan: !!plan,
        hasExecution: !!execNote || executing || artifacts.length > 0,
        executionComplete,
      }),
    [
      status,
      awaitingApproval,
      hasUserMessage,
      plan,
      execNote,
      executing,
      artifacts.length,
      executionComplete,
    ],
  );

  const stepLabel =
    PIPELINE_STEPS.find((s) => s.id === currentStep)?.label ?? "Context";

  const historyForApi: ChatMessage[] = messages
    .filter((m) => m.id !== "welcome")
    .map((m) => ({ role: m.role, content: m.content }));

  function onNewChat() {
    if (busy || executing) return;
    setThreadId(null);
    setMessages([makeWelcome()]);
    setPlan(null);
    setStatus("chatting");
    setAwaitingApproval(false);
    setExecNote(null);
    setExecutionComplete(false);
    setArtifacts([]);
    setExecSummary(null);
    setActiveRoute(null);
    setError(null);
    setInput("");
    lastOpenedPlanKeyRef.current = "";
    setView("chat");
  }

  async function onSubmit(e?: FormEvent) {
    e?.preventDefault();
    const text = input.trim();
    if (!text || busy || executing) return;
    setError(null);

    // After execute network failure: "try again" re-runs specialists, not a new intake loop
    if (
      lastExecuteFailedRef.current &&
      plan &&
      lastRouteRef.current &&
      isExecuteRetryIntent(text)
    ) {
      setInput("");
      setMessages((prev) => [
        ...prev,
        { id: uid(), role: "user", content: text },
        {
          id: uid(),
          role: "assistant",
          content: `Retrying **${routeLabel(lastRouteRef.current!)}** with the same plan…`,
        },
      ]);
      await onApprove(lastRouteRef.current);
      return;
    }

    // Don't wipe a good plan just because the user is still chatting
    setExecNote(null);
    setInput("");
    // Stay on chat while waiting; navigate only after response if plan is ready
    setView("chat");
    const userMsg: UiMessage = { id: uid(), role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setBusy(true);
    try {
      const res: ChatResponse = await sendChat(text, threadId, historyForApi);
      setThreadId(res.thread_id);
      setMessages((prev) => [
        ...prev,
        { id: uid(), role: "assistant", content: res.reply },
      ]);

      const reply = res.reply || "";
      const apiPlan = res.plan ?? null;
      const meatyPlan =
        !!apiPlan &&
        !!(
          apiPlan.strategy_summary &&
          apiPlan.strategy_summary.trim().length > 20
        ) &&
        (!!apiPlan.action_steps?.length || !!apiPlan.deliverables?.length);

      // Prefer API flags first — these are authoritative
      const apiSaysReady =
        !!res.awaiting_approval || res.status === "plan_ready";

      let nextPlan = apiPlan;
      // If flags say ready but body is missing, synthesize a reviewable plan from reply
      if (apiSaysReady && !nextPlan) {
        nextPlan = {
          thread_id: res.thread_id,
          strategy_summary: reply.slice(0, 1800) || "Plan ready for review.",
          stage: "0",
          constraint: "product",
          recommended_route: "both",
          action_steps: [
            {
              step: 1,
              action: "Review and route to Builder and/or Copywriting",
              owner: "user",
            },
          ],
          deliverables: [
            {
              type: "build",
              title: "Implementation pack (from strategist lock)",
              spec: "See chat plan for details",
            },
            {
              type: "copy",
              title: "Copy pack (from strategist lock)",
              spec: "See chat plan for details",
            },
          ],
        };
      }

      const meatyNow =
        meatyPlan ||
        !!(
          nextPlan &&
          nextPlan.strategy_summary &&
          nextPlan.strategy_summary.trim().length > 20 &&
          (!!nextPlan.action_steps?.length || !!nextPlan.deliverables?.length)
        );

      const shouldOpen =
        !!nextPlan &&
        (apiSaysReady ||
          shouldAutoOpenPlan({
            awaitingApproval: !!res.awaiting_approval,
            status: res.status || "chatting",
            reply,
            meatyPlan: meatyNow,
            hasPlan: !!nextPlan,
            userMessage: text,
          }));

      if (nextPlan) {
        setPlan(nextPlan);
      }

      if (shouldOpen && nextPlan) {
        setAwaitingApproval(true);
        setStatus("plan_ready");
        const planKey = [
          res.thread_id,
          (nextPlan.strategy_summary || "").slice(0, 80),
          String(nextPlan.action_steps?.length || 0),
          String(nextPlan.deliverables?.length || 0),
        ].join("|");
        // Always open Plan when a new plan is ready (re-open if content changed)
        if (planKey !== lastOpenedPlanKeyRef.current) {
          lastOpenedPlanKeyRef.current = planKey;
          setView("plan");
        } else {
          // Same plan re-confirmed — still jump to Plan so user sees approve CTAs
          setView("plan");
        }
      } else {
        setAwaitingApproval(!!res.awaiting_approval);
        setStatus(res.status || "chatting");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  async function onApprove(route: "copy" | "build" | "both") {
    if (!plan || executing) return;
    const label = routeLabel(route);
    const tid = plan.thread_id || threadId || uid();
    lastRouteRef.current = route;
    lastExecuteFailedRef.current = false;

    setAwaitingApproval(false);
    setStatus("executing");
    setExecuting(true);
    setExecutionComplete(false);
    setArtifacts([]);
    setExecSummary(null);
    setActiveRoute(route);
    setError(null);
    setExecNote(formatHandoffNote(`Running → ${label}`));
    setMessages((prev) => [
      ...prev,
      {
        id: uid(),
        role: "assistant",
        content: `Running **${label}** now. This can take 1–3 minutes (API may cold-start once).`,
      },
    ]);
    setView("pipeline");

    try {
      const res = await runExecute(tid, route, { ...plan, thread_id: tid });
      setThreadId(res.thread_id || tid);
      setArtifacts(res.artifacts || []);
      setExecSummary(res.summary || null);
      setExecNote(
        formatHandoffNote(
          res.status === "done"
            ? `Complete → ${label}\n${res.artifacts?.length ?? 0} artifact(s)`
            : `Finished with issues → ${label}\n${res.summary || ""}`,
        ),
      );

      if (res.status === "done" && (res.artifacts?.length ?? 0) > 0) {
        lastExecuteFailedRef.current = false;
        setExecutionComplete(true);
        setStatus("done");
        setMessages((prev) => [
          ...prev,
          {
            id: uid(),
            role: "assistant",
            content: `**${label} finished** — ${res.artifacts.length} output(s).\n\nSee **Outputs** for paste-ready drafts.\n\n${res.summary || ""}\n\n---\n\n${artifactsToMarkdown(res.artifacts, res.summary)}`,
          },
        ]);
        setView("outputs");
      } else if (res.status === "error") {
        lastExecuteFailedRef.current = true;
        setExecutionComplete(false);
        // Restore Plan so re-approve works without re-diagnosing
        setAwaitingApproval(true);
        setStatus("plan_ready");
        setError(res.summary || "Execution failed");
        setMessages((prev) => [
          ...prev,
          {
            id: uid(),
            role: "assistant",
            content: `**Execute failed:** ${res.summary || "Unknown error"}\n\nYour plan is still saved. Open **Plan** and re-route, or type **try again**.`,
          },
        ]);
        setView("plan");
      } else {
        lastExecuteFailedRef.current = false;
        setExecutionComplete(true);
        setStatus("done");
        setMessages((prev) => [
          ...prev,
          {
            id: uid(),
            role: "assistant",
            content:
              res.summary ||
              "Specialists finished but returned no artifacts. Re-run from Plan if needed.",
          },
        ]);
        setView("outputs");
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      lastExecuteFailedRef.current = true;
      setError(msg);
      // Critical: don't strand the user — unlock Plan for immediate re-approve
      setAwaitingApproval(true);
      setStatus("plan_ready");
      setExecutionComplete(false);
      setExecNote(formatHandoffNote(`Failed → ${label}\n${msg}`));
      setMessages((prev) => [
        ...prev,
        {
          id: uid(),
          role: "assistant",
          content: `**Execute failed:** ${msg}\n\nI already auto-retried the network once. Plan is still ready — open **Plan** and hit the route again, or type **try again** here.`,
        },
      ]);
      setView("plan");
    } finally {
      setExecuting(false);
    }
  }

  function onReject() {
    if (executing) return;
    setAwaitingApproval(false);
    setStatus("chatting");
    setExecNote(null);
    setExecutionComplete(false);
    setArtifacts([]);
    setExecSummary(null);
    setActiveRoute(null);
    setView("chat");
    setMessages((prev) => [
      ...prev,
      {
        id: uid(),
        role: "assistant",
        content:
          "Okay — plan parked. Tell me what to change and I'll revise.",
      },
    ]);
  }

  return (
    <div className={menuOpen ? "app-frame menu-open" : "app-frame"}>
      <Sidebar
        view={view}
        onNavigate={setView}
        onNewChat={onNewChat}
        systemsLive={systemsLive}
        stepLabel={stepLabel}
        outputCount={artifacts.length}
        menuOpen={menuOpen}
        onMenuOpenChange={setMenuOpen}
      />
      <div className="main-area">
        <div className="main-glow" aria-hidden />
        {view === "chat" && (
          <ChatView
            messages={messages}
            busy={busy || executing}
            input={input}
            setInput={setInput}
            onSubmit={onSubmit}
            systemsLive={systemsLive}
            error={error}
            logRef={logRef}
          />
        )}
        {view === "pipeline" && (
          <PipelineView
            current={currentStep}
            route={activeRoute || plan?.recommended_route}
            stage={plan?.stage}
            constraint={plan?.constraint}
            execNote={execNote}
            executing={executing}
            artifacts={artifacts}
            execSummary={execSummary}
            routeLabel={activeRoute ? routeLabel(activeRoute) : null}
            onOpenChat={() => setView("chat")}
            onOpenPlan={() => setView("plan")}
          />
        )}
        {view === "plan" && (
          <PlanView
            plan={plan}
            awaitingApproval={awaitingApproval}
            status={status}
            execNote={execNote}
            executing={executing}
            artifacts={artifacts}
            execSummary={execSummary}
            onApprove={onApprove}
            onReject={onReject}
            onOpenPipeline={() => setView("pipeline")}
            onOpenChat={() => setView("chat")}
          />
        )}
        {view === "outputs" && (
          <OutputsView
            artifacts={artifacts}
            execSummary={execSummary}
            executing={executing}
            routeLabel={activeRoute ? routeLabel(activeRoute) : null}
            activeRoute={activeRoute}
            onOpenPlan={() => setView("plan")}
            onOpenPipeline={() => setView("pipeline")}
            onOpenChat={() => setView("chat")}
          />
        )}
        {view === "agents" && (
          <AgentsView
            current={currentStep}
            hasPlan={!!plan}
            execNote={execNote}
            executing={executing}
            activeRoute={activeRoute}
            artifactCount={artifacts.length}
          />
        )}
      </div>
    </div>
  );
}
