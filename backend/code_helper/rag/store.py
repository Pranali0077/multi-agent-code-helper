"""Pinecone index management and vector storage."""
import time
from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec

from .chunker import Chunk
from ..settings import (
    PINECONE_INDEX_NAME,
    PINECONE_CLOUD,
    PINECONE_REGION,
    EMBED_DIM,
    get_pinecone_api_key,
)

UPSERT_BATCH_SIZE = 100

def get_client() -> Pinecone:
    """Return an authenticated Pinecone client."""
    return Pinecone(api_key=get_pinecone_api_key())

def ensure_index(pc: Pinecone, index_name: str = PINECONE_INDEX_NAME) -> Any:
    """
    Ensure the Pinecone index exists with exactly 2048 dimensions and cosine metric.
    Fails loudly if an existing index has differing parameters.
    """
    try:
        existing_indexes = [idx.name for idx in pc.list_indexes()]
    except Exception as e:
        if "401" in str(e) or "UNAUTHENTICATED" in str(e):
            raise RuntimeError(
                "Pinecone authentication failed (401 UNAUTHENTICATED). "
                "Your PINECONE_API_KEY in backend/code_helper/.env appears to be invalid or expired. "
                "Generate a fresh key at https://app.pinecone.io/ -> API Keys."
            ) from e
        raise

    if index_name in existing_indexes:
        desc = pc.describe_index(index_name)
        dim = getattr(desc, "dimension", None)
        metric = getattr(desc, "metric", None)
        if dim != EMBED_DIM or metric != "cosine":
            raise ValueError(
                f"Pinecone index '{index_name}' exists with dimension={dim}, metric='{metric}'; "
                f"expected dimension={EMBED_DIM}, metric='cosine'."
            )
        return desc

    # Create index
    pc.create_index(
        name=index_name,
        dimension=EMBED_DIM,
        metric="cosine",
        spec=ServerlessSpec(
            cloud=PINECONE_CLOUD,
            region=PINECONE_REGION,
        ),
    )

    # Wait until ready
    for _ in range(60):
        desc = pc.describe_index(index_name)
        status = getattr(desc, "status", {})
        is_ready = status.get("ready") if isinstance(status, dict) else getattr(status, "ready", False)
        if is_ready:
            break
        time.sleep(1)

    return desc

def get_index(index_name: str = PINECONE_INDEX_NAME):
    """Retrieve an active Pinecone index object, ensuring it exists first."""
    pc = get_client()
    ensure_index(pc, index_name)
    return pc.Index(index_name)

def store_chunks(chunks: List[Chunk], vectors: List[List[float]], index_name: str = PINECONE_INDEX_NAME) -> int:
    """
    Upsert chunks and vectors into Pinecone with deterministic IDs and metadata.
    id format: <file>:<start_line>-<end_line>
    metadata: {file, start_line, end_line, text}
    """
    if len(chunks) != len(vectors):
        raise ValueError(f"Mismatched chunks ({len(chunks)}) and vectors ({len(vectors)})")

    if not chunks:
        return 0

    index = get_index(index_name)
    records: List[Dict[str, Any]] = []

    for chunk, vector in zip(chunks, vectors):
        records.append({
            "id": chunk.id,
            "values": vector,
            "metadata": {
                "file": chunk.file,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "text": chunk.text,
            },
        })

    total_upserted = 0
    for i in range(0, len(records), UPSERT_BATCH_SIZE):
        batch = records[i : i + UPSERT_BATCH_SIZE]
        index.upsert(vectors=batch)
        total_upserted += len(batch)

    return total_upserted
