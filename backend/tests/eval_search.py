import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from code_helper.rag.search import search
from code_helper.rag.loader import load_python_files
from code_helper.rag.chunker import chunk_text
from code_helper.settings import get_target_project_path

def run_eval():
    target_path = get_target_project_path()
    files = load_python_files(target_path)

    print("=== CHUNK SIZE COMPARISON ===")
    for size, overlap in [(800, 150), (400, 80)]:
        print(f"\nConfiguration: size={size}, overlap={overlap}")
        total = 0
        for rel_path, content in files:
            chunks = chunk_text(rel_path, content, size=size, overlap=overlap)
            total += len(chunks)
            print(f"  {rel_path}: {len(chunks)} chunk(s), length={len(content)} chars")
        print(f"Total chunks: {total}")

    print("\n=== SEARCH TEST (5 QUESTIONS) ===")
    questions = [
        ("Where is the User class defined?", "models.py"),
        ("Where is the greeting formatted with decorative banners?", "utils.py"),
        ("Where is the application entry point and run function?", "main.py"),
        ("Where is user info converted to a dictionary?", "models.py"),
        ("Where are greetings generated with hello messages?", "utils.py"),
    ]

    passed = 0
    for q, expected in questions:
        results = search(q, top_k=3)
        top_files = [r["file"] for r in results]
        scores = [round(r["score"], 4) for r in results]
        hit = expected in top_files
        if hit:
            passed += 1
            rank = top_files.index(expected) + 1
            status = f"PASS (ranked #{rank})"
        else:
            status = "FAIL"

        print(f"Question: \"{q}\"")
        print(f"  Expected: {expected}")
        print(f"  Top 3 results: {top_files}")
        print(f"  Similarity scores: {scores}")
        print(f"  Result: {status}\n")

    print(f"Gate 1 Accuracy: {passed}/5 test questions matched in top 3.")

if __name__ == "__main__":
    run_eval()
