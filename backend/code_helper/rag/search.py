"""Semantic search against Pinecone code index."""
from typing import List, Dict, Any

from .embedder import embed
from .store import get_index
from ..settings import PINECONE_INDEX_NAME

def search(query: str, top_k: int = 4, index_name: str = PINECONE_INDEX_NAME) -> List[Dict[str, Any]]:
    """
    Embed the query using input_type='query', query Pinecone index,
    and return matches formatted as:
    [{'file': str, 'start_line': int, 'end_line': int, 'score': float, 'text': str}]
    """
    if not query or not query.strip():
        return []

    vectors = embed([query], input_type="query")
    if not vectors:
        return []

    index = get_index(index_name)
    response = index.query(
        vector=vectors[0],
        top_k=top_k,
        include_metadata=True,
    )

    results: List[Dict[str, Any]] = []
    matches = response.get("matches", []) if isinstance(response, dict) else getattr(response, "matches", [])

    for match in matches:
        metadata = match.get("metadata", {}) if isinstance(match, dict) else getattr(match, "metadata", {})
        score = match.get("score", 0.0) if isinstance(match, dict) else getattr(match, "score", 0.0)

        results.append({
            "file": metadata.get("file", "") if isinstance(metadata, dict) else getattr(metadata, "file", ""),
            "start_line": int(metadata.get("start_line", 1) if isinstance(metadata, dict) else getattr(metadata, "start_line", 1)),
            "end_line": int(metadata.get("end_line", 1) if isinstance(metadata, dict) else getattr(metadata, "end_line", 1)),
            "score": float(score),
            "text": metadata.get("text", "") if isinstance(metadata, dict) else getattr(metadata, "text", ""),
        })

    return results
