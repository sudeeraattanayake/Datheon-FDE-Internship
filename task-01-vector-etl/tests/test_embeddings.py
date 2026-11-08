import numpy as np
import pytest
from src.embeddings import generate_embeddings


def test_empty_input():
    assert generate_embeddings([]) == []


def test_invalid_text():
    with pytest.raises(ValueError):
        generate_embeddings([""])


def test_invalid_batch_size():
    with pytest.raises(ValueError):
        generate_embeddings(["valid text"], batch_size=0)


def test_embedding_generation():
    texts = [
        "Employees must follow HR policies.",
        "The finance department manages invoices.",
    ]

    vectors = generate_embeddings(texts)

    assert len(vectors) == 2
    assert len(vectors[0]) == 384

    for vector in vectors:
        assert np.isfinite(vector).all()
        assert np.isclose(np.linalg.norm(vector), 1.0, atol=1e-4)
