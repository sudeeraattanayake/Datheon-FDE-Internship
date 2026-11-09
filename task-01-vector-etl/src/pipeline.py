from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from src.chunking import semantic_chunk_documents
from src.loaders import Document, load_document
from src.vector_store import EnterpriseVectorStore

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IngestionResult:
    """Summary of a completed document ingestion."""

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

        if (
            isinstance(max_words, bool)
            or not isinstance(max_words, int)
            or max_words <= 0
        ):
            raise ValueError(
                "max_words must be a positive integer"
            )

        if (
            isinstance(similarity_threshold, bool)
            or not isinstance(
                similarity_threshold, (int, float)
            )
            or not math.isfinite(similarity_threshold)
            or not 0 <= similarity_threshold <= 1
        ):
            raise ValueError(
                "similarity_threshold must be between 0 and 1"
            )

        self.max_words = max_words
        self.similarity_threshold = float(
            similarity_threshold
        )

        self.store = EnterpriseVectorStore(
            persist_directory=persist_directory
        )

    @staticmethod
    def _validate_source_name(
        source_name: str | None,
    ) -> str | None:
        """Validate and sanitize an optional source filename."""

        if source_name is None:
            return None

        if not isinstance(source_name, str):
            raise ValueError(
                "source_name must be a string"
            )

        normalized = source_name.replace("\\", "/")
        filename = Path(normalized).name.strip()

        if not filename or filename in {".", ".."}:
            raise ValueError(
                "source_name must be a valid filename"
            )

        return filename

    def ingest(
        self,
        path: str | Path,
        metadata: dict[str, Any],
        batch_size: int = 32,
        source_name: str | None = None,
    ) -> IngestionResult:
        """
        Load, chunk, embed and index a document.

        source_name:
            Optional original filename for uploaded files.
            The temporary file path is still used for loading.
        """

        if (
            isinstance(batch_size, bool)
            or not isinstance(batch_size, int)
            or batch_size <= 0
        ):
            raise ValueError(
                "batch_size must be a positive integer"
            )

        if not isinstance(metadata, dict):
            raise ValueError(
                "metadata must be a dictionary"
            )

        source = Path(path)

        validated_name = self._validate_source_name(
            source_name
        )

        display_name = validated_name or source.name

        started = time.perf_counter()

        logger.info(
            "Starting ingestion: %s",
            display_name,
        )

        try:
            documents = load_document(
                source,
                metadata,
            )

            # Preserve the original filename before chunking.
            if validated_name is not None:
                normalized_documents = []

                for document in documents:
                    updated_metadata = dict(
                        document.metadata
                    )

                    updated_metadata["source"] = (
                        validated_name
                    )

                    updated_metadata[
                        "original_filename"
                    ] = validated_name

                    normalized_documents.append(
                        Document(
                            text=document.text,
                            metadata=updated_metadata,
                        )
                    )

                documents = normalized_documents

            chunks = semantic_chunk_documents(
                documents,
                max_words=self.max_words,
                similarity_threshold=(
                    self.similarity_threshold
                ),
            )

            processed_count = (
                self.store.add_documents(
                    chunks,
                    batch_size=batch_size,
                )
            )

            elapsed = (
                time.perf_counter() - started
            )

            logger.info(
                "Ingested %s: %d documents, "
                "%d chunks in %.3fs",
                display_name,
                len(documents),
                processed_count,
                elapsed,
            )

            return IngestionResult(
                source=display_name,
                documents_loaded=len(documents),
                chunks_created=processed_count,
                elapsed_seconds=elapsed,
            )

        except Exception:
            logger.exception(
                "Document ingestion failed: %s",
                display_name,
            )
            raise

    def search(
        self,
        query: str,
        department: str,
        access_tier: str,
        n_results: int = 5,
    ) -> list[dict[str, Any]]:
        """Perform metadata-filtered semantic search."""

        return self.store.search(
            query=query,
            department=department,
            access_tier=access_tier,
            n_results=n_results,
        )
