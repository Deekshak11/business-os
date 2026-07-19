# -*- coding: utf-8 -*-
"""Build RAG-optimized Copy-OS vault from original 14 mega-docs."""
from __future__ import annotations

import re
from pathlib import Path

SRC = Path(r"H:\Copy OS")
DST = Path(r"H:\Copy-OS")

# Original filename -> (folder, type, stage_default, base_slug, tags)
DOC_META = {
    "01 - Navigation System & User Guide.md": (
        "00-Navigation",
        "navigation",
        "all",
        "Nav",
        ["navigation", "workflows", "glossary"],
    ),
    "02 - Universal Laws of Pesuasion.md": (
        "01-Strategic-Foundation",
        "framework",
        "strategy",
        "Laws",
        ["persuasion", "cialdini", "kahneman", "principles"],
    ),
    "03 - Market Diagnosis.md": (
        "01-Strategic-Foundation",
        "framework",
        "strategy",
        "Market",
        ["awareness", "schwartz", "avatar", "sophistication"],
    ),
    "04 - Positioning.md": (
        "01-Strategic-Foundation",
        "framework",
        "strategy",
        "Positioning",
        ["big-idea", "mechanism", "usp", "voice"],
    ),
    "05 - Irresistible Offers.md": (
        "01-Strategic-Foundation",
        "framework",
        "strategy",
        "Offers",
        ["value-equation", "stack", "guarantee", "urgency"],
    ),
    "06 - Universal Structures.md": (
        "02-Copy-Architecture",
        "structure",
        "writing",
        "Structures",
        ["sales-letter", "vsl", "webinar", "blueprint"],
    ),
    "07 - Headlines & Leads.md": (
        "02-Copy-Architecture",
        "structure",
        "writing",
        "Headlines-Leads",
        ["headlines", "leads", "formulas", "swipes"],
    ),
    "08 - Bullets & Fascinations.md": (
        "02-Copy-Architecture",
        "structure",
        "writing",
        "Bullets",
        ["bullets", "fascinations", "bencivenga"],
    ),
    "09 - Proof & Credibility.md": (
        "03-Tactical-Execution",
        "framework",
        "writing",
        "Proof",
        ["proof", "testimonials", "credibility"],
    ),
    "10 - Persuasive Language.md": (
        "03-Tactical-Execution",
        "process",
        "writing",
        "Language",
        ["power-words", "hypnotic", "clarity"],
    ),
    "11 - Funnels and Email Sequences.md": (
        "03-Tactical-Execution",
        "process",
        "funnels",
        "Funnels-Email",
        ["funnels", "email", "sequences", "value-ladder"],
    ),
    "12 - Overcoming Objections.md": (
        "03-Tactical-Execution",
        "framework",
        "writing",
        "Objections",
        ["objections", "spin", "faq", "false-beliefs"],
    ),
    "13 - Optimization.md": (
        "04-Systems-Optimization",
        "process",
        "optimize",
        "Optimization",
        ["testing", "metrics", "ltv-cac", "benchmarks"],
    ),
    "14 - Reference Library.md": (
        "04-Systems-Optimization",
        "swipe",
        "reference",
        "Reference",
        ["swipes", "templates", "checklists", "power-words"],
    ),
}

# Split on H1 or H2 that look like major sections
SPLIT_RE = re.compile(
    r"^(#{1,2})\s+\*{0,2}(SECTION|PART|WORKFLOW|BLOCK)\b.*$",
    re.MULTILINE | re.IGNORECASE,
)

# Also split pure H1 titles that aren't the first line sometimes
H1_RE = re.compile(r"^(#)\s+\*{0,2}.+\*{0,2}\s*$", re.MULTILINE)


def slugify(text: str, max_len: int = 60) -> str:
    t = re.sub(r"[*_#`]", "", text)
    t = re.sub(r"[^\w\s\-]", "", t, flags=re.UNICODE)
    t = re.sub(r"\s+", "-", t.strip())
    t = re.sub(r"-+", "-", t)
    t = t.strip("-")
    if len(t) > max_len:
        t = t[:max_len].rstrip("-")
    return t or "section"


def extract_title(header_line: str) -> str:
    t = re.sub(r"^#+\s*", "", header_line).strip()
    t = t.strip("*").strip()
    return t


def when_to_use_for(doc_slug: str, title: str) -> str:
    tl = (doc_slug + " " + title).lower()
    rules = [
        ("headline", "Use when writing or scoring headlines / openings."),
        ("lead", "Use when choosing or writing leads by awareness state."),
        ("bullet", "Use when writing bullets, fascinations, or curiosity lines."),
        ("offer", "Use when engineering the offer, stack, price, guarantee, urgency."),
        ("state", "Use when diagnosing Schwartz awareness state for the market."),
        ("sophistication", "Use when diagnosing market sophistication stage."),
        ("big idea", "Use when creating or scoring a Big Idea."),
        ("mechanism", "Use when defining unique mechanism / USP."),
        ("cialdini", "Use when applying Cialdini triggers in copy."),
        ("kahneman", "Use when leveraging System 1 / heuristics."),
        ("proof", "Use when stacking credibility and testimonials."),
        ("objection", "Use when handling price/time/trust objections in copy."),
        ("funnel", "Use when mapping funnels or value ladder."),
        ("email", "Use when writing email sequences."),
        ("vsl", "Use when structuring a VSL."),
        ("webinar", "Use when building webinar / perfect webinar copy."),
        ("test", "Use when prioritizing tests and reading metrics."),
        ("swipe", "Use as reference/swipes — adapt, do not copy blindly."),
        ("workflow", "Use for step-by-step execution of a common copy task."),
        ("glossary", "Use to define a technical copy term."),
        ("navigation", "Use to orient which Copy-OS doc/section to open."),
    ]
    for key, msg in rules:
        if key in tl:
            return msg
    return f"Use when working on topics covered in: {title}"


def frontmatter(
    title: str,
    ftype: str,
    source: str,
    stage: str,
    tags: list[str],
    summary: str,
    when_to_use: str,
    parent: str,
    section_id: str,
) -> str:
    tags_s = ", ".join(tags)
    # Escape quotes in YAML strings
    def yq(s: str) -> str:
        return s.replace('"', "'")

    return f"""---
title: "{yq(title)}"
type: {ftype}
source: "{yq(source)}"
stage: {stage}
tags: [{tags_s}]
keywords: []
parent_doc: "{yq(parent)}"
section_id: "{yq(section_id)}"
last_updated: 2026-07-16
summary: "{yq(summary[:220])}"
when_to_use: "{yq(when_to_use[:220])}"
---

"""


def split_document(text: str) -> list[tuple[str, str]]:
    """Return list of (header_or_preamble_title, body including header)."""
    matches = list(SPLIT_RE.finditer(text))
    if not matches:
        # Fallback: split on all H1
        matches = list(H1_RE.finditer(text))
        # Keep only matches that are reasonably major (short-ish titles)
        filtered = []
        for m in matches:
            line = m.group(0)
            if len(line) < 120:
                filtered.append(m)
        matches = filtered

    if not matches:
        return [("Full-Document", text)]

    chunks: list[tuple[str, str]] = []
    # Preamble before first section
    first = matches[0].start()
    if first > 50:
        pre = text[:first].strip()
        if pre:
            chunks.append(("Preamble-Index", pre))

    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        title = extract_title(m.group(0).split("\n")[0])
        chunks.append((title, body))

    return chunks


def process_all() -> dict:
    stats = {"files": 0, "chunks": 0, "by_folder": {}}
    for name, meta in DOC_META.items():
        folder, ftype, stage, base_slug, tags = meta
        src_path = SRC / name
        if not src_path.exists():
            print(f"MISSING: {src_path}")
            continue
        text = src_path.read_text(encoding="utf-8", errors="replace")
        chunks = split_document(text)
        out_dir = DST / folder
        out_dir.mkdir(parents=True, exist_ok=True)

        index_lines = [
            f"# Index — {base_slug}",
            "",
            f"Source: `{name}`",
            f"Chunks: {len(chunks)}",
            "",
            "| # | File | Section |",
            "|---|------|---------|",
        ]

        for idx, (title, body) in enumerate(chunks, start=1):
            sec_slug = slugify(title)
            fname = f"{base_slug}-{idx:02d}-{sec_slug}.md"
            # Avoid path too long
            if len(fname) > 100:
                fname = f"{base_slug}-{idx:02d}-{sec_slug[:40]}.md"

            summary = f"Copy-OS section from {name}: {title}"
            when = when_to_use_for(base_slug, title)
            # Soft-type overrides for swipes/checklists
            local_type = ftype
            tl = title.lower()
            if "checklist" in tl:
                local_type = "checklist"
            elif "swipe" in tl or "template" in tl:
                local_type = "swipe"
            elif "workflow" in tl:
                local_type = "process"

            fm = frontmatter(
                title=title,
                ftype=local_type,
                source=name,
                stage=stage,
                tags=tags,
                summary=summary,
                when_to_use=when,
                parent=name,
                section_id=f"{base_slug}-{idx:02d}",
            )
            # Ensure body starts with a clean H1 for chunking
            if not body.lstrip().startswith("#"):
                body = f"# {title}\n\n{body}"

            related = (
                f"\n\n---\n\n## Related\n\n"
                f"- Parent: `{name}`\n"
                f"- Folder: `{folder}/`\n"
                f"- MOC: `05-MOCs/Query-Router.md`\n"
            )
            (out_dir / fname).write_text(fm + body + related, encoding="utf-8")
            index_lines.append(f"| {idx} | `{fname}` | {title[:80]} |")
            stats["chunks"] += 1

        # Per-doc index
        idx_fm = frontmatter(
            title=f"Index — {base_slug}",
            ftype="moc",
            source=name,
            stage=stage,
            tags=tags + ["index"],
            summary=f"Section index for {name}",
            when_to_use="Use to find the right section file inside this document family.",
            parent=name,
            section_id=f"{base_slug}-index",
        )
        (out_dir / f"{base_slug}-00-Index.md").write_text(
            idx_fm + "\n".join(index_lines) + "\n", encoding="utf-8"
        )
        stats["files"] += 1
        stats["by_folder"][folder] = stats["by_folder"].get(folder, 0) + len(chunks)
        print(f"OK {name}: {len(chunks)} chunks -> {folder}/")

    return stats


if __name__ == "__main__":
    # Clean previous content folders except this script
    if DST.exists():
        for p in DST.iterdir():
            if p.name.startswith("_"):
                continue
            if p.is_dir():
                import shutil

                shutil.rmtree(p)
            elif p.suffix == ".md":
                p.unlink()
    DST.mkdir(parents=True, exist_ok=True)
    (DST / "05-MOCs").mkdir(exist_ok=True)
    (DST / "06-Resources").mkdir(exist_ok=True)
    stats = process_all()
    print("STATS", stats)
