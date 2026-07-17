import type { PipelineStepId } from "../lib/pipeline";
import { PageHeader } from "./PageHeader";

type Props = {
  current: PipelineStepId;
  hasPlan: boolean;
  execNote: string | null;
  executing?: boolean;
  activeRoute?: "copy" | "build" | "both" | null;
  artifactCount?: number;
};

export function AgentsView({
  current,
  hasPlan,
  execNote,
  executing,
  activeRoute,
  artifactCount = 0,
}: Props) {
  const strategistActive =
    !executing &&
    (current === "context" ||
      current === "strategy" ||
      current === "plan" ||
      current === "approve");

  const copyActive =
    executing &&
    (activeRoute === "copy" || activeRoute === "both");
  const buildActive =
    executing &&
    (activeRoute === "build" || activeRoute === "both");

  const copyDone =
    !executing &&
    artifactCount > 0 &&
    (!!execNote && /copywriting|copy/i.test(execNote));
  const buildDone =
    !executing &&
    artifactCount > 0 &&
    (!!execNote && /builder|build/i.test(execNote));

  return (
    <div className="view agents-view">
      <PageHeader
        title={
          <>
            Specialist <em className="font-display text-gradient">agents</em>
          </>
        }
        description="Business Strategist, Copywriting Agent, and Builder Agent."
      />

      <div className="page-body">
        <div className="page-rail">
          <div className="agents-grid">
            <article
              className={
                strategistActive ? "agent-tile active" : "agent-tile"
              }
            >
              <div className="agent-num font-mono">01</div>
              <h3>Business Strategist</h3>
              <p>Hormozi vault · stages · frameworks · plan</p>
              <span className="badge">
                {strategistActive ? "Active" : "Standby"}
              </span>
            </article>
            <article
              className={
                copyActive || copyDone ? "agent-tile active" : "agent-tile"
              }
            >
              <div className="agent-num font-mono">02</div>
              <h3>Copywriting Agent</h3>
              <p>Copy-OS RAG · headlines, pages, sequences</p>
              <span className="badge">
                {copyActive
                  ? "Running…"
                  : copyDone
                    ? "Outputs ready"
                    : "After approve"}
              </span>
            </article>
            <article
              className={
                buildActive || buildDone ? "agent-tile active" : "agent-tile"
              }
            >
              <div className="agent-num font-mono">03</div>
              <h3>Builder Agent</h3>
              <p>Implementation pack · checklists · ship order</p>
              <span className="badge">
                {buildActive
                  ? "Running…"
                  : buildDone
                    ? "Outputs ready"
                    : "After approve"}
              </span>
            </article>
          </div>

          {executing && (
            <p className="empty" style={{ marginTop: "1.25rem" }}>
              Specialists are generating artifacts now (stage 05). Watch{" "}
              <strong>Pipeline</strong> for status; finished drafts open under{" "}
              <strong>Outputs</strong> (06) — usually 30–90s.
            </p>
          )}

          {!executing && artifactCount > 0 && (
            <p className="empty" style={{ marginTop: "1.25rem" }}>
              {artifactCount} artifact(s) ready — open <strong>Outputs</strong>{" "}
              (last menu item) for the full pack.
            </p>
          )}

          {!hasPlan && !executing && (
            <p className="empty" style={{ marginTop: "1.25rem" }}>
              Start in Chat. When a plan is ready, approve it to run specialists.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
