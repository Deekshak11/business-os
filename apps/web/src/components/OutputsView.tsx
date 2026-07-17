import type { Artifact } from "../api";
import { ArtifactsPanel } from "./ArtifactsPanel";
import { PageHeader } from "./PageHeader";

type Props = {
  artifacts: Artifact[];
  execSummary: string | null;
  executing: boolean;
  routeLabel: string | null;
  activeRoute: "copy" | "build" | "both" | null;
  onOpenPlan: () => void;
  onOpenPipeline: () => void;
  onOpenChat: () => void;
};

export function OutputsView({
  artifacts,
  execSummary,
  executing,
  routeLabel,
  activeRoute,
  onOpenPlan,
  onOpenPipeline,
  onOpenChat,
}: Props) {
  const copyCount = artifacts.filter((a) => a.agent === "copy").length;
  const buildCount = artifacts.filter((a) => a.agent === "build").length;

  return (
    <div className="view outputs-view">
      <PageHeader
        title={
          <>
            Specialist <em className="font-display text-gradient">outputs</em>
          </>
        }
        description="Paste-ready drafts from Copywriting Agent and Builder Agent."
        actions={
          <>
            <button
              type="button"
              className="btn btn-ghost btn-focus"
              onClick={onOpenPipeline}
            >
              Pipeline
            </button>
            <button
              type="button"
              className="btn btn-ghost btn-focus"
              onClick={onOpenPlan}
            >
              Plan
            </button>
            <button
              type="button"
              className="btn btn-ghost btn-focus"
              onClick={onOpenChat}
            >
              Chat
            </button>
          </>
        }
      />

      <div className="page-body">
        <div className="page-rail">
          {!executing && artifacts.length === 0 && (
            <div className="empty-card card-elevated">
              <p className="empty">
                No outputs yet. Approve a plan and route it to{" "}
                <strong>Copywriting Agent</strong>,{" "}
                <strong>Builder Agent</strong>, or <strong>Both</strong>. Real
                drafts land here when stage 05 finishes.
              </p>
              <div className="actions action-row-focus">
                <button
                  type="button"
                  className="btn btn-primary btn-focus"
                  onClick={onOpenPlan}
                >
                  Go to plan
                </button>
                <button
                  type="button"
                  className="btn btn-ghost btn-focus"
                  onClick={onOpenPipeline}
                >
                  View pipeline
                </button>
              </div>
            </div>
          )}

          {(executing || artifacts.length > 0) && (
            <>
              {!executing && artifacts.length > 0 && (
                <div className="outputs-stats chip-row">
                  <span className="chip">
                    <strong>{artifacts.length}</strong> total
                  </span>
                  {copyCount > 0 && (
                    <span className="chip">
                      Copywriting <strong>{copyCount}</strong>
                    </span>
                  )}
                  {buildCount > 0 && (
                    <span className="chip">
                      Builder <strong>{buildCount}</strong>
                    </span>
                  )}
                  {activeRoute && (
                    <span className="chip chip-glow">
                      Route {activeRoute}
                    </span>
                  )}
                </div>
              )}

              <ArtifactsPanel
                artifacts={artifacts}
                summary={execSummary}
                executing={executing}
                routeLabel={routeLabel}
                filterable
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
