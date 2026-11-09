from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any
import chromadb
from src.embeddings import generate_embeddings
from src.loaders import Document, validate_metadata

logger = logging.getLogger(__name__)


class EnterpriseVectorStore:
    """Persistent ChromaDB store with cosine similarity."""

    def __init__(
        self,
        persist_directory: str | Path = "data/processed/chroma_db",
        collection_name: str = "enterprise_documents",
    ) -> None:

        if (
            not isinstance(collection_name, str)
            or not collection_name.strip()
        ):
            raise ValueError(
                "collection_name must not be empty"
            )

        self.client = chromadb.PersistentClient(
            path=str(persist_directory)
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        )

        logger.info(
            "Vector store initialized: %s",
            collection_name,
        )

    @staticmethod
    def _validate_batch_size(batch_size: int) -> None:

        if (
            isinstance(batch_size, bool)
            or not isinstance(batch_size, int)
            or batch_size <= 0
        ):
            raise ValueError(
                "batch_size must be a positive integer"
            )

    @staticmethod
    def _prepare_document(
        document: Document,
    ) -> tuple[str, dict[str, Any], str]:
        """Validate and prepare a document for indexing."""

        if not isinstance(document.text, str):
            raise ValueError(
                "Document text must be a string"
            )

        if not document.text.strip():
            raise ValueError(
                "Cannot index an empty document"
            )

        metadata = validate_metadata(
            document.metadata
        )

        clean_metadata = {
            key: value
            for key, value in metadata.items()
            if isinstance(value, (str, int, float, bool))
        }

        payload = (
            document.text
            + repr(sorted(clean_metadata.items()))
        )

        document_id = hashlib.sha256(
            payload.encode("utf-8")
        ).hexdigest()

        return (
            document.text,
            clean_metadata,
            document_id,
        )

    def add_documents(
        self,
        documents: list[Document],
        batch_size: int = 32,
    ) -> int:
        """Upsert document chunks using deterministic IDs."""

        self._validate_batch_size(batch_size)

        if not documents:
            return 0

        # Validate every document before writing any batches.
        prepared = [
            self._prepare_document(document)
            for document in documents
        ]

        for start in range(
            0,
            len(prepared),
            batch_size,
        ):
            batch = prepared[
                start:start + batch_size
            ]

            texts = [
                item[0] for item in batch
            ]

            metadatas = [
                item[1] for item in batch
            ]

            ids = [
                item[2] for item in batch
            ]

            embeddings = generate_embeddings(
                texts,
                batch_size=batch_size,
            )

            try:
                self.collection.upsert(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas,
                    embeddings=embeddings,
                )

            except Exception:
                logger.exception(
                    "Failed to index batch starting at %d",
                    start,
                )
                raise

            logger.info(
                "Indexed batch of %d documents",
                len(batch),
            )

        return len(prepared)

    def search(
        self,
        query: str,
        department: str,
        access_tier: str,
        n_results: int = 5,
    ) -> list[dict[str, Any]]:
        """Search vectors with department and access-tier filters."""

        if (
            not isinstance(query, str)
            or not query.strip()
        ):
            raise ValueError(
                "Query must not be empty"
            )

        if (
            not isinstance(department, str)
            or not department.strip()
        ):
            raise ValueError(
                "Department is required"
            )

        if (
            not isinstance(access_tier, str)
            or not access_tier.strip()
        ):
            raise ValueError(
                "Access tier is required"
            )

        if (
            isinstance(n_results, bool)
            or not isinstance(n_results, int)
            or n_results <= 0
        ):
            raise ValueError(
                "n_results must be a positive integer"
            )

        total_documents = self.collection.count()

        if total_documents == 0:
            return []

        query_embedding = generate_embeddings(
            [query]
        )[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(
                n_results,
                total_documents,
            ),
            where={
                "$and": [
                    {
                        "department": {
                            "$eq": department
                        }
                    },
                    {
                        "access_tier": {
                            "$eq": access_tier
                        }
                    },
                ]
            },
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        matches: list[dict[str, Any]] = []

        texts = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for text, metadata, distance in zip(
            texts,
            metadatas,
            distances,
        ):
            matches.append(
                {
                    "text": text,
                    "metadata": metadata,
                    "cosine_distance": float(
                        distance
                    ),
                }
            )

        return matches
