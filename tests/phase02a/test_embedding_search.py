import numpy as np
import pytest

from ai.embeddings.search import cosine_similarity


class TestCosineSimilarity:
    def test_identical_vectors(self):
        v = [1.0, 2.0, 3.0]
        assert cosine_similarity(v, v) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        a = [1.0, 0.0, 0.0]
        b = [0.0, 1.0, 0.0]
        assert cosine_similarity(a, b) == pytest.approx(0.0)

    def test_opposite_vectors(self):
        a = [1.0, 0.0]
        b = [-1.0, 0.0]
        assert cosine_similarity(a, b) == pytest.approx(-1.0)

    def test_zero_vector(self):
        a = [0.0, 0.0]
        b = [1.0, 1.0]
        assert cosine_similarity(a, b) == 0.0

    def test_float_precision(self):
        a = [0.5, 0.5]
        b = [0.5, 0.5]
        sim = cosine_similarity(a, b)
        assert 0.99 <= sim <= 1.01


class TestEmbeddingDimension:
    def test_default_dim(self):
        from ai.embeddings import model

        assert model.EMBEDDING_DIM == 1024
