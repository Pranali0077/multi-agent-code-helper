"""Offline tests for embedder.py with mocked LiteLLM."""
import pytest
from unittest.mock import patch, MagicMock
from code_helper.rag import embedder

@pytest.fixture(autouse=True)
def mock_nvidia_key(monkeypatch):
    """Ensure a dummy key is present in environment for offline testing."""
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-dummy-mock-key")
    monkeypatch.setenv("NVIDIA_NIM_API_KEY", "nvapi-dummy-mock-key")

def test_embed_empty_list():
    """Empty list returns empty list without calling litellm."""
    with patch("litellm.embedding") as mock_litellm:
        assert embedder.embed([]) == []
        mock_litellm.assert_not_called()

def test_embed_valid_2048_dims():
    """Valid 2048-dim vectors are accepted and returned."""
    mock_vec = [0.05] * 2048
    mock_resp = {"data": [{"embedding": mock_vec}]}

    with patch("litellm.embedding", return_value=mock_resp) as mock_litellm:
        results = embedder.embed(["hello world"], input_type="passage")
        assert len(results) == 1
        assert len(results[0]) == 2048
        assert results[0] == mock_vec
        mock_litellm.assert_called_once()

def test_embed_rejects_1024_dims():
    """1024-dim vectors must be rejected without padding."""
    mock_vec = [0.05] * 1024
    mock_resp = {"data": [{"embedding": mock_vec}]}

    with patch("litellm.embedding", return_value=mock_resp):
        with pytest.raises(ValueError, match="Expected 2048 dims, got 1024"):
            embedder.embed(["test text"])

def test_embed_rejects_2049_dims():
    """2049-dim vectors must be rejected without truncation."""
    mock_vec = [0.05] * 2049
    mock_resp = {"data": [{"embedding": mock_vec}]}

    with patch("litellm.embedding", return_value=mock_resp):
        with pytest.raises(ValueError, match="Expected 2048 dims, got 2049"):
            embedder.embed(["test text"])

def test_embed_batches_in_16():
    """Embedder batches texts into groups of 16."""
    mock_vec = [0.01] * 2048
    texts = [f"text chunk {i}" for i in range(25)]

    def side_effect(*args, **kwargs):
        inp = kwargs.get("input", [])
        return {"data": [{"embedding": mock_vec} for _ in inp]}

    with patch("litellm.embedding", side_effect=side_effect) as mock_litellm:
        results = embedder.embed(texts, input_type="passage")
        assert len(results) == 25
        assert mock_litellm.call_count == 2  # batch 1: 16 items, batch 2: 9 items

def test_embed_input_type_rejected_retry():
    """If provider rejects input_type parameter, retry without it."""
    mock_vec = [0.02] * 2048
    calls = []

    def side_effect(*args, **kwargs):
        calls.append(kwargs)
        if "input_type" in kwargs:
            raise TypeError("unexpected keyword argument 'input_type'")
        return {"data": [{"embedding": mock_vec}]}

    with patch("litellm.embedding", side_effect=side_effect):
        results = embedder.embed(["test input_type fallback"], input_type="query")
        assert len(results) == 1
        assert len(results[0]) == 2048
        assert len(calls) == 2
        assert "input_type" in calls[0]
        assert "input_type" not in calls[1]
