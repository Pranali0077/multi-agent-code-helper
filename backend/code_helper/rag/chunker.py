"""Splits source code into overlapping chunks with line number metadata."""
from dataclasses import dataclass
from typing import List

@dataclass
class Chunk:
    file: str
    start_line: int
    end_line: int
    text: str

    @property
    def id(self) -> str:
        """Deterministic Pinecone ID formatted as <file>:<start_line>-<end_line>."""
        return f"{self.file}:{self.start_line}-{self.end_line}"

def chunk_text(file: str, text: str, size: int = 800, overlap: int = 150) -> List[Chunk]:
    """
    Split text into character windows that prefer to end at newlines.
    Tracks 1-indexed start_line and end_line for each chunk.
    Never produces empty chunks.
    """
    if not text or not text.strip():
        return []

    if size <= 0:
        raise ValueError(f"Chunk size must be positive, got {size}")
    if overlap < 0 or overlap >= size:
        raise ValueError(f"Overlap must be non-negative and less than size ({size}), got {overlap}")

    n = len(text)
    chunks: List[Chunk] = []
    start_idx = 0

    while start_idx < n:
        if start_idx + size >= n:
            end_idx = n
        else:
            cand_end = start_idx + size
            # Look backwards from cand_end down to start_idx + size // 2 for a newline
            search_start = start_idx + (size // 2)
            nl_pos = text.rfind("\n", search_start, cand_end)
            if nl_pos != -1:
                end_idx = nl_pos + 1
            else:
                end_idx = cand_end

        chunk_str = text[start_idx:end_idx]

        if chunk_str.strip():
            start_line = text[:start_idx].count("\n") + 1
            last_char_idx = max(start_idx, end_idx - 1)
            end_line = text[:last_char_idx].count("\n") + 1

            chunks.append(Chunk(
                file=file,
                start_line=start_line,
                end_line=end_line,
                text=chunk_str,
            ))

        if end_idx >= n:
            break

        next_start = max(start_idx + 1, end_idx - overlap)
        start_idx = next_start

    return chunks
