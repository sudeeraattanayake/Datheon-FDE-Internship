from __future__ import annotations
import hashlib
import os
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder
from src.security import Identity, allowed, filter_for

_embedder = None
_reranker = None

def embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _embedder

def reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker

def collection():
    db_path = os.environ.get("RAG_DB_PATH", "data/chroma_db")
    return chromadb.PersistentClient(path=db_path).get_or_create_collection(
        name="task02_secure_rag", metadata={"hnsw:space": "cosine"})

def rewrite(query: str) -> str:
    """Deterministic rewrite; no LLM needed. Keep original semantics."""
    cleaned = " ".join(query.strip().split())
    replacements = {"pto": "paid time off", "hr": "human resources", "faq": "frequently asked questions"}
    words = cleaned.split()
    return " ".join(replacements.get(w.lower(), w) for w in words)

def index_chunks(chunks: list[tuple[str, dict]]) -> int:
    if not chunks:
        return 0
    texts = [text for text, _ in chunks]
    vectors = embedder().encode(texts, normalize_embeddings=True).tolist()
    ids = [hashlib.sha256((text + repr(sorted(meta.items()))).encode()).hexdigest() for text, meta in chunks]
    collection().upsert(ids=ids, documents=texts, metadatas=[meta for _, meta in chunks], embeddings=vectors)
    return len(chunks)

def retrieve(query: str, identity: Identity, top_k: int = 5) -> list[dict]:
    col = collection()
    if col.count() == 0:
        return []
    rewritten = rewrite(query)
    vector = embedder().encode([rewritten], normalize_embeddings=True).tolist()
    result = col.query(query_embeddings=vector, n_results=min(max(top_k * 4, 10), col.count()),
                       where=filter_for(identity), include=["documents", "metadatas", "distances"])
    candidates = []
    for text, meta, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
        if allowed(identity, meta):
            candidates.append({"text": text, "metadata": meta, "cosine_distance": float(distance)})
    if not candidates:
        return []
    scores = reranker().predict([(rewritten, item["text"]) for item in candidates])
    for item, score in zip(candidates, scores):
        item["rerank_score"] = float(score)
    return sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)[:top_k]
