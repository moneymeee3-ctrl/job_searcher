"""EMBEDHUNT AI — Semantic embedding engine.

Uses sentence-transformers `all-MiniLM-L6-v2` when available. Falls back to a
deterministic offline character-n-gram embedding so unit tests run without the
heavy dependency or any network access (graceful degradation).
"""
from __future__ import annotations

import hashlib
import math
import re

_MODEL_NAME = "all-MiniLM-L6-v2"
_FALLBACK_DIM = 128
_TOKEN_RE = re.compile(r"[a-z0-9+#.]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall((text or "").lower())


def _char_ngrams(token: str, n: int = 3) -> list[str]:
    t = f"^{token}$"
    if len(t) <= n:
        return [t]
    return [t[i:i + n] for i in range(len(t) - n + 1)]


class EmbeddingEngine:
    """Embeds text/skills to dense vectors with pluggable backend."""

    def __init__(self, model_name: str = _MODEL_NAME, use_model: bool | None = None):
        self.model_name = model_name
        self._model = None
        self._use_model = use_model
        self._cache: dict[str, list[float]] = {}

    # ---- backend ----
    def _load_model(self):
        if self._model is not None:
            return self._model
        if self._use_model is False:
            return None
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
            self._model = SentenceTransformer(self.model_name)
            self._use_model = True
        except Exception:
            self._model = None
            self._use_model = False
        return self._model

    @property
    def uses_model(self) -> bool:
        self._load_model()
        return bool(self._use_model)

    # ---- embedding ----
    def embed_text(self, text: str) -> list[float]:
        key = (text or "").strip()
        if key in self._cache:
            return self._cache[key]
        model = self._load_model()
        if model is not None:
            vec = model.encode(key, normalize_embeddings=True)
            out = [float(x) for x in vec]
        else:
            out = self._fallback_embed(key)
        self._cache[key] = out
        return out

    def embed_batch(self, texts) -> list[list[float]]:
        return [self.embed_text(t) for t in texts]

    def embed_skills(self, skills) -> dict[str, list[float]]:
        return {s: self.embed_text(s) for s in skills}

    @staticmethod
    def cosine_similarity(a: list[float], b: list[float]) -> float:
        if not a or not b:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na == 0.0 or nb == 0.0:
            return 0.0
        return max(0.0, min(1.0, dot / (na * nb)))

    def find_similar_skills(self, skill: str, candidates, top_k: int = 5,
                            threshold: float = 0.0) -> list[tuple[str, float]]:
        q = self.embed_text(skill)
        scored: list[tuple[str, float]] = []
        for c in candidates:
            s = self.cosine_similarity(q, self.embed_text(c))
            if s >= threshold:
                scored.append((c, round(s, 4)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    # ---- offline fallback ----
    def _fallback_embed(self, text: str) -> list[float]:
        vec = [0.0] * _FALLBACK_DIM
        for tok in _tokenize(text):
            for gram in _char_ngrams(tok, 3):
                h = int(hashlib.md5(gram.encode()).hexdigest(), 16)
                sign = 1.0 if (h >> 8) & 1 else -1.0
                vec[h % _FALLBACK_DIM] += sign
            h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
            vec[h % _FALLBACK_DIM] += 2.0
        norm = math.sqrt(sum(x * x for x in vec))
        if norm == 0.0:
            return vec
        return [x / norm for x in vec]


_default_engine: EmbeddingEngine | None = None


def get_embedding_engine() -> EmbeddingEngine:
    global _default_engine
    if _default_engine is None:
        _default_engine = EmbeddingEngine()
    return _default_engine
