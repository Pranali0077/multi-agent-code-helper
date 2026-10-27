"""RAG search tool exposing semantic codebase search to ADK agents."""
from typing import List
from ..rag.search import search

MIN_RELEVANCE_SCORE = 0.2

def search_codebase(query: str, top_k: int = 4) -> str:
    """
    Search the target codebase for relevant code snippets using semantic search.
    Returns formatted code matches with file path, line numbers, similarity score, and code text.
    Returns 'No relevant code found.' if no results match or best score is below 0.2.
    """
    try:
        results = search(query=query, top_k=top_k)
        if not results:
            return "No relevant code found."

        best_score = max((item.get("score", 0.0) for item in results), default=0.0)
        if best_score < MIN_RELEVANCE_SCORE:
            return "No relevant code found."

        parts: List[str] = []
        for item in results:
            header = f"{item['file']}:{item['start_line']}-{item['end_line']} ({item['score']:.2f})"
            code_text = item["text"].strip()
            parts.append(f"{header}\n```python\n{code_text}\n```")

        return "\n\n".join(parts)
    except Exception as e:
        return f"Error searching codebase: {e}"
