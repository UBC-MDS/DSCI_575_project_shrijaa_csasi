# src/bm25.py

import os
import re
import pickle
import pandas as pd
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from pathlib import Path
import nltk
from nltk.corpus import stopwords
nltk.download("stopwords", quiet=True)
STOPWORDS = set(stopwords.words("english"))

# Paths
_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH  = str(_ROOT / "data/processed/documents.parquet")
INDEX_PATH = str(_ROOT / "data/processed/bm25_index.pkl")
CORPUS_PATH = str(_ROOT / "data/processed/bm25_corpus.pkl")


# Text Preprocessing
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # remove punctuation
    tokens = text.split()  # whitespace tokenizer
    tokens = [token for token in tokens if token not in STOPWORDS]
    return tokens

# Load Documents
def load_documents():
    df = pd.read_parquet(DATA_PATH)
    df = df.dropna(subset=['text_clean'])
    return [
        Document(
            page_content=row['text_clean'],
            metadata={k: (v.tolist() if hasattr(v, 'tolist') else v)
                      for k, v in row.items() if k != 'text_clean'}
        )
        for _, row in df.iterrows()
    ]

# Build BM25 Index
def build_bm25(documents):
    tokenized_corpus = []
    # Apply preprocessing
    for doc in documents:
        doc.metadata["text_clean"] = doc.page_content  
        tokens = preprocess_text(doc.page_content)
        tokenized_corpus.append(tokens)
        doc.page_content = " ".join(tokens)  

    retriever = BM25Retriever.from_documents(documents)
    return retriever

# Save BM25 Index
def save_bm25(retriever,tokenized_corpus):
    with open(INDEX_PATH, "wb") as f:
        pickle.dump(retriever, f)
    with open(CORPUS_PATH, "wb") as f:
        pickle.dump(tokenized_corpus, f)

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
    os.makedirs(str(_ROOT / "data/processed"), exist_ok=True)

    documents = load_documents()
    retriever, tokenized_corpus = build_bm25(documents)

    save_bm25(retriever,tokenized_corpus)

    print("BM25 index built and saved!")