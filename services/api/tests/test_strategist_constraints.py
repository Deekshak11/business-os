"""Unit tests for preference extraction + playbook routing helpers."""

from app.agents.strategist import (
    extract_preferences,
    _playbook_queries_for,
    _infer_stage_hint,
)
from app.schemas.plan import ChatMessage


def test_outreach_preference_detected():
    prefs = extract_preferences(
        "NO REACHOUTSSS. only content for lead gen. cta is in end of video",
        [ChatMessage(role="user", content="i hate cold outreach so no")],
    )
    assert prefs
    blob = " ".join(prefs).lower()
    assert "content" in blob or "outreach" in blob


def test_playbook_routing_hooks_and_closing():
    qs = _playbook_queries_for(
        "youtube hooks and book a call on calendly for no-show automation",
        "0",
    )
    joined = " ".join(qs).lower()
    assert "hook" in joined or "closing" in joined or "lead" in joined


def test_stage_hint():
    assert _infer_stage_hint("I am on stage 0", None) == "0"
