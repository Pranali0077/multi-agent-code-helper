"""Offline tests for search_codebase RAG tool."""
from unittest.mock import patch
from code_helper.tools.rag_tools import search_codebase, MIN_RELEVANCE_SCORE

def test_min_relevance_score_constant():
    assert MIN_RELEVANCE_SCORE == 0.2

def test_search_codebase_empty_results():
    with patch("code_helper.tools.rag_tools.search", return_value=[]):
        res = search_codebase("find something")
        assert res == "No relevant code found."

def test_search_codebase_below_threshold():
    mock_results = [
        {"file": "main.py", "start_line": 1, "end_line": 10, "score": 0.15, "text": "print('hello')"},
        {"file": "utils.py", "start_line": 1, "end_line": 5, "score": 0.05, "text": "def foo(): pass"},
    ]
    with patch("code_helper.tools.rag_tools.search", return_value=mock_results):
        res = search_codebase("capital of France")
        assert res == "No relevant code found."

def test_search_codebase_above_threshold():
    mock_results = [
        {"file": "models.py", "start_line": 1, "end_line": 10, "score": 0.85, "text": "class User:\n    pass"},
        {"file": "utils.py", "start_line": 1, "end_line": 5, "score": 0.10, "text": "def greet(): pass"},
    ]
    with patch("code_helper.tools.rag_tools.search", return_value=mock_results):
        res = search_codebase("User class")
        assert "models.py:1-10 (0.85)" in res
        assert "class User:" in res
