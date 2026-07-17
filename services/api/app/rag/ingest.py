"""
Ingest Hormozi + Copy-OS markdown vaults into Chroma.

Usage (from services/api with venv active):
  python -m app.rag.ingest
  python -m app.rag.ingest --collection hormozi
  python -m app.rag.ingest --collection copyos
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

# Allow `python -m app.rag.ingest` from services/api
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.config import settings
from app.rag.frontmatter import flatten_metadata, parse_markdown_with_frontmatter
from app.rag.store import RagStore

# Skip builder artifacts and huge indexes that dilute RAG
SKIP_NAME_PARTS = {
    "_build_rag_vault.py",
    "ORIGINALS-NOTE.md",
    "ANYTHINGLLM-SETUP.md",
    "README.md",
}


def iter_md_files(root: Path) -> list[Path]:
    if not root.exists():
        raise FileNotFoundError(f"Vault path missing: {root}")
    files = []
    for p in root.rglob("*.md"):
        if any(part.startswith(".") for part in p.parts):
            continue
        if p.name in SKIP_NAME_PARTS:
            continue
        # Keep per-doc indexes; skip huge optional later if needed
        files.append(p)
    return sorted(files)


def chunk_text(text: str, max_chars: int = 1800, overlap: int = 200) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i : i + max_chars])
        i += max_chars - overlap
    return chunks


def file_id(path: Path, idx: int) -> str:
    h = hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:16]
    return f"{h}_{idx}"


def ingest_collection(store: RagStore, name: str, root: Path, reset: bool = True) -> int:
    print(f"\n=== Ingesting `{name}` from {root} ===")
    files = iter_md_files(root)
    print(f"Found {len(files)} markdown files")
    if reset:
        store.reset_collection(name)
    col = store.get_or_create(name)

    ids: list[str] = []
    docs: list[str] = []
    metas: list[dict] = []
    batch = 0
    total_chunks = 0

    def flush():
        nonlocal ids, docs, metas, batch, total_chunks
        if not ids:
            return
        col.add(ids=ids, documents=docs, metadatas=metas)
        total_chunks += len(ids)
        batch += 1
        print(f"  batch {batch}: +{len(ids)} chunks (total {total_chunks})")
        ids, docs, metas = [], [], []

    for fp in files:
        rel = str(fp.relative_to(root)).replace("\\", "/")
        raw = fp.read_text(encoding="utf-8", errors="replace")
        meta, body = parse_markdown_with_frontmatter(raw)
        flat = flatten_metadata(meta, rel)
        flat["collection"] = name
        flat["filename"] = fp.name
        # Prefer body; if empty use full
        content = body.strip() or raw.strip()
        # Prepend title for retrieval quality
        title = flat.get("title") or fp.stem
        for i, chunk in enumerate(chunk_text(content)):
            piece = f"# {title}\n\n{chunk}" if i == 0 else chunk
            ids.append(file_id(fp, i))
            docs.append(piece)
            m = dict(flat)
            m["chunk_index"] = i
            metas.append(m)
            if len(ids) >= 64:
                flush()

    flush()
    print(f"Done `{name}`: {total_chunks} chunks from {len(files)} files")
    return total_chunks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--collection",
        choices=["hormozi", "copyos", "all"],
        default="all",
    )
    parser.add_argument("--no-reset", action="store_true")
    args = parser.parse_args()
    store = RagStore()
    reset = not args.no_reset

    totals = {}
    if args.collection in ("hormozi", "all"):
        totals["hormozi"] = ingest_collection(
            store, "hormozi", settings.hormozi_path, reset=reset
        )
    if args.collection in ("copyos", "all"):
        totals["copyos"] = ingest_collection(
            store, "copyos", settings.copyos_path, reset=reset
        )
    print("\n=== SUMMARY ===")
    for k, v in totals.items():
        print(f"  {k}: {v} chunks")


if __name__ == "__main__":
    main()
