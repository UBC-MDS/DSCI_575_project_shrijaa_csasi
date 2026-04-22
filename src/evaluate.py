import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.bm25 import load_bm25, search as bm25_search
from src.semantic import load_faiss, search_faiss

# ── Query Set ────────────────────────────────────────────────────────────────
QUERIES = [
    # (query, type_label)
    ("taylor swift album", "Easy / Keyword"),
    ("ed sheeran songs", "Easy / Keyword"),
    ("classical piano music", "Easy / Keyword"),
    ("jazz instrumental album", "Easy / Keyword"),
    ("music to relax while studying", "Medium / Semantic"),
    ("songs for a long road trip", "Medium / Semantic"),
    ("calming instrumental musi", "Medium / Semantic"),
    ("upbeat music for working out", "Medium / Semantic"),
    ("best album for heartbreak", "Complex"),
    ("music without lyrics for focus", "Complex"),
]

TOP_K = 5

def format_bm25_results(docs):
    """Formats BM25 results into markdown table rows."""
    rows = []
    for i, doc in enumerate(docs, 1):
        title  = doc.metadata.get("product_title", "N/A")
        rating = doc.metadata.get("rating", "N/A")
        review = doc.metadata.get("text", "") or ""
        review = review[:120].replace("\n", " ").strip()
        rows.append(f"| {i} | {title} | {rating} | {review}... |")
    return rows

def format_semantic_results(docs_and_scores):
    """Formats semantic search results (with scores) into markdown table rows."""
    rows = []
    for i, (doc, score) in enumerate(docs_and_scores, 1):
        title   = doc.metadata.get("product_title", "N/A")
        rating  = doc.metadata.get("rating", "N/A")
        sim     = round(1 / (1 + score), 3)
        review  = doc.metadata.get("text", "") or ""
        review  = review[:120].replace("\n", " ").strip()
        rows.append(f"| {i} | {title} | {rating} | {sim} | {review}... |")
    return rows

def main():
    print("Loading retrievers...")
    bm25_retriever = load_bm25()
    faiss_store    = load_faiss()
    print("Done.\n")

    print("## Retrieved Results\n")

    for query, qtype in QUERIES:
        print(f"### Query: \"{query}\"")
        print(f"**Type:** {qtype}\n")

        # BM25
        bm25_docs = bm25_search(query, bm25_retriever, k=TOP_K)
        print("**BM25 Results:**\n")
        print("| Rank | Product Title | Rating | Review Snippet |")
        print("|------|--------------|--------|----------------|")
        for row in format_bm25_results(bm25_docs):
            print(row)
        print()

        # Semantic
        sem_results = search_faiss(query, faiss_store, k=TOP_K)
        print("**Semantic Results:**\n")
        print("| Rank | Product Title | Rating | Similarity | Review Snippet |")
        print("|------|--------------|--------|------------|----------------|")
        for row in format_semantic_results(sem_results):
            print(row)
        print()
        print("---\n")

if __name__ == "__main__":
    main()