import type { Artifact } from "../api";
import {
  PIPELINE_STEPS,
  PipelineStepId,
  isStepActive,
  isStepDone,
} from "../lib/pipeline";
import {
  formatConstraint,
  formatRoute,
  formatStage,
} from "../lib/format";
import { formatHandoffNote } from "../lib/handoff";
import { ArtifactsPanel } from "./ArtifactsPanel";
import { PageHeader } from "./PageHeader";

type Props = {
  current: PipelineStepId;
  route?: string | null;
  stage?: string | null;
  constraint?: string | null;
  execNote?: string | null;
  executing?: boolean;
  artifacts?: Artifact[];
  execSummary?: string | null;
  routeLabel?: string | null;
  onOpenChat: () => void;
  onOpenPlan: () => void;
};

export function PipelineView({
  current,
  route,
  stage,
  constraint,
  execNote,
  executing,
  artifacts = [],
  execSummary,
  routeLabel: agentRouteLabel,
  onOpenChat,
  onOpenPlan,
}: Props) {
  const active = PIPELINE_STEPS.find((s) => s.id === current)!;
  const routeChip = formatRoute(route);

  return (
    <div className="view pipeline-view">
      <PageHeader
        title={
          <>
            Live <em className="font-display text-gradient">pipeline</em>
          </>
        }
        description="Live progress across strategy, approval, and specialist handoff."
      />

      <div className="page-body">
        <div className="page-rail">
          <div className="pipeline-layout">
            <div className="pipeline-track horizontal" role="list">
              {PIPELINE_STEPS.map((s, i) => {
                const done = isStepDone(current, s.id);
                const on = isStepActive(current, s.id);
                return (
                  <div
                    key={s.id}
                    role="listitem"
                    className={
                      on
                        ? "pipe-node horizontal active"
                        : done
                          ? "pipe-node horizontal done"
                          : "pipe-node horizontal"
                    }
                  >
                    <div className="pipe-orb">
                      <span className="font-mono">{s.short}</span>
                      {i < PIPELINE_STEPS.length - 1 && (
                        <span className="pipe-line-h" aria-hidden />
                      )}
                    </div>
                    <div className="pipe-meta">
                      <strong>{s.label}</strong>
                      <span className="pipe-desc">{s.description}</span>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="stage-stage card-elevated">
              <div className="pulse-ring" aria-hidden />
              <p className="font-mono stage-kicker">Current step</p>
              <h2>{active.label}</h2>
              <p>{active.description}</p>

              <div className="chip-row" style={{ marginTop: "1.1rem" }}>
                {stage && stage !== "unknown" && (
                  <span className="chip">
                    <strong>{formatStage(stage)}</strong>
                  </span>
                )}
                {constraint && constraint !== "unknown" && (
                  <span className="chip">
                    Constraint{" "}
                    <strong>{formatConstraint(constraint)}</strong>
                  </span>
                )}
                {routeChip && (
                  <span className="chip">
                    Route <strong>{routeChip}</strong>
                  </span>
                )}
                {executing && (
                  <span className="chip chip-glow">Running specialists</span>
                )}
                {current === "done" && artifacts.length > 0 && (
                  <span className="chip chip-glow">
                    {artifacts.length} output(s)
                  </span>
                )}
              </div>

              {formatHandoffNote(execNote) ? (
                <div className="exec-note">
                  <p className="section-label">Handoff status</p>
                  <p style={{ whiteSpace: "pre-wrap", margin: 0 }}>
                    {formatHandoffNote(execNote)}
                  </p>
                </div>
              ) : null}

              <div className="actions action-row-focus">
                {(current === "context" || current === "strategy") && (
                  <button
                    type="button"
                    className="btn btn-primary btn-focus"
                    onClick={onOpenChat}
                  >
                    Continue in chat
                  </button>
                )}
                {(current === "plan" || current === "approve") && (
                  <button
                    type="button"
                    className="btn btn-electric btn-focus"
                    onClick={onOpenPlan}
                  >
                    Review plan
                  </button>
                )}
                {(current === "execute" || current === "done") && (
                  <>
                    <button
                      type="button"
                      className="btn btn-ghost btn-focus"
                      onClick={onOpenPlan}
                    >
                      View plan
                    </button>
                    <button
                      type="button"
                      className="btn btn-primary btn-focus"
                      onClick={onOpenChat}
                    >
                      Open chat
                    </button>
                  </>
                )}
              </div>
            </div>

            {(executing || artifacts.length > 0) && (
              <ArtifactsPanel
                artifacts={artifacts}
                summary={execSummary}
                executing={!!executing}
                routeLabel={agentRouteLabel}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
