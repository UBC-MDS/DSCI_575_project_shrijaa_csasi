# src/hybrid.py

from pathlib import Path
from langchain_community.retrievers import BM25Retriever
from src.bm25 import load_bm25
from src.semantic import load_faiss
from src.utils import preprocess_text


def build_hybrid_retriever(
    bm25_retriever,
    vector_store,
    bm25_weight=0.4,
    semantic_weight=0.6,
    k=5
):
    """
    Combines already-loaded BM25 and FAISS retrievers into a hybrid retriever.
    IMPORTANT: Do NOT load inside this function — pass cached objects instead.
    """
    bm25_retriever.k = k

    return {
        "bm25": bm25_retriever,
        "faiss": vector_store,
        "bm25_weight": bm25_weight,
        "semantic_weight": semantic_weight,
        "k": k
    }


def search_hybrid(query, retriever):
    """
    Combines BM25 and semantic results, deduplicates, and returns top-k Documents.
    """
    k = retriever["k"]

    # --- BM25 results ---
    bm25_docs = retriever["bm25"].invoke(query)

    # --- Semantic results ---
    sem_results = retriever["faiss"].similarity_search_with_score(query, k=k)
    sem_docs = [doc for doc, _ in sem_results]

    # --- Combine with weighted scoring ---
    scores = {}
    doc_map = {}

    bm25_w = retriever["bm25_weight"]
    sem_w = retriever["semantic_weight"]

    # BM25 scoring
    for rank, doc in enumerate(bm25_docs):
        key = hash(doc.page_content)  # safer than slicing
        scores[key] = scores.get(key, 0) + bm25_w * (1 / (rank + 1))
        doc_map[key] = doc

    # Semantic scoring
    for rank, doc in enumerate(sem_docs):
        key = hash(doc.page_content)
        scores[key] = scores.get(key, 0) + sem_w * (1 / (rank + 1))
        doc_map[key] = doc

    # --- Re-rank ---
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return [doc_map[key] for key, _ in ranked[:k]]