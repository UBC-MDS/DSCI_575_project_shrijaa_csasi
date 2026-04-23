# src/bm25.py

import os
import pickle
from pathlib import Path
from langchain_community.retrievers import BM25Retriever
from src.utils import load_documents, preprocess_text
from src.s3_utils import download_file

# Paths
_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH  = str(_ROOT / "data/processed/documents.parquet")
INDEX_PATH = str(_ROOT / "data/processed/bm25_index.pkl")
CORPUS_PATH = str(_ROOT / "data/processed/bm25_corpus.pkl")

# Build BM25 Index
def build_bm25(documents):
    """Tokenizes documents and builds BM25 index. Returns retriever and tokenized corpus."""
    tokenized_corpus = []
    # Apply preprocessing
    for doc in documents:
        doc.metadata["text_clean"] = doc.page_content  
        tokens = preprocess_text(doc.page_content)
        tokenized_corpus.append(tokens)
        doc.page_content = " ".join(tokens)  

    retriever = BM25Retriever.from_documents(documents)
    return retriever, tokenized_corpus

# Save BM25 Index
def save_bm25(retriever,tokenized_corpus):
    """Serializes the BM25 retriever and tokenized corpus to disk as pickle files."""
    with open(INDEX_PATH, "wb") as f:
        pickle.dump(retriever, f)
    with open(CORPUS_PATH, "wb") as f:
        pickle.dump(tokenized_corpus, f)

# Load BM25 Index
def load_bm25():
    """Deserializes and returns the BM25 retriever from disk.
       Falls back to S3 if file is missing locally."""
    
    # If file doesn't exist locally → download from S3
    if not os.path.exists(INDEX_PATH):
        download_file(
            bucket="dsci575-project-data",
            key="bm25_index.pkl",  
            local_path=INDEX_PATH
        )

    with open(INDEX_PATH, "rb") as f:
        return pickle.load(f)

# Search Function
def search(query, retriever, k=5):
    """Preprocesses the query, performs BM25 search, and returns top-k matching documents."""
    query_tokens = preprocess_text(query)
    query_clean = " ".join(query_tokens)

    retriever.k = k
    results = retriever.invoke(query_clean)

    return results

# Main (for building index)
if __name__ == "__main__":
    os.makedirs(str(_ROOT / "data/processed"), exist_ok=True)

    documents = load_documents(DATA_PATH)
    retriever, tokenized_corpus = build_bm25(documents)

    save_bm25(retriever,tokenized_corpus)

    print("BM25 index built and saved!")