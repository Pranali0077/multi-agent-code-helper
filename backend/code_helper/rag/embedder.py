"""Embedder using LiteLLM and NVIDIA NIM embeddings with strict 2048-dim validation."""
import os
import time
from typing import List
import litellm

from ..settings import NVIDIA_EMBED_MODEL, EMBED_DIM, get_nvidia_api_key

BATCH_SIZE = 16
MAX_RETRIES = 5
INITIAL_BACKOFF = 2.0

def _embed_batch(batch: List[str], input_type: str) -> List[List[float]]:
    """Embed a single batch of texts with retry on rate limit and fallback for input_type."""
    # Ensure both keys are in os.environ for litellm
    api_key = get_nvidia_api_key()
    os.environ["NVIDIA_API_KEY"] = api_key
    os.environ["NVIDIA_NIM_API_KEY"] = api_key

    last_exc = None
    for attempt in range(MAX_RETRIES):
        try:
            try:
                resp = litellm.embedding(
                    model=NVIDIA_EMBED_MODEL,
                    input=batch,
                    input_type=input_type,
                    api_key=api_key,
                )
            except Exception as e:
                # If input_type is rejected by the provider/LiteLLM, drop it and retry
                err_str = str(e).lower()
                if "input_type" in err_str or "unexpected" in err_str or "unsupported" in err_str:
                    resp = litellm.embedding(
                        model=NVIDIA_EMBED_MODEL,
                        input=batch,
                        api_key=api_key,
                    )
                else:
                    raise

            vectors = [item["embedding"] for item in resp["data"]]
            for v in vectors:
                if len(v) != EMBED_DIM:
                    raise ValueError(f"Expected {EMBED_DIM} dims, got {len(v)}. Never pad or truncate.")
            return vectors

        except Exception as e:
            last_exc = e
            err_str = str(e).lower()
            # If rate limited (429), back off and retry
            if "429" in err_str or "rate limit" in err_str or "quota" in err_str:
                wait_time = INITIAL_BACKOFF * (2 ** attempt)
                time.sleep(wait_time)
                continue
            raise

    raise RuntimeError(f"Failed to embed batch after {MAX_RETRIES} attempts: {last_exc}")

def embed(texts: List[str], input_type: str = "passage") -> List[List[float]]:
    """
    Embed a list of texts in batches of 16.
    input_type: 'passage' or 'query'
    Strictly enforces 2048 dimensions, never pads or truncates.
    """
    if not texts:
        return []

    all_vectors: List[List[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        vectors = _embed_batch(batch, input_type=input_type)
        all_vectors.extend(vectors)

    return all_vectors
