"""Tests for chunker.py."""
import pytest
from code_helper.rag.chunker import chunk_text, Chunk

def test_chunk_empty_and_whitespace():
    """Empty or whitespace-only text should produce zero chunks."""
    assert chunk_text("test.py", "") == []
    assert chunk_text("test.py", "   \n\n\t  \n  ") == []

def test_chunk_small_file_single_chunk():
    """Text smaller than chunk size produces exactly one chunk with accurate lines."""
    code = "def hello():\n    print('world')\n"
    chunks = chunk_text("hello.py", code, size=800, overlap=150)
    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.file == "hello.py"
    assert chunk.start_line == 1
    assert chunk.end_line == 2
    assert chunk.text == code
    assert chunk.id == "hello.py:1-2"

def test_chunk_no_empty_chunks():
    """Chunker must never yield empty or whitespace-only chunks."""
    code = "\n\n\n" + ("x = 1\n" * 200) + "\n\n\n"
    chunks = chunk_text("test.py", code, size=200, overlap=50)
    assert len(chunks) > 1
    for c in chunks:
        assert c.text.strip() != "", f"Found empty chunk: {c}"

def test_chunk_line_numbers_coverage():
    """Verify start_line and end_line accurately reflect code content."""
    lines = [f"line_{i} = {i}" for i in range(1, 101)]
    code = "\n".join(lines) + "\n"

    chunks = chunk_text("code.py", code, size=300, overlap=50)
    assert len(chunks) > 1

    code_lines = code.splitlines()
    for c in chunks:
        assert c.start_line >= 1
        assert c.end_line <= len(code_lines)
        assert c.start_line <= c.end_line
        # Verify that the chunk's text is indeed from those lines
        chunk_lines = c.text.strip().splitlines()
        first_line = chunk_lines[0].strip()
        last_line = chunk_lines[-1].strip()
        assert first_line in code_lines[c.start_line - 1]
        assert last_line in code_lines[c.end_line - 1]

def test_chunk_prefers_newline_boundary():
    """Chunker should prefer ending at a newline instead of cutting mid-line."""
    line1 = "first_variable = 'a' * 100\n"
    line2 = "second_variable = 'b' * 100\n"
    line3 = "third_variable = 'c' * 100\n"
    code = line1 + line2 + line3

    # Size large enough for line1 + line2 but smaller than line1 + line2 + line3
    size = len(line1) + len(line2) + 10
    chunks = chunk_text("vars.py", code, size=size, overlap=20)
    assert len(chunks) >= 2
    # The first chunk should end with a newline
    assert chunks[0].text.endswith("\n")

def test_chunk_invalid_arguments():
    """Invalid size or overlap parameters must raise ValueError."""
    with pytest.raises(ValueError):
        chunk_text("test.py", "abc", size=0)
    with pytest.raises(ValueError):
        chunk_text("test.py", "abc", size=100, overlap=100)
    with pytest.raises(ValueError):
        chunk_text("test.py", "abc", size=100, overlap=-5)
