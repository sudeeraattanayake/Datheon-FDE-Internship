from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from src.chunking import semantic_chunk_documents
from src.loaders import load_document
from src.vector_store import EnterpriseVectorStore

logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    source: str
    documents_loaded: int
    chunks_created: int
    elapsed_seconds: float


class EnterpriseETLPipeline:
    """End-to-end enterprise document ingestion pipeline."""

    def __init__(
        self,
        persist_directory: str | Path = "data/processed/chroma_db",
        max_words: int = 150,
        similarity_threshold: float = 0.65,
    ) -> None:
        if max_words <= 0:
            raise ValueError("max_words must be positive")

        self.max_words = max_words
        self.similarity_threshold = similarity_threshold

        self.store = EnterpriseVectorStore(
            persist_directory=persist_directory
        )

    def ingest(
        self,
        path: str | Path,
        metadata: dict[str, Any],
        batch_size: int = 32,
    ) -> IngestionResult:
        """Load, semantically chunk, embed and index a document."""
        started = time.perf_counter()
        source = Path(path)

        logger.info("Starting ingestion: %s", source.name)

        documents = load_document(source, metadata)

        chunks = semantic_chunk_documents(
            documents,
            max_words=self.max_words,
            similarity_threshold=self.similarity_threshold,
        )

        indexed_count = self.store.add_documents(
            chunks,
            batch_size=batch_size,
        )

        elapsed = time.perf_counter() - started

        logger.info(
            "Ingested %s: %d documents, %d chunks in %.3fs",
            source.name,
            len(documents),
            indexed_count,
            elapsed,
        )

        return IngestionResult(
            source=source.name,
            documents_loaded=len(documents),
            chunks_created=indexed_count,
            elapsed_seconds=elapsed,
        )

    def search(
        self,
        query: str,
        department: str,
        access_tier: str,
        n_results: int = 5,
    ) -> list[dict[str, Any]]:
        return self.store.search(
            query=query,
            department=department,
            access_tier=access_tier,
            n_results=n_results,
        )
