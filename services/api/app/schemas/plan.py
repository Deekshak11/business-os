"""Shared Plan JSON contract for Strategist → approval → executors."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class Constraint(str, Enum):
    product = "product"
    marketing = "marketing"
    sales = "sales"
    cs = "cs"
    ops = "ops"
    cash = "cash"
    unknown = "unknown"


class Route(str, Enum):
    copy = "copy"
    build = "build"
    both = "both"
    none = "none"


class DeliverableType(str, Enum):
    copy = "copy"
    build = "build"


class Citation(BaseModel):
    name: str = ""
    file: str = ""
    why: str = ""


class BusinessContext(BaseModel):
    industry: str = ""
    offer: str = ""
    headcount: Optional[int] = None
    revenue_signals: str = ""
    goals: str = ""
    constraints_stated: list[str] = Field(default_factory=list)


class ActionStep(BaseModel):
    step: int
    action: str
    owner: str = "user"  # user | copy | build


class Deliverable(BaseModel):
    id: str = Field(default_factory=lambda: f"d-{uuid4().hex[:8]}")
    type: DeliverableType
    title: str
    spec: str = ""
    acceptance: list[str] = Field(default_factory=list)


class Plan(BaseModel):
    version: str = "1.0"
    thread_id: str = Field(default_factory=lambda: str(uuid4()))
    business_context: BusinessContext = Field(default_factory=BusinessContext)
    stage: str = "unknown"
    constraint: Constraint = Constraint.unknown
    strategy_summary: str = ""
    frameworks_cited: list[Citation] = Field(default_factory=list)
    action_steps: list[ActionStep] = Field(default_factory=list)
    deliverables: list[Deliverable] = Field(default_factory=list)
    recommended_route: Route = Route.none
    risks: list[str] = Field(default_factory=list)
    questions_still_open: list[str] = Field(default_factory=list)
    raw_assistant_notes: str = ""

    def to_handoff_dict(self) -> dict[str, Any]:
        """Compact dict for executor prompts (no bloated chat history)."""
        return self.model_dump(mode="json")


class ChatMessage(BaseModel):
    role: str  # user | assistant | system
    content: str


class ChatRequest(BaseModel):
    thread_id: Optional[str] = None
    message: str
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    thread_id: str
    reply: str
    plan: Optional[Plan] = None
    awaiting_approval: bool = False
    status: str = "chatting"  # chatting | plan_ready | awaiting_approval | executing | done


class ApprovalRequest(BaseModel):
    thread_id: str
    approved: bool
    route: Optional[Route] = None
    plan_edits: Optional[dict[str, Any]] = None
    notes: str = ""


class Artifact(BaseModel):
    """Specialist output the user can read / copy / ship."""

    id: str = Field(default_factory=lambda: f"a-{uuid4().hex[:8]}")
    agent: str  # copy | build
    title: str
    kind: str = "deliverable"  # headline | page | email | script | pack | note
    content: str = ""
    sources: list[str] = Field(default_factory=list)


class ExecuteRequest(BaseModel):
    thread_id: str
    route: Route  # copy | build | both
    plan: Plan
    notes: str = ""


class ExecuteResponse(BaseModel):
    thread_id: str
    status: str = "done"  # done | error
    route: str
    summary: str = ""
    artifacts: list[Artifact] = Field(default_factory=list)
    agent_logs: list[str] = Field(default_factory=list)


class RagQueryRequest(BaseModel):
    collection: str  # hormozi | copyos
    query: str
    n_results: int = 6
    where: Optional[dict[str, Any]] = None


class RagHit(BaseModel):
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    distance: Optional[float] = None


class RagQueryResponse(BaseModel):
    collection: str
    hits: list[RagHit]
