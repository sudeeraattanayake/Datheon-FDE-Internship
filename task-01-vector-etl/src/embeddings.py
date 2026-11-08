from __future__ import annotations

import logging
from functools import lru_cache
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load and cache the embedding model."""
    logger.info("Loading embedding model: %s", MODEL_NAME)
    return SentenceTransformer(MODEL_NAME)


def generate_embeddings(
    texts: list[str],
    batch_size: int = 32,
) -> list[list[float]]:
    """Generate normalized embeddings for valid text inputs."""
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    if not texts:
        return []

    if any(not isinstance(text, str) or not text.strip() for text in texts):
        raise ValueError("All texts must be non-empty strings")

    model = get_embedding_model()

    vectors = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True,
    )

    result = np.asarray(vectors, dtype=np.float32)

    if not np.isfinite(result).all():
        raise ValueError("Embedding model produced non-finite values")

    logger.info("Generated %d embeddings", len(texts))
    return result.tolist()
