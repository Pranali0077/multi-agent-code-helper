"""CLI script to index the target project into Pinecone via RAG pipeline.
Safe to re-run; uses deterministic chunk IDs.
"""
import sys
from pathlib import Path

# Ensure backend root is on sys.path if run directly as a script
backend_root = Path(__file__).resolve().parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from code_helper.settings import get_target_project_path, PINECONE_INDEX_NAME
from code_helper.rag.loader import load_python_files
from code_helper.rag.chunker import chunk_text, Chunk
from code_helper.rag.embedder import embed
from code_helper.rag.store import store_chunks

def index_codebase(target_path: Path | None = None, chunk_size: int = 800, overlap: int = 150) -> int:
    """Run read -> split -> embed -> store on the target project."""
    if target_path is None:
        target_path = get_target_project_path()

    print(f"Indexing codebase from: {target_path}")
    files = load_python_files(target_path)
    print(f"Loaded {len(files)} Python files.")

    all_chunks: list[Chunk] = []
    print("Chunk counts per file:")
    for rel_path, content in files:
        file_chunks = chunk_text(rel_path, content, size=chunk_size, overlap=overlap)
        print(f"  - {rel_path}: {len(file_chunks)} chunk(s)")
        all_chunks.extend(file_chunks)

    print(f"Generated {len(all_chunks)} chunks (size={chunk_size}, overlap={overlap}).")
    if not all_chunks:
        print("No chunks to index.")
        return 0

    print("Generating embeddings via LiteLLM / NVIDIA NIM (2048 dims)...")
    texts = [c.text for c in all_chunks]
    vectors = embed(texts, input_type="passage")
    print(f"Successfully generated {len(vectors)} embedding vectors.")

    print(f"Upserting records to Pinecone index '{PINECONE_INDEX_NAME}'...")
    stored = store_chunks(all_chunks, vectors, index_name=PINECONE_INDEX_NAME)
    print(f"Indexing complete. Successfully stored {stored} chunks in Pinecone.")
    return stored

if __name__ == "__main__":
    try:
        index_codebase()
    except Exception as e:
        print(f"Error during indexing: {e}", file=sys.stderr)
        sys.exit(1)
