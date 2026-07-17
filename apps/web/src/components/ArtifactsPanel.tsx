import { useState } from "react";
import { Artifact } from "../api";
import { cleanArtifactBody } from "../lib/artifactText";
import { Markdown } from "./Markdown";

// Re-export cleaners so existing imports keep working
export {
  cleanArtifactBody,
  prettifyIfRawJson,
  scrubArtifactText,
  stripDuplicateTitle,
  stripInlineSourcesDump,
} from "../lib/artifactText";

type Props = {
  artifacts: Artifact[];
  summary?: string | null;
  executing?: boolean;
  routeLabel?: string | null;
  /** When true, show filter chips for Copy / Build */
  filterable?: boolean;
};

function agentName(agent: string) {
  if (agent === "copy") return "Copywriting Agent";
  if (agent === "build") return "Builder Agent";
  return agent;
}

export function ArtifactsPanel({
  artifacts,
  summary,
  executing,
  routeLabel,
  filterable = false,
}: Props) {
  const [filter, setFilter] = useState<"all" | "copy" | "build">("all");

  if (executing) {
    return (
      <div className="artifacts-panel card-elevated">
        <p className="section-label">Execute · stage 05</p>
        <h3 className="artifacts-heading">
          {routeLabel ? `${routeLabel} running…` : "Specialists running…"}
        </h3>
        <p className="muted-line">
          Generating paste-ready outputs from the approved plan. Results open
          under <strong>Outputs</strong> when finished (also summarized in Chat).
        </p>
        <div className="exec-progress">
          <span className="spinner" />
          <span>Working — usually 30–90 seconds</span>
        </div>
      </div>
    );
  }

  if (!artifacts.length) {
    return null;
  }

  const visible =
    filter === "all"
      ? artifacts
      : artifacts.filter((a) => a.agent === filter);

  const copyN = artifacts.filter((a) => a.agent === "copy").length;
  const buildN = artifacts.filter((a) => a.agent === "build").length;

  return (
    <div className="artifacts-panel">
      <div className="artifacts-intro">
        <p className="section-label">Outputs · ready to use</p>
        {summary ? <p className="artifacts-summary">{summary}</p> : null}
        <p className="muted-line">
          Full drafts from specialists. Copy any section into your tools.
        </p>
      </div>

      {filterable && (copyN > 0 || buildN > 0) && (
        <div className="outputs-filter chip-row">
          <button
            type="button"
            className={filter === "all" ? "chip chip-glow" : "chip chip-btn"}
            onClick={() => setFilter("all")}
          >
            All ({artifacts.length})
          </button>
          {copyN > 0 && (
            <button
              type="button"
              className={filter === "copy" ? "chip chip-glow" : "chip chip-btn"}
              onClick={() => setFilter("copy")}
            >
              Copywriting ({copyN})
            </button>
          )}
          {buildN > 0 && (
            <button
              type="button"
              className={
                filter === "build" ? "chip chip-glow" : "chip chip-btn"
              }
              onClick={() => setFilter("build")}
            >
              Builder ({buildN})
            </button>
          )}
        </div>
      )}

      <div className="artifacts-list">
        {visible.map((a) => {
          const body = cleanArtifactBody(a.title, a.content);
          return (
            <article key={a.id} className="artifact-card card-elevated">
              <div className="artifact-meta">
                <span className="chip">{agentName(a.agent)}</span>
                <span className="chip chip-kind">{a.kind}</span>
              </div>
              <div className="artifact-title-row">
                <h3>{a.title}</h3>
                <button
                  type="button"
                  className="btn btn-ghost btn-sm"
                  onClick={() => {
                    void navigator.clipboard?.writeText(body);
                  }}
                >
                  Copy
                </button>
              </div>
              <div className="artifact-body">
                <Markdown content={body} />
              </div>
              {!!a.sources?.length && (
                <div className="artifact-sources">
                  <span className="section-label">Sources</span>
                  <ul>
                    {a.sources.map((s, i) => (
                      <li key={i} className="font-mono">
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </article>
          );
        })}
      </div>
    </div>
  );
}
