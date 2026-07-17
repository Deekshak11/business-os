"""Route approved plans to specialist agents and collect artifacts."""

from __future__ import annotations

from typing import Any

from app.agents.builder import run_builder
from app.agents.copywriter import run_copywriter
from app.schemas.plan import Artifact, ExecuteResponse, Plan, Route


def run_execution(
    *,
    thread_id: str,
    route: Route,
    plan: Plan,
) -> ExecuteResponse:
    if plan.thread_id != thread_id:
        plan = plan.model_copy(update={"thread_id": thread_id})

    if route not in (Route.copy, Route.build, Route.both):
        return ExecuteResponse(
            thread_id=thread_id,
            status="error",
            route=route.value,
            summary="Invalid route — choose copy, build, or both.",
            artifacts=[],
            agent_logs=["route:invalid"],
        )

    artifacts: list[Artifact] = []
    logs: list[str] = []
    summaries: list[str] = []
    errors: list[str] = []

    run_copy = route in (Route.copy, Route.both)
    run_build = route in (Route.build, Route.both)

    if run_copy:
        logs.append("copy:start")
        out = run_copywriter(plan)
        logs.append(str(out.get("log") or "copy:done"))
        summaries.append(str(out.get("summary") or ""))
        artifacts.extend(out.get("artifacts") or [])
        if out.get("error"):
            errors.append(f"copy: {out['error']}")

    if run_build:
        logs.append("build:start")
        out = run_builder(plan)
        logs.append(str(out.get("log") or "build:done"))
        summaries.append(str(out.get("summary") or ""))
        artifacts.extend(out.get("artifacts") or [])
        if out.get("error"):
            errors.append(f"build: {out['error']}")

    if errors and not artifacts:
        return ExecuteResponse(
            thread_id=thread_id,
            status="error",
            route=route.value,
            summary=" · ".join(errors),
            artifacts=[],
            agent_logs=logs,
        )

    summary_parts = [s for s in summaries if s]
    if errors:
        summary_parts.append("Partial errors: " + " · ".join(errors))

    return ExecuteResponse(
        thread_id=thread_id,
        status="done",
        route=route.value,
        summary=" ".join(summary_parts) or f"Produced {len(artifacts)} artifact(s).",
        artifacts=artifacts,
        agent_logs=logs,
    )
