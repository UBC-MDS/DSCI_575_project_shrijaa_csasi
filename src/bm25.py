# src/bm25.py

import os
import re
import pickle
import pandas as pd
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document


# Paths
DATA_PATH = "data/processed/documents.parquet"
INDEX_PATH = "data/processed/bm25_index.pkl"


# Text Preprocessing
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # remove punctuation
    tokens = text.split()  # whitespace tokenizer
    return tokens

# Load Documents
def load_documents():
    df = pd.read_parquet(DATA_PATH)

    documents = [
        Document(
            page_content=row["page_content"],
            metadata=row["metadata"]
        )
        for _, row in df.iterrows()
    ]

    return documents

# Build BM25 Index
def build_bm25(documents):
    # Apply preprocessing
    for doc in documents:
        tokens = preprocess_text(doc.page_content)
        doc.page_content = " ".join(tokens)  

    retriever = BM25Retriever.from_documents(documents)
    return retriever

# Save BM25 Index
def save_bm25(retriever):
    with open(INDEX_PATH, "wb") as f:
        pickle.dump(retriever, f)

# Load BM25 Index
def load_bm25():
    with open(INDEX_PATH, "rb") as f:
        return pickle.load(f)

# Search Function
def search(query, retriever, k=5):
    query_tokens = preprocess_text(query)
    query_clean = " ".join(query_tokens)

    retriever.k = k
    results = retriever.invoke(query_clean)

    return results
# Main (for building index)
if __name__ == "__main__":
    os.makedirs("data/processed", exist_ok=True)

    documents = load_documents()
    retriever = build_bm25(documents)

    save_bm25(retriever)

    print("BM25 index built and saved!")