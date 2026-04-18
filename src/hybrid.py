# src/hybrid.py

from pathlib import Path
from langchain_community.retrievers import BM25Retriever
from src.bm25 import load_bm25
from src.semantic import load_faiss
from src.utils import preprocess_text


def build_hybrid_retriever(bm25_weight=0.4, semantic_weight=0.6, k=5):
    """Returns a dict with both retrievers and their weights."""
    bm25_retriever = load_bm25()
    bm25_retriever.k = k
    vector_store = load_faiss()
    return {
        "bm25": bm25_retriever,
        "faiss": vector_store,
        "bm25_weight": bm25_weight,
        "semantic_weight": semantic_weight,
    }

def search_hybrid(query, retriever, k=5):
    """Combines BM25 and semantic results, deduplicates, and returns top-k Documents."""
    # BM25 results
    query_clean = " ".join(preprocess_text(query))
    retriever["bm25"].k = k
    bm25_docs = retriever["bm25"].invoke(query_clean)

    # Semantic results
    sem_results = retriever["faiss"].similarity_search_with_score(query, k=k)
    sem_docs = [doc for doc, _ in sem_results]

    # Weighted combination: BM25 rank score + semantic rank score
    scores = {}
    doc_map = {}

    bm25_w = retriever["bm25_weight"]
    sem_w = retriever["semantic_weight"]

    # --- MERGE: collect docs from both retrievers into scores/doc_map dicts ---
    for rank, doc in enumerate(bm25_docs):
        key = doc.page_content[:100]
        scores[key] = scores.get(key, 0) + bm25_w * (1 / (rank + 1))
        doc_map[key] = doc

    # same key = duplicate gets merged with combined score; different keys = unique docs from either retriever
    for rank, doc in enumerate(sem_docs):
        key = doc.page_content[:100]
        scores[key] = scores.get(key, 0) + sem_w * (1 / (rank + 1))
        doc_map[key] = doc

    # --- RE-RANK: sort by combined weighted score ---
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [doc_map[key] for key, _ in ranked[:k]]