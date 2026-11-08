from __future__ import annotations

import logging
import re
import numpy as np
from src.embeddings import generate_embeddings
from src.loaders import Document

logger = logging.getLogger(__name__)


def split_sentences(text: str) -> list[str]:
    """Split text on sentence boundaries."""
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
        if sentence.strip()
    ]


def semantic_chunk_documents(
    documents: list[Document],
    max_words: int = 150,
    overlap_sentences: int = 1,
    similarity_threshold: float = 0.65,
) -> list[Document]:
    """Split documents using embedding similarity and word limits."""
    if max_words <= 0:
        raise ValueError("max_words must be positive")
    if overlap_sentences < 0:
        raise ValueError("overlap_sentences cannot be negative")
    if not -1.0 <= similarity_threshold <= 1.0:
        raise ValueError("similarity_threshold must be between -1 and 1")

    chunks: list[Document] = []

    for document in documents:
        sentences = split_sentences(document.text)
        if not sentences:
            continue

        # Ensure every segment respects max_words.
        segments: list[str] = []
        for sentence in sentences:
            words = sentence.split()
            for start in range(0, len(words), max_words):
                segments.append(" ".join(words[start:start + max_words]))

        if not segments:
            continue

        vectors = np.asarray(generate_embeddings(segments), dtype=np.float32)

        current: list[str] = []
        current_words = 0
        chunk_index = 0

        def emit(parts: list[str]) -> None:
            nonlocal chunk_index
            if not parts:
                return

            chunks.append(
                Document(
                    text=" ".join(parts),
                    metadata={
                        **document.metadata,
                        "chunk_index": chunk_index,
                        "chunking_method": "embedding_similarity",
                    },
                )
            )
            chunk_index += 1

        for index, segment in enumerate(segments):
            words_count = len(segment.split())

            similarity = 1.0
            if index > 0:
                similarity = float(
                    np.dot(vectors[index - 1], vectors[index])
                )

            topic_changed = (
                index > 0 and similarity < similarity_threshold
            )

            exceeds_limit = (
                current_words + words_count > max_words
            )

            if current and (topic_changed or exceeds_limit):
                emit(current)

                # Overlap only for size-based splits, not topic changes.
                overlap = (
                    current[-overlap_sentences:]
                    if exceeds_limit and not topic_changed
                    else []
                )

                current = list(overlap)

                while (
                    current
                    and sum(len(item.split()) for item in current)
                    + words_count > max_words
                ):
                    current.pop(0)

                current_words = sum(
                    len(item.split()) for item in current
                )

            current.append(segment)
            current_words += words_count

        if current:
            emit(current)

    logger.info("Generated %d semantic chunks", len(chunks))
    return chunks
