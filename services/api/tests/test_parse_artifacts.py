"""Tests for specialist output salvage / scrub."""

from app.llm.parse_artifacts import (
    parse_specialist_output,
    scrub_body,
    unescape_content,
)


def test_unescape_literal_n():
    assert "\n" in unescape_content("a\\nb")
    assert unescape_content("line1\\n\\nline2").count("\n") >= 2


def test_scrub_quote_glue_screenshot():
    raw = (
        '"\\n\\n"Testimonial Scripts (3)\\n"\\n\\n"'
        "Script 1: Pre-Shoot Prep\\n\"\\nHey [Name] — excited."
    )
    out = scrub_body(raw)
    assert "\\n" not in out
    assert "Testimonial Scripts (3)" in out
    assert "Script 1: Pre-Shoot Prep" in out
    assert "Hey [Name]" in out
    assert not out.startswith('"')


def test_parse_valid_json():
    raw = """
    {
      "summary": "Two drafts ready.",
      "artifacts": [
        {
          "title": "VSL Script",
          "kind": "script",
          "content": "## Hook\\n\\nStop the no-shows.\\n\\n## CTA\\n\\nBook a call.",
          "sources": ["Hormozi.md"]
        },
        {
          "title": "Email 1",
          "kind": "email",
          "content": "Subject: Quick win\\n\\nHey {{name}},\\n\\nHere is the free build.",
          "sources": []
        }
      ]
    }
    """
    summary, arts = parse_specialist_output(raw, agent="copy")
    assert "Two drafts" in summary
    assert len(arts) == 2
    assert arts[0].title == "VSL Script"
    assert "\n" in arts[0].content
    assert "\\n" not in arts[0].content
    assert "Stop the no-shows" in arts[0].content
    assert arts[0].sources == ["Hormozi.md"]


def test_parse_delimiter_format():
    raw = """
<<<SUMMARY>>>
Pack ready.
<<<ARTIFACT>>>
title: YouTube VSL
kind: script
---
## Hook

Your calendar is full of ghosts.

## CTA

Book the free build.
<<<ARTIFACT>>>
title: Nurture email
kind: email
---
Subject: Still free

Hey — the build slot is open.
"""
    summary, arts = parse_specialist_output(raw, agent="copy")
    assert "Pack ready" in summary
    assert len(arts) == 2
    assert arts[0].title == "YouTube VSL"
    assert "calendar is full" in arts[0].content
    assert "\\n" not in arts[0].content


def test_parse_truncated_json_regex_salvage():
    # Unclosed content string — classic Flash truncation
    raw = (
        '{"summary":"ok","artifacts":[{"title":"VSL","kind":"script",'
        '"content":"## Hook\\n\\nHello world this is the script body'
    )
    summary, arts = parse_specialist_output(raw, agent="copy", fallback_title="Copy")
    assert arts
    assert "Hello world" in arts[0].content
    assert "\\n" not in arts[0].content


def test_scrub_preserves_fenced_json():
    md = 'Setup:\n\n```json\n{"nodes": []}\n```\n\nDone.'
    out = scrub_body(md)
    assert "```json" in out
    assert '"nodes"' in out


def test_clean_markdown_untouched():
    md = "## Hook\n\n**Bold**\n\n1. One\n2. Two"
    assert scrub_body(md) == md
