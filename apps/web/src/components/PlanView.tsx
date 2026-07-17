import type { Artifact, Plan } from "../api";
import {
  displayField,
  formatConstraint,
  formatRoute,
  formatStage,
  isEmptyValue,
} from "../lib/format";
import { formatHandoffNote } from "../lib/handoff";
import { ArtifactsPanel } from "./ArtifactsPanel";
import { Markdown } from "./Markdown";
import { PageHeader } from "./PageHeader";

type Props = {
  plan: Plan | null;
  awaitingApproval: boolean;
  /** Pipeline/session status — plan_ready also shows approve buttons */
  status?: string;
  execNote: string | null;
  executing?: boolean;
  artifacts?: Artifact[];
  execSummary?: string | null;
  onApprove: (route: "copy" | "build" | "both") => void;
  onReject: () => void;
  onOpenPipeline: () => void;
  onOpenChat: () => void;
};

export function PlanView({
  plan,
  awaitingApproval,
  status,
  execNote,
  executing,
  artifacts = [],
  execSummary,
  onApprove,
  onReject,
  onOpenPipeline,
  onOpenChat,
}: Props) {
  const routeLabel = plan ? formatRoute(plan.recommended_route) : null;
  const meaty =
    !!plan &&
    !!(plan.strategy_summary && plan.strategy_summary.trim().length > 20) &&
    (!!plan.action_steps?.length || !!plan.deliverables?.length);
  // Show approve if flag is set OR plan is ready/meaty and not already executing
  const canApprove =
    !executing &&
    (awaitingApproval ||
      status === "plan_ready" ||
      (meaty &&
        !execNote &&
        plan?.recommended_route != null &&
        plan.recommended_route !== "none"));

  return (
    <div className="view plan-view">
      <PageHeader
        title={
          <>
            Execution <em className="font-display text-gradient">plan</em>
          </>
        }
        description="Review the strategy, then send it to Copywriting or Builder."
        actions={
          <>
            <button
              type="button"
              className="btn btn-ghost btn-focus"
              onClick={onOpenChat}
            >
              Chat
            </button>
            <button
              type="button"
              className="btn btn-ghost btn-focus"
              onClick={onOpenPipeline}
            >
              Pipeline
            </button>
          </>
        }
      />

      <div className="page-body">
        <div className="page-rail">
          {!plan ? (
            <div className="empty-card card-elevated">
              <p className="empty">
                No plan yet. Keep chatting with the Strategist — once it has
                enough context, the plan will show up here for approval.
              </p>
              <button
                type="button"
                className="btn btn-primary btn-focus"
                onClick={onOpenChat}
              >
                Go to chat
              </button>
            </div>
          ) : (
            <div className="card-elevated plan-panel">
              <div className="chip-row">
                <span className="chip">
                  <strong>{formatStage(plan.stage)}</strong>
                </span>
                <span className="chip">
                  Constraint{" "}
                  <strong>{formatConstraint(plan.constraint)}</strong>
                </span>
                {routeLabel && (
                  <span className="chip">
                    Route <strong>{routeLabel}</strong>
                  </span>
                )}
                {awaitingApproval && (
                  <span className="chip chip-glow">Ready to approve</span>
                )}
              </div>

              <section className="plan-section">
                <h3 className="section-label">Summary</h3>
                <div className="section-body">
                  {!isEmptyValue(plan.strategy_summary) ? (
                    <Markdown content={plan.strategy_summary!} />
                  ) : (
                    <p className="muted-line">No summary yet.</p>
                  )}
                </div>
              </section>

              <div className="plan-meta-grid">
                <div>
                  <h3 className="section-label">Goal</h3>
                  <p className="section-body">
                    {displayField(plan.business_context?.goals)}
                  </p>
                </div>
                <div>
                  <h3 className="section-label">Offer</h3>
                  <p className="section-body">
                    {displayField(plan.business_context?.offer)}
                  </p>
                </div>
              </div>

              {!!plan.action_steps?.length && (
                <section className="plan-section">
                  <h3 className="section-label">Actions</h3>
                  <ol className="action-list clean">
                    {plan.action_steps.map((s) => (
                      <li key={s.step}>{s.action}</li>
                    ))}
                  </ol>
                </section>
              )}

              {!!plan.frameworks_cited?.length && (
                <section className="plan-section">
                  <h3 className="section-label">From the vault</h3>
                  <ul className="cite-list">
                    {plan.frameworks_cited.map((c, i) => (
                      <li key={i} className="cite-card">
                        <div className="cite-name">
                          {c.name || "Framework"}
                        </div>
                        {c.file ? (
                          <div className="cite-file">{c.file}</div>
                        ) : null}
                        {c.why ? (
                          <div className="cite-why">{c.why}</div>
                        ) : null}
                      </li>
                    ))}
                  </ul>
                </section>
              )}

              {!!plan.deliverables?.length && (
                <section className="plan-section">
                  <h3 className="section-label">Deliverables</h3>
                  <ul className="action-list clean">
                    {plan.deliverables.map((d, i) => (
                      <li key={d.id || i}>
                        {d.title}
                        {d.spec ? ` — ${d.spec}` : ""}
                      </li>
                    ))}
                  </ul>
                </section>
              )}

              {!!plan.questions_still_open?.length && (
                <section className="plan-section">
                  <h3 className="section-label">Still need</h3>
                  <ul className="action-list clean">
                    {plan.questions_still_open.map((q, i) => (
                      <li key={i}>{q}</li>
                    ))}
                  </ul>
                </section>
              )}

              {!!plan.risks?.length && (
                <section className="plan-section">
                  <h3 className="section-label">Risks</h3>
                  <ul className="action-list clean">
                    {plan.risks.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </section>
              )}

              {formatHandoffNote(execNote) ? (
                <div className="exec-note">
                  <p className="section-label">Handoff status</p>
                  <p style={{ whiteSpace: "pre-wrap", margin: 0 }}>
                    {formatHandoffNote(execNote)}
                  </p>
                </div>
              ) : null}

              <div
                className={`actions sticky-actions action-row-focus ${canApprove ? "lit" : ""}`}
              >
                {canApprove ? (
                  <>
                    <span className="actions-label">
                      Approve &amp; run stage 05 specialists (drafts land in Outputs)
                    </span>
                    <button
                      type="button"
                      className="btn btn-electric btn-focus"
                      onClick={() => onApprove("copy")}
                    >
                      Copywriting Agent
                    </button>
                    <button
                      type="button"
                      className="btn btn-electric btn-focus"
                      onClick={() => onApprove("build")}
                    >
                      Builder Agent
                    </button>
                    <button
                      type="button"
                      className="btn btn-primary btn-focus"
                      onClick={() => onApprove("both")}
                    >
                      Both
                    </button>
                    <button
                      type="button"
                      className="btn btn-ghost btn-focus"
                      onClick={onReject}
                    >
                      Revise in chat
                    </button>
                  </>
                ) : executing ? (
                  <p className="muted-line" style={{ margin: 0 }}>
                    Specialists running on stage 05 · Execute. Watch{" "}
                    <button
                      type="button"
                      className="linkish"
                      onClick={onOpenPipeline}
                    >
                      Pipeline
                    </button>{" "}
                    for live progress and artifacts.
                  </p>
                ) : execNote || artifacts.length > 0 ? (
                  <p className="muted-line" style={{ margin: 0 }}>
                    {artifacts.length
                      ? `${artifacts.length} output(s) ready — open Outputs (last menu · stage 06). Start a new chat for another run.`
                      : "Handoff recorded. Open Pipeline for stage status."}
                  </p>
                ) : (
                  <p className="muted-line" style={{ margin: 0 }}>
                    Keep chatting until the strategist marks this plan ready to
                    approve.
                  </p>
                )}
              </div>
            </div>
          )}

          {(executing || artifacts.length > 0) && (
            <div style={{ marginTop: "1.25rem" }}>
              <ArtifactsPanel
                artifacts={artifacts}
                summary={execSummary}
                executing={!!executing}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
