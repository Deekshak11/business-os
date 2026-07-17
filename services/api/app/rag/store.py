from __future__ import annotations

from functools import lru_cache
from typing import Any, Optional

import chromadb
from chromadb.utils import embedding_functions

from app.config import settings


class RagStore:
    def __init__(self) -> None:
        self._client = chromadb.PersistentClient(path=str(settings.chroma_dir))
        self._ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=settings.embedding_model
        )

    def get_or_create(self, name: str):
        return self._client.get_or_create_collection(
            name=name,
            embedding_function=self._ef,
            metadata={"hnsw:space": "cosine"},
        )

    def reset_collection(self, name: str) -> None:
        try:
            self._client.delete_collection(name)
        except Exception:
            pass
        self.get_or_create(name)

    def query(
        self,
        collection: str,
        query: str,
        n_results: int = 6,
        where: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        col = self.get_or_create(collection)
        kwargs: dict[str, Any] = {
            "query_texts": [query],
            "n_results": min(n_results, 20),
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where
        res = col.query(**kwargs)
        hits: list[dict[str, Any]] = []
        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]
        for i, doc in enumerate(docs):
            hits.append(
                {
                    "text": doc or "",
                    "metadata": metas[i] if i < len(metas) else {},
                    "distance": dists[i] if i < len(dists) else None,
                }
            )
        return hits


@lru_cache(maxsize=1)
def get_store() -> RagStore:
    return RagStore()
