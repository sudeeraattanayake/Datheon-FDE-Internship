from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
import chromadb
from src.embeddings import generate_embeddings
from src.loaders import Document, validate_metadata

logger = logging.getLogger(__name__)


class EnterpriseVectorStore:
    """Persistent ChromaDB vector store with metadata filtering."""

    def __init__(
        self,
        persist_directory: str | Path = "data/processed/chroma_db",
        collection_name: str = "enterprise_documents",
    ) -> None:
        self.client = chromadb.PersistentClient(
            path=str(persist_directory)
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(
        self,
        documents: list[Document],
        batch_size: int = 32,
    ) -> int:
        """Insert document chunks using deterministic IDs."""
        import hashlib

        if batch_size <= 0:
            raise ValueError("batch_size must be positive")

        if not documents:
            return 0

        for start in range(0, len(documents), batch_size):
            batch = documents[start:start + batch_size]

            texts = []
            metadatas = []
            ids = []

            for document in batch:
                if not document.text.strip():
                    raise ValueError("Cannot index an empty document")

                metadata = validate_metadata(document.metadata)

                # ChromaDB accepts scalar metadata values.
                clean_metadata = {
                    key: value
                    for key, value in metadata.items()
                    if isinstance(value, (str, int, float, bool))
                }

                payload = (
                    document.text
                    + repr(sorted(clean_metadata.items()))
                )
                doc_id = hashlib.sha256(
                    payload.encode("utf-8")
                ).hexdigest()

                texts.append(document.text)
                metadatas.append(clean_metadata)
                ids.append(doc_id)

            embeddings = generate_embeddings(texts, batch_size=batch_size)

            self.collection.upsert(
                ids=ids,
                documents=texts,
                metadatas=metadatas,
                embeddings=embeddings,
            )

            logger.info("Indexed batch of %d documents", len(batch))

        return len(documents)

    def search(
        self,
        query: str,
        department: str,
        access_tier: str,
        n_results: int = 5,
    ) -> list[dict[str, Any]]:
        """Retrieve results restricted to the requested metadata."""
        if not query.strip():
            raise ValueError("Query must not be empty")

        if not department.strip() or not access_tier.strip():
            raise ValueError("Department and access tier are required")

        if n_results <= 0:
            raise ValueError("n_results must be positive")

        if self.collection.count() == 0:
            return []

        query_embedding = generate_embeddings([query])[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, self.collection.count()),
            where={
                "$and": [
                    {"department": {"$eq": department}},
                    {"access_tier": {"$eq": access_tier}},
                ]
            },
            include=["documents", "metadatas", "distances"],
        )

        matches = []

        for text, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            matches.append(
                {
                    "text": text,
                    "metadata": metadata,
                    "cosine_distance": float(distance),
                }
            )

        return matches
